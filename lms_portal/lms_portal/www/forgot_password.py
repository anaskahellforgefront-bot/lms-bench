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
def send_reset_otp(email):
    email = email.strip()
    if not frappe.db.exists("User", email):
        frappe.throw(_("No account found with this email."))

    otp = ''.join(random.choices(string.digits, k=6))
    
    cache_key = f"reset_otp:{email}"
    frappe.cache().set_value(cache_key, otp, expires_in_sec=300)
    
    subject = "Reset Your Password"
    message = f"<h1>{otp}</h1><p>Use this code to reset your password.</p>"
    frappe.sendmail(recipients=[email], subject=subject, message=message, now=True)
    
    print(f"Reset OTP: {otp}")
    return {"message": "OTP Sent"}

@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    email = email.strip()
    otp = str(otp).strip()
    cache_key = f"reset_otp:{email}"
    cached_otp = frappe.cache().get_value(cache_key)
    
    if not cached_otp or str(cached_otp).strip() != otp:
        frappe.throw(_("Invalid Code"))
    
    return {"message": "Verified"}

@frappe.whitelist(allow_guest=True)
def reset_password(email, otp, new_password):
    email = email.strip()
    otp = str(otp).strip()
    cache_key = f"reset_otp:{email}"
    cached_otp = frappe.cache().get_value(cache_key)
    
    if not cached_otp or str(cached_otp).strip() != otp:
        frappe.throw(_("Invalid or Expired OTP."))

    from frappe.utils.password import update_password
    update_password(email, new_password)
    
    frappe.cache().delete_value(cache_key)
    frappe.db.commit()
    
    return {"message": "Password Reset Successfully"}