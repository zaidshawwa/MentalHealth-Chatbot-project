import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

class AppointmentManager:
    def __init__(self):
        # إعداد OAuth2 للوصول إلى Google Sheets
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('/path/to/credentials.json', self.scope)
        self.client = gspread.authorize(self.creds)  # الاتصال بخدمة Google Sheets
        self.sheet = self.client.open('MentalHealth').sheet1  # فتح الورقة الأولى في ملف Google Sheets

    def store_appointment_data(self, data):
        """
        دالة لإضافة البيانات إلى Google Sheets
        """
        self.sheet.append_row(data)  # إضافة صف جديد من البيانات إلى الورقة

    def authenticate_gmail(self):
        """
        دالة مصادقة للوصول إلى Gmail API
        """
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)  # تحميل التوكن من الملف إذا كان موجودًا

        # إذا كانت بيانات المصادقة غير صالحة أو منتهية الصلاحية، يتم تجديدها أو طلبها من المستخدم
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # تجديد التوكن إذا كان منتهي الصلاحية
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/path/to/credentials.json', ['https://www.googleapis.com/auth/gmail.send'])
                creds = flow.run_local_server(port=0)  # مصادقة عبر واجهة المستخدم

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)  # تخزين التوكن بعد التجديد

        service = build('gmail', 'v1', credentials=creds)  # بناء خدمة Gmail API
        return service
    
    def send_confirmation_email(self, service, to_email, appointment_details):
        """
        إرسال بريد إلكتروني لتأكيد الموعد باستخدام Gmail API
        """
        try:
            message = MIMEMultipart()  # إنشاء رسالة بريد إلكتروني
            message['to'] = to_email
            message['subject'] = "Appointment Confirmation"
            
            # إنشاء محتوى البريد الإلكتروني
            body = f"""
Dear {appointment_details['Patient Name']},

Your appointment has been confirmed.

Date: {appointment_details['Date']}
Time: {appointment_details['Time']}
Specialist: {appointment_details['Specialty']}
Location: {appointment_details['Location']}
Phone: {appointment_details['Phone']}
Condition: {appointment_details['Patient\'s Condition']}
Additional Notes: {appointment_details['Additional Notes']}

Thank you for booking with us!

Best regards,
Mental Health Support Team
"""
            message.attach(MIMEText(body, 'plain'))  # إرفاق نص البريد
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()  # تحويل الرسالة إلى تنسيق قابل للإرسال
            send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()  # إرسال الرسالة
            print(f"Message sent to {to_email}, Message Id: {send_message['id']}")  # طباعة رسالة النجاح
        except Exception as error:
            print(f"An error occurred: {error}")  # طباعة الخطأ إذا حدث

    def detect_appointment_request(self, user_input):
        """
        الكشف عن ما إذا كانت المحادثة تتعلق بحجز موعد
        """
        appointment_keywords = ["booking", "appointment", "time", "schedule an appointment", "I need an appointment"]
        
        return any(keyword in user_input.lower() for keyword in appointment_keywords)  # التحقق من وجود كلمات حجز الموعد في الإدخال

    def ask_for_appointment_details(self, user_input):
        """
        طلب تفاصيل الموعد من المستخدم بطريقة حوارية.
        """
        # تتبع جمع التفاصيل باستخدام معجم (collected_data) لتخزين المدخلات
        if "name" not in self.collected_data:
            self.collected_data["name"] = user_input
            return "Please provide the specialty (e.g., Psychologist, Psychiatrist, etc.)."
        
        if "specialty" not in self.collected_data:
            self.collected_data["specialty"] = user_input
            return "Please provide the appointment date (e.g., 2023-10-20)."
        
        if "date" not in self.collected_data:
            self.collected_data["date"] = user_input
            return "Please provide the appointment time (e.g., 10:00 AM)."
        
        if "time" not in self.collected_data:
            self.collected_data["time"] = user_input
            return "Please provide your email address."
        
        if "email" not in self.collected_data:
            self.collected_data["email"] = user_input
            return "Please provide your phone number."
        
        if "phone" not in self.collected_data:
            self.collected_data["phone"] = user_input
            return "Please provide your location."
        
        if "location" not in self.collected_data:
            self.collected_data["location"] = user_input
            return "Please describe your condition (e.g., Anxiety, Stress)."
        
        if "condition" not in self.collected_data:
            self.collected_data["condition"] = user_input
            return "Please provide any additional notes you may have."
        
        if "notes" not in self.collected_data:
            self.collected_data["notes"] = user_input
            # بعد جمع جميع التفاصيل، نقوم بتخزينها
            appointment_data = [
                self.collected_data["name"],
                self.collected_data["specialty"],
                self.collected_data["date"],
                self.collected_data["time"],
                self.collected_data["email"],
                self.collected_data["phone"],
                self.collected_data["location"],
                self.collected_data["condition"],
                self.collected_data["notes"]
            ]
            # تخزين البيانات في Google Sheets
            self.store_appointment_data(appointment_data)
            
            # إرسال تأكيد بالبريد الإلكتروني للمريض
            service = self.authenticate_gmail()
            self.send_confirmation_email(service, self.collected_data["email"], self.collected_data)
            
            # إعادة تعيين collected_data بعد تخزين البيانات
            self.collected_data = {}
            self.asking_for_appointment = False

            return "Your appointment has been successfully booked. A confirmation email has been sent."

        return "Sorry, something went wrong. Please try again."

