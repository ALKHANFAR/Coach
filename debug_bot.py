from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

@app.route('/slack/events', methods=['POST'])
def slack_events():
    print("=" * 50)
    print("📡 طلب جديد وارد!")
    
    print(f"🌍 IP المرسل: {request.remote_addr}")
    print(f"📋 Headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"📥 البيانات الواردة: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ خطأ في قراءة JSON: {e}")
        return "Invalid JSON", 400
    
    if 'challenge' in data:
        challenge = data['challenge']
        print(f"🔐 Challenge detected: {challenge}")
        return challenge, 200, {'Content-Type': 'text/plain'}
    
    if 'event' in data:
        event = data['event']
        print(f"🎯 نوع الحدث: {event.get('type')}")
        
        if event.get('type') == 'app_mention':
            print("✅ تم اكتشاف app_mention!")
            
            channel = event.get('channel')
            text = event.get('text', '')
            
            print(f"📍 القناة: {channel}")
            print(f"💬 النص: {text}")
            
            try:
                url = "https://slack.com/api/chat.postMessage"
                headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
                payload = {"channel": channel, "text": "تم استلام رسالتك!"}
                
                response = requests.post(url, headers=headers, json=payload)
                result = response.json()
                
                print(f"📨 رد Slack: {result}")
                
            except Exception as e:
                print(f"💥 خطأ: {e}")
    
    return 'OK', 200

@app.route('/health')
def health():
    return {'status': 'working'}

if __name__ == '__main__':
    print("🔧 بدء تشغيل بوت التشخيص...")
    app.run(host='0.0.0.0', port=8006, debug=True)
