import frappe
from frappe import _
from frappe.utils import date_diff, nowdate, flt, get_datetime

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/sign_in"
        raise frappe.Redirect

    # --- أضف هذا السطر هنا ---
    context.csrf_token = frappe.sessions.get_csrf_token() 
    # ------------------------

    user = frappe.session.user
    
    # 1. Member & User Data
    if not frappe.db.exists("LMS Member", {"user": user}):
        frappe.local.flags.redirect_location = "/memberships"
        raise frappe.Redirect

    member = frappe.get_doc("LMS Member", {"user": user})
    
    # 🔥🔥🔥 الحل الجذري للمشكلة 🔥🔥🔥
    # هذا السطر يضمن أن النظام لا يرى "None" أبداً، بل يرى 0.0
    member.total_unpaid_fines = flt(member.total_unpaid_fines)
    
    user_doc = frappe.get_doc("User", user)
    
    context.member = member
    context.user_image = user_doc.user_image 

    # 2. Stats
    tier = frappe.get_doc("LMS Membership Type", member.membership_type)
    active_loans = frappe.db.count("LMS Loan", {"member": member.name, "status": "Active"})
    active_queues = frappe.db.count("LMS Queue", {"member": member.name, "status": "Waiting"})
    
    max_books = int(flt(tier.max_books)) # تحويل لانتجر للأمان
    used = active_loans + active_queues
    
    context.stats = {
        "tier": tier.tier_name,
        "max_books": max_books,
        "used": used,
        "progress": int((used / max_books) * 100) if max_books > 0 else 0
    }

    # 3. Active Loans
    loans = frappe.get_all("LMS Loan", 
        filters={"member": member.name, "status": "Active"}, 
        fields=["name", "book", "loan_date", "due_date"]
    )
    
    context.loans = []
    settings = frappe.get_single("LMS Settings")
    daily_fine = flt(settings.daily_fine)
    
    for l in loans:
        book = frappe.db.get_value("LMS Book", l.book, 
            ["name", "title", "title_ar", "author", "author_ar", "cover_image", "category", "description", "description_ar", "rating", "rental_price", "total_copies", "available_copies", "status"], 
            as_dict=True
        )
        
        if not book: continue

        days_diff = date_diff(l.due_date, nowdate())
        
        if days_diff < 0:
            l.msg = f"{abs(int(days_diff))} Days Late"
            l.color = "danger"
            l.fine_est = abs(int(days_diff)) * daily_fine
        else:
            l.msg = f"{int(days_diff)} Days Left"
            l.color = "success"
            l.fine_est = 0

        l.book_data = book
        l.book_data['user_action'] = 'return'
        
        # تنظيف أرقام الكتاب للمودال
        l.book_data['rating'] = flt(l.book_data.get('rating') or 0)
        l.book_data['rental_price'] = flt(l.book_data.get('rental_price') or 0)
        
        context.loans.append(l)

    # 4. Queues
    queues = frappe.get_all("LMS Queue", 
        filters={"member": member.name, "status": ["in", ["Waiting", "Ready to Pickup"]]}, 
        fields=["name", "book", "status", "creation"]
    )
    context.queues = []
    
    for q in queues:
        book = frappe.db.get_value("LMS Book", q.book, 
            ["name", "title", "title_ar", "author", "author_ar", "cover_image", "category", "description", "description_ar", "rating", "rental_price", "total_copies", "available_copies", "status"], 
            as_dict=True
        )
        
        if not book: continue

        if q.status == "Waiting":
            ahead = frappe.db.count("LMS Queue", {"book": q.book, "status": "Waiting", "creation": ["<", q.creation]})
            q.pos_label = f"#{ahead + 1} in Line"
            q.color = "primary"
            book['user_action'] = 'leave_queue'
        else:
            q.pos_label = "Ready to Pickup!"
            q.color = "success"
            book['user_action'] = 'claim'

        # تنظيف أرقام الكتاب
        book['rating'] = flt(book.get('rating') or 0)
        book['rental_price'] = flt(book.get('rental_price') or 0)

        q.book_data = book
        context.queues.append(q)

    # 5. History
    history = []
    
    # A. Loans
    old_loans = frappe.get_all("LMS Loan", filters={"member": member.name, "status": ["in", ["Returned", "Overdue"]]}, fields=["book", "status", "loan_date", "return_date"])
    for x in old_loans:
        b_title = frappe.db.get_value("LMS Book", x.book, "title") or "Unknown"
        history.append({
            "date": x.return_date or x.loan_date,
            "type": "Loan",
            "desc": f"Borrowed: {b_title}",
            "status": x.status,
            "icon": "fa-book"
        })

    # B. Transactions
    trans = frappe.get_all("LMS Transaction", filters={"member": member.name}, fields=["creation", "amount", "type", "reference"])
    for t in trans:
        history.append({
            "date": t.creation,
            "type": "Payment",
            "desc": f"Paid {int(flt(t.amount))} EGP ({t.reference})",
            "status": "Success",
            "icon": "fa-wallet"
        })

    # C. Queues
    old_queues = frappe.get_all("LMS Queue", filters={"member": member.name, "status": ["in", ["Completed", "Cancelled", "Expired"]]}, fields=["book", "status", "creation"])
    for q in old_queues:
        b_title = frappe.db.get_value("LMS Book", q.book, "title") or "Unknown"
        history.append({
            "date": q.creation,
            "type": "Reservation",
            "desc": f"Queue for: {b_title}",
            "status": q.status,
            "icon": "fa-hourglass"
        })

    history.sort(key=lambda x: str(x['date']), reverse=True)
    context.history = history