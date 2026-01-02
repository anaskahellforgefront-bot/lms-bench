import frappe

def execute():
    frappe.db.begin()
    
    # -------------------------------------------
    # 1. إنشاء جدول الأسئلة الشائعة (LMS FAQ)
    # -------------------------------------------
    if not frappe.db.exists("DocType", "LMS FAQ"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "LMS Portal",
            "custom": 1,
            "name": "LMS FAQ",
            "sort_field": "sort_order",
            "sort_order": "ASC",
            "fields": [
                {"fieldname": "question_en", "fieldtype": "Data", "label": "Question (EN)", "reqd": 1},
                {"fieldname": "question_ar", "fieldtype": "Data", "label": "Question (AR)", "reqd": 1},
                {"fieldname": "answer_en", "fieldtype": "Text Editor", "label": "Answer (EN)", "reqd": 1},
                {"fieldname": "answer_ar", "fieldtype": "Text Editor", "label": "Answer (AR)", "reqd": 1},
                {"fieldname": "category", "fieldtype": "Select", "label": "Category", "options": "General\nMemberships\nBorrowing & Fines\nTechnical"},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published", "default": 1},
                {"fieldname": "sort_order", "fieldtype": "Int", "label": "Sort Order", "default": 0}
            ],
            "permissions": [{"role": "All", "read": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("✅ LMS FAQ DocType Created.")

    # -------------------------------------------
    # 2. إنشاء جدول رسائل الاتصال (LMS Contact Message)
    # -------------------------------------------
    if not frappe.db.exists("DocType", "LMS Contact Message"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "LMS Portal",
            "custom": 1,
            "name": "LMS Contact Message",
            "sort_field": "creation",
            "sort_order": "DESC",
            "fields": [
                {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name", "reqd": 1},
                {"fieldname": "email", "fieldtype": "Data", "label": "Email", "reqd": 1},
                {"fieldname": "subject", "fieldtype": "Data", "label": "Subject"},
                {"fieldname": "message", "fieldtype": "Small Text", "label": "Message", "reqd": 1},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "New\nRead\nReplied", "default": "New"},
                {"fieldname": "is_member", "fieldtype": "Check", "label": "Is Existing Member?", "read_only": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("✅ LMS Contact Message DocType Created.")

    # -------------------------------------------
    # 3. تحديث الإعدادات (LMS Settings) ببيانات التواصل
    # -------------------------------------------
    if frappe.db.exists("DocType", "LMS Settings"):
        doc = frappe.get_doc("DocType", "LMS Settings")
        
        # قائمة الحقول الجديدة للتواصل
        contact_fields = [
            {"fieldname": "sb_contact", "fieldtype": "Section Break", "label": "Contact Info"},
            {"fieldname": "support_email", "fieldtype": "Data", "label": "Support Email"},
            {"fieldname": "support_phone", "fieldtype": "Data", "label": "Support Phone"},
            {"fieldname": "address_en", "fieldtype": "Small Text", "label": "Address (EN)"},
            {"fieldname": "address_ar", "fieldtype": "Small Text", "label": "Address (AR)"},
            {"fieldname": "map_embed", "fieldtype": "Small Text", "label": "Google Maps Embed Code (HTML)"},
            {"fieldname": "working_hours_en", "fieldtype": "Data", "label": "Working Hours (EN)"},
            {"fieldname": "working_hours_ar", "fieldtype": "Data", "label": "Working Hours (AR)"}
        ]
        
        existing = [f.fieldname for f in doc.fields]
        added = False
        for cf in contact_fields:
            if cf["fieldname"] not in existing:
                doc.append("fields", cf)
                added = True
        
        if added:
            doc.save()
            print("✅ LMS Settings Updated with Contact Fields.")

        # ملء الإعدادات ببيانات افتراضية
        settings = frappe.get_doc("LMS Settings")
        settings.support_email = "help@lms-elite.com"
        settings.support_phone = "+20 100 200 3000"
        settings.address_en = "123 Knowledge St, Digital District, Cairo, Egypt"
        settings.address_ar = "١٢٣ شارع المعرفة، الحي الرقمي، القاهرة، مصر"
        settings.working_hours_en = "Sun - Thu: 9:00 AM - 10:00 PM"
        settings.working_hours_ar = "الأحد - الخميس: ٩ صباحاً - ١٠ مساءً"
        # رابط خريطة افتراضي (ميدان التحرير كمثال)
        settings.map_embed = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3453.161746244799!2d31.23307537637841!3d30.06080761774351!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x145840b8f41315b9%3A0x7d672809d84c3752!2sTahrir%20Square!5e0!3m2!1sen!2seg!4v1703630000000!5m2!1sen!2seg" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
        settings.save()

    # -------------------------------------------
    # 4. توليد أسئلة شائعة (Dummy Content)
    # -------------------------------------------
    # تنظيف القديم
    frappe.db.sql("DELETE FROM `tabLMS FAQ`")
    
    faqs = [
        {
            "q_en": "How do I reset my password?",
            "q_ar": "كيف يمكنني استعادة كلمة المرور؟",
            "a_en": "Go to the Sign In page and click on 'Forgot Password'. Enter your email to receive an OTP.",
            "a_ar": "اذهب لصفحة تسجيل الدخول واضغط على 'نسيت كلمة المرور'. أدخل بريدك لاستلام رمز التحقق.",
            "cat": "Technical"
        },
        {
            "q_en": "What happens if I return a book late?",
            "q_ar": "ماذا يحدث إذا تأخرت في إرجاع الكتاب؟",
            "a_en": "A fine of <strong>10 EGP</strong> is applied for every day of delay. Elite members are exempt.",
            "a_ar": "يتم تطبيق غرامة قدرها <strong>١٠ جنيه</strong> عن كل يوم تأخير. أعضاء النخبة معفيون.",
            "cat": "Borrowing & Fines"
        },
        {
            "q_en": "Can I upgrade my membership later?",
            "q_ar": "هل يمكنني ترقية عضويتي لاحقاً؟",
            "a_en": "Yes! Go to the 'Memberships' page at any time and choose a higher tier.",
            "a_ar": "نعم! اذهب لصفحة 'العضويات' في أي وقت واختر باقة أعلى.",
            "cat": "Memberships"
        },
        {
            "q_en": "Is there a limit to how many books I can borrow?",
            "q_ar": "هل هناك حد أقصى لعدد الكتب المستعارة؟",
            "a_en": "Yes. Standard members can borrow 2 books, while Elite members can borrow up to 10.",
            "a_ar": "نعم. العضوية الأساسية تتيح كتابين، بينما تتيح عضوية النخبة حتى ١٠ كتب.",
            "cat": "Memberships"
        },
        {
            "q_en": "Do you offer digital books (PDF)?",
            "q_ar": "هل توفرون كتباً رقمية (PDF)؟",
            "a_en": "Yes, our library includes a vast collection of e-books accessible directly from your dashboard.",
            "a_ar": "نعم، مكتبتنا تضم مجموعة ضخمة من الكتب الإلكترونية المتاحة مباشرة من لوحة التحكم.",
            "cat": "General"
        }
    ]

    for f in faqs:
        doc = frappe.get_doc({
            "doctype": "LMS FAQ",
            "question_en": f["q_en"],
            "question_ar": f["q_ar"],
            "answer_en": f["a_en"],
            "answer_ar": f["a_ar"],
            "category": f["cat"],
            "published": 1
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Generated 5 Professional FAQs.")