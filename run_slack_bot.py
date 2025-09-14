#!/usr/bin/env python3
"""
تشغيل البوت مع إصلاح مشاكل الرد
"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog

# تحميل متغيرات البيئة
load_dotenv()

# إعداد الـ logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# إنشاء التطبيق
app = FastAPI(
    title="Siyadah Ops AI - Slack Bot",
    description="نظام إدارة العمليات الذكي مع تكامل Slack",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استيراد Slack Bot
try:
    from app.integrations.slack_bot import handler, app as slack_app
    from app.routers.slack import router as slack_router
    
    # تسجيل مسارات Slack
    app.include_router(slack_router)
    
    logger.info("✅ Slack Bot integration loaded successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to load Slack Bot: {e}")
    sys.exit(1)

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "مرحباً بك في Siyadah Ops AI 🚀",
        "status": "running",
        "slack_bot": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """فحص صحة النظام"""
    try:
        # فحص متغيرات البيئة
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        slack_secret = os.getenv("SLACK_SIGNING_SECRET")
        
        return {
            "status": "healthy",
            "slack_token_configured": bool(slack_token and slack_token.startswith("xoxb-")),
            "slack_secret_configured": bool(slack_secret),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "mongodb_configured": bool(os.getenv("MONGO_URI"))
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/slack/events")
async def slack_webhook(request):
    """webhook لاستقبال أحداث Slack"""
    try:
        return await handler.handle(request)
    except Exception as e:
        logger.error(f"Slack webhook error: {e}")
        return {"error": "Internal server error"}

def check_environment():
    """فحص متغيرات البيئة المطلوبة"""
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_SIGNING_SECRET", 
        "OPENAI_API_KEY",
        "MONGO_URI"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    # فحص صحة الـ token
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token.startswith("xoxb-"):
        logger.error("❌ Invalid SLACK_BOT_TOKEN format")
        return False
    
    logger.info("✅ All environment variables are configured correctly")
    return True

if __name__ == "__main__":
    print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot...")
    print("=" * 60)
    
    # فحص متغيرات البيئة
    if not check_environment():
        print("❌ فشل في فحص متغيرات البيئة")
        print("📝 تأكد من إعداد ملف .env بشكل صحيح")
        sys.exit(1)
    
    # عرض معلومات النظام
    print(f"🌐 النظام متاح على: http://127.0.0.1:8000")
    print(f"📚 الوثائق متاحة على: http://127.0.0.1:8000/docs")
    print(f"🔍 فحص الصحة: http://127.0.0.1:8000/health")
    print(f"📡 Slack Webhook: http://127.0.0.1:8000/slack/events")
    print("\n" + "=" * 60)
    print("✅ البوت جاهز لاستقبال الرسائل من Slack!")
    print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
    
    # تشغيل الخادم
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        reload=False,
        log_level="info"
    )
