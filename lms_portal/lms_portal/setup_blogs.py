import frappe

def execute():
    frappe.db.begin()
    
    # 1. LMS Blog
    if not frappe.db.exists("DocType", "LMS Blog"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "LMS Portal",
            "custom": 1,
            "name": "LMS Blog",
            "sort_field": "creation",
            "sort_order": "DESC",
            "fields": [
                {"fieldname": "title_en", "fieldtype": "Data", "label": "Title (English)", "reqd": 1},
                {"fieldname": "title_ar", "fieldtype": "Data", "label": "Title (Arabic)", "reqd": 1},
                {"fieldname": "route", "fieldtype": "Data", "label": "Route", "unique": 1},
                {"fieldname": "cover_image", "fieldtype": "Attach Image", "label": "Cover Image"},
                {"fieldname": "short_desc_en", "fieldtype": "Small Text", "label": "Short Description (EN)"},
                {"fieldname": "short_desc_ar", "fieldtype": "Small Text", "label": "Short Description (AR)"},
                {"fieldname": "content_en", "fieldtype": "Text Editor", "label": "Content (English)"},
                {"fieldname": "content_ar", "fieldtype": "Text Editor", "label": "Content (Arabic)"},
                {"fieldname": "author", "fieldtype": "Data", "label": "Author Name", "default": "LMS Team"},
                {"fieldname": "published", "fieldtype": "Check", "label": "Published", "default": 1},
                {"fieldname": "tags", "fieldtype": "Data", "label": "Tags"},
                {"fieldname": "read_time", "fieldtype": "Int", "label": "Read Time (Min)", "default": 5},
                {"fieldname": "likes", "fieldtype": "Int", "label": "Likes", "default": 0}
            ],
            "permissions": [{"role": "All", "read": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("✅ LMS Blog DocType Created.")

    # 2. LMS Blog Comment
    if not frappe.db.exists("DocType", "LMS Blog Comment"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "LMS Portal",
            "custom": 1,
            "name": "LMS Blog Comment",
            "sort_field": "creation",
            "sort_order": "ASC",
            "fields": [
                {"fieldname": "article", "fieldtype": "Link", "options": "LMS Blog", "label": "Article", "reqd": 1},
                {"fieldname": "user", "fieldtype": "Link", "options": "User", "label": "User", "reqd": 1},
                {"fieldname": "user_name", "fieldtype": "Data", "label": "Full Name"},
                {"fieldname": "comment", "fieldtype": "Small Text", "label": "Comment", "reqd": 1},
                {"fieldname": "date", "fieldtype": "Datetime", "label": "Date", "default": "Now"}
            ],
            "permissions": [{"role": "All", "read": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("✅ LMS Blog Comment DocType Created.")

    frappe.db.commit()

def fix_schema():
    """ اصلاح الحقول الناقصة """
    frappe.db.begin()
    
    doctype = "LMS Blog"
    if frappe.db.exists("DocType", doctype):
        doc = frappe.get_doc("DocType", doctype)
        
        # التاكد من وجود حقل tags
        field_names = [d.fieldname for d in doc.fields]
        
        if "tags" not in field_names:
            doc.append("fields", {
                "fieldname": "tags",
                "fieldtype": "Data",
                "label": "Tags",
                "insert_after": "published"
            })
            doc.save()
            print("✅ Fixed: 'tags' field added.")
        else:
            print("ℹ️ 'tags' field already exists.")
            
    frappe.db.commit()
