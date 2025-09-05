

class EmergencyResponseHandler:
    # قائمة الكلمات المفتاحية التي تشير إلى حالات الطوارئ مثل التفكير في الانتحار أو الأذى.
    crisis_keywords = ["Suicide", "Hurt myself", "Kill myself", "Harm", "Murder", "I don't want to live"]


    @staticmethod
    def check_and_respond(user_input, experts_db):
        """
        دالة ثابتة للتحقق مما إذا كان الإدخال يحتوي على كلمات تشير إلى حالة طارئة.
        إذا تم العثور على كلمة من قائمة الكلمات الطارئة، يتم إرجاع رد طارئ مع معلومات حول المتخصصين.
        """
        t = user_input.replace(" ", "")  # إزالة الفراغات من الإدخال لزيادة دقة البحث
        if any(k in t for k in EmergencyResponseHandler.crisis_keywords):
            # إذا كان الإدخال يحتوي على أي كلمة من الكلمات الطارئة، يتم استدعاء دالة الرد الطارئ.
            return EmergencyResponseHandler.emergency_reply(experts_db)
        return None  # إذا لم يتم العثور على كلمات طارئة، يتم إرجاع None


    @staticmethod
    def emergency_reply(experts_db):
        """
        دالة ثابتة تقوم بإنشاء رد طارئ يحتوي على قائمة بأماكن المتخصصين المتاحة.
        """
        locations = set(expert["location"] for expert in experts_db)  # استخراج جميع المواقع من قاعدة بيانات الخبراء
        emergency_message = (
            "I'm really sorry you're feeling this way. Your safety is important.\n"
            "I'm here to provide information, but I can't offer therapy.\n"
            "I can help you get specialists who can help you.\n"
            "What is your location within the following locations:\n"
        )
        # إضافة المواقع المتاحة إلى الرسالة
        for location in locations:
            emergency_message += f"- {location}\n"
        return emergency_message  # إرجاع الرسالة الطارئة التي تحتوي على المواقع
