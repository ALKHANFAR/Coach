#!/usr/bin/env python3
"""
تشغيل مبسط للبوت مع إصلاح المشاكل
"""
import os
import sys
import socket
import uvicorn
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def find_free_port(start_port=8000, max_port=8020):
    """البحث عن منفذ متاح"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def main():
    print("🚀 بدء تشغيل Siyadah Ops AI...")
    print("=" * 50)
    
    # فحص متغيرات البيئة
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token or not slack_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح!")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    
    # البحث عن منفذ متاح
    port = find_free_port()
    if not port:
        print("❌ لا توجد منافذ متاحة!")
        return
    
    print(f"🌐 بدء تشغيل الخادم على المنفذ {port}...")
    
    # تشغيل النظام
    try:
        from run_bot_no_db import app
        
        print(f"🚀 النظام متاح على: http://127.0.0.1:{port}")
        print(f"📚 الوثائق: http://127.0.0.1:{port}/docs")
        print(f"🔍 فحص الصحة: http://127.0.0.1:{port}/health")
        print(f"📡 Slack Webhook: http://127.0.0.1:{port}/slack/events")
        print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
        print("=" * 50)
        
        uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        print("📝 تأكد من تثبيت جميع المتطلبات: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
