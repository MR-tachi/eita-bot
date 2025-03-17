import requests

def test_eitaa_bot(token, chat_id):
    """تست ساده ربات ایتا"""
    base_url = "https://eitaayar.ir/api/"
    
    # تست ارسال یک پیام ساده
    url = f"{base_url}{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': "تست ربات ایتا 🤖"
    }
    
    try:
        print("در حال ارسال درخواست...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, data=data)
        print(f"\nکد پاسخ: {response.status_code}")
        print(f"پاسخ: {response.text}")
        
        return response.json()
    except Exception as e:
        print(f"خطا: {e}")
        return None

def main():
    print("=== برنامه تست ربات ایتا ===")
    
    # دریافت اطلاعات از کاربر
    token = input("لطفا توکن ربات را وارد کنید (با bot شروع شود): ")
    chat_id = input("لطفا chat_id را وارد کنید: ")
    
    # اطمینان از صحت توکن
    if not token.startswith('bot'):
        token = 'bot' + token
    
    # تست ربات
    result = test_eitaa_bot(token, chat_id)
    
    if result and result.get('ok'):
        print("\n✅ تست موفقیت‌آمیز بود!")
    else:
        print("\n❌ تست با خطا مواجه شد.")

if __name__ == "__main__":
    main() 