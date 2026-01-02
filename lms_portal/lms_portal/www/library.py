

import frappe
from frappe import _
# تأكد من استدعاء هذه المكتبة
import frappe.sessions 

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/sign_in"
        raise frappe.Redirect

    # --- FIX START: إرسال التوكن يدوياً للقالب ---
    context.csrf_token = frappe.sessions.get_csrf_token()
    # --- FIX END ---

    user = frappe.session.user
    
    # 1. Member Data
    member = frappe.db.get_value("LMS Member", {"user": user}, ["name", "full_name", "membership_type"], as_dict=True)
    if not member:
        context.member = {"full_name": user, "membership_type": "Guest"}
        member_name = None
    else:
        context.member = member
        member_name = member.name

    # 2. Categories
    raw_cats = frappe.db.sql("SELECT DISTINCT category FROM `tabLMS Book` WHERE category != ''", as_dict=True)
    cat_map = {
        "Programming": "برمجة", "Self-Help": "تطوير الذات", "Finance": "مالية",
        "History": "تاريخ", "Sci-Fi": "خيال علمي", "Fiction": "روايات",
        "Psychology": "علم نفس", "Business": "أعمال", "Biography": "سير ذاتية",
        "Philosophy": "فلسفة", "New Arrivals": "وصل حديثاً"
    }
    for c in raw_cats:
        c['name'] = c['category']
        c['label_ar'] = cat_map.get(c['category'], c['category'])
    context.categories = raw_cats

    # 3. Books
    books = frappe.get_all(
        "LMS Book", 
        fields=[
            "name", "title", "title_ar", "author", "author_ar", 
            "cover_image", "status", "category", "rating", 
            "rental_price", "total_copies", "available_copies",
            "description", "description_ar"
        ], 
        order_by="creation desc"
    )

    # 4. Smart Logic (User Context)
    if member_name:
        # الكتب التي يملكها
        my_loans = [x.book for x in frappe.get_all("LMS Loan", {"member": member_name, "status": "Active"}, "book")]
        
        # الكتب التي في الطابور
        my_queues = frappe.get_all("LMS Queue", {"member": member_name, "status": ["in", ["Waiting", "Ready to Pickup"]]}, ["book", "status"])
        queue_map = {q.book: q.status for q in my_queues}

        for b in books:
            if b.name in my_loans:
                b.user_action = "return"
            elif b.name in queue_map:
                if queue_map[b.name] == "Ready to Pickup":
                    b.user_action = "claim" # جاء دوره
                else:
                    b.user_action = "leave_queue" # إلغاء حجز
            elif b.status == "Available":
                b.user_action = "borrow"
            else:
                b.user_action = "reserve"
    else:
        for b in books: b.user_action = "borrow"

    context.books = books