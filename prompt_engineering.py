import re
from specialist_manager import SpecialistManager


class PromptEngineering:
    
    def prepare_prompt(self, user_input):
        """
        تحضير النص الموجه (prompt) باستخدام مدخلات المستخدم.
        يتم تحديد دور المساعد، الحدود، الأسلوب، ومثالين سابقين لتمكين النموذج من توليد الردود بشكل مناسب.
        """
        SYSTEM_PROMPT = """
        [ROLE]
        You are an informational, empathetic, and calm support worker. Your mission: to listen, reflect feelings, and provide general, evidence-based information, links to credible resources, and simple exercises to calm anxiety.

        [BOUNDARIES]
        - You are not a therapist and do not provide a diagnosis or treatment plan.
        - Do not make judgments, promises, or medical claims.
        - In any case of danger or harm to self/others: Provide an immediate safety message and direct to urgent help.

        [STYLE]
        - Use simple Arabic, short sentences, a supportive and kind tone, and no complex medical jargon.
        - Always begin with a brief summary of what you have understood (reflect feelings), followed by one short follow-up question, one practical suggestion (breathing exercise/emotion regulation), and a reminder of boundaries.

        [OUTPUT]
        - Divide the response into 4 short paragraphs: (Sympathy) – (Summary) – (Practical Suggestion) – (Reminder and Limitations).
        """

        FEW_SHOT_EXAMPLES = """
        Example 1:
        Human: I've been feeling really anxious lately and can't seem to shake it off.
        Assistant: I understand that anxiety can be overwhelming. It's important to acknowledge these feelings rather than fighting them. Have you noticed any specific triggers for your anxiety? Some helpful techniques include deep breathing exercises, grounding techniques like the 5-4-3-2-1 method, or gentle physical activity. Would you like to explore what might be contributing to these feelings?

        Example 2:
        Human: I feel like I'm not good enough and everyone is better than me.
        Assistant: Those feelings of inadequacy can be really painful. It's common to compare ourselves to others, but remember that you're seeing their highlight reel, not their struggles. Your worth isn't determined by comparison to others. What are some things you're proud of about yourself? Let's focus on your strengths and achievements, no matter how small they might seem.

        Example 3:
        Human: I'm having trouble sleeping and my mind won't stop racing.
        Assistant: Racing thoughts at bedtime are very common and can be exhausting. Creating a bedtime routine can help signal to your mind that it's time to wind down. Try writing down your worries before bed, practice progressive muscle relaxation, or try the 4-7-8 breathing technique. Limiting screen time an hour before bed can also help. What does your current bedtime routine look like?
        """
        
        # التعامل مع الرد من المتخصصين إذا كان موجودًا
        specialist_response = SpecialistManager().handle_specialists(user_input)
        if specialist_response:  
            # إذا كان هناك رد من المتخصص، يتم إضافته إلى النص الموجه
            prompt = f"User: {user_input}\nExperts Info: {specialist_response}\nAssistant:"
        else:
            # إذا لم يكن هناك رد من المتخصص، نستخدم النص الأساسي مع أمثلة سابقه
            prompt = SYSTEM_PROMPT + "\n\n" + FEW_SHOT_EXAMPLES + f"\nUser: {user_input}\nAssistant:"
        
        return prompt  # إرجاع النص الموجه النهائي

    def clean_response(self, response):
        """تنظيف وتنسيق الاستجابة من النموذج"""
        # استبدال الرموز غير المرغوب فيها وتنظيف الاستجابة
        response = response.replace("\xa0", " ").strip()  # إزالة مسافات غير مرئية
        response = re.sub(r'<\|.*?\|>', '', response)  # إزالة النصوص داخل القوالب غير المرغوب فيها
        response = response.replace("\'", "")  # إزالة العلامات غير المرغوب فيها
        response = re.sub(r'(\n)+', '\n', response)  # دمج الأسطر المتعددة إلى سطر واحد
        response = re.sub(r"\b(I wish you|I hope that)\b", "", response)  # إزالة العبارات غير المفيدة
        response = re.sub(r"\bI will\b", "", response)  # إزالة العبارات المستقبلية غير المرغوب فيها
        response = re.sub(r'\s+', ' ', response).strip()  # إزالة المسافات الزائدة بين الكلمات

        # إذا كانت الاستجابة قصيرة جدًا أو فارغة، يتم إعادة توجيه المستخدم لشرح مشاعره
        if len(response) < 10 or not response:
            return "I understand you're going through something difficult. Can you help me understand what you're feeling right now?"

        return response  # إرجاع الاستجابة بعد تنظيفها
