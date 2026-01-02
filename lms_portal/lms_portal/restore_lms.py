import frappe
from frappe.utils import now_datetime

def execute():
    frappe.flags.in_test = True
    print("\n" + "="*60)
    print("🚀 STARTING FULL LMS RESTORATION (FILE BASED EXECUTION)")
    print("="*60)

    # ==============================================================================
    # 1. CLEANUP
    # ==============================================================================
    print("\n🧹 Wiping old data...")
    tables = ["LMS Book", "LMS Member", "LMS Loan", "LMS Queue", "LMS Transaction", 
              "LMS Membership Type", "LMS Blog", "LMS Testimonial", "LMS Settings", "LMS OTP", "LMS FAQ"]
    for t in tables:
        try:
            frappe.db.sql(f"DELETE FROM `tab{t}`")
        except Exception:
            pass
    print("✅ Cleanup Done.")

    # ==============================================================================
    # 2. SCHEMA RECONSTRUCTION (Based on your DUMP analysis)
    # ==============================================================================
    print("\n🏗️ Rebuilding Schema...")

    # A. LMS OTP (Missing in dump but required for system)
    if not frappe.db.exists("DocType", "LMS OTP"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS OTP", "module": "LMS Portal", "custom": 1,
            "fields": [{"fieldname": "user", "fieldtype": "Data"}, {"fieldname": "otp", "fieldtype": "Data"}, {"fieldname": "expiry", "fieldtype": "Datetime"}],
            "permissions": [{"role": "Guest", "read": 1, "write": 1}]
        }).insert()

    # B. LMS FAQ (Required for Help Page)
    if not frappe.db.exists("DocType", "LMS FAQ"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS FAQ", "module": "LMS Portal", "custom": 1,
            "fields": [
                {"fieldname": "question", "fieldtype": "Data", "label": "Question"},
                {"fieldname": "question_en", "fieldtype": "Data", "label": "Question EN"},
                {"fieldname": "question_ar", "fieldtype": "Data", "label": "Question AR"},
                {"fieldname": "answer", "fieldtype": "Text Editor", "label": "Answer"},
                {"fieldname": "answer_en", "fieldtype": "Text Editor", "label": "Answer EN"},
                {"fieldname": "answer_ar", "fieldtype": "Text Editor", "label": "Answer AR"},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published", "default": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # C. LMS Book (With Publisher, Shelf, Preview URL)
    if not frappe.db.exists("DocType", "LMS Book"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS Book", "module": "LMS Portal", "custom": 1, "autoname": "field:isbn",
            "fields": [
                {"fieldname": "isbn", "fieldtype": "Data", "label": "ISBN", "unique": 1},
                {"fieldname": "title", "fieldtype": "Data", "label": "Title"},
                {"fieldname": "title_ar", "fieldtype": "Data", "label": "Title AR"},
                {"fieldname": "author", "fieldtype": "Data", "label": "Author"},
                {"fieldname": "author_ar", "fieldtype": "Data", "label": "Author AR"},
                {"fieldname": "category", "fieldtype": "Select", "label": "Category", "options": "Psychology\nBiography\nFinance\nProgramming\nSci-Fi\nBusiness\nSelf-Help\nFiction\nPhilosophy\nHistory\nNew Arrivals"},
                {"fieldname": "description", "fieldtype": "Text Editor", "label": "Desc"},
                {"fieldname": "description_ar", "fieldtype": "Text Editor", "label": "Desc AR"},
                {"fieldname": "cover_image", "fieldtype": "Attach Image", "label": "Cover"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Available\nBorrowed\nReserved"},
                {"fieldname": "rental_price", "fieldtype": "Currency", "label": "Rent Price"},
                {"fieldname": "full_price", "fieldtype": "Currency", "label": "Full Price"},
                {"fieldname": "total_copies", "fieldtype": "Int", "label": "Total"},
                {"fieldname": "available_copies", "fieldtype": "Int", "label": "Available"},
                {"fieldname": "rating", "fieldtype": "Float", "label": "Rating"},
                {"fieldname": "publisher", "fieldtype": "Data", "label": "Publisher"},
                {"fieldname": "shelf_location", "fieldtype": "Data", "label": "Shelf"},
                {"fieldname": "preview_url", "fieldtype": "Data", "label": "Preview URL"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # D. LMS Membership Type (With Currency, BG Image, Fine Discount)
    if not frappe.db.exists("DocType", "LMS Membership Type"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS Membership Type", "module": "LMS Portal", "custom": 1,
            "autoname": "field:tier_name",
            "fields": [
                {"fieldname": "tier_name", "fieldtype": "Data", "label": "Name", "unique": 1},
                {"fieldname": "tier_name_ar", "fieldtype": "Data", "label": "Name AR"},
                {"fieldname": "max_books", "fieldtype": "Int", "label": "Max Books"},
                {"fieldname": "max_days", "fieldtype": "Int", "label": "Max Days"},
                {"fieldname": "price", "fieldtype": "Currency", "label": "Price"},
                {"fieldname": "currency", "fieldtype": "Data", "label": "Currency", "default": "EGP"},
                {"fieldname": "description_en", "fieldtype": "Text", "label": "Desc EN"},
                {"fieldname": "description_ar", "fieldtype": "Text", "label": "Desc AR"},
                {"fieldname": "features_en", "fieldtype": "Code", "label": "Features EN", "options": "HTML"},
                {"fieldname": "features_ar", "fieldtype": "Code", "label": "Features AR", "options": "HTML"},
                {"fieldname": "bg_image", "fieldtype": "Attach Image", "label": "BG Image"},
                {"fieldname": "is_featured", "fieldtype": "Check", "label": "Featured"},
                {"fieldname": "fine_discount", "fieldtype": "Float", "label": "Fine Discount"},
                {"fieldname": "badge_color", "fieldtype": "Data", "label": "Badge Color"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # E. LMS Testimonial (With Published)
    if not frappe.db.exists("DocType", "LMS Testimonial"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS Testimonial", "module": "LMS Portal", "custom": 1,
            "fields": [
                {"fieldname": "reviewer_name", "fieldtype": "Data", "label": "Name"},
                {"fieldname": "reviewer_image", "fieldtype": "Attach Image", "label": "Image"},
                {"fieldname": "content_en", "fieldtype": "Text", "label": "Content EN"},
                {"fieldname": "content_ar", "fieldtype": "Text", "label": "Content AR"},
                {"fieldname": "rating", "fieldtype": "Float", "label": "Rating"},
                {"fieldname": "role", "fieldtype": "Data", "label": "Role"},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published", "default": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # F. LMS Blog (With Route, Author, Likes)
    if not frappe.db.exists("DocType", "LMS Blog"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS Blog", "module": "LMS Portal", "custom": 1,
            "fields": [
                {"fieldname": "title_en", "fieldtype": "Data", "label": "Title EN"},
                {"fieldname": "title_ar", "fieldtype": "Data", "label": "Title AR"},
                {"fieldname": "cover_image", "fieldtype": "Attach Image", "label": "Cover"},
                {"fieldname": "content_en", "fieldtype": "Text Editor", "label": "Content EN"},
                {"fieldname": "content_ar", "fieldtype": "Text Editor", "label": "Content AR"},
                {"fieldname": "short_desc_en", "fieldtype": "Small Text", "label": "Short EN"},
                {"fieldname": "short_desc_ar", "fieldtype": "Small Text", "label": "Short AR"},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published"},
                {"fieldname": "route", "fieldtype": "Data", "label": "Route"},
                {"fieldname": "read_time", "fieldtype": "Int", "label": "Read Time"},
                {"fieldname": "author", "fieldtype": "Data", "label": "Author"},
                {"fieldname": "likes", "fieldtype": "Int", "label": "Likes"},
                {"fieldname": "tags", "fieldtype": "Data", "label": "Tags"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # G. LMS Settings (With address fields, map, working hours)
    if not frappe.db.exists("DocType", "LMS Settings"):
        frappe.get_doc({
            "doctype": "DocType", "name": "LMS Settings", "module": "LMS Portal", "custom": 1, "issingle": 1,
            "fields": [
                {"fieldname": "daily_fine", "fieldtype": "Currency"},
                {"fieldname": "reservation_fee", "fieldtype": "Currency"},
                {"fieldname": "loan_period", "fieldtype": "Int"},
                {"fieldname": "reservation_time", "fieldtype": "Int"},
                {"fieldname": "otp_expiry", "fieldtype": "Int"},
                {"fieldname": "support_email", "fieldtype": "Data"},
                {"fieldname": "support_phone", "fieldtype": "Data"},
                {"fieldname": "address_en", "fieldtype": "Data"},
                {"fieldname": "address_ar", "fieldtype": "Data"},
                {"fieldname": "map_embed", "fieldtype": "Code", "options": "HTML"},
                {"fieldname": "working_hours_en", "fieldtype": "Data"},
                {"fieldname": "working_hours_ar", "fieldtype": "Data"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        }).insert()

    # H. Other Core Tables
    docs_defs = [
        ("LMS Member", {"autoname": "field:user", "fields": [
            {"fieldname": "user", "fieldtype": "Link", "options": "User", "unique": 1},
            {"fieldname": "full_name", "fieldtype": "Data"},
            {"fieldname": "membership_type", "fieldtype": "Link", "options": "LMS Membership Type"},
            {"fieldname": "status", "fieldtype": "Select", "options": "Active\nSuspended\nBanned"},
            {"fieldname": "total_unpaid_fines", "fieldtype": "Currency"},
            {"fieldname": "is_banned", "fieldtype": "Check"},
            {"fieldname": "phone", "fieldtype": "Data"}, {"fieldname": "bio", "fieldtype": "Text"}, {"fieldname": "join_date", "fieldtype": "Date"}
        ]}),
        ("LMS Loan", {"autoname": "hash", "fields": [
            {"fieldname": "book", "fieldtype": "Link", "options": "LMS Book"},
            {"fieldname": "member", "fieldtype": "Link", "options": "LMS Member"},
            {"fieldname": "loan_date", "fieldtype": "Date"}, {"fieldname": "due_date", "fieldtype": "Date"},
            {"fieldname": "return_date", "fieldtype": "Date"}, {"fieldname": "status", "fieldtype": "Select", "options": "Active\nReturned\nOverdue"},
            {"fieldname": "total_fine", "fieldtype": "Currency"}, {"fieldname": "daily_fine", "fieldtype": "Currency"}
        ]}),
        ("LMS Queue", {"autoname": "hash", "fields": [
            {"fieldname": "book", "fieldtype": "Link", "options": "LMS Book"},
            {"fieldname": "member", "fieldtype": "Link", "options": "LMS Member"},
            {"fieldname": "status", "fieldtype": "Select", "options": "Waiting\nReady to Pickup\nCompleted\nCancelled\nExpired"},
            {"fieldname": "fee_paid", "fieldtype": "Currency"}, {"fieldname": "is_paid", "fieldtype": "Check"},
            {"fieldname": "requested_at", "fieldtype": "Datetime"}, {"fieldname": "expires_at", "fieldtype": "Datetime"}
        ]}),
        ("LMS Transaction", {"fields": [
             {"fieldname": "member", "fieldtype": "Link", "options": "LMS Member"},
             {"fieldname": "amount", "fieldtype": "Currency"}, {"fieldname": "type", "fieldtype": "Data"},
             {"fieldname": "reference", "fieldtype": "Data"}, {"fieldname": "book", "fieldtype": "Link", "options": "LMS Book"}
        ]})
    ]
    for dname, dconf in docs_defs:
        if not frappe.db.exists("DocType", dname):
            dconf["doctype"] = "DocType"
            dconf["name"] = dname
            dconf["module"] = "LMS Portal"
            dconf["custom"] = 1
            frappe.get_doc(dconf).insert()

    frappe.db.commit()
    print("✅ Schema Built Successfully.")

    # ==============================================================================
    # 3. DATA INJECTION
    # ==============================================================================
    print("\n💉 Injecting Data...")

    # A. Users
    users = ["anaskahelloring@gmail.com", "omaroring2024@gmail.com", "suspended@test.com", "banned@test.com", "user2@test.com", "user1@test.com", "anas@elite.com"]
    for u in users:
        if not frappe.db.exists("User", u):
            frappe.get_doc({"doctype": "User", "email": u, "first_name": u.split("@")[0], "enabled": 1}).insert(ignore_permissions=True)

    # B. Membership Types
    mt_data = [
        {"name": "Elite", "tier_name": "Elite", "max_books": 20, "max_days": 60, "price": 500, "currency": "EGP", "tier_name_ar": "نخبة", "description_en": "Ultimate access.", "features_en": "<ul><li>20 Books</li></ul>"},
        {"name": "Gold", "tier_name": "Gold", "max_books": 10, "max_days": 30, "price": 250, "currency": "EGP", "tier_name_ar": "ذهبي", "description_en": "Best value.", "features_en": "<ul><li>10 Books</li></ul>"},
        {"name": "Standard", "tier_name": "Standard", "max_books": 3, "max_days": 14, "price": 100, "currency": "EGP", "tier_name_ar": "أساسي", "description_en": "Casual.", "features_en": "<ul><li>3 Books</li></ul>"}
    ]
    for d in mt_data:
        if not frappe.db.exists("LMS Membership Type", d['name']):
            frappe.get_doc({"doctype": "LMS Membership Type", **d}).insert()

    # C. Books (Full List)
    books_data = [
        {"isbn": "9326577052", "title": "Thinking, Fast & Slow", "author": "Daniel Kahneman", "category": "Psychology", "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 4, "publisher": "Global Press"},
        {"isbn": "7937631042", "title": "Elon Musk", "author": "Walter Isaacson", "category": "Biography", "cover_image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 4, "publisher": "Global Press"},
        {"isbn": "1862574952", "title": "Intelligent Investor", "author": "Benjamin Graham", "category": "Finance", "cover_image": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 3, "publisher": "Global Press"},
        {"isbn": "1740517470", "title": "Psychology of Money", "author": "Morgan Housel", "category": "Finance", "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6803436964", "title": "Pragmatic Programmer", "author": "Andrew Hunt", "category": "Programming", "cover_image": "https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 4, "publisher": "Global Press"},
        {"isbn": "3611414605", "title": "Leonardo da Vinci", "author": "Walter Isaacson", "category": "Biography", "cover_image": "https://images.unsplash.com/photo-1585863267072-a1f9435b5463?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "1128087556", "title": "Steve Jobs", "author": "Walter Isaacson", "category": "Biography", "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6338545765", "title": "Rich Dad Poor Dad", "author": "Robert Kiyosaki", "category": "Finance", "cover_image": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "9856083990", "title": "Man's Search", "author": "Viktor Frankl", "category": "Psychology", "cover_image": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "2074604157", "title": "Influence", "author": "Robert Cialdini", "category": "Psychology", "cover_image": "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "8772686197", "title": "Neuromancer", "author": "William Gibson", "category": "Sci-Fi", "cover_image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6638042774", "title": "Fahrenheit 451", "author": "Ray Bradbury", "category": "Sci-Fi", "cover_image": "https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6806673556", "title": "Dune", "author": "Frank Herbert", "category": "Sci-Fi", "cover_image": "https://images.unsplash.com/photo-1621351183012-e2f99720b1fe?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "2173898378", "title": "Start with Why", "author": "Simon Sinek", "category": "Business", "cover_image": "https://images.unsplash.com/photo-1554496225-ee9ebc82c3c9?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "2141788934", "title": "Deep Work", "author": "Cal Newport", "category": "Business", "cover_image": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "4603221101", "title": "Zero to One", "author": "Peter Thiel", "category": "Business", "cover_image": "https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "5606626479", "title": "Python Crash Course", "author": "Eric Matthes", "category": "Programming", "cover_image": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6512065396", "title": "Clean Code", "author": "Robert Martin", "category": "Programming", "cover_image": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "9298768863", "title": "Think & Grow Rich", "author": "Napoleon Hill", "category": "Self-Help", "cover_image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "3268587385", "title": "48 Laws of Power", "author": "Robert Greene", "category": "Self-Help", "cover_image": "https://images.unsplash.com/photo-1495640388908-05fa85288e61?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "2907321590", "title": "Atomic Habits", "author": "James Clear", "category": "Self-Help", "cover_image": "https://images.unsplash.com/photo-1585863267072-a1f9435b5463?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "3455967305", "title": "Crime & Punishment", "author": "Dostoevsky", "category": "Fiction", "cover_image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "4653845288", "title": "1984", "author": "George Orwell", "category": "Fiction", "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "8264215414", "title": "The Alchemist", "author": "Paulo Coelho", "category": "Fiction", "cover_image": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "8868291992", "title": "Beyond Good & Evil", "author": "Nietzsche", "category": "Philosophy", "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6577701588", "title": "The Republic", "author": "Plato", "category": "Philosophy", "cover_image": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "3264213149", "title": "Meditations", "author": "Marcus Aurelius", "category": "Philosophy", "cover_image": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "6377322883", "title": "Guns, Germs, Steel", "author": "Jared Diamond", "category": "History", "cover_image": "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "5760115901", "title": "The Silk Roads", "author": "Peter Frankopan", "category": "History", "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"},
        {"isbn": "9470973246", "title": "Sapiens", "author": "Yuval Harari", "category": "History", "cover_image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&h=900&fit=crop&q=80", "status": "Available", "rental_price": 100, "total_copies": 10, "available_copies": 5, "publisher": "Global Press"}
    ]
    for b in books_data:
        if not frappe.db.exists("LMS Book", b['isbn']):
            frappe.get_doc({"doctype": "LMS Book", **b}).insert(ignore_permissions=True)

    # D. LMS Members
    members = [
        {"user": "anaskahelloring@gmail.com", "full_name": "Anas Kahell", "membership_type": "Gold", "status": "Active"},
        {"user": "omaroring2024@gmail.com", "full_name": "omar", "membership_type": "Standard", "status": "Active"},
        {"user": "suspended@test.com", "full_name": "Lazy User", "membership_type": "Gold", "status": "Suspended"},
        {"user": "banned@test.com", "full_name": "Bad User", "membership_type": "Standard", "status": "Banned"},
        {"user": "user2@test.com", "full_name": "Sarah Smith", "membership_type": "Gold", "status": "Active"},
        {"user": "user1@test.com", "full_name": "John Doe", "membership_type": "Standard", "status": "Active"},
        {"user": "anas@elite.com", "full_name": "Anas Manager", "membership_type": "Elite", "status": "Active"}
    ]
    for m in members:
        if not frappe.db.exists("LMS Member", m['user']):
            frappe.get_doc({"doctype": "LMS Member", **m}).insert(ignore_links=True)

    # E. Blogs, Testimonials, Settings, FAQs
    blogs = [
        {"title_en": "The Art of Reading 5", "content_en": "<p>Content...</p>", "published": 1, "route": "blog-5", "author": "LMS", "likes": 0, "read_time": 5},
        {"title_en": "The Art of Reading 4", "content_en": "<p>Content...</p>", "published": 1, "route": "blog-4", "author": "LMS", "likes": 0, "read_time": 5},
        {"title_en": "The Art of Reading 3", "content_en": "<p>Content...</p>", "published": 1, "route": "blog-3", "author": "LMS", "likes": 0, "read_time": 5},
        {"title_en": "The Art of Reading 2", "content_en": "<p>Content...</p>", "published": 1, "route": "blog-2", "author": "LMS", "likes": 0, "read_time": 5},
        {"title_en": "The Art of Reading 1", "content_en": "<p>Content...</p>", "published": 1, "route": "blog-1", "author": "LMS", "likes": 0, "read_time": 5}
    ]
    for b in blogs:
        if not frappe.db.exists("LMS Blog", {"title_en": b["title_en"]}):
            frappe.get_doc({"doctype": "LMS Blog", **b}).insert(ignore_links=True)

    testis = [
        {"reviewer_name": "Anas Farag Kahell", "content_en": "dsdsdsd", "rating": 1.0, "published": 1},
        {"reviewer_name": "Ali", "content_en": "Great!", "rating": 1.0, "published": 1}
    ]
    for t in testis:
        if not frappe.db.exists("LMS Testimonial", {"reviewer_name": t["reviewer_name"]}):
            frappe.get_doc({"doctype": "LMS Testimonial", **t}).insert(ignore_links=True)

    if frappe.db.exists("LMS Settings", "LMS Settings"):
        s = frappe.get_doc("LMS Settings", "LMS Settings")
        s.daily_fine = 20
        s.reservation_fee = 20
        s.loan_period = 14
        s.address_en = "123 Knowledge St, Digital District, Cairo, Egypt"
        s.address_ar = "١٢٣ شارع المعرفة، الحي الرقمي، القاهرة، مصر"
        s.working_hours_en = "Sun - Thu: 9:00 AM - 10:00 PM"
        s.working_hours_ar = "الأحد - الخميس: ٩ صباحاً - ١٠ مساءً"
        s.support_email = "help@lms-elite.com"
        s.support_phone = "+20 100 200 3000"
        s.save()
    else:
        frappe.get_doc({
            "doctype": "LMS Settings", 
            "daily_fine": 20, "reservation_fee": 20, "loan_period": 14,
            "address_en": "123 Knowledge St, Digital District, Cairo, Egypt",
            "support_email": "help@lms-elite.com"
        }).insert()

    faqs = [
        {"question": "How to borrow?", "question_en": "How to borrow?", "answer": "<p>Click borrow</p>", "answer_en": "<p>Click borrow</p>", "published": 1},
        {"question": "Loan period?", "question_en": "Loan period?", "answer": "<p>14 days</p>", "answer_en": "<p>14 days</p>", "published": 1}
    ]
    for f in faqs:
        if not frappe.db.exists("LMS FAQ", {"question": f["question"]}):
            frappe.get_doc({"doctype": "LMS FAQ", **f}).insert(ignore_links=True)

    # F. Transactions, Loans, Queue (Exact Data)
    loans_data = [
        {"book": "9326577052", "member": "omaroring2024@gmail.com", "loan_date": "2025-12-28", "due_date": "2026-01-11", "status": "Active"},
        {"book": "7937631042", "member": "omaroring2024@gmail.com", "loan_date": "2025-12-28", "due_date": "2026-01-11", "status": "Active"},
        {"book": "1862574952", "member": "omaroring2024@gmail.com", "loan_date": "2025-12-28", "due_date": "2026-01-11", "status": "Active"},
        {"book": "1862574952", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-28", "due_date": "2026-01-27", "status": "Active"},
        {"book": "6803436964", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-28", "due_date": "2026-02-26", "status": "Active"},
        {"book": "1740517470", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-27", "due_date": "2026-02-25", "status": "Returned", "return_date": "2025-12-28"},
        {"book": "7937631042", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-27", "due_date": "2026-02-25", "status": "Returned", "return_date": "2025-12-27"},
        {"book": "0942565697810", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-27", "due_date": "2026-01-10", "status": "Active"},
        {"book": "8079262863759", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-27", "due_date": "2026-01-10", "status": "Active"},
        {"book": "8079262863759", "member": "anaskahelloring@gmail.com", "loan_date": "2025-12-27", "due_date": "2026-01-10", "status": "Returned", "return_date": "2025-12-27"}
    ]
    for l in loans_data:
        if frappe.db.exists("LMS Book", l['book']):
            frappe.get_doc({"doctype": "LMS Loan", **l}).insert(ignore_links=True)

    queue_data = [
        {"book": "0378316863838", "member": "anaskahelloring@gmail.com", "status": "Waiting", "fee_paid": 20, "is_paid": 1},
        {"book": "9713643057854", "member": "anaskahelloring@gmail.com", "status": "Cancelled", "fee_paid": 20, "is_paid": 1},
        {"book": "9723708932997", "member": "anaskahelloring@gmail.com", "status": "Cancelled", "fee_paid": 20, "is_paid": 1},
        {"book": "0378316863838", "member": "anaskahelloring@gmail.com", "status": "Expired", "fee_paid": 20, "is_paid": 1}
    ]
    for q in queue_data:
        frappe.get_doc({"doctype": "LMS Queue", **q}).insert(ignore_links=True)

    trans_data = [
        {"member": "omaroring2024@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "omaroring2024@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "omaroring2024@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 100, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 60, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for reserve"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for borrow"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for reserve"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for reserve"},
        {"member": "anaskahelloring@gmail.com", "amount": 20, "type": "Wallet Payment", "reference": "Payment for reserve"}
    ]
    for t in trans_data:
        frappe.get_doc({"doctype": "LMS Transaction", **t}).insert(ignore_links=True)

    frappe.db.commit()
    frappe.flags.in_test = False
    print("\n" + "="*60)
    print("🎉 EXECUTION COMPLETE! YOUR LIBRARY IS BACK!")
    print("="*60 + "\n")