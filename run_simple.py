#!/usr/bin/env python3
"""
تشغيل مبسط جداً للبوت - حل جذري ومضمون
"""
import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def main():
    print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot...")
    print("=" * 50)
    
    # فحص متغيرات البيئة الأساسية
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN غير موجود!")
        print("📝 تأكد من إعداد ملف .env")
        return
    
    if not slack_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح!")
        print("📝 يجب أن يبدأ بـ xoxb-")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    print("🌐 بدء تشغيل الخادم...")
    
    # تشغيل النظام
    try:
        import uvicorn
        from run_bot_no_db import app
        
        print("🚀 النظام متاح على: http://127.0.0.1:8002")
        print("📚 الوثائق: http://127.0.0.1:8002/docs")
        print("🔍 فحص الصحة: http://127.0.0.1:8002/health")
        print("📡 Slack Webhook: http://127.0.0.1:8002/slack/events")
        print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
        print("=" * 50)
        
        uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        print("📝 تأكد من تثبيت جميع المتطلبات: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
