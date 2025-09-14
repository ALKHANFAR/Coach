#!/usr/bin/env python3
"""
إعداد سريع للبوت مع فحص شامل
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def check_slack_token():
    """فحص صحة الـ Slack token"""
    token = os.getenv("SLACK_BOT_TOKEN")
    
    if not token:
        print("❌ SLACK_BOT_TOKEN غير موجود")
        return False
    
    if not token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح (يجب أن يبدأ بـ xoxb-)")
        return False
    
    # اختبار الـ token مع Slack API
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://slack.com/api/auth.test", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✅ SLACK_BOT_TOKEN صحيح - البوت: {data.get('bot_id', 'غير معروف')}")
                return True
            else:
                print(f"❌ SLACK_BOT_TOKEN غير صحيح: {data.get('error', 'خطأ غير معروف')}")
                return False
        else:
            print(f"❌ خطأ في الاتصال مع Slack API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في فحص الـ token: {e}")
        return False

def check_openai_key():
    """فحص صحة مفتاح OpenAI"""
    key = os.getenv("OPENAI_API_KEY")
    
    if not key:
        print("❌ OPENAI_API_KEY غير موجود")
        return False
    
    if not key.startswith("sk-"):
        print("❌ OPENAI_API_KEY غير صحيح (يجب أن يبدأ بـ sk-)")
        return False
    
    print("✅ OPENAI_API_KEY موجود")
    return True

def check_webhook_url():
    """فحص صحة webhook URL"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL غير موجود")
        return False
    
    if not webhook_url.startswith("https://webhook.site/"):
        print("❌ SLACK_WEBHOOK_URL غير صحيح")
        return False
    
    # اختبار الـ webhook
    try:
        test_data = {"test": "connection", "timestamp": "2024-01-01T00:00:00Z"}
        response = requests.post(webhook_url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ SLACK_WEBHOOK_URL يعمل بشكل صحيح")
            return True
        else:
            print(f"❌ SLACK_WEBHOOK_URL لا يعمل: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في فحص webhook: {e}")
        return False

def test_slack_integration():
    """اختبار التكامل مع Slack"""
    try:
        from app.integrations.slack_bot import app as slack_app
        
        if slack_app:
            print("✅ Slack Bot integration محمل بنجاح")
            return True
        else:
            print("❌ فشل في تحميل Slack Bot integration")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تحميل Slack Bot: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إعداد وفحص Siyadah Ops AI - Slack Bot")
    print("=" * 50)
    
    # فحص متغيرات البيئة
    print("\n📋 فحص متغيرات البيئة:")
    checks = [
        ("Slack Bot Token", check_slack_token),
        ("OpenAI API Key", check_openai_key),
        ("Webhook URL", check_webhook_url),
        ("Slack Integration", test_slack_integration)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 فحص {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ جميع الفحوصات نجحت!")
        print("🚀 البوت جاهز للتشغيل")
        print("\n📝 للبدء:")
        print("   python run_slack_bot.py")
        print("\n💡 للاختبار:")
        print("   1. أضف البوت للقناة: /invite @Siyadah Ops AI")
        print("   2. اكتب: @Siyadah Ops AI مهمة: اختبار")
        print("   3. راقب الرد في القناة")
    else:
        print("❌ بعض الفحوصات فشلت!")
        print("📝 راجع الإعدادات في ملف .env")
        print("\n🔧 خطوات الإصلاح:")
        print("   1. تأكد من صحة SLACK_BOT_TOKEN")
        print("   2. تأكد من صحة OPENAI_API_KEY")
        print("   3. تأكد من صحة SLACK_WEBHOOK_URL")
        print("   4. أعد تشغيل هذا الفحص")

if __name__ == "__main__":
    main()
