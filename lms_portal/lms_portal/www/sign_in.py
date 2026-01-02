import frappe
from frappe import _
from frappe.auth import LoginManager

no_cache = 1

def get_context(context):
    # FIX: Ensure headers dict exists
    if frappe.response.headers is None:
        frappe.response.headers = {}

    frappe.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    frappe.response.headers["Pragma"] = "no-cache"
    frappe.response.headers["Expires"] = "0"

    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/library"
        raise frappe.Redirect

    context.login_failed = False
    context.error_message = ""

    if frappe.request.method == "POST":
        email = frappe.form_dict.get("email", "").strip()
        password = frappe.form_dict.get("password", "").strip()
        
        try:
            login_manager = LoginManager()
            login_manager.authenticate(user=email, pwd=password)
            login_manager.post_login()
            
            frappe.db.commit()
            
            frappe.local.flags.redirect_location = "/library"
            raise frappe.Redirect

        except frappe.AuthenticationError:
            frappe.clear_messages()
            context.login_failed = True
            context.error_message = _("Invalid email or password")
            
        except Exception as e:
            frappe.clear_messages()
            context.login_failed = True
            context.error_message = str(e)
