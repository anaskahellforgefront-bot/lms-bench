import frappe
from frappe import _

no_cache = 1

def get_context(context):
    # 1. LIVE STATS (Trust Signals)
    # أرقام حقيقية لزرع الثقة
    context.stats = {
        "books": frappe.db.count("LMS Book"),
        "members": frappe.db.count("LMS Member"),
        "loans": frappe.db.count("LMS Loan"), # إجمالي العمليات
        "reviews": frappe.db.count("LMS Testimonial")
    }

    # 2. POWER BOOKS (Best Sellers)
    # الكتب التي نريد تسويقها (الأعلى تقييماً)
    context.power_books = frappe.get_all("LMS Book",
        fields=["name", "title", "title_ar", "cover_image", "author", "author_ar", "category", "rating", "description", "description_ar"],
        filters={"rating": [">=", 4]},
        order_by="rating desc", 
        limit=8
    )

    # 3. NEW ARRIVALS (Fresh Content)
    # لإظهار أن المكتبة متجددة دائماً
    context.new_books = frappe.get_all("LMS Book",
        fields=["name", "title", "title_ar", "cover_image", "author", "author_ar"],
        order_by="creation desc", 
        limit=10
    )

    # 4. MEMBERSHIP TIERS (The Product)
    # الخطط مرتبة للسعر
    context.plans = frappe.get_all("LMS Membership Type",
        fields=["name", "tier_name", "tier_name_ar", "price", "max_books", "max_days", "description_en", "description_ar", "features_en", "features_ar"],
        order_by="price asc"
    )

    # 5. SOCIAL PROOF (Testimonials)
    context.testimonials = frappe.get_all("LMS Testimonial",
        filters={"published": 1},
        fields=["reviewer_name", "role", "reviewer_image", "content_en", "content_ar", "rating"],
        order_by="creation desc",
        limit=6
    )