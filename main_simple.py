"""Siyadah Ops AI - نسخة مبسطة للاختبار"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

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

@app.get("/")
async def root():
    return {"message": "مرحباً بك في Siyadah Ops AI"}

@app.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    return {"status": "ok", "message": "Siyadah Ops AI is running"}

@app.get("/prompts/coach")
async def get_coach_prompts():
    """عرض prompts الكوتش"""
    return {
        "agent_type": "coach",
        "prompts": [
            {
                "name": "system",
                "template": "أنت كوتش ذكي متخصص في تحفيز موظفي شركة د10",
                "variables": ["{name}", "{department}", "{performance_level}"]
            }
        ]
    }

@app.post("/coach/ping")
async def coach_ping(data: dict):
    """اختبار الكوتش"""
    return {
        "message": f"مرحباً {data.get('user_email', 'عزيزي الموظف')}! أداؤك ممتاز في قسم {data.get('department', 'عام')} 🚀",
        "performance_level": "good",
        "should_send": True
    }

@app.post("/tasks")
async def create_task(data: dict):
    """إنشاء مهمة"""
    return {
        "id": "12345",
        "title": data.get("title", "مهمة جديدة"),
        "assignee_email": data.get("assignee_email", "test@d10.sa"),
        "status": "open",
        "message": "تم إنشاء المهمة بنجاح"
    }

@app.post("/kpis/upsert")
async def upsert_kpi(data: dict):
    """تحديث KPI"""
    target = data.get("target", 0)
    actual = data.get("actual", 0)
    drift = max(0.0, (target - actual) / target) if target > 0 else 0.0
    
    return {
        "user_email": data.get("user_email", "test@d10.sa"),
        "target": target,
        "actual": actual,
        "drift": drift,
        "performance_level": "excellent" if drift < 0.15 else "good" if drift < 0.25 else "needs_improvement"
    }

@app.post("/slack/mock")
async def slack_mock(data: dict):
    """اختبار Slack"""
    text = data.get("text", "")
    
    if text.startswith("مهمة:"):
        return {
            "success": True,
            "message": f"✅ تم إنشاء المهمة: {text.replace('مهمة:', '').strip()}",
            "type": "task_created"
        }
    elif text.startswith("هدف:"):
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {text.replace('هدف:', '').strip()}",
            "type": "goal_expanded",
            "project_data": {
                "project_title": "مشروع جديد",
                "tasks": [
                    {"title": "تحليل المتطلبات", "department": "general", "days": 2},
                    {"title": "التنفيذ", "department": "general", "days": 5}
                ]
            }
        }
    else:
        return {
            "success": True,
            "message": "مرحباً! يمكنني مساعدتك في إنشاء المهام وتفكيك الأهداف",
            "type": "help"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
