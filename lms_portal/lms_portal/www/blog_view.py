import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/sign_in"
        raise frappe.Redirect

    blog_name = frappe.form_dict.get("name")
    
    if not blog_name or not frappe.db.exists("LMS Blog", blog_name):
        frappe.local.flags.redirect_location = "/blogs"
        raise frappe.Redirect

    # 1. جلب تفاصيل المقال
    blog = frappe.get_doc("LMS Blog", blog_name)
    
    # 2. جلب التعليقات + صورة المستخدم
    # نستخدم user.user_image لجلب الصورة من جدول المستخدم المرتبط
    comments = frappe.get_all(
        "LMS Blog Comment",
        filters={"article": blog_name},
        fields=["user_name", "comment", "date", "creation", "user.user_image as avatar"],
        order_by="creation desc"
    )

    context.blog = blog
    context.comments = comments

@frappe.whitelist()
def post_comment(blog_name, comment_text):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"))

    if not comment_text:
        frappe.throw(_("Comment cannot be empty"))

    # جلب بيانات المستخدم الحالي (الاسم والصورة)
    user_details = frappe.db.get_value("User", frappe.session.user, ["full_name", "user_image"], as_dict=True)
    current_user_name = user_details.full_name if user_details else "Unknown"
    current_user_image = user_details.user_image if user_details else None

    new_comment = frappe.get_doc({
        "doctype": "LMS Blog Comment",
        "article": blog_name,
        "user": frappe.session.user,
        "user_name": current_user_name,
        "comment": comment_text,
        "date": frappe.utils.now()
    })
    new_comment.insert(ignore_permissions=True)
    
    return {
        "message": "Saved",
        "user": new_comment.user_name,
        "avatar": current_user_image,  # نرجع رابط الصورة
        "date": frappe.utils.format_date(new_comment.date),
        "text": new_comment.comment
    }