import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/sign_in"
        raise frappe.Redirect

    user_doc = frappe.get_doc("User", frappe.session.user)
    
    member = frappe.db.get_value(
        "LMS Member", 
        {"user": frappe.session.user}, 
        ["name", "membership_type"], 
        as_dict=True
    )

    context.my_user = user_doc
    context.member = member or {"membership_type": "Standard"}

@frappe.whitelist()
def update_profile(first_name, last_name, bio=None):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login first"))

    user = frappe.get_doc("User", frappe.session.user)
    user.first_name = first_name
    user.last_name = last_name
    
    if hasattr(user, 'bio'):
        user.bio = bio
        
    user.save(ignore_permissions=True)
    
    if frappe.db.exists("LMS Member", {"user": frappe.session.user}):
        frappe.db.set_value("LMS Member", {"user": frappe.session.user}, "full_name", f"{first_name} {last_name}")
    
    frappe.db.commit()
    return {"message": "Profile Updated"}

@frappe.whitelist()
def upload_profile_image():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please login first"))
    
    if 'file' not in frappe.request.files:
        frappe.throw(_("No file attached"))
    
    file = frappe.request.files['file']
    fname = file.filename
    content = file.stream.read()

    saved_file = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "attached_to_doctype": "User",
        "attached_to_name": user,
        "content": content,
        "is_private": 0
    })
    saved_file.save(ignore_permissions=True)

    frappe.db.set_value("User", user, "user_image", saved_file.file_url)
    frappe.db.commit()

    return {"file_url": saved_file.file_url}

@frappe.whitelist()
def delete_profile_image():
    """ حذف الصورة والعودة للصورة الافتراضية """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please login first"))

    frappe.db.set_value("User", user, "user_image", "")
    frappe.db.commit()
    return {"message": "Image Deleted"}