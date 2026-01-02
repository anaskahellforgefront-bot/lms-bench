import frappe
from frappe.utils import now_datetime, add_days, getdate, add_months, flt, cint
import random

def init_db():
    print("🚀 STARTING THE ULTIMATE SYSTEM POPULATION...")
    print("⚠️  WARNING: This will WIPE all LMS data and rebuild a realistic ecosystem.")
    
    # قائمة المستخدمين الوهميين لإنشائهم
    dummy_users = [
        {"email": "student@lms.com", "first_name": "Sarah", "last_name": "Miller", "bio": "Avid reader and medical student."},
        {"email": "dev@lms.com", "first_name": "Karim", "last_name": "Ahmed", "bio": "Software engineer looking for clean code."},
        {"email": "bookworm@lms.com", "first_name": "Laila", "last_name": "Ezz", "bio": "History enthusiast."},
        {"email": "pro@lms.com", "first_name": "Omar", "last_name": "Kamal", "bio": "Business administration expert."}
    ]

    frappe.db.begin()

    # ====================================================================
    # PHASE 1: THE PURGE (تنظيف شامل مع الحفاظ على المستخدمين)
    # ====================================================================
    print("\n🧹 PHASE 1: Cleaning Slate...")
    
    tables = [
        "LMS Loan", "LMS Queue", "LMS Transaction", "LMS Blog Comment", 
        "LMS Contact Message", "LMS Book", "LMS Blog", "LMS Member", 
        "LMS Membership Type", "LMS Testimonial", "LMS FAQ"
    ]

    for dt in tables:
        frappe.db.sql(f"DELETE FROM `tab{dt}`")
        # تصفير العدادات
        frappe.db.sql(f"UPDATE `tabSeries` SET current = 0 WHERE name='{dt}-'")
        print(f"   ✓ Wiped {dt}")
    
    frappe.db.commit() # حفظ التنظيف

    # ====================================================================
    # PHASE 2: SETTINGS (الإعدادات الأساسية)
    # ====================================================================
    print("\n⚙️  PHASE 2: Configuring System Settings...")
    
    settings = frappe.get_doc("LMS Settings")
    settings.update({
        "support_email": "help@lms-elite.com",
        "support_phone": "+20 123 456 7890",
        "address_en": "Digital Knowledge Park, Building 5, Cairo, Egypt",
        "address_ar": "مجمع المعرفة الرقمي، مبنى ٥، القاهرة، مصر",
        "working_hours_en": "Daily: 09:00 AM - 10:00 PM",
        "working_hours_ar": "يومياً: ٠٩:٠٠ ص - ١٠:٠٠ م",
        "map_embed": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3455.123456789!2d31.123456!3d30.123456!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzDCsDA3JzM0LjUiTiAzMcKwMDcnMzQuNSJF!5e0!3m2!1sen!2seg!4v1600000000000!5m2!1sen!2seg" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
        "loan_period": 14,
        "daily_fine": 20.0,
        "reservation_fee": 50.0,
        "reservation_time": 24,
        "otp_expiry": 10
    })
    settings.save(ignore_permissions=True)
    frappe.db.commit()

    # ====================================================================
    # PHASE 3: MEMBERSHIP TIERS (الخطط)
    # ====================================================================
    print("\n💎 PHASE 3: Creating Membership Tiers...")
    
    plans = [
        {
            "tier_name": "Standard", "tier_name_ar": "الأساسية",
            "price": 0, "currency": "EGP", "max_books": 3, "max_days": 10,
            "badge_color": "#64748B", "is_featured": 0,
            "description_en": "Entry level access to the library.",
            "description_ar": "دخول أساسي للمكتبة.",
            "features_en": "<ul><li>Borrow 3 Books</li><li>10 Days Loan</li><li>Community Access</li></ul>",
            "features_ar": "<ul><li>استعارة ٣ كتب</li><li>مدة ١٠ أيام</li><li>دخول المجتمع</li></ul>"
        },
        {
            "tier_name": "Gold", "tier_name_ar": "الذهبية",
            "price": 250, "currency": "EGP", "max_books": 10, "max_days": 20,
            "badge_color": "#F59E0B", "is_featured": 1,
            "description_en": "Best value for regular readers.",
            "description_ar": "أفضل قيمة للقراء المنتظمين.",
            "features_en": "<ul><li>Borrow 10 Books</li><li>20 Days Loan</li><li>No Reservation Fees</li><li>Workshops Access</li></ul>",
            "features_ar": "<ul><li>استعارة ١٠ كتب</li><li>مدة ٢٠ يوماً</li><li>إعفاء من رسوم الحجز</li><li>دخول ورش العمل</li></ul>"
        },
        {
            "tier_name": "Elite", "tier_name_ar": "النخبة",
            "price": 600, "currency": "EGP", "max_books": 25, "max_days": 45,
            "badge_color": "#2563EB", "is_featured": 0,
            "description_en": "Unlimited knowledge without boundaries.",
            "description_ar": "معرفة بلا حدود.",
            "features_en": "<ul><li>Borrow 25 Books</li><li>45 Days Loan</li><li>VIP Lounge</li><li>Free Coffee</li><li>Dedicated Assistant</li></ul>",
            "features_ar": "<ul><li>استعارة ٢٥ كتاب</li><li>مدة ٤٥ يوماً</li><li>قاعة كبار الزوار</li><li>قهوة مجانية</li><li>مساعد شخصي</li></ul>"
        }
    ]

    plan_docs = {}
    for p in plans:
        doc = frappe.get_doc({"doctype": "LMS Membership Type", **p}).insert(ignore_permissions=True)
        plan_docs[p['tier_name']] = doc.name
        print(f"   + Plan: {p['tier_name']}")
    
    frappe.db.commit()

    # ====================================================================
    # PHASE 4: USERS & MEMBERS (إنشاء مجتمع الأعضاء)
    # ====================================================================
    print("\n👥 PHASE 4: Registering Members...")

    members_list = []

    # 1. Add current Administrator as Elite Member
    if not frappe.db.exists("LMS Member", {"user": frappe.session.user}):
        admin_member = frappe.get_doc({
            "doctype": "LMS Member",
            "user": frappe.session.user,
            "full_name": "System Administrator",
            "membership_type": plan_docs["Elite"],
            "status": "Active",
            "phone": "01000000000",
            "bio": "The library guardian."
        }).insert(ignore_permissions=True)
        members_list.append(admin_member.name)
        print("   + Member: Admin (Elite)")

    # 2. Create/Update Dummy Users and make them Members
    for u in dummy_users:
        # Check if User exists, if not create
        if not frappe.db.exists("User", u["email"]):
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": u["email"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "enabled": 1,
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
        
        # Create LMS Member profile
        if not frappe.db.exists("LMS Member", {"user": u["email"]}):
            # Assign random plan
            plan_name = random.choice(list(plan_docs.values()))
            mem = frappe.get_doc({
                "doctype": "LMS Member",
                "user": u["email"],
                "full_name": f"{u['first_name']} {u['last_name']}",
                "membership_type": plan_name,
                "status": "Active",
                "phone": f"010{random.randint(10000000, 99999999)}",
                "bio": u["bio"]
            }).insert(ignore_permissions=True)
            members_list.append(mem.name)
            print(f"   + Member: {u['first_name']} ({plan_name})")

    frappe.db.commit()

    # ====================================================================
    # PHASE 5: BOOKS (المكتبة الضخمة)
    # ====================================================================
    print("\n📚 PHASE 5: Stocking Shelves (Books)...")

    # صور حقيقية ثابتة لضمان الجودة
    covers = {
        "code": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&q=80",
        "history": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=600&q=80",
        "novel": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&q=80",
        "biz": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=600&q=80",
        "self": "https://images.unsplash.com/photo-1555449372-2bd056488d75?w=600&q=80"
    }

    raw_books = [
        # Programming
        {"title": "Clean Code", "ar": "الكود النظيف", "auth": "Robert Martin", "cat": "Programming", "img": covers["code"]},
        {"title": "The Pragmatic Programmer", "ar": "المبرمج البراجماتي", "auth": "Andrew Hunt", "cat": "Programming", "img": covers["code"]},
        {"title": "Python Crash Course", "ar": "دورة بايثون المكثفة", "auth": "Eric Matthes", "cat": "Programming", "img": covers["code"]},
        # Fiction
        {"title": "The Alchemist", "ar": "الخيميائي", "auth": "Paulo Coelho", "cat": "Fiction", "img": covers["novel"]},
        {"title": "1984", "ar": "١٩٨٤", "auth": "George Orwell", "cat": "Fiction", "img": covers["novel"]},
        {"title": "Crime and Punishment", "ar": "الجريمة والعقاب", "auth": "Dostoevsky", "cat": "Fiction", "img": covers["novel"]},
        # Business
        {"title": "Zero to One", "ar": "من الصفر إلى الواحد", "auth": "Peter Thiel", "cat": "Business", "img": covers["biz"]},
        {"title": "Rich Dad Poor Dad", "ar": "الأب الغني والأب الفقير", "auth": "Robert Kiyosaki", "cat": "Business", "img": covers["biz"]},
        # History
        {"title": "Sapiens", "ar": "العاقل", "auth": "Yuval Harari", "cat": "History", "img": covers["history"]},
        # Self Help
        {"title": "Atomic Habits", "ar": "العادات الذرية", "auth": "James Clear", "cat": "Self-Help", "img": covers["self"]}
    ]

    created_books = []

    # Multiply books to have a larger library (creates copies like Vol 1, Vol 2...)
    for i in range(1, 4): 
        for b in raw_books:
            suffix = "" if i == 1 else f" (Vol. {i})"
            suffix_ar = "" if i == 1 else f" (مجلد {i})"
            
            isbn = f"ISBN-{random.randint(1000,9999)}-{random.randint(10,99)}-{i}"
            
            book_doc = frappe.get_doc({
                "doctype": "LMS Book",
                "isbn": isbn,
                "title": f"{b['title']}{suffix}",
                "title_ar": f"{b['ar']}{suffix_ar}",
                "author": b["auth"],
                "author_ar": b["auth"], # Simplification
                "category": b["cat"],
                "status": "Available", # Will change in simulation
                "cover_image": b["img"],
                "description": f"<p>This is a masterpiece in {b['cat']}. Essential reading.</p>",
                "description_ar": f"<p>هذا الكتاب تحفة فنية في مجال {b['ar']}. قراءة ضرورية.</p>",
                "rating": round(random.uniform(3.5, 5.0), 1),
                "total_copies": random.randint(3, 8),
                "available_copies": 0, # Calculated automatically usually, but we set initial
                "rental_price": random.choice([20, 30, 50, 60]),
                "full_price": random.choice([300, 450, 600]),
                "publisher": "Global Pub House"
            })
            # Reset available to total initially
            book_doc.available_copies = book_doc.total_copies
            book_doc.insert(ignore_permissions=True)
            created_books.append(book_doc.name)
    
    print(f"   ✓ Created {len(created_books)} Books.")
    frappe.db.commit()

    # ====================================================================
    # PHASE 6: SIMULATION (محاكاة الحياة: استعارات، تأخير، قوائم انتظار)
    # ====================================================================
    print("\n🎲 PHASE 6: Simulating Library Activity (Transactions & Loans)...")
    
    for book_name in created_books:
        # Roll a dice for what happens to this book
        scenario = random.choice(["avail", "borrowed", "late", "returned", "queue"])
        book = frappe.get_doc("LMS Book", book_name)
        member = random.choice(members_list)

        if scenario == "avail":
            continue # Leave as is

        elif scenario in ["borrowed", "late"]:
            if book.available_copies > 0:
                # Create Loan
                loan_date = add_days(now_datetime(), -random.randint(1, 20))
                due_date = add_days(loan_date, 14)
                
                status = "Active"
                # If 'late', make loan date older
                if scenario == "late":
                    loan_date = add_days(now_datetime(), -30)
                    due_date = add_days(loan_date, 14) # Was due 16 days ago
                
                frappe.get_doc({
                    "doctype": "LMS Loan",
                    "book": book.name,
                    "member": member,
                    "loan_date": loan_date,
                    "due_date": due_date,
                    "status": "Active" # Late is calculated by logic, status remains Active
                }).insert(ignore_permissions=True)
                
                # Update book status
                book.available_copies -= 1
                book.status = "Borrowed" if book.available_copies == 0 else "Available"
                book.save(ignore_permissions=True)
                
                print(f"   -> Loan created for {book.title} ({scenario})")

        elif scenario == "returned":
            # Create a completed loan history
            l_date = add_days(now_datetime(), -40)
            frappe.get_doc({
                "doctype": "LMS Loan",
                "book": book.name,
                "member": member,
                "loan_date": l_date,
                "due_date": add_days(l_date, 14),
                "return_date": add_days(l_date, 10),
                "status": "Returned"
            }).insert(ignore_permissions=True)
            
            # 🔥 التعديل هنا: استخدام Wallet Payment بدلاً من Book Rental
            frappe.get_doc({
                "doctype": "LMS Transaction",
                "member": member,
                "amount": book.rental_price,
                "type": "Wallet Payment", 
                "reference": f"PAY-{random.randint(1000,9999)}",
                "book": book.name
            }).insert(ignore_permissions=True)

        elif scenario == "queue":
            # Make book unavailable first (Simulate all copies taken)
            book.available_copies = 0
            book.status = "Borrowed"
            book.save(ignore_permissions=True)
            
            # Add to Queue
            frappe.get_doc({
                "doctype": "LMS Queue",
                "book": book.name,
                "member": member,
                "status": "Waiting",
                "requested_at": now_datetime(),
                "is_paid": 1,
                "fee_paid": 50
            }).insert(ignore_permissions=True)
            print(f"   -> Queued {book.title}")

    frappe.db.commit()

    # ====================================================================
    # PHASE 7: BLOGS & CONTENT (المحتوى التحريري)
    # ====================================================================
    print("\n✍️ PHASE 7: Publishing Blogs & Comments...")
    
    blogs = [
        {
            "t": "The Future of Digital Libraries", "tar": "مستقبل المكتبات الرقمية",
            "img": "https://images.unsplash.com/photo-1507842217121-9e9f14781f32?w=600&q=80",
            "cat": "Technology"
        },
        {
            "t": "Why Reading Matters", "tar": "لماذا القراءة مهمة",
            "img": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=600&q=80",
            "cat": "Education"
        }
    ]

    for b in blogs:
        blog = frappe.get_doc({
            "doctype": "LMS Blog",
            "title_en": b["t"], "title_ar": b["tar"],
            "route": b["t"].lower().replace(" ", "-"),
            "cover_image": b["img"],
            "short_desc_en": "An insightful look into the subject.",
            "short_desc_ar": "نظرة متعمقة في هذا الموضوع.",
            "content_en": "<h3>Introduction</h3><p>Content goes here...</p>",
            "content_ar": "<h3>مقدمة</h3><p>المحتوى هنا...</p>",
            "author": "Editor In Chief",
            "read_time": 5,
            "published": 1,
            "tags": b["cat"]
        }).insert(ignore_permissions=True)

        # Add Comments
        for _ in range(2):
            commode_user = random.choice(dummy_users)
            frappe.get_doc({
                "doctype": "LMS Blog Comment",
                "article": blog.name,
                "user": commode_user["email"],
                "user_name": commode_user["first_name"],
                "comment": "Great article! Thanks for sharing.",
                "date": now_datetime()
            }).insert(ignore_permissions=True)

    # ====================================================================
    # PHASE 8: STATIC PAGES (FAQ, Testimonials, Contact)
    # ====================================================================
    print("\nℹ️ PHASE 8: Finalizing Static Content...")
    
    # FAQ
    frappe.get_doc({"doctype": "LMS FAQ", "question_en": "How to borrow?", "answer_en": "Click borrow.", "question_ar": "كيف استعير؟", "answer_ar": "اضغط استعارة", "published": 1, "sort_order": 1}).insert(ignore_permissions=True)
    
    # Testimonial
    frappe.get_doc({"doctype": "LMS Testimonial", "reviewer_name": "Ali Hassan", "role": "Student", "content_en": "Best library ever!", "content_ar": "أفضل مكتبة!", "rating": 5, "published": 1}).insert(ignore_permissions=True)
    
    # Contact Msg
    frappe.get_doc({"doctype": "LMS Contact Message", "full_name": "Stranger", "email": "stranger@gmail.com", "subject": "Hello", "message": "Is it open on Friday?", "status": "New"}).insert(ignore_permissions=True)

    frappe.db.commit()

    print("\n✅✅✅ POPULATION COMPLETE! The system is now alive.")