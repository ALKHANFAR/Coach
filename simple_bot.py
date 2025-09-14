from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء تطبيق Flask
app = Flask(__name__)

# تحميل SLACK_BOT_TOKEN من متغيرات البيئة
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    print(f"📥 تم استلام: {data}")
    
    if 'challenge' in data:
        print(f"✅ Challenge: {data['challenge']}")
        return data['challenge'], 200, {'Content-Type': 'text/plain'}
    
    if 'event' in data:
        event = data['event']
        print(f"🔍 Event type: {event.get('type')}")
        print(f"🔍 Full event: {event}")
        
        if event.get('type') in ['app_mention', 'message'] and not event.get('bot_id'):
            channel = event.get('channel')
            text = event.get('text', '')
            
            print(f"📤 إرسال رد إلى قناة: {channel}")
            
            url = "https://slack.com/api/chat.postMessage"
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
            payload = {"channel": channel, "text": "مرحباً! أنا أعمل الآن! 🚀"}
            
            response = requests.post(url, headers=headers, json=payload)
            print(f"✅ نتيجة الإرسال: {response.json()}")
    
    return 'OK', 200

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة الخادم"""
    print("🏥 تم طلب فحص الصحة")
    return jsonify({'status': 'working'})

if __name__ == '__main__':
    print("🚀 بدء تشغيل Simple Slack Bot...")
    print(f"🔑 تم تحميل SLACK_BOT_TOKEN: {'✅ موجود' if SLACK_BOT_TOKEN else '❌ غير موجود'}")
    print("🌐 الخادم يعمل على المنفذ 8004")
    print("📡 انتظار الأحداث من Slack...")
    
    app.run(host='0.0.0.0', port=8005, debug=True)

