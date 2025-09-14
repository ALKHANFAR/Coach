#!/usr/bin/env python3
"""
تشغيل مباشر للبوت - حل جذري ومضمون
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# فحص متغيرات البيئة
slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token or not slack_token.startswith("xoxb-"):
    print("❌ SLACK_BOT_TOKEN غير صحيح!")
    sys.exit(1)

print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot...")
print("🌐 النظام متاح على: http://127.0.0.1:8002")
print("📡 Slack Webhook: http://127.0.0.1:8002/slack/events")
print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
print("=" * 50)

# تشغيل النظام
try:
    from run_bot_no_db import app
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
except Exception as e:
    print(f"❌ خطأ: {e}")
    sys.exit(1)
