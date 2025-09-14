#!/usr/bin/env python3
"""
تكوين Webhook.site للعمل مع Slack
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class WebhookConfig:
    """تكوين Webhook.site"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    
    def is_configured(self) -> bool:
        """التحقق من تكوين Webhook"""
        return bool(self.webhook_url and self.webhook_url.startswith("https://webhook.site/"))
    
    def test_connection(self) -> bool:
        """اختبار الاتصال مع Webhook"""
        if not self.is_configured():
            print("❌ Webhook غير مُعرّف")
            return False
        
        try:
            # إرسال طلب اختبار
            test_data = {"test": "connection", "timestamp": "2024-01-01T00:00:00Z"}
            response = requests.post(self.webhook_url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                print("✅ الاتصال مع Webhook ناجح!")
                return True
            else:
                print(f"❌ خطأ في الاتصال: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def send_slack_event(self, event_data: dict) -> bool:
        """إرسال حدث Slack إلى Webhook"""
        if not self.is_configured():
            print("❌ Webhook غير مُعرّف")
            return False
        
        try:
            response = requests.post(self.webhook_url, json=event_data, timeout=10)
            
            if response.status_code == 200:
                print("✅ تم إرسال حدث Slack بنجاح!")
                return True
            else:
                print(f"❌ خطأ في إرسال الحدث: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في إرسال الحدث: {e}")
            return False
    
    def get_config_info(self) -> dict:
        """جلب معلومات التكوين"""
        return {
            "webhook_url": self.webhook_url,
            "is_configured": self.is_configured(),
            "slack_bot_token": self.slack_bot_token[:10] + "..." if self.slack_bot_token else None,
            "slack_signing_secret": self.slack_signing_secret[:10] + "..." if self.slack_signing_secret else None
        }

def setup_slack_webhook():
    """إعداد Slack Webhook"""
    print("🔗 إعداد Slack Webhook...")
    
    config = WebhookConfig()
    
    if not config.is_configured():
        print("❌ SLACK_WEBHOOK_URL غير موجود في ملف .env")
        print("📝 أضف: SLACK_WEBHOOK_URL=https://webhook.site/your-unique-id")
        return False
    
    print(f"🌐 Webhook URL: {config.webhook_url}")
    
    # اختبار الاتصال
    if config.test_connection():
        print("✅ Webhook جاهز للاستخدام!")
        return True
    else:
        print("❌ فشل في اختبار Webhook")
        return False

def create_slack_app_guide():
    """إنشاء دليل إعداد تطبيق Slack مع Webhook"""
    guide = """
# 🚀 دليل إعداد Slack مع Webhook.site

## الخطوة 1: إنشاء تطبيق Slack
1. اذهب إلى: https://api.slack.com/apps
2. اضغط "Create New App"
3. اختر "From scratch"
4. أدخل اسم: "Siyadah Ops AI"
5. اختر Workspace الخاص بك

## الخطوة 2: إعداد Event Subscriptions
1. اذهب إلى "Event Subscriptions"
2. فعّل "Enable Events"
3. أضف Request URL: https://webhook.site/6b74a037-5cfb-4c86-b189-bbd523d29c94
4. أضف Bot Events:
   - app_mentions
   - message.channels

## الخطوة 3: إعداد OAuth & Permissions
1. اذهب إلى "OAuth & Permissions"
2. في "Scopes" أضف:
   - app_mentions:read
   - chat:write
   - users:read
3. اضغط "Install to Workspace"
4. انسخ "Bot User OAuth Token" (xoxb-...)

## الخطوة 4: إعداد Signing Secret
1. اذهب إلى "Basic Information"
2. انسخ "Signing Secret"

## الخطوة 5: تحديث ملف .env
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-secret-here
SLACK_WEBHOOK_URL=https://webhook.site/6b74a037-5cfb-4c86-b189-bbd523d29c94

## الخطوة 6: اختبار التكامل
1. شغل النظام: python main_perfect.py
2. أضف البوت للقناة: /invite @Siyadah Ops AI
3. اكتب: @Siyadah Ops AI مهمة: اختبار
4. راقب البيانات في: https://webhook.site/6b74a037-5cfb-4c86-b189-bbd523d29c94

## ✅ جاهز للاستخدام!
"""
    
    with open("SLACK_WEBHOOK_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("📄 تم إنشاء دليل Webhook: SLACK_WEBHOOK_GUIDE.md")

if __name__ == "__main__":
    print("🚀 إعداد Webhook.site مع Slack")
    print("=" * 50)
    
    # إنشاء دليل الإعداد
    create_slack_app_guide()
    
    # إعداد Webhook
    if setup_slack_webhook():
        print("\n📋 الخطوات التالية:")
        print("1. اتبع دليل SLACK_WEBHOOK_GUIDE.md")
        print("2. أضف الـ tokens في ملف .env")
        print("3. شغل النظام: python main_perfect.py")
        print("4. اختبر: @Siyadah Ops AI مهمة: اختبار")
        print("5. راقب البيانات في: https://webhook.site/6b74a037-5cfb-4c86-b189-bbd523d29c94")
    else:
        print("\n❌ فشل في إعداد Webhook")
        print("📝 تأكد من إضافة SLACK_WEBHOOK_URL في ملف .env")
