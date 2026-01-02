import frappe
from frappe import _
import random
import string

no_cache = 1

def get_context(context):
    plans = frappe.get_all(
        "LMS Membership Type",
        fields=[
            "name", "tier_name", "tier_name_ar", 
            "price", "currency", 
            "description_en", "description_ar", 
            "features_en", "features_ar", 
            "badge_color", "is_featured"
        ],
        order_by="price asc"
    )
    
    context.plans = plans
    context.current_plan = None

    if frappe.session.user != "Guest":
        member = frappe.db.get_value("LMS Member", {"user": frappe.session.user}, ["membership_type"], as_dict=True)
        if member:
            context.current_plan = member.membership_type

@frappe.whitelist()
def initiate_payment(plan_name):
    """ إرسال أو إعادة إرسال الكود """
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login first"))

    plan = frappe.get_doc("LMS Membership Type", plan_name)
    user = frappe.session.user
    
    # توليد كود جديد
    payment_code = ''.join(random.choices(string.digits, k=6))
    cache_key = f"pay_otp:{user}"
    
    # الصلاحية 10 دقائق
    frappe.cache().set_value(cache_key, {"code": payment_code, "plan": plan_name}, expires_in_sec=600)
    
    # محاكاة الإيميل (طباعة في التيرمينال)
    print(f"\n💎 [LMS PAYMENT] Resend/New OTP for {user} -> Code: {payment_code}\n")
    
    return {"message": "Code Sent"}

@frappe.whitelist()
def verify_payment(otp):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login first"))

    user = frappe.session.user
    cache_key = f"pay_otp:{user}"
    cached_data = frappe.cache().get_value(cache_key)
    
    if not cached_data or str(cached_data.get("code")) != str(otp):
        frappe.throw(_("Invalid or Expired Payment Code"))

    target_plan = cached_data.get("plan")
    
    if frappe.db.exists("LMS Member", {"user": user}):
        frappe.db.set_value("LMS Member", {"user": user}, "membership_type", target_plan)
        frappe.db.commit()
        frappe.cache().delete_value(cache_key)
        
        return {"message": "Success"}
    else:
        frappe.throw(_("Member record not found"))