import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from emergency_response_handler import EmergencyResponseHandler
from specialist_manager import SpecialistManager
from appointment_manager import AppointmentManager
from prompt_engineering import PromptEngineering


class MentalHealthChatbot:
    def __init__(self, model_name="adanal/dialogpt-finetuned"):
        # تحميل النموذج والمحول من Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # تحديد الجهاز الذي سيعمل عليه النموذج (GPU أو CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # تعيين token padding إذا لم يكن موجودًا
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # متغيرات الحالة للتحكم في تدفق المحادثة
        self.ask_to_location = False
        self.asking_for_appointment = False
        
        # تهيئة الأدوات المساعدة مثل معالجة الاستجابات الطارئة وإدارة المتخصصين
        self.prompt_engineering = PromptEngineering()
        self.specialist_manager = SpecialistManager()
        self.appointment_manager = AppointmentManager()

    def _encode_and_concat(self, text, bot_input_ids):
        """
        دالة مساعدة لتحويل النص إلى توكنز ودمجها مع مدخلات المحادثة السابقة.
        """
        tokens = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
        return torch.cat([bot_input_ids, tokens], dim=-1)

    def _handle_emergency(self, user_input, bot_input_ids):
        """
        التعامل مع الاستجابات الطارئة.
        إذا كان هناك رد طارئ، يتم التعامل معه وإرجاعه.
        """
        emergency_response = EmergencyResponseHandler().check_and_respond(user_input)
        if emergency_response:
            self.ask_to_location = True
            # دمج الرد الطارئ مع المدخلات
            bot_input_ids = self._encode_and_concat(emergency_response, bot_input_ids)
            return emergency_response, bot_input_ids
        return None, bot_input_ids

    def _handle_specialists(self, user_input, bot_input_ids):
        """
        التعامل مع الاستفسارات الخاصة بالموقع المتخصص.
        إذا تم طلب تحديد موقع المتخصص، يتم معالجة ذلك.
        """
        if self.ask_to_location:
            reply, is_location_existing = self.specialist_manager.handle_specialists(user_input)
            if is_location_existing:
                self.asking_for_appointment = True
            self.ask_to_location = False
            # دمج الرد الخاص بالموقع مع المدخلات
            bot_input_ids = self._encode_and_concat(reply, bot_input_ids)
            return reply, bot_input_ids
        return None, bot_input_ids

    def _handle_appointment_request(self, user_input, bot_input_ids):
        """
        التعامل مع طلبات تحديد المواعيد.
        إذا كان المستخدم يرغب في تحديد موعد، يتم معالجة ذلك.
        """
        if self.appointment_manager.detect_appointment_request(user_input):
            self.asking_for_appointment = True
        
        if self.asking_for_appointment:
            if "no" in user_input.lower():
                # الرد في حالة رفض تقديم المعلومات
                response = (
                    "I understand that you may not want to provide your information right now, and we completely respect that.\n"
                    "Providing these details helps us schedule an appointment with the specialist more accurately.\n"
                    "If you need more time or would prefer to cancel the booking, we are here to assist you at any time.\n"
                    "If you'd like any further assistance, we can direct you to support lines or additional help."
                )
                self.asking_for_appointment = False
                # دمج الرد مع المدخلات
                bot_input_ids = self._encode_and_concat(response, bot_input_ids)
                return response, bot_input_ids
            else:
                # تخزين البيانات المتعلقة بالموعد
                return self.appointment_manager.store_appointment_data(user_input), bot_input_ids
       
        return None, bot_input_ids



    def generate_response(self, user_input, chat_history_ids=None):
        """
        توليد الردود باستخدام النموذج المدرب مع الإدخال الموجه.
        """
        # إعداد النص الموجه
        prompt = self.prepare_prompt(user_input)
        inputs = self.tokenizer.encode(prompt + self.tokenizer.eos_token, return_tensors="pt").to(self.device)

        bot_input_ids = chat_history_ids if chat_history_ids is not None else inputs

        # التعامل مع الاستجابات الطارئة
        emergency_response, bot_input_ids = self._handle_emergency(user_input, bot_input_ids)
        if emergency_response:
            return emergency_response, bot_input_ids

        # التعامل مع استفسارات المتخصصين والموقع
        reply, bot_input_ids = self._handle_specialists(user_input, bot_input_ids)
        if reply:
            return reply, bot_input_ids

        # التعامل مع طلبات تحديد المواعيد
        response, bot_input_ids = self._handle_appointment_request(user_input, bot_input_ids)
        if response:
            return response, bot_input_ids

        # توليد الرد العام باستخدام النموذج المدرب
        with torch.no_grad():
            outputs = self.model.generate(
                bot_input_ids,
                max_length=inputs.shape[1] + 100,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=self.tokenizer.eos_token_id,
                attention_mask=torch.ones_like(inputs)
            )

        chat_history_ids = outputs
        response = self.tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=False)
        response = self.prompt_engineering.clean_response(response)

        return response, chat_history_ids
