import frappe

def execute():
    print("\n" + "="*60)
    print("🚀 STARTING SCHEMA DUMP FOR: LMS Portal")
    print("="*60 + "\n")

    # 1. جلب كل الدوكس التابعة للموديول الخاص بنا فقط
    doctypes = frappe.get_all("DocType", 
        filters={"module": "LMS Portal"}, 
        fields=["name", "issingle"]
    )

    if not doctypes:
        print("⚠️ No DocTypes found for module 'LMS Portal'.")
        print("   Make sure your DocTypes are assigned to the correct module.")
        return

    for dt in doctypes:
        doc_name = dt.name
        meta = frappe.get_meta(doc_name)
        
        print(f"📄 DocType: {doc_name} {'(Single)' if dt.issingle else ''}")
        print("-" * 40)
        
        # طباعة الحقول
        for field in meta.fields:
            req_mark = "*" if field.reqd else " "
            print(f"   [{req_mark}] {field.fieldname:<20} | Type: {field.fieldtype:<15} | Label: {field.label}")
            
            # لو في خيارات (زي Select أو Link) نطبعها
            if field.options:
                print(f"        ↳ Options: {field.options}")
        
        print("\n")

    print("="*60)
    print("✅ DUMP COMPLETE")
    print("="*60 + "\n")
