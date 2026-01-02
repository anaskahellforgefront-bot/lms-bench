import frappe
from frappe import _

def get_context(context):
    # 1. Fetch Published Reviews
    reviews = frappe.get_all("LMS Testimonial",
        filters={"published": 1},
        fields=["reviewer_name", "role", "reviewer_image", "content_en", "content_ar", "rating", "creation"],
        order_by="rating desc, creation desc" # Show highest rated first
    )
    
    # 2. Calculate Real Stats
    total = len(reviews)
    avg = 5.0
    if total > 0:
        avg = round(sum(r.rating for r in reviews) / total, 1)
        
    context.reviews = reviews
    context.stats = {
        "count": total,
        "avg": avg,
        "stars_5": len([r for r in reviews if r.rating == 5]),
        "happy": int((len([r for r in reviews if r.rating >= 4]) / total) * 100) if total > 0 else 100
    }

@frappe.whitelist(allow_guest=True)
def submit_review(rating, content):
    if frappe.session.user == "Guest":
        return {"status": "error", "message": "auth_required"}

    if not rating or not content:
        return {"status": "error", "message": "Missing fields"}

    try:
        user = frappe.get_doc("User", frappe.session.user)
        role = "Member"
        
        # Check membership
        if frappe.db.exists("LMS Member", {"user": user.name}):
            role = frappe.db.get_value("LMS Member", {"user": user.name}, "membership_type")

        doc = frappe.get_doc({
            "doctype": "LMS Testimonial",
            "reviewer_name": user.full_name,
            "reviewer_image": user.user_image,
            "role": role,
            "content_en": content,
            "content_ar": content,
            "rating": rating,
            "published": 1 # Publish immediately
        })
        doc.insert(ignore_permissions=True)
        return {"status": "success", "message": "Review submitted successfully!"}
        
    except Exception as e:
        frappe.log_error("Review Error", str(e))
        return {"status": "error", "message": "System Error"}