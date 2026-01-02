import frappe
from frappe import _
from frappe.utils import add_days, nowdate, date_diff, flt, getdate, now_datetime
import random
import string

# ==================================================================
# 1. MAIN API: INITIATE ACTION (FULLY SECURED & PERMISSION BYPASSED)
# ==================================================================
@frappe.whitelist()
def initiate_action(action, book_name=None):
    """
    هذه الدالة مسؤولة عن بدء أي عملية (استعارة، إرجاع، حجز).
    تم وضع ignore_permissions في البداية لضمان عدم توقف الكود.
    """
    user = frappe.session.user
    if user == "Guest": 
        frappe.throw(_("Please login first"))

    # 🔥 CRITICAL FIX: تفعيل وضع المدير مؤقتاً لتجاوز أخطاء 403
    frappe.flags.ignore_permissions = True

    try:
        # 1. جلب بيانات العضو
        member_name = frappe.db.get_value("LMS Member", {"user": user})
        if not member_name:
            frappe.throw(_("Member profile not found for this user."))
            
        member = frappe.get_doc("LMS Member", member_name)

        # 2. جلب الإعدادات (باستخدام get_single للأنواع الفردية)
        try:
            settings = frappe.get_single("LMS Settings")
        except:
            # محاولة بديلة في حالة حدوث مشكلة في الكاش
            settings = frappe.get_doc("LMS Settings", "LMS Settings")

        amount = 0.0
        otp_details = {"action": action, "book": book_name}
        
        # ----------------------------------
        # SCENARIO 1: LEAVE QUEUE (No OTP Required)
        # ----------------------------------
        if action == "leave_queue":
            execute_leave_queue(member, book_name)
            return {"status": "done", "message": "Reservation cancelled successfully."}

        # ----------------------------------
        # SCENARIO 2: ACTIONS REQUIRING OTP
        # ----------------------------------

        # --- A. BORROW (استعارة) ---
        if action == "borrow":
            check_eligibility(member) 
            book = frappe.get_doc("LMS Book", book_name)
            
            # التأكد هل الكتاب محجوز لهذا الشخص تحديداً؟
            is_reserved_for_me = check_if_reserved_for_me(book_name, member.name)
            
            if book.status != "Available" and not is_reserved_for_me:
                frappe.throw(_("Book is not available."))
                
            amount = book.rental_price

        # --- B. RETURN (إرجاع) ---
        elif action == "return":
            loan = frappe.db.get_value("LMS Loan", {"book": book_name, "member": member.name, "status": "Active"}, "name")
            if not loan: 
                frappe.throw(_("No active loan found for this book."))
            
            loan_doc = frappe.get_doc("LMS Loan", loan)
            otp_details["loan_name"] = loan
            
            # حساب الغرامات
            overdue = date_diff(nowdate(), loan_doc.due_date)
            if overdue > 0:
                fine = overdue * flt(settings.daily_fine)
                amount = fine
                otp_details["is_fine"] = 1
            else:
                amount = 0.0

        # --- C. RESERVE (حجز في الطابور) ---
        elif action == "reserve":
            if member.is_banned: 
                frappe.throw(_("Account is banned."))
            
            check_eligibility(member)

            if frappe.db.exists("LMS Queue", {"book": book_name, "member": member.name, "status": "Waiting"}):
                frappe.throw(_("You are already in the queue for this book."))
                
            amount = settings.reservation_fee

        # --- GENERATE OTP (إنشاء الرمز) ---
        otp = str(random.randint(100000, 999999))
        cache_key = f"lms_otp:{user}"
        final_amount = flt(amount)
        
        data_to_cache = {
            "code": otp,
            "amount": final_amount,
            "details": otp_details
        }
        
        # حفظ الرمز في الكاش لمدة 10 دقائق
        frappe.cache().set_value(cache_key, data_to_cache, expires_in_sec=600)

        # طباعة الرمز في التيرمينال للمطور
        print(f"\n🔐 OTP for {user} [{action}]: {otp} | Amount: {final_amount}\n")
        
        return {"status": "otp_sent", "amount": final_amount}

    except Exception as e:
        frappe.log_error(f"LMS Action Error: {str(e)}")
        raise e
        
    finally:
        # إرجاع الصلاحيات لوضعها الطبيعي بعد انتهاء الدالة
        frappe.flags.ignore_permissions = False


# ==================================================================
# 2. MAIN API: CONFIRM ACTION (OTP VERIFICATION)
# ==================================================================
@frappe.whitelist()
def confirm_action(otp, rating=0):
    user = frappe.session.user
    
    # 🔥 CRITICAL FIX: تفعيل وضع المدير هنا أيضاً
    frappe.flags.ignore_permissions = True
    
    try:
        cache_key = f"lms_otp:{user}"
        cached_data = frappe.cache().get_value(cache_key)
        
        if not cached_data:
            frappe.throw(_("OTP has expired. Please try again."))

        stored_code = str(cached_data.get("code")).strip()
        input_code = str(otp).strip()
        
        if stored_code != input_code:
            frappe.throw(_("Invalid OTP Code"))
            
        # استخراج تفاصيل العملية من الكاش
        action = cached_data["details"]["action"]
        book_name = cached_data["details"].get("book")
        amount = flt(cached_data.get("amount"))
        
        # جلب بيانات العضو
        member_name = frappe.db.get_value("LMS Member", {"user": user})
        member = frappe.get_doc("LMS Member", member_name)
        
        # تسجيل معاملة مالية إذا وجد مبلغ
        if amount > 0:
            create_transaction(member.name, amount, f"Payment for {action}")

        # تنفيذ العملية المطلوبة
        if action == "borrow":
            execute_borrow(member, book_name)
        
        elif action == "return":
            loan_name = cached_data["details"]["loan_name"]
            execute_return(member, loan_name, rating)
        
        elif action == "reserve":
            execute_reserve(member, book_name)

        # مسح الكاش بعد النجاح
        frappe.cache().delete_value(cache_key)
        return {"status": "success"}

    except Exception as e:
        frappe.log_error(f"LMS Confirm Error: {str(e)}")
        raise e

    finally:
        frappe.flags.ignore_permissions = False


# ==================================================================
# 3. HELPER FUNCTIONS (ALL PERMISSIONS BYPASSED)
# ==================================================================

def check_eligibility(member):
    if member.is_banned: 
        frappe.throw(_("Account Banned."))
    if member.total_unpaid_fines > 0: 
        frappe.throw(_("Unpaid fines exist."))
        
    active_loans = frappe.db.count("LMS Loan", {"member": member.name, "status": "Active"})
    active_queues = frappe.db.count("LMS Queue", {"member": member.name, "status": "Waiting"})
    total_active = active_loans + active_queues
    
    tier = frappe.get_doc("LMS Membership Type", member.membership_type)
    if total_active >= tier.max_books:
        frappe.throw(_("Limit Reached ({0}/{1}).").format(total_active, tier.max_books))

def check_if_reserved_for_me(book_name, member_name):
    return frappe.db.exists("LMS Queue", {
        "book": book_name, "member": member_name, "status": "Ready to Pickup"
    })

def execute_borrow(member, book_name):
    book = frappe.get_doc("LMS Book", book_name)
    tier = frappe.get_doc("LMS Membership Type", member.membership_type)
    
    # إغلاق الحجز في الطابور إذا وجد
    q_entry = frappe.db.get_value("LMS Queue", {"book": book_name, "member": member.name, "status": "Ready to Pickup"}, "name")
    if q_entry:
        frappe.db.set_value("LMS Queue", q_entry, "status", "Completed")

    # إنشاء سجل الاستعارة
    loan = frappe.get_doc({
        "doctype": "LMS Loan",
        "book": book_name,
        "member": member.name,
        "loan_date": nowdate(),
        "due_date": add_days(nowdate(), tier.max_days),
        "status": "Active"
    })
    loan.insert(ignore_permissions=True)
    
    # تحديث حالة الكتاب
    book.available_copies -= 1
    if book.available_copies <= 0:
        book.status = "Borrowed"
    book.save(ignore_permissions=True)

def execute_return(member, loan_name, rating):
    loan = frappe.get_doc("LMS Loan", loan_name)
    loan.status = "Returned"
    loan.return_date = nowdate()
    loan.save(ignore_permissions=True)
    
    book = frappe.get_doc("LMS Book", loan.book)
    
    # تحديث التقييم
    if rating and int(rating) > 0:
        current = book.rating or 5.0
        new_rating = (current + flt(rating)) / 2.0
        book.rating = round(new_rating, 1)
    
    # التحقق من الطابور (هل هناك شخص ينتظر؟)
    next_in_line = frappe.get_all("LMS Queue", 
        filters={"book": book.name, "status": "Waiting"}, 
        order_by="creation asc", limit=1
    )
    
    if next_in_line:
        # تخصيص الكتاب للشخص التالي
        q_doc = frappe.get_doc("LMS Queue", next_in_line[0].name)
        q_doc.status = "Ready to Pickup"
        q_doc.expires_at = add_days(now_datetime(), 1)
        q_doc.save(ignore_permissions=True)
        
        book.status = "Reserved"
        book.save(ignore_permissions=True)
    else:
        # إتاحة الكتاب للجميع
        book.status = "Available"
        book.available_copies += 1
        book.save(ignore_permissions=True)

def execute_reserve(member, book_name):
    fee = frappe.db.get_single_value("LMS Settings", "reservation_fee") or 0
    frappe.get_doc({
        "doctype": "LMS Queue",
        "book": book_name,
        "member": member.name,
        "requested_at": now_datetime(),
        "status": "Waiting",
        "is_paid": 1,
        "fee_paid": fee
    }).insert(ignore_permissions=True)

def execute_leave_queue(member, book_name):
    q_name = frappe.db.get_value("LMS Queue", {"book": book_name, "member": member.name, "status": "Waiting"})
    if q_name:
        frappe.db.set_value("LMS Queue", q_name, "status", "Cancelled")

def create_transaction(member_name, amount, ref):
    frappe.get_doc({
        "doctype": "LMS Transaction",
        "member": member_name,
        "type": "Wallet Payment",
        "amount": amount,
        "reference": ref
    }).insert(ignore_permissions=True)