"""Siyadah Ops AI - النظام الرئيسي"""
import os
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, tasks, prompts, kpis, coach, digests, slack
from app.db import init_db

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
    title="Siyadah Ops AI",
    description="نظام إدارة العمليات الذكي لشركة د10",
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

# تسجيل الـ routers
app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(prompts.router)
app.include_router(kpis.router)
app.include_router(coach.router)
app.include_router(digests.router)
app.include_router(slack.router)

@app.on_event("startup")
async def startup_event():
    """تهيئة النظام عند البدء"""
    logger.info("🚀 Starting Siyadah Ops AI...")
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # لا نوقف التطبيق إذا فشل MongoDB
    logger.info("✅ System initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """تنظيف النظام عند الإغلاق"""
    logger.info("🛑 Shutting down Siyadah Ops AI...")

if __name__ == "__main__":
    import uvicorn
    # استخدام PORT من متغير البيئة أو المنفذ الافتراضي
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🌐 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
