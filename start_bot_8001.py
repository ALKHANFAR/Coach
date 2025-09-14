#!/usr/bin/env python3
"""
تشغيل البوت على المنفذ 8001
"""
import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def main():
    print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot على المنفذ 8001...")
    print("=" * 60)
    
    # فحص متغيرات البيئة الأساسية
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_secret = os.getenv("SLACK_SIGNING_SECRET")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not slack_token or not slack_secret or not openai_key:
        print("❌ متغيرات البيئة غير مكتملة!")
        print("📝 تأكد من إعداد ملف .env")
        return
    
    if not slack_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح!")
        print("📝 يجب أن يبدأ بـ xoxb-")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    print("🌐 بدء تشغيل الخادم على المنفذ 8001...")
    
    # تشغيل النظام
    try:
        import uvicorn
        from app import app
        
        print("🚀 النظام متاح على: http://127.0.0.1:8001")
        print("📚 الوثائق: http://127.0.0.1:8001/docs")
        print("🔍 فحص الصحة: http://127.0.0.1:8001/health")
        print("📡 Slack Webhook: http://127.0.0.1:8001/slack/events")
        print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
        print("=" * 60)
        
        uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        print("📝 تأكد من تثبيت جميع المتطلبات: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
