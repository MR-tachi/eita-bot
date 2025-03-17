<?php

require_once 'jdate.php'; // یا هر کتابخانه تاریخ شمسی دیگر

class EitaaBot {
    private $token;
    private $api_url = 'https://eitaayar.ir/api/';

    public function __construct($token) {
        $this->token = $token;
    }

    // دریافت پیام‌های ورودی
    public function getUpdates() {
        $url = $this->api_url . $this->token . '/getUpdates';
        return $this->sendRequest($url, []);
    }

    // پردازش پیام‌های دریافتی
    public function handleUpdates() {
        $updates = $this->getUpdates();
        
        if (isset($updates['messages'])) {
            foreach ($updates['messages'] as $message) {
                $this->processMessage($message);
            }
        }
    }

    // پردازش هر پیام
    private function processMessage($message) {
        $chat_id = $message['chat_id'];
        $text = $message['text'] ?? '';

        switch (strtolower($text)) {
            case '/start':
                $this->sendMessage($chat_id, "سلام! به ربات ما خوش آمدید.\n\nاز دستورات زیر می‌توانید استفاده کنید:\n/help - راهنما\n/time - زمان فعلی\n/about - درباره ما");
                break;

            case '/help':
                $this->sendMessage($chat_id, "راهنمای دستورات:\n/start - شروع\n/time - نمایش زمان\n/about - درباره ما");
                break;

            case '/time':
                $time = jdate('Y/m/d H:i:s');
                $this->sendMessage($chat_id, "زمان فعلی: $time");
                break;

            case '/about':
                $this->sendMessage($chat_id, "این یک ربات نمونه است که با API ایتا ساخته شده است.");
                break;

            default:
                // پاسخ به پیام‌های معمولی
                if (strpos($text, 'سلام') !== false) {
                    $this->sendMessage($chat_id, "سلام! چطور می‌تونم کمکتون کنم؟");
                } elseif (strpos($text, 'خداحافظ') !== false) {
                    $this->sendMessage($chat_id, "خداحافظ! روز خوبی داشته باشید.");
                } else {
                    $this->sendMessage($chat_id, "پیام شما دریافت شد. برای دیدن لیست دستورات، /help را وارد کنید.");
                }
                break;
        }
    }

    // ارسال پیام متنی
    public function sendMessage($chat_id, $text) {
        $url = $this->api_url . $this->token . '/sendMessage';
        $data = [
            'chat_id' => $chat_id,
            'text' => $text
        ];
        return $this->sendRequest($url, $data);
    }

    // ارسال فایل
    public function sendFile($chat_id, $file_path, $caption = '', $title = '') {
        $url = $this->api_url . $this->token . '/sendFile';
        $data = [
            'chat_id' => $chat_id,
            'file' => new CURLFile(realpath($file_path)),
            'caption' => $caption,
            'title' => $title
        ];
        return $this->sendRequest($url, $data);
    }

    private function sendRequest($url, $data) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}

// نحوه استفاده از ربات تعاملی
$token = 'bot368550:cd9b867f-e504-404c-8a23-97ab478ba77a'; // توکن خودتون رو اینجا بذارید
$bot = new EitaaBot($token);

// اجرای حلقه اصلی ربات
while (true) {
    $bot->handleUpdates();
    sleep(2); // تاخیر 2 ثانیه‌ای بین هر بررسی
} 