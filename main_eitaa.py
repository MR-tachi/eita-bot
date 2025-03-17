import sqlite3
import json
from flask import Flask, request, jsonify
from functools import wraps
import hashlib
import hmac
import time

app = Flask(__name__)

# تنظیمات
BOT_TOKEN = "bot368550:cd9b867f-e504-404c-8a23-97ab478ba77a"
CHANNEL_LINK = "https://eitaa.com/joinchat/2595095666Ca068ffb164" 
MANAGER_CHAT_ID = 123456789
MAX_ATTEMPTS = 2

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valid_codes (
            code TEXT PRIMARY KEY
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO valid_codes (code) VALUES ('1012'), ('1013')")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eitaa_id INTEGER UNIQUE,
            personnel_code TEXT,
            answers TEXT,
            submitted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def verify_eitaa_hash(data_check_string, hash):
    """تایید اعتبار درخواست‌های دریافتی از ایتا"""
    secret_key = hmac.new(BOT_TOKEN.encode(), msg=None, digestmod=hashlib.sha256)
    return hmac.new(
        secret_key.digest(),
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest() == hash

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        init_data = request.args.get('initData', '')
        if not init_data:
            return jsonify({'error': 'No init data provided'}), 401
            
        # اعتبارسنجی داده‌های ورودی
        try:
            data_pairs = dict(pair.split('=') for pair in init_data.split('&'))
            hash = data_pairs.pop('hash')
            data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data_pairs.items()))
            
            if not verify_eitaa_hash(data_check_string, hash):
                return jsonify({'error': 'Invalid hash'}), 401
                
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """صفحه اصلی برنامک"""
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <script src="https://developer.eitaa.com/eitaa-web-app.js"></script>
        <title>فرم ثبت نام</title>
        <style>
            body { font-family: Vazir, Tahoma; }
            .form-container { padding: 20px; }
            .input-group { margin-bottom: 15px; }
            button { padding: 10px; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <div id="personnel-code-form">
                <div class="input-group">
                    <label>کد پرسنلی:</label>
                    <input type="text" id="personnel-code">
                </div>
                <button onclick="checkPersonnelCode()">تایید</button>
            </div>
            <div id="questions-form" style="display: none;">
                <!-- سوالات اینجا به صورت پویا اضافه می‌شوند -->
            </div>
        </div>
        <script>
            let attempts = 0;
            const questions = [
                "نام کامل خود را وارد کنید.",
                "شغل شما چیست؟"
            ];
            let currentQuestion = 0;
            let answers = [];

            async function checkPersonnelCode() {
                const code = document.getElementById('personnel-code').value;
                const response = await fetch('/check-code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code})
                });
                const data = await response.json();
                
                if (data.valid) {
                    document.getElementById('personnel-code-form').style.display = 'none';
                    showQuestions();
                } else {
                    attempts++;
                    if (attempts >= 2) {
                        Eitaa.WebApp.close();
                    } else {
                        alert('کد نامعتبر است. لطفا مجددا تلاش کنید.');
                    }
                }
            }

            function showQuestions() {
                const container = document.getElementById('questions-form');
                container.style.display = 'block';
                container.innerHTML = `
                    <div class="input-group">
                        <label>${questions[currentQuestion]}</label>
                        <input type="text" id="current-answer">
                    </div>
                    <button onclick="submitAnswer()">ثبت پاسخ</button>
                `;
            }

            async function submitAnswer() {
                const answer = document.getElementById('current-answer').value;
                answers.push(answer);
                
                if (currentQuestion < questions.length - 1) {
                    currentQuestion++;
                    showQuestions();
                } else {
                    await submitForm();
                }
            }

            async function submitForm() {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        answers: answers,
                        personnel_code: document.getElementById('personnel-code').value
                    })
                });
                
                if (response.ok) {
                    alert('فرم با موفقیت ثبت شد.');
                    Eitaa.WebApp.openEitaaLink(${CHANNEL_LINK});
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/check-code', methods=['POST'])
@auth_required
def check_code():
    """بررسی اعتبار کد پرسنلی"""
    code = request.json.get('code')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM valid_codes WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return jsonify({'valid': result is not None})

@app.route('/submit', methods=['POST'])
@auth_required
def submit():
    """ثبت پاسخ‌های کاربر"""
    data = request.json
    user_id = request.args.get('user_id')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (eitaa_id, personnel_code, answers, submitted)
            VALUES (?, ?, ?, 1)
        """, (user_id, data['personnel_code'], json.dumps(data['answers'])))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    create_db()
    app.run(debug=True) 