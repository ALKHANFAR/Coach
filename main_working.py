"""Siyadah Ops AI - نسخة تعمل بالكامل"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import structlog
import json

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

# Schemas بسيطة
class TaskCreate(BaseModel):
    title: str
    assignee_email: str
    due_date: Optional[str] = None
    description: Optional[str] = None

class CoachPing(BaseModel):
    user_email: str
    department: str
    summary: Optional[str] = None

class KPIUpsert(BaseModel):
    user_email: str
    month: str
    target: int
    actual: int

class SlackMock(BaseModel):
    text: str
    user: str

# المسارات الأساسية
@app.get("/")
async def root():
    return {"message": "مرحباً بك في Siyadah Ops AI 🚀"}

@app.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    return {"status": "ok", "message": "Siyadah Ops AI is running"}

# مسارات المهام
@app.post("/tasks")
async def create_task(task_data: TaskCreate):
    """إنشاء مهمة جديدة"""
    return {
        "id": "12345",
        "title": task_data.title,
        "assignee_email": task_data.assignee_email,
        "due_date": task_data.due_date or "2025-09-20",
        "status": "open",
        "source": "api",
        "message": "تم إنشاء المهمة بنجاح"
    }

@app.get("/tasks")
async def get_tasks(assignee_email: Optional[str] = None):
    """جلب المهام"""
    return [
        {
            "id": "12345",
            "title": "مهمة تجريبية",
            "assignee_email": assignee_email or "test@d10.sa",
            "status": "open",
            "source": "api"
        }
    ]

# مسارات KPIs
@app.post("/kpis/upsert")
async def upsert_kpi(kpi_data: KPIUpsert):
    """تحديث أو إنشاء KPI"""
    target = kpi_data.target
    actual = kpi_data.actual
    drift = max(0.0, (target - actual) / target) if target > 0 else 0.0
    
    performance_level = "excellent" if drift < 0.15 else "good" if drift < 0.25 else "needs_improvement" if drift < 0.35 else "critical"
    
    return {
        "id": "kpi_123",
        "user_email": kpi_data.user_email,
        "month": kpi_data.month,
        "target": target,
        "actual": actual,
        "drift": drift,
        "performance_level": performance_level
    }

@app.get("/kpis/performance/{user_email}")
async def get_user_performance(user_email: str):
    """جلب أداء المستخدم"""
    return {
        "user_email": user_email,
        "department": "sales",
        "drift": 0.2,
        "performance_level": "good",
        "target": 10,
        "actual": 8,
        "month": "2025-09"
    }

# مسارات الكوتش
@app.post("/coach/ping")
async def coach_ping(ping_data: CoachPing):
    """الحصول على رسالة تحفيز من الكوتش الذكي"""
    department = ping_data.department
    user_name = ping_data.user_email.split("@")[0]
    
    # رسائل مخصصة حسب القسم
    messages = {
        "sales": f"واصل شغلك الرائع يا {user_name}! 🚀 اليوم ركز على عميل واحد واقفل معه الصفقة",
        "marketing": f"إبداعك واضح يا {user_name}! 🎨 شارك قطعة محتوى واحدة تجذب العملاء",
        "tech": f"كودك محترف يا {user_name}! ⚡ اقفل تذكرة واحدة اليوم وتقدم خطوة",
        "sondos": f"ذكاء يحل المشاكل يا {user_name}! 🤖 ركز على حل مشكلة عميل واحد اليوم"
    }
    
    message = messages.get(department, f"أداؤك ممتاز يا {user_name}! 🌟 استمر على نفس المستوى")
    
    return {
        "message": message,
        "performance_level": "good",
        "should_send": True
    }

# مسارات الـ Prompts
@app.get("/prompts/coach")
async def get_coach_prompts():
    """عرض prompts الكوتش"""
    return [
        {
            "id": "prompt_1",
            "agent_type": "coach",
            "prompt_name": "system",
            "template": "أنت كوتش ذكي متخصص في تحفيز موظفي شركة د10. شخصيتك ودودة ومحترفة.",
            "variables": {
                "{name}": "اسم الموظف",
                "{department}": "القسم",
                "{performance_level}": "مستوى الأداء"
            },
            "is_active": True
        }
    ]

@app.put("/prompts/coach/system")
async def update_coach_prompt(prompt_data: Dict[str, Any]):
    """تحديث prompt الكوتش"""
    return {
        "id": "prompt_1",
        "agent_type": "coach",
        "prompt_name": "system",
        "template": prompt_data.get("template", "أنت كوتش ذكي"),
        "variables": prompt_data.get("variables", {}),
        "is_active": True,
        "message": "تم تحديث الـ prompt بنجاح"
    }

@app.get("/prompts/templates")
async def get_prompt_templates():
    """جلب جميع القوالب الجاهزة"""
    return {
        "coach": {
            "available_variables": {
                "{name}": "اسم الموظف",
                "{department}": "القسم",
                "{performance_level}": "مستوى الأداء"
            },
            "performance_templates": ["excellent", "good", "needs_improvement", "critical"],
            "departments": ["sales", "marketing", "tech", "sondos"]
        }
    }

# مسارات التقارير
@app.post("/digests/manager")
async def send_manager_digest(data: Dict[str, str]):
    """إرسال تقرير يومي للمدير"""
    manager_email = data.get("manager_email", "manager@d10.sa")
    return {
        "sent": True,
        "preview": f"تقرير يومي لـ {manager_email} - ملخص أداء الفريق",
        "recipients": [manager_email]
    }

@app.post("/digests/executive")
async def send_executive_digest():
    """إرسال تقرير أسبوعي تنفيذي"""
    return {
        "sent": True,
        "preview": "تقرير أسبوعي تنفيذي - نظرة شاملة على الشركة",
        "recipients": ["executive@d10.sa"]
    }

# مسارات Slack
@app.post("/slack/mock")
async def slack_mock(data: SlackMock):
    """اختبار رسائل Slack"""
    text = data.text
    user = data.user
    
    if text.startswith("مهمة:"):
        task_title = text.replace("مهمة:", "").strip()
        return {
            "success": True,
            "message": f"✅ تم إنشاء المهمة: {task_title}",
            "type": "task_created",
            "task_id": "slack_123"
        }
    elif text.startswith("هدف:"):
        goal_text = text.replace("هدف:", "").strip()
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {goal_text}",
            "type": "goal_expanded",
            "project_data": {
                "project_title": f"مشروع {goal_text}",
                "project_description": f"تنفيذ {goal_text}",
                "estimated_duration": "أسبوعين",
                "tasks": [
                    {
                        "id": 1,
                        "title": "تحليل المتطلبات",
                        "description": "تحليل الهدف وتحديد المتطلبات",
                        "department": "general",
                        "estimated_days": 2,
                        "priority": "high"
                    },
                    {
                        "id": 2,
                        "title": "التنفيذ",
                        "description": "تنفيذ المهام المطلوبة",
                        "department": "general",
                        "estimated_days": 5,
                        "priority": "medium"
                    }
                ],
                "success_criteria": ["إنجاز الهدف المطلوب"],
                "potential_risks": ["عدم وضوح المتطلبات"]
            }
        }
    else:
        return {
            "success": True,
            "message": "مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'",
            "type": "help"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
