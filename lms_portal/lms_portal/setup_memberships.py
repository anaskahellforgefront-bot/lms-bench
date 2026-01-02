import frappe

def execute():
    frappe.db.begin()
    
    # 1. تنظيف الجدول القديم تماماً (Wipe Data)
    frappe.db.sql("DELETE FROM `tabLMS Membership Type`")
    
    # 2. تحديث هيكل DocType لإضافة الحقول العربية
    doctype = "LMS Membership Type"
    if frappe.db.exists("DocType", doctype):
        doc = frappe.get_doc("DocType", doctype)
        
        # قائمة الحقول الجديدة (ثنائية اللغة)
        new_fields = [
            {"fieldname": "tier_name_ar", "fieldtype": "Data", "label": "Tier Name (Arabic)", "insert_after": "tier_name"},
            {"fieldname": "price", "fieldtype": "Currency", "label": "Price", "insert_after": "tier_name_ar", "reqd": 1},
            {"fieldname": "currency", "fieldtype": "Data", "label": "Currency", "default": "EGP", "insert_after": "price"},
            
            {"fieldname": "description_en", "fieldtype": "Small Text", "label": "Desc (EN)", "insert_after": "currency"},
            {"fieldname": "description_ar", "fieldtype": "Small Text", "label": "Desc (AR)", "insert_after": "description_en"},
            
            {"fieldname": "features_en", "fieldtype": "Text Editor", "label": "Features (EN)", "insert_after": "description_ar"},
            {"fieldname": "features_ar", "fieldtype": "Text Editor", "label": "Features (AR)", "insert_after": "features_en"},
            
            {"fieldname": "is_featured", "fieldtype": "Check", "label": "Is Best Value?", "insert_after": "badge_color"}
        ]
        
        existing_fields = [f.fieldname for f in doc.fields]
        for nf in new_fields:
            if nf["fieldname"] not in existing_fields:
                doc.append("fields", nf)
        
        doc.save()
        print("✅ Schema Updated: Bilingual Fields Added.")

    # 3. إدخال الباقات الجديدة الاحترافية
    plans = [
        {
            "name": "Standard", # ID
            "tier_name": "Standard", "tier_name_ar": "الأساسية",
            "price": 0,
            "is_featured": 0,
            "max_books": 2, "max_days": 7, "badge_color": "#94A3B8",
            "desc_en": "Start your reading journey.",
            "desc_ar": "ابدأ رحلتك في القراءة.",
            "feat_en": "<ul><li>Borrow 2 Books</li><li>7 Days Loan Period</li><li>General Access</li></ul>",
            "feat_ar": "<ul><li>استعارة كتابين</li><li>مدة استعارة ٧ أيام</li><li>وصول للمجموعة العامة</li></ul>"
        },
        {
            "name": "Premium",
            "tier_name": "Premium", "tier_name_ar": "المميزة",
            "price": 200,
            "is_featured": 1, # دي الباقة اللي هتبقا مميزة في النص
            "max_books": 5, "max_days": 14, "badge_color": "#3B82F6",
            "desc_en": "More flexibility for avid readers.",
            "desc_ar": "مرونة أكثر للقراء النهمين.",
            "feat_en": "<ul><li>Borrow 5 Books</li><li>14 Days Loan Period</li><li>Priority Support</li><li>New Arrivals Access</li></ul>",
            "feat_ar": "<ul><li>استعارة ٥ كتب</li><li>مدة استعارة ١٤ يوم</li><li>أولوية الدعم</li><li>وصول للإصدارات الجديدة</li></ul>"
        },
        {
            "name": "Elite",
            "tier_name": "Elite", "tier_name_ar": "النخبة",
            "price": 500,
            "is_featured": 0,
            "max_books": 10, "max_days": 30, "badge_color": "#F59E0B",
            "desc_en": "Ultimate access without limits.",
            "desc_ar": "تجربة بلا حدود للنخبة.",
            "feat_en": "<ul><li>Borrow 10 Books</li><li>30 Days Loan Period</li><li>VIP Lounge Access</li><li>Private Locker</li></ul>",
            "feat_ar": "<ul><li>استعارة ١٠ كتب</li><li>مدة استعارة ٣٠ يوم</li><li>دخول قاعة كبار الزوار</li><li>خزانة خاصة</li></ul>"
        }
    ]

    for p in plans:
        # نحذف القديم إن وجد لضمان التحديث
        frappe.db.delete("LMS Membership Type", {"name": p["name"]})
        
        new_plan = frappe.get_doc({
            "doctype": "LMS Membership Type",
            "tier_name": p["tier_name"],
            "tier_name_ar": p["tier_name_ar"],
            "price": p["price"],
            "currency": "EGP",
            "max_books": p["max_books"],
            "max_days": p["max_days"],
            "badge_color": p["badge_color"],
            "description_en": p["desc_en"],
            "description_ar": p["desc_ar"],
            "features_en": p["feat_en"],
            "features_ar": p["feat_ar"],
            "is_featured": p["is_featured"]
        })
        new_plan.name = p["name"] # Force Name
        new_plan.insert(ignore_permissions=True)
        print(f"✨ Created Plan: {p['name']}")

    frappe.db.commit()
    print("✅ Membership Re-Calibration Complete.")