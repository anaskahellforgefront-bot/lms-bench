import frappe
import random

def execute():
    frappe.db.begin()
    
    # تنظيف البيانات القديمة (اختياري)
    frappe.db.sql("DELETE FROM `tabLMS Blog`")
    frappe.db.sql("DELETE FROM `tabLMS Blog Comment`")

    # قائمة المواضيع الاحترافية (عربي / إنجليزي)
    topics = [
        {
            "title_en": "The Future of AI in Education",
            "title_ar": "مستقبل الذكاء الاصطناعي في التعليم",
            "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1000&auto=format&fit=crop",
            "cat": "Technology",
            "desc_en": "How Artificial Intelligence is reshaping the way we learn and teach.",
            "desc_ar": "كيف يعيد الذكاء الاصطناعي تشكيل طريقة تعلمنا وتدريسنا.",
            "html_en": """<h3>The Revolution is Here</h3><p>Artificial Intelligence is not just a buzzword; it's a fundamental shift in how education is delivered. From personalized learning paths to automated grading, AI is freeing up teachers to focus on mentorship.</p><blockquote>"AI will not replace teachers, but teachers who use AI will replace those who don't."</blockquote><p>We are entering an era of <strong>hyper-personalized education</strong>.</p>""",
            "html_ar": """<h3>الثورة بدأت بالفعل</h3><p>الذكاء الاصطناعي ليس مجرد كلمة طنانة؛ إنه تحول جوهري في كيفية تقديم التعليم. من مسارات التعلم المخصصة إلى التصحيح الآلي، يحرر الذكاء الاصطناعي المعلمين للتركيز على التوجيه والإرشاد.</p><blockquote>"لن يستبدل الذكاء الاصطناعي المعلمين، لكن المعلمين الذين يستخدمون الذكاء الاصطناعي سيستبدلون أولئك الذين لا يفعلون."</blockquote><p>نحن ندخل حقبة <strong>التعليم فائق التخصيص</strong>.</p>"""
        },
        {
            "title_en": "Deep Work: Rules for Focused Success",
            "title_ar": "العمل العميق: قواعد النجاح المركز",
            "image": "https://images.unsplash.com/photo-1499750310159-57751c67abb2?q=80&w=1000&auto=format&fit=crop",
            "cat": "Productivity",
            "desc_en": "Mastering the art of deep work in a distracted world.",
            "desc_ar": "إتقان فن العمل العميق في عالم مليء بالمشتتات.",
            "html_en": """<h3>Distraction is the Enemy</h3><p>In a world of notifications and social media, the ability to focus without distraction is a superpower. Deep work allows you to master hard things quickly.</p><ul><li>Eliminate distractions</li><li>Embrace boredom</li><li>Quit social media</li></ul>""",
            "html_ar": """<h3>التشتت هو العدو</h3><p>في عالم مليء بالإشعارات ووسائل التواصل الاجتماعي، تعد القدرة على التركيز دون تشتيت قوة خارقة. يتيح لك العمل العميق إتقان الأشياء الصعبة بسرعة.</p><ul><li>تخلص من المشتتات</li><li>تقبل الملل</li><li>توقف عن استخدام وسائل التواصل</li></ul>"""
        },
        {
            "title_en": "Mastering Python for Data Science",
            "title_ar": "إحتراف بايثون لعلوم البيانات",
            "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
            "cat": "Programming",
            "desc_en": "A comprehensive guide to starting your journey in Data Science using Python.",
            "desc_ar": "دليل شامل لبدء رحلتك في علوم البيانات باستخدام لغة بايثون.",
            "html_en": """<h3>Why Python?</h3><p>Python provides a vast ecosystem of libraries like Pandas, NumPy, and Scikit-learn making it the go-to language for data analysis.</p>""",
            "html_ar": """<h3>لماذا بايثون؟</h3><p>توفر بايثون نظامًا بيئيًا ضخمًا من المكتبات مثل Pandas و NumPy و Scikit-learn مما يجعلها اللغة الأولى لتحليل البيانات.</p>"""
        },
        {
            "title_en": "The Psychology of Money",
            "title_ar": "سيكولوجية المال",
            "image": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?q=80&w=1000&auto=format&fit=crop",
            "cat": "Finance",
            "desc_en": "Timeless lessons on wealth, greed, and happiness.",
            "desc_ar": "دروس خالدة حول الثروة والجشع والسعادة.",
            "html_en": """<h3>Money is Emotional</h3><p>Doing well with money isn’t necessarily about what you know. It’s about how you behave. And behavior is hard to teach, even to really smart people.</p>""",
            "html_ar": """<h3>المال عاطفي</h3><p>النجاح المالي لا يتعلق بالضرورة بما تعرفه، بل بكيفية تصرفك. والسلوك صعب التدريس، حتى للأشخاص الأذكياء جداً.</p>"""
        },
        {
            "title_en": "Minimalism: Live More with Less",
            "title_ar": "التبسيط: عش أكثر بأقل",
            "image": "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?q=80&w=1000&auto=format&fit=crop",
            "cat": "Lifestyle",
            "desc_en": "How decluttering your life leads to mental clarity.",
            "desc_ar": "كيف يؤدي التخلص من الفوضى في حياتك إلى الصفاء الذهني.",
            "html_en": """<h3>Less is More</h3><p>Minimalism is not about having nothing. It's about making room for what matters most.</p>""",
            "html_ar": """<h3>الأقل هو الأكثر</h3><p>التبسيط لا يعني عدم امتلاك أي شيء. بل يعني إفساح المجال لما هو أهم.</p>"""
        }
    ]

    # توليد 15 مقال (تكرار القائمة 3 مرات مع تغييرات طفيفة)
    count = 1
    for i in range(3):
        for t in topics:
            # إنشاء المقال
            route_name = f"blog-post-{count}"
            doc = frappe.get_doc({
                "doctype": "LMS Blog",
                "title_en": f"{t['title_en']} (Part {i+1})",
                "title_ar": f"{t['title_ar']} (الجزء {i+1})",
                "route": route_name,
                "cover_image": t['image'],
                "short_desc_en": t['desc_en'],
                "short_desc_ar": t['desc_ar'],
                "content_en": t['html_en'],
                "content_ar": t['html_ar'],
                "author": "Anas Ahmed",
                "read_time": random.randint(3, 10),
                "tags": t['cat'],
                "published": 1,
                "likes": random.randint(10, 500)
            })
            doc.insert(ignore_permissions=True)
            print(f"📝 Generated Article: {doc.title_en}")

            # إضافة تعليقات وهمية (2-3 تعليقات لكل مقال)
            for j in range(random.randint(2, 4)):
                comment = frappe.get_doc({
                    "doctype": "LMS Blog Comment",
                    "article": doc.name,
                    "user": frappe.session.user, # يستخدم المستخدم الحالي (Administrator)
                    "user_name": random.choice(["Ali Hassan", "Sarah Smith", "Mohamed Ezz", "John Doe"]),
                    "comment": random.choice([
                        "Great article!", "مقال رائع جداً", 
                        "Thanks for sharing.", "شكراً لك على هذه المعلومات القيمة.",
                        "Looking forward to the next part.", "ننتظر المزيد!"
                    ]),
                    "date": frappe.utils.now()
                })
                comment.insert(ignore_permissions=True)
            
            count += 1

    frappe.db.commit()
    print("✅ Successfully generated 15 articles with comments.")