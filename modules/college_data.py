class CollegeData:
    def __init__(self):
        self.college_name = "V.S.B Engineering College"

    def get_college_name(self):
        return self.college_name

    def get_departments(self):
        return [
            {"name": "Computer and Communication Engineering"},
            {"name": "Computer Science Engineering"},
            {"name": "Information Technology"},
            {"name": "Electronics and Communication Engineering"}
        ]

    def get_facilities(self):
        return [
            "Library",
            "WiFi Campus",
            "Hostel",
            "Transport",
            "Sports Complex"
        ]

    def get_scholarships(self):
        return [
            "Merit Scholarship",
            "Government Scholarship",
            "Sports Scholarship"
        ]

    def get_contact_info(self):
        return {
            "phone": "+91XXXXXXXXXX",
            "email": "info@vsbec.com",
            "website": "https://www.vsbec.com",
            "location": "Karur, Tamil Nadu"
        }

    def get_admission_requirements(self):
        return {
            "bachelor": [
                "12th Pass",
                "TNEA Counseling"
            ]
        }

    def get_faqs(self):
        return [
            {
                "question": "How to apply?",
                "answer": "Apply through TNEA counseling."
            }
        ]

    def search_faq(self, query):
        return self.get_faqs()

    def get_full_info(self):
        return {
            "college": self.college_name,
            "departments": self.get_departments(),
            "facilities": self.get_facilities()
        }

    def format_info_for_chat(self):
        return f"College Name: {self.college_name}"

college_data = CollegeData()
