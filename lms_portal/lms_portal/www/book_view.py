import frappe
from frappe import _
import random
import string

no_cache = 1

def get_context(context):
    book_name = frappe.form_dict.get("name")
    
    # التحقق من وجود الكتاب
    if not book_name or not frappe.db.exists("LMS Book", book_name):
        frappe.local.flags.redirect_location = "/library"
        raise frappe.Redirect

    # 1. تفاصيل الكتاب
    book = frappe.get_doc("LMS Book", book_name)
    context.book = book

    # 2. حالة العضو الحالية (التصحيح هنا)
    user = frappe.session.user
    
    # قيم افتراضية لتجنب الأخطاء في القالب
    context.has_active_loan = False
    context.in_queue = False
    context.queue_position = 0
    
    if user != "Guest":
        # 🔥 الخطوة الحاسمة: جلب اسم العضو (ID) المرتبط بهذا المستخدم
        member_name = frappe.db.get_value("LMS Member", {"user": user})
        
        if member_name:
            # أ) التحقق من الاستعارة النشطة باستخدام كود العضو الصحيح
            context.has_active_loan = frappe.db.count("LMS Loan", {
                "book": book_name, 
                "member": member_name, 
                "status": "Active"
            })
            
            # ب) التحقق من الطابور باستخدام كود العضو الصحيح
            queue_entry = frappe.db.get_value("LMS Queue", {
                "book": book_name,
                "member": member_name,
                "status": ["in", ["Waiting", "Ready to Pickup"]]
            }, "name")
            
            if queue_entry:
                context.in_queue = True
                # حساب الدور في الطابور
                older_entries = frappe.db.count("LMS Queue", {
                    "book": book_name,
                    "status": "Waiting",
                    "creation": ["<", frappe.db.get_value("LMS Queue", queue_entry, "creation")]
                })
                context.queue_position = older_entries + 1

@frappe.whitelist()
def initiate_borrow(book_name):
    """ زر الاستعارة: يرسل OTP """
    if frappe.session.user == "Guest": frappe.throw(_("Login required"))
    
    otp = ''.join(random.choices(string.digits, k=6))
    cache_key = f"borrow_otp:{frappe.session.user}"
    frappe.cache().set_value(cache_key, {"code": otp, "book": book_name, "action": "Borrow"}, expires_in_sec=600)
    
    # محاكاة إرسال الإيميل (طباعة في التيرمينال)
    print(f"📖 Borrow OTP for {frappe.session.user}: {otp}")
    
    return {"status": "success"}

@frappe.whitelist()
def confirm_borrow(otp):
    """ تأكيد الاستعارة """
    user = frappe.session.user
    cache_key = f"borrow_otp:{user}"
    data = frappe.cache().get_value(cache_key)
    
    if not data or str(data.get("code")) != str(otp):
        frappe.throw(_("Invalid OTP"))
        
    book_name = data.get("book")
    
    # استدعاء دالة العمليات المركزية لضمان توحيد المنطق
    from lms_portal.library_ops import initiate_action
    return initiate_action("borrow", book_name)