#!/usr/bin/env python3
"""
إعداد Slack Bot - الطريقة الأسهل والأضمن
"""

import os
from dotenv import load_dotenv

def setup_slack():
    """إعداد Slack Bot"""
    print("🔗 إعداد Slack Bot...")
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # التحقق من وجود الـ tokens
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN غير موجود في ملف .env")
        print("📝 أضف: SLACK_BOT_TOKEN=xoxb-your-token-here")
        return False
    
    if not signing_secret:
        print("❌ SLACK_SIGNING_SECRET غير موجود في ملف .env")
        print("📝 أضف: SLACK_SIGNING_SECRET=your-secret-here")
        return False
    
    # التحقق من صحة الـ token
    if not bot_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح (يجب أن يبدأ بـ xoxb-)")
        return False
    
    print("✅ إعداد Slack Bot مكتمل!")
    print(f"🤖 Bot Token: {bot_token[:10]}...")
    print(f"🔐 Signing Secret: {signing_secret[:10]}...")
    
    return True

def test_slack_connection():
    """اختبار الاتصال مع Slack"""
    try:
        from slack_bolt import App
        from app.config import settings
        
        app = App(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret
        )
        
        print("✅ الاتصال مع Slack ناجح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال مع Slack: {e}")
        return False

def create_slack_app_guide():
    """إنشاء دليل إنشاء تطبيق Slack"""
    guide = """
# 🚀 دليل إنشاء تطبيق Slack (5 دقائق)

## الخطوة 1: إنشاء التطبيق
1. اذهب إلى: https://api.slack.com/apps
2. اضغط "Create New App"
3. اختر "From scratch"
4. أدخل اسم: "Siyadah Ops AI"
5. اختر Workspace الخاص بك

## الخطوة 2: إعداد Bot Token
1. اذهب إلى "OAuth & Permissions"
2. في "Scopes" أضف:
   - app_mentions:read
   - chat:write
   - users:read
3. اضغط "Install to Workspace"
4. انسخ "Bot User OAuth Token" (xoxb-...)

## الخطوة 3: إعداد Signing Secret
1. اذهب إلى "Basic Information"
2. انسخ "Signing Secret"

## الخطوة 4: تحديث ملف .env
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-secret-here

## الخطوة 5: إضافة البوت للقناة
1. في Slack: /invite @Siyadah Ops AI
2. اكتب: @Siyadah Ops AI مهمة: اختبار

## ✅ جاهز للاستخدام!
"""
    
    with open("SLACK_SETUP_GUIDE.txt", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("📄 تم إنشاء دليل الإعداد: SLACK_SETUP_GUIDE.txt")

if __name__ == "__main__":
    print("🚀 إعداد Slack Bot...")
    
    # إنشاء دليل الإعداد
    create_slack_app_guide()
    
    # إعداد Slack
    if setup_slack():
        # اختبار الاتصال
        test_slack_connection()
    
    print("\n📋 الخطوات التالية:")
    print("1. اتبع دليل SLACK_SETUP_GUIDE.txt")
    print("2. أضف الـ tokens في ملف .env")
    print("3. شغل النظام: python main_perfect.py")
    print("4. اختبر: @Siyadah Ops AI مهمة: اختبار")
