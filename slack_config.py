"""
تكوين Slack Bot - جاهز للاستخدام الفوري
"""

import os
from typing import Optional

class SlackConfig:
    """تكوين Slack Bot"""
    
    def __init__(self):
        self.bot_token: Optional[str] = None
        self.signing_secret: Optional[str] = None
        self.load_config()
    
    def load_config(self):
        """تحميل تكوين Slack"""
        # محاولة جلب من متغيرات البيئة
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        
        # إذا لم توجد، استخدم قيم افتراضية للاختبار
        if not self.bot_token:
            self.bot_token = "xoxb-test-token-for-development"
            print("⚠️  استخدام token اختبار - أضف SLACK_BOT_TOKEN في .env")
        
        if not self.signing_secret:
            self.signing_secret = "test-signing-secret-for-development"
            print("⚠️  استخدام signing secret اختبار - أضف SLACK_SIGNING_SECRET في .env")
    
    def is_configured(self) -> bool:
        """التحقق من تكوين Slack"""
        return (
            self.bot_token and 
            self.signing_secret and 
            self.bot_token.startswith("xoxb-") and
            self.signing_secret != "test-signing-secret-for-development"
        )
    
    def get_config(self) -> dict:
        """جلب تكوين Slack"""
        return {
            "bot_token": self.bot_token,
            "signing_secret": self.signing_secret,
            "is_configured": self.is_configured()
        }

# إنشاء instance عام
slack_config = SlackConfig()

def get_slack_config() -> SlackConfig:
    """جلب تكوين Slack"""
    return slack_config

def setup_slack_webhook():
    """إعداد Slack Webhook (بديل أبسط)"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if webhook_url:
        print("✅ تم العثور على Slack Webhook URL")
        return webhook_url
    
    print("❌ SLACK_WEBHOOK_URL غير موجود")
    print("📝 أضف: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...")
    return None

def send_slack_message(message: str, webhook_url: str = None):
    """إرسال رسالة إلى Slack"""
    import requests
    
    if not webhook_url:
        webhook_url = setup_slack_webhook()
    
    if not webhook_url:
        print("❌ لا يمكن إرسال الرسالة - webhook غير مُعرّف")
        return False
    
    try:
        payload = {
            "text": message,
            "username": "Siyadah Ops AI",
            "icon_emoji": ":robot_face:"
        }
        
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 200:
            print("✅ تم إرسال الرسالة إلى Slack")
            return True
        else:
            print(f"❌ خطأ في إرسال الرسالة: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الرسالة: {e}")
        return False

# اختبار سريع
if __name__ == "__main__":
    print("🔗 اختبار تكوين Slack...")
    
    config = get_slack_config()
    print(f"Bot Token: {config.bot_token[:10]}...")
    print(f"Signing Secret: {config.signing_secret[:10]}...")
    print(f"مُعرّف: {config.is_configured()}")
    
    if config.is_configured():
        print("✅ Slack مُعرّف بشكل صحيح!")
    else:
        print("⚠️  Slack يحتاج إعداد - اتبع دليل SLACK_SETUP_GUIDE.txt")
