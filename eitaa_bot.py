import requests
import time
import jdatetime  # برای تاریخ شمسی

class EitaaBot:
    def __init__(self, token):
        self.token = token
        self.api_url = 'https://eitaayar.ir/api/'

    def get_updates(self):
        url = f"{self.api_url}{self.token}/getUpdates"
        response = requests.post(url)
        return response.json()

    def send_message(self, chat_id, text):
        url = f"{self.api_url}{self.token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, data=data)
        return response.json()

    def send_file(self, chat_id, file_path, caption='', title=''):
        url = f"{self.api_url}{self.token}/sendFile"
        files = {
            'file': open(file_path, 'rb')
        }
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'title': title
        }
        response = requests.post(url, files=files, data=data)
        return response.json()

    def process_message(self, message):
        chat_id = message.get('chat_id')
        text = message.get('text', '')

        if text.lower() == '/start':
            self.send_message(chat_id, 
                "سلام! به ربات ما خوش آمدید.\n\n"
                "از دستورات زیر می‌توانید استفاده کنید:\n"
                "/help - راهنما\n"
                "/time - زمان فعلی\n"
                "/about - درباره ما")

        elif text.lower() == '/help':
            self.send_message(chat_id,
                "راهنمای دستورات:\n"
                "/start - شروع\n"
                "/time - نمایش زمان\n"
                "/about - درباره ما")

        elif text.lower() == '/time':
            current_time = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.send_message(chat_id, f"زمان فعلی: {current_time}")

        elif text.lower() == '/about':
            self.send_message(chat_id, "این یک ربات نمونه است که با API ایتا ساخته شده است.")

        elif 'سلام' in text:
            self.send_message(chat_id, "سلام! چطور می‌تونم کمکتون کنم؟")

        elif 'خداحافظ' in text:
            self.send_message(chat_id, "خداحافظ! روز خوبی داشته باشید.")

        else:
            self.send_message(chat_id, "پیام شما دریافت شد. برای دیدن لیست دستورات، /help را وارد کنید.")

    def handle_updates(self):
        updates = self.get_updates()
        if 'messages' in updates:
            for message in updates['messages']:
                self.process_message(message)

def main():
    # توکن خود را اینجا قرار دهید
    token = 'bot368550:131ff932-cf46-41ec-83ca-e9f8381784c1'
    bot = EitaaBot(token)

    # تست ارسال پیام
    chat_id = input("لطفا chat_id مقصد را وارد کنید: ")
    test_message = "این یک پیام تستی است! 😊"
    
    print("در حال ارسال پیام تستی...")
    response = bot.send_message(chat_id, test_message)
    print("پاسخ سرور:", response)

    # اگر می‌خواهید ربات به کار عادی خود ادامه دهد، این قسمت را هم اضافه کنید
    print("\nربات شروع به کار کرد...")
    while True:
        try:
            bot.handle_updates()
            time.sleep(2)
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()