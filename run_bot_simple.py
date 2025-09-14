#!/usr/bin/env python3
"""
تشغيل مبسط جداً للبوت
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot...")
    print("🌐 النظام متاح على: http://127.0.0.1:8001")
    print("📡 Slack Webhook: http://127.0.0.1:8001/slack/events")
    print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
