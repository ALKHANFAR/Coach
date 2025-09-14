#!/usr/bin/env python3
"""
اختبار Webhook.site مع Slack
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_webhook():
    """اختبار webhook.site"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL غير موجود في ملف .env")
        return False
    
    print(f"🔗 اختبار webhook: {webhook_url}")
    
    # بيانات اختبار محاكية لـ Slack
    test_data = {
        "token": "verification_token",
        "team_id": "T1234567890",
        "api_app_id": "A1234567890",
        "event": {
            "type": "app_mention",
            "text": "<@U1234567890> مهمة: اختبار webhook",
            "user": "U1234567890",
            "channel": "C1234567890",
            "ts": "1234567890.123456"
        },
        "type": "event_callback",
        "event_id": "Ev1234567890",
        "event_time": 1234567890
    }
    
    try:
        print("📤 إرسال بيانات اختبار...")
        response = requests.post(webhook_url, json=test_data)
        
        if response.status_code == 200:
            print("✅ تم إرسال البيانات بنجاح!")
            print(f"📊 البيانات المرسلة:")
            print(json.dumps(test_data, ensure_ascii=False, indent=2))
            print(f"\n🌐 تحقق من النتائج في: {webhook_url}")
            return True
        else:
            print(f"❌ خطأ في الإرسال: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")
        return False

def test_slack_challenge():
    """اختبار Slack URL Verification"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL غير موجود في ملف .env")
        return False
    
    # بيانات تحقق URL
    challenge_data = {
        "token": "verification_token",
        "challenge": "test_challenge_string",
        "type": "url_verification"
    }
    
    try:
        print("🔐 اختبار Slack URL Verification...")
        response = requests.post(webhook_url, json=challenge_data)
        
        if response.status_code == 200:
            print("✅ تم إرسال تحقق URL بنجاح!")
            print(f"📊 بيانات التحقق:")
            print(json.dumps(challenge_data, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"❌ خطأ في تحقق URL: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تحقق URL: {e}")
        return False

def monitor_webhook():
    """مراقبة webhook"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    print(f"👀 مراقبة webhook: {webhook_url}")
    print("📋 افتح الرابط في المتصفح لمراقبة البيانات الواردة")
    print("🔄 أرسل رسائل في Slack لرؤية البيانات في الوقت الفعلي")
    print("\n📝 أمثلة للاختبار:")
    print("   @Siyadah Ops AI مهمة: اختبار webhook")
    print("   @Siyadah Ops AI هدف: تطوير ميزة جديدة")
    print("   @Siyadah Ops AI مساعدة")

if __name__ == "__main__":
    print("🚀 اختبار Webhook.site مع Slack")
    print("=" * 50)
    
    # اختبار إرسال البيانات
    print("\n1️⃣ اختبار إرسال البيانات:")
    test_webhook()
    
    print("\n2️⃣ اختبار Slack URL Verification:")
    test_slack_challenge()
    
    print("\n3️⃣ مراقبة Webhook:")
    monitor_webhook()
    
    print("\n✅ انتهى الاختبار!")
    print("🌐 تحقق من النتائج في: https://webhook.site/6b74a037-5cfb-4c86-b189-bbd523d29c94")
