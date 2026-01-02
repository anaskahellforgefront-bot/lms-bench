import frappe
import random

def execute():
    frappe.db.begin()
    
    # 1. تحديث هيكل الكتب (LMS Book) وإضافة Rating
    doctype = "LMS Book"
    if frappe.db.exists("DocType", doctype):
        doc = frappe.get_doc("DocType", doctype)
        
        # تحديث خيارات التصنيف
        new_options = "New Arrivals\nProgramming\nSelf-Help\nFinance\nHistory\nSci-Fi\nFiction\nPsychology\nBusiness\nBiography\nPhilosophy"
        for field in doc.fields:
            if field.fieldname == "category":
                field.options = new_options
                break
        
        # الحقول الجديدة بما فيها Rating
        new_fields = [
            {"fieldname": "title_ar", "fieldtype": "Data", "label": "Title (Arabic)", "insert_after": "title"},
            {"fieldname": "author_ar", "fieldtype": "Data", "label": "Author (Arabic)", "insert_after": "author"},
            {"fieldname": "description_ar", "fieldtype": "Text Editor", "label": "Description (Arabic)", "insert_after": "description"},
            {"fieldname": "rating", "fieldtype": "Float", "label": "Rating (5 Stars)", "default": 0, "insert_after": "category"},
            {"fieldname": "total_copies", "fieldtype": "Int", "label": "Total Copies", "default": 1, "insert_after": "status"},
            {"fieldname": "available_copies", "fieldtype": "Int", "label": "Available Copies", "default": 1, "insert_after": "total_copies"}
        ]
        
        existing = [f.fieldname for f in doc.fields]
        added = False
        for nf in new_fields:
            if nf["fieldname"] not in existing:
                doc.append("fields", nf)
                added = True
        
        # حفظ التعديلات
        doc.save()
        print("✅ LMS Book Schema Updated (Rating Added).")

    # 2. توليد الكتب مع التقييمات
    frappe.db.sql("DELETE FROM `tabLMS Book`")
    
    books_data = [
        # (نفس قائمة الكتب السابقة مع إضافة التقييم)
        {"title": "Clean Code", "title_ar": "الكود النظيف", "author": "Robert C. Martin", "author_ar": "روبرت مارتن", "cat": "Programming", "img": "https://m.media-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg", "desc": "Agile Software Craftsmanship.", "desc_ar": "حرفة البرمجيات الرشيقة.", "price": 500, "rent": 50, "status": "Available", "rating": 4.8},
        {"title": "Atomic Habits", "title_ar": "العادات الذرية", "author": "James Clear", "author_ar": "جيمس كلير", "cat": "Self-Help", "img": "https://m.media-amazon.com/images/I/51-nXsSRfZL._SX328_BO1,204,203,200_.jpg", "desc": "Build Good Habits.", "desc_ar": "بناء عادات جيدة.", "price": 300, "rent": 30, "status": "Borrowed", "rating": 4.9},
        {"title": "The Psychology of Money", "title_ar": "سيكولوجية المال", "author": "Morgan Housel", "author_ar": "مورجان هاوسل", "cat": "Finance", "img": "https://m.media-amazon.com/images/I/41r6F2LRf8L._SX323_BO1,204,203,200_.jpg", "desc": "Lessons on wealth.", "desc_ar": "دروس عن الثروة.", "price": 350, "rent": 35, "status": "Available", "rating": 4.7},
        {"title": "Rich Dad Poor Dad", "title_ar": "الأب الغني والأب الفقير", "author": "Robert Kiyosaki", "author_ar": "روبرت كيوساكي", "cat": "Finance", "img": "https://m.media-amazon.com/images/I/51u2E5fNq8L._SX331_BO1,204,203,200_.jpg", "desc": "Rich vs Poor mindset.", "desc_ar": "عقلية الغني والفقير.", "price": 250, "rent": 25, "status": "Available", "rating": 4.6},
        {"title": "Sapiens", "title_ar": "العاقل", "author": "Yuval Noah Harari", "author_ar": "يوفال نوح هراري", "cat": "History", "img": "https://m.media-amazon.com/images/I/51Sn8PEXwcL._SX307_BO1,204,203,200_.jpg", "desc": "History of Humankind.", "desc_ar": "تاريخ البشرية.", "price": 400, "rent": 40, "status": "Reserved", "rating": 4.5},
        {"title": "Dune", "title_ar": "كثيب", "author": "Frank Herbert", "author_ar": "فرانك هربرت", "cat": "Sci-Fi", "img": "https://m.media-amazon.com/images/I/41yJ75gpV-L._SX324_BO1,204,203,200_.jpg", "desc": "Sci-fi masterpiece.", "desc_ar": "تحفة الخيال العلمي.", "price": 450, "rent": 45, "status": "Available", "rating": 4.4},
        {"title": "1984", "title_ar": "١٩٨٤", "author": "George Orwell", "author_ar": "جورج أورويل", "cat": "Fiction", "img": "https://m.media-amazon.com/images/I/41aM4xOZxaL._SX277_BO1,204,203,200_.jpg", "desc": "Dystopian novel.", "desc_ar": "رواية ديستوبية.", "price": 200, "rent": 20, "status": "Available", "rating": 4.8},
        {"title": "Thinking, Fast and Slow", "title_ar": "التفكير السريع والبطيء", "author": "Daniel Kahneman", "author_ar": "دانيال كانيمان", "cat": "Psychology", "img": "https://m.media-amazon.com/images/I/41shdN2iLmL._SX332_BO1,204,203,200_.jpg", "desc": "How we think.", "desc_ar": "كيف نفكر.", "price": 380, "rent": 38, "status": "Borrowed", "rating": 4.3},
        {"title": "The Pragmatic Programmer", "title_ar": "المبرمج البراغماتي", "author": "Andrew Hunt", "author_ar": "أندرو هانت", "cat": "Programming", "img": "https://m.media-amazon.com/images/I/51W1sBPO7tL._SX380_BO1,204,203,200_.jpg", "desc": "Coding mastery.", "desc_ar": "إتقان البرمجة.", "price": 550, "rent": 55, "status": "Available", "rating": 4.9},
        {"title": "Zero to One", "title_ar": "من الصفر إلى الواحد", "author": "Peter Thiel", "author_ar": "بيتر ثيل", "cat": "Business", "img": "https://m.media-amazon.com/images/I/51z7m8QBWtL._SX325_BO1,204,203,200_.jpg", "desc": "Startups notes.", "desc_ar": "ملاحظات الشركات الناشئة.", "price": 300, "rent": 30, "status": "Available", "rating": 4.5},
        {"title": "Introduction to Algorithms", "title_ar": "مقدمة في الخوارزميات", "author": "Thomas H. Cormen", "author_ar": "توماس كورمن", "cat": "Programming", "img": "https://m.media-amazon.com/images/I/41SNoh5ZhOL._SX404_BO1,204,203,200_.jpg", "desc": "Algorithms guide.", "desc_ar": "دليل الخوارزميات.", "price": 800, "rent": 80, "status": "Available", "rating": 4.7},
        {"title": "Deep Work", "title_ar": "العمل العميق", "author": "Cal Newport", "author_ar": "كال نيوبورت", "cat": "Self-Help", "img": "https://m.media-amazon.com/images/I/417zLta1uQL._SX319_BO1,204,203,200_.jpg", "desc": "Focused success.", "desc_ar": "النجاح المركز.", "price": 280, "rent": 28, "status": "Available", "rating": 4.6},
        {"title": "The Lean Startup", "title_ar": "الشركة الناشئة المرنة", "author": "Eric Ries", "author_ar": "إريك ريس", "cat": "Business", "img": "https://m.media-amazon.com/images/I/51aEhyjQGrL._SX329_BO1,204,203,200_.jpg", "desc": "Innovation.", "desc_ar": "الابتكار.", "price": 310, "rent": 31, "status": "Borrowed", "rating": 4.4},
        {"title": "Harry Potter", "title_ar": "هاري بوتر", "author": "J.K. Rowling", "author_ar": "جي كي رولينج", "cat": "Fiction", "img": "https://m.media-amazon.com/images/I/51HSkTKlauL._SX346_BO1,204,203,200_.jpg", "desc": "Magic world.", "desc_ar": "عالم السحر.", "price": 250, "rent": 25, "status": "Available", "rating": 4.9},
        {"title": "The 48 Laws of Power", "title_ar": "قواعد السطوة", "author": "Robert Greene", "author_ar": "روبرت جرين", "cat": "Self-Help", "img": "https://m.media-amazon.com/images/I/41Hl2o7yZBL._SX326_BO1,204,203,200_.jpg", "desc": "Power dynamics.", "desc_ar": "ديناميكيات القوة.", "price": 400, "rent": 40, "status": "Available", "rating": 4.3},
        {"title": "Start with Why", "title_ar": "ابدأ بـ لماذا", "author": "Simon Sinek", "author_ar": "سايمون سينك", "cat": "Business", "img": "https://m.media-amazon.com/images/I/51D8z2-Z7rL._SX324_BO1,204,203,200_.jpg", "desc": "Inspiration.", "desc_ar": "الإلهام.", "price": 290, "rent": 29, "status": "Available", "rating": 4.5},
        {"title": "Meditations", "title_ar": "التأملات", "author": "Marcus Aurelius", "author_ar": "ماركوس أوريليوس", "cat": "Philosophy", "img": "https://m.media-amazon.com/images/I/41-3y9s-9qL._SX331_BO1,204,203,200_.jpg", "desc": "Personal writings.", "desc_ar": "كتابات شخصية.", "price": 220, "rent": 22, "status": "Available", "rating": 4.6},
        {"title": "Alchemist", "title_ar": "الخيميائي", "author": "Paulo Coelho", "author_ar": "باولو كويلو", "cat": "Fiction", "img": "https://m.media-amazon.com/images/I/51Z0nLAfLmL._SX329_BO1,204,203,200_.jpg", "desc": "Follow your dream.", "desc_ar": "اتبع حلمك.", "price": 200, "rent": 20, "status": "Available", "rating": 4.8},
        {"title": "Principles", "title_ar": "المبادئ", "author": "Ray Dalio", "author_ar": "راي داليو", "cat": "Business", "img": "https://m.media-amazon.com/images/I/41Z-16ZqZ9L._SX356_BO1,204,203,200_.jpg", "desc": "Life and work.", "desc_ar": "الحياة والعمل.", "price": 600, "rent": 60, "status": "Available", "rating": 4.7},
        {"title": "Becoming", "title_ar": "وأصبحت", "author": "Michelle Obama", "author_ar": "ميشيل أوباما", "cat": "Biography", "img": "https://m.media-amazon.com/images/I/41wKl0W2-4L._SX327_BO1,204,203,200_.jpg", "desc": "Memoir.", "desc_ar": "مذكرات.", "price": 350, "rent": 35, "status": "Reserved", "rating": 4.8}
    ]

    for b in books_data:
        # إضافة Rating هنا
        rating_val = b.get("rating", round(random.uniform(3.5, 5.0), 1))
        
        doc = frappe.get_doc({
            "doctype": "LMS Book",
            "title": b["title"], "title_ar": b["title_ar"],
            "author": b["author"], "author_ar": b["author_ar"],
            "category": b["cat"],
            "description": b["desc"], "description_ar": b["desc_ar"],
            "cover_image": b["img"],
            "full_price": b["price"], "rental_price": b["rent"],
            "status": b["status"],
            "rating": rating_val,  # <--- إضافة التقييم
            "isbn": ''.join(random.choices('0123456789', k=13)),
            "publisher": "Amazon Books",
            "shelf_location": f"Row {random.randint(1,20)}-{random.choice(['A','B','C'])}",
            "total_copies": 3 if b["status"] == "Available" else 1,
            "available_copies": 3 if b["status"] == "Available" else 0
        })
        doc.insert(ignore_permissions=True)
        print(f"📚 Generated: {b['title']} ({rating_val}⭐)")

    frappe.db.commit()
    print("✅ All Books Generated Successfully with Ratings.")