import frappe

def execute():
    frappe.db.begin()
    
    print("\n🚧 STARTING FULL SCHEMA SETUP...\n")

    # ========================================================
    # 1. إنشاء جدول آراء العملاء (LMS Testimonial) - للتسويق
    # ========================================================
    if not frappe.db.exists("DocType", "LMS Testimonial"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "LMS Portal",
            "custom": 1,
            "name": "LMS Testimonial",
            "sort_field": "creation",
            "sort_order": "DESC",
            "fields": [
                {"fieldname": "reviewer_name", "fieldtype": "Data", "label": "Reviewer Name", "reqd": 1},
                {"fieldname": "reviewer_image", "fieldtype": "Attach Image", "label": "Reviewer Image"},
                {"fieldname": "role", "fieldtype": "Data", "label": "Role (e.g. Software Engineer)", "default": "Member"},
                {"fieldname": "content_en", "fieldtype": "Small Text", "label": "Review (English)", "reqd": 1},
                {"fieldname": "content_ar", "fieldtype": "Small Text", "label": "Review (Arabic)", "reqd": 1},
                {"fieldname": "rating", "fieldtype": "Rating", "label": "Rating", "default": 5},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published", "default": 1}
            ],
            "permissions": [{"role": "All", "read": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("✅ LMS Testimonial DocType Created.")

    # ========================================================
    # 2. تحديث إعدادات النظام (إضافة عربون الحجز)
    # ========================================================
    if frappe.db.exists("DocType", "LMS Settings"):
        doc = frappe.get_doc("DocType", "LMS Settings")
        fields = [f.fieldname for f in doc.fields]
        
        if "reservation_fee" not in fields:
            doc.append("fields", {
                "fieldname": "reservation_fee",
                "fieldtype": "Currency",
                "label": "Queue Reservation Fee (EGP)",
                "default": 20,
                "insert_after": "daily_fine"
            })
            doc.save()
            print("✅ LMS Settings Updated (Reservation Fee Added).")
            
            # Set Default Value
            settings = frappe.get_single("LMS Settings")
            settings.reservation_fee = 20
            settings.save()

    # ========================================================
    # 3. تحديث العضو (LMS Member) - للحظر والغرامات
    # ========================================================
    if frappe.db.exists("DocType", "LMS Member"):
        doc = frappe.get_doc("DocType", "LMS Member")
        fields = [f.fieldname for f in doc.fields]
        
        # حقل الحظر
        if "is_banned" not in fields:
            doc.append("fields", {
                "fieldname": "is_banned", "fieldtype": "Check", "label": "Is Banned", 
                "insert_after": "status", "default": 0
            })
        
        # حقل إجمالي الغرامات المستحقة (للعرض السريع)
        if "total_unpaid_fines" not in fields:
            doc.append("fields", {
                "fieldname": "total_unpaid_fines", "fieldtype": "Currency", "label": "Total Unpaid Fines", 
                "read_only": 1, "default": 0, "insert_after": "membership_type"
            })
            
        doc.save()
        print("✅ LMS Member Updated (Ban & Fines Tracking).")

    # ========================================================
    # 4. تحديث طابور الانتظار (LMS Queue) - للدفع
    # ========================================================
    if frappe.db.exists("DocType", "LMS Queue"):
        doc = frappe.get_doc("DocType", "LMS Queue")
        fields = [f.fieldname for f in doc.fields]
        
        if "fee_paid" not in fields:
            doc.append("fields", {
                "fieldname": "fee_paid", "fieldtype": "Currency", "label": "Reservation Fee Paid", 
                "read_only": 1, "insert_after": "status"
            })
            doc.append("fields", {
                "fieldname": "is_paid", "fieldtype": "Check", "label": "Is Paid?", 
                "read_only": 1, "default": 0, "insert_after": "fee_paid"
            })
        
        doc.save()
        print("✅ LMS Queue Updated (Payment Tracking).")

    # ========================================================
    # 5. إضافة بيانات تجريبية للآراء (Testimonials)
    # ========================================================
    frappe.db.sql("DELETE FROM `tabLMS Testimonial`")
    
    testimonials = [
        {
            "name": "Ahmed Ali", "role": "Senior Developer",
            "en": "This library changed my career. The collection of tech books is unmatched.",
            "ar": "هذه المكتبة غيرت مساري المهني. مجموعة الكتب التقنية لا مثيل لها.",
            "rating": 5
        },
        {
            "name": "Sarah Miller", "role": "Student",
            "en": "The reservation system is so smooth. I love the notifications!",
            "ar": "نظام الحجز سلس جداً. أحببت نظام الإشعارات والتنبيهات!",
            "rating": 5
        },
        {
            "name": "Mohamed Samy", "role": "Entrepreneur",
            "en": "Elite Membership is worth every penny. VIP Lounge is amazing.",
            "ar": "عضوية النخبة تستحق كل جنيه. قاعة كبار الزوار مذهلة.",
            "rating": 4
        }
    ]
    
    for t in testimonials:
        doc = frappe.get_doc({
            "doctype": "LMS Testimonial",
            "reviewer_name": t["name"],
            "role": t["role"],
            "content_en": t["en"],
            "content_ar": t["ar"],
            "rating": t["rating"],
            "published": 1
        })
        doc.insert(ignore_permissions=True)
        
    print("✅ Testimonials Generated.")

    frappe.db.commit()
    print("\n🚀 FULL SCHEMA SETUP COMPLETE.\n")