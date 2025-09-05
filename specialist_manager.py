# تعريف فئة SpecialistManager لإدارة المتخصصين في المجال الطبي
class SpecialistManager:
    def __init__(self):
        # قاعدة بيانات للمختصين تحتوي على معلومات مثل الاسم، التخصص، الهاتف، البريد الإلكتروني، ساعات العمل، والموقع
        self.experts_db = [
            {"name": "Dr. John Doe", "specialty": "Psychiatrist", "phone": "+1234567890", "email": "johndoe@example.com", "working_hours": "9 AM - 5 PM", "location": "New York"},
            {"name": "Nurse Mary Smith", "specialty": "Mental Health Nurse", "phone": "+9876543210", "email": "marysmith@example.com", "working_hours": "8 AM - 4 PM", "location": "Los Angeles"},
            {"name": "Dr. Alice Brown", "specialty": "Psychologist", "phone": "+1122334455", "email": "alicebrown@example.com", "working_hours": "10 AM - 6 PM", "location": "Chicago"}
        ]
        # يتم تخزين البيانات في self.experts_db وتكون جاهزة للاستخدام في باقي الدوال


    def handle_specialists(self, user_input):
        """
        هذه الدالة تستقبل مدخلات المستخدم وتتعامل مع الموقع للبحث عن المختصين
        يتم استدعاء دالة extract_location لاستخراج الموقع من النص المدخل
        ثم يتم البحث عن المختصين حسب الموقع باستخدام دالة find_experts_by_location
        """
        # استدعاء دالة لاستخراج الموقع من نص المستخدم
        is_existing, location = self.extract_location(user_input)
        # استدعاء دالة للبحث عن المختصين حسب الموقع
        return self.find_experts_by_location(is_existing, location)

    def extract_location(self, text):
        """
        دالة لاستخراج الموقع من النص المدخل بواسطة المستخدم
        """
        # إنشاء مجموعة تحتوي على المواقع المختلفة للمختصين في قاعدة البيانات
        locations = set(expert["location"] for expert in self.experts_db)
        # البحث إذا كان أحد المواقع موجودًا في النص المدخل
        for location in locations:
            # التحقق من وجود الموقع في النص مع تجاهل حالة الأحرف (صغيرة أو كبيرة)
            if location.lower() in text.lower():
                return True, location  # إذا تم العثور على الموقع، إعادة True مع الموقع
        return False, text  # إذا لم يتم العثور على الموقع، إعادة False مع النص كما هو

    def find_experts_by_location(self, is_existing, location):
        """
        دالة للبحث عن المختصين بناءً على الموقع
        """
        if is_existing:
            # إذا تم العثور على الموقع، نقوم بتصفية المختصين في ذلك الموقع
            experts_list = [expert for expert in self.experts_db if expert["location"].lower() == location.lower()]
            # إعداد نص يحتوي على معلومات المختصين الموجودين في الموقع
            experts_info = "\n".join([f"Name: {expert['name']}, Specialty: {expert['specialty']}" for expert in experts_list])

            # إضافة رسالة تحتوي على تفاصيل المختصين في الموقع
            experts_info = f"Here is the list of available specialists based on your location:\n{experts_info}\nWould you like me to schedule an appointment with a specialist to assist you?"

            return experts_info  # إرجاع تفاصيل المختصين
        else:
            # إذا لم يتم العثور على أي مختصين في الموقع، إرجاع رسالة اعتذار
            return f"Sorry, we couldn't find any specialists in your location ({location})."
