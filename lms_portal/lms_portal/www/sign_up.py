import frappe
from frappe import _
import random
import string

no_cache = 1

def get_context(context):
    if frappe.response.headers is None:
        frappe.response.headers = {}
    frappe.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    frappe.response.headers["Pragma"] = "no-cache"
    frappe.response.headers["Expires"] = "0"
    
    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/library"
        raise frappe.Redirect

@frappe.whitelist(allow_guest=True)
def send_otp(email, full_name):
    email = email.strip()
    if frappe.db.exists("User", email):
        frappe.throw(_("Account already exists. Please Sign In."))

    otp = ''.join(random.choices(string.digits, k=6))
    
    # الكود صالح لـ 5 دقائق في السيرفر لضمان وصوله
    cache_key = f"signup_otp:{email}"
    frappe.cache().set_value(cache_key, otp, expires_in_sec=300)
    
    subject = "LMS Verification Code"
    message = f"<h1>{otp}</h1><p>Valid for 5 minutes.</p>"
    frappe.sendmail(recipients=[email], subject=subject, message=message, now=True)
    
    print(f"OTP Sent: {otp}")
    return {"message": "OTP Sent"}

@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    email = email.strip()
    otp = str(otp).strip()
    cache_key = f"signup_otp:{email}"
    cached_otp = frappe.cache().get_value(cache_key)
    
    if not cached_otp or str(cached_otp).strip() != otp:
        frappe.throw(_("Invalid Code"))
    
    return {"message": "Verified"}

@frappe.whitelist(allow_guest=True)
def create_account(email, otp, password, full_name):
    email = email.strip()
    otp = str(otp).strip()
    cache_key = f"signup_otp:{email}"
    cached_otp = frappe.cache().get_value(cache_key)
    
    if not cached_otp or str(cached_otp).strip() != otp:
        frappe.throw(_("Invalid or Expired Code."))

    # 1. تجهيز بيانات المستخدم
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "enabled": 1,
        "send_welcome_email": 0,
        "new_password": password
    })
    
    # 🔥 التصحيح: إضافة صلاحية Website User للمستخدم الجديد 🔥
    user.append("roles", {
        "role": "Website User"
    })
    
    # حفظ المستخدم
    user.insert(ignore_permissions=True)

    # 2. إنشاء عضو المكتبة
    member = frappe.get_doc({
        "doctype": "LMS Member",
        "user": email,
        "full_name": full_name,
        "email": email,
        "membership_type": "Standard"
    })
    member.insert(ignore_permissions=True)
    
    # 3. تنظيف وإنهاء
    frappe.cache().delete_value(cache_key)
    frappe.db.commit()
    
    return {"message": "Created"}