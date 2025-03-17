import requests
import json

class EitaaBot:
    def __init__(self, token):
        """مقداردهی اولیه ربات با توکن"""
        self.token = token
        self.base_url = "https://eitaayar.ir/api/"

    def call_api(self, method, data=None, files=None):
        """تابع کلی برای فراخوانی API"""
        url = f"{self.base_url}{self.token}/{method}"
        try:
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"خطا در فراخوانی {method}: {e}")
            return None

    def send_message(self, chat_id, text):
        """ارسال پیام متنی"""
        data = {
            'chat_id': chat_id,
            'text': text
        }
        return self.call_api('sendMessage', data)

    def send_file(self, chat_id, file_path, caption=None):
        """ارسال فایل"""
        files = {
            'file': open(file_path, 'rb')
        }
        data = {
            'chat_id': chat_id
        }
        if caption:
            data['caption'] = caption
        return self.call_api('sendFile', data, files)

    def get_updates(self):
        """دریافت پیام‌های جدید"""
        return self.call_api('getUpdates')

def main():
    # توکن ربات خود را اینجا قرار دهید
    TOKEN = "bot368550:YOUR-TOKEN-HERE"
    
    # ایجاد یک نمونه از ربات
    bot = EitaaBot(TOKEN)
    
    # تست اولیه - ارسال پیام
    print("=== تست ربات ایتا ===")
    chat_id = input("لطفا chat_id را وارد کنید: ")
    
    # ارسال پیام تست
    print("\nتست ارسال پیام...")
    result = bot.send_message(chat_id, "سلام! 👋 این یک پیام تست است.")
    print(f"نتیجه: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # تست دریافت پیام‌ها
    print("\nدر حال دریافت پیام‌های جدید...")
    updates = bot.get_updates()
    print(f"پیام‌های دریافتی: {json.dumps(updates, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main() 