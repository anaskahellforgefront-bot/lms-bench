import frappe

def get_context(context):
    # بيانات الفريق (بدون سوشيال ميديا)
    context.team = [
        {
            "name": "Dr. Sarah Mitchell",
            "role": "Chief Executive Officer",
            "bio": "Visionary leader with 15+ years in EdTech. Previously led global initiatives at Google Education.",
            "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=600"
        },
        {
            "name": "James Carter",
            "role": "Head of Technology",
            "bio": "Architect behind the LMS Elite engine. Passionate about scalable systems and open source.",
            "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=600"
        },
        {
            "name": "Elena Rodriguez",
            "role": "Director of Content",
            "bio": "Curates our world-class library. Former senior librarian at the New York Public Library.",
            "image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=600"
        },
        {
            "name": "Michael Chang",
            "role": "Lead Developer",
            "bio": "Full-stack wizard specializing in Python and Frappe Framework. Loves clean code.",
            "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=600"
        },
        {
            "name": "Priya Patel",
            "role": "Community Manager",
            "bio": "The voice of LMS Elite. Dedicated to building a thriving community of learners.",
            "image": "https://images.unsplash.com/photo-1598550874175-4d7112ee7f38?q=80&w=600"
        },
        {
            "name": "David Kim",
            "role": "UX/UI Designer",
            "bio": "Crafting intuitive and beautiful experiences. Believes design is intelligence made visible.",
            "image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=600"
        }
    ]