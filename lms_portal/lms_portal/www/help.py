import frappe
from frappe import _

no_cache = 1

def get_context(context):
    # 1. جلب إعدادات التواصل (للعرض في الصفحة)
    context.settings = frappe.get_single("LMS Settings")

    # 2. جلب الأسئلة الشائعة (المنشورة فقط)
    context.faqs = frappe.get_all(
        "LMS FAQ",
        filters={"published": 1},
        fields=["question_en", "question_ar", "answer_en", "answer_ar", "category"],
        order_by="sort_order asc"
    )

@frappe.whitelist()
def send_message(full_name, email, subject, message):
    """ API لاستقبال رسائل العملاء """
    
    # تحقق بسيط
    if not full_name or not email or not message:
        frappe.throw(_("All fields are required"))

    # هل المستخدم عضو مسجل؟
    is_member = 1 if frappe.db.exists("LMS Member", {"user": frappe.session.user}) else 0
    
    # إنشاء السجل في النظام
    doc = frappe.get_doc({
        "doctype": "LMS Contact Message",
        "full_name": full_name,
        "email": email,
        "subject": subject,
        "message": message,
        "status": "New",
        "is_member": is_member
    })
    doc.insert(ignore_permissions=True)
    
    # (اختياري) إرسال إشعار للمشرفين هنا
    
    return {"message": "Sent", "id": doc.name}