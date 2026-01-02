import frappe

def print_structure():
    print("\n🔍 INSPECTING LMS DOCTYPES STRUCTURE...\n")
    
    # جلب كل الـ Doctypes التابعة للتطبيق
    doctypes = frappe.get_all("DocType", filters={"module": "LMS Portal"}, pluck="name")
    
    if not doctypes:
        # حل بديل إذا لم يكن الموديول مضبوطاً بدقة، نجلب كل ما يبدأ بـ LMS
        doctypes = frappe.get_all("DocType", filters={"name": ["like", "LMS%"]}, pluck="name")

    for dt in doctypes:
        print(f"=========================================")
        print(f"📄 DocType: {dt}")
        print(f"=========================================")
        
        try:
            meta = frappe.get_meta(dt)
            # طباعة الحقول المخصصة
            print(f"{'Field Name':<30} | {'Field Type':<15} | {'Label'}")
            print("-" * 70)
            
            for field in meta.fields:
                print(f"{field.fieldname:<30} | {field.fieldtype:<15} | {field.label}")
            
            print("\n")
        except Exception as e:
            print(f"❌ Error loading meta for {dt}: {e}\n")