import frappe

no_cache = 1

def get_context(context):
    # 1. الحارس: ممنوع دخول الزوار
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/sign_in"
        raise frappe.Redirect

    # 2. جلب المقالات (فقط المنشورة)
    # نجلب الحقول اللازمة للعرض الخارجي فقط لتسريع الأداء
    context.blogs = frappe.get_all(
        "LMS Blog",
        filters={"published": 1},
        fields=[
            "name", "route", "title_en", "title_ar", 
            "cover_image", "short_desc_en", "short_desc_ar", 
            "author", "read_time", "creation", "tags"
        ],
        order_by="creation desc"
    )