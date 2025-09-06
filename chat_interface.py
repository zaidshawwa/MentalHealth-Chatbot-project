import gradio as gr
from mental_health_chatbot import MentalHealthChatbot  # استيراد الفئة الجديدة

class ChatInterface:
    def __init__(self):
        """إعداد الفئة للمحادثة مع نموذج الذكاء الاصطناعي"""
        self.chatbot = MentalHealthChatbot()  # إنشاء كائن من فئة MentalHealthChatbot
        self.model, self.tokenizer = self.chatbot.model, self.chatbot.tokenizer  # تحميل النموذج والمحولات

    def chat_interface(self, message, history):
        """واجهة المحادثة التي تظهر رسائل المستخدم والروبوت"""
        try:
            # توليد الرد باستخدام النموذج
            emergency_response, bot_input_ids = self.chatbot.generate_response(message, history)
            if emergency_response:
                history.append([message, emergency_response])
                return history, ""

            # إضافة المحادثة إلى التاريخ
            history.append([message, bot_input_ids])
            return history, ""

        except Exception as e:
            # التعامل مع الأخطاء وتقديم رد احتياطي
            error_response = "I'm here to support you. Could you please rephrase your question?"
            history.append([message, error_response])
            return history, ""

    def launch_interface(self):
        """إطلاق واجهة Gradio للمستخدمين للتفاعل مع نموذج المحادثة"""
        # إعدادات CSS لتنسيق واجهة المستخدم
        css = """
        .gradio-container {
            max-width: 900px !important;
            margin: auto !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .message-row {
            margin: 8px 0;
        }

        .user-message {
            color: #2d3436;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            margin-left: 20%;
            margin-right: 5px;
            border: 1px solid #dfe6e9;
        }

        .bot-message {
            color: #2d3436;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            margin-right: 20%;
            margin-left: 5px;
            border-left: 4px solid #636e72;
        }
        """

        with gr.Blocks(css=css, title="Mental Health Counseling Chatbot") as demo:
            gr.HTML("""
            <div class="disclaimer">
                <h2>🌟 Mental Health Support Chatbot</h2>
                <p><strong>Note:</strong> This chatbot is designed to provide supportive conversations and general guidance.
                It is NOT a replacement for professional mental health care. If you're experiencing a mental health crisis,
                please contact a healthcare professional or crisis helpline immediately.</p>
            </div>
            """)

            with gr.Row():
                with gr.Column():
                    chatbot_interface = gr.Chatbot(
                        value=[],
                        elem_id="chatbot",
                        bubble_full_width=False,
                        height=500,
                        label="💬 Mental Health Support Chat",
                        show_label=True,
                        avatar_images=["👤", "🤖"],  # User and bot avatars
                        show_share_button=False
                    )

            with gr.Row(elem_classes="input-area"):
                with gr.Column(scale=4):
                    msg = gr.Textbox(
                        placeholder="💭 Share what's on your mind... I'm here to listen and support you.",
                        label="Your Message",
                        lines=4,
                        max_lines=5,
                        show_label=False,
                        container=False
                    )
                with gr.Column(scale=1, min_width=100):
                    send_btn = gr.Button("Send", elem_classes="send-btn", size="lg")
                    clear = gr.Button("Clear", variant="secondary", elem_classes="clear-btn")

            # إعداد الأسئلة التجريبية
            with gr.Row():
                gr.Examples(
                    examples=[
                        ["I've been feeling really anxious lately and can't seem to shake it off."],
                        ["I don't feel motivated to do anything anymore."],
                        ["I feel like I'm not good enough compared to others."],
                        ["I can't fall asleep because my mind won't stop racing."],
                        ["I'm having problems communicating with my partner."],
                        ["What are some healthy ways to deal with stress?"],
                        ["I feel stuck in my current situation and don't know how to change."],
                    ],
                    inputs=msg,
                    label="💡 Try these example questions:"
                )

            # ربط الأحداث للزر Send وإرسال الرسائل باستخدام Enter
            msg.submit(self.chat_interface, [msg, chatbot_interface], [chatbot_interface, msg])
            send_btn.click(self.chat_interface, [msg, chatbot_interface], [chatbot_interface, msg])
            clear.click(lambda: ([], ""), None, [chatbot_interface, msg], queue=False)

            # إطلاق الواجهة
            demo.launch(
                share=True,  # إنشاء رابط عام
                debug=False,
                server_name="0.0.0.0"
            )
