"""Siyadah Ops AI - النسخة مع Agent Manager"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
import json
import random
import asyncio
import openai
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv("env")

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

# إعداد OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# إنشاء التطبيق
app = FastAPI(
    title="Siyadah Ops AI with Agent Manager",
    description="نظام إدارة العمليات الذكي لشركة د10 مع مدير الـ Agents",
    version="2.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تخزين مؤقت في الذاكرة (بدلاً من MongoDB)
tasks_storage = []
kpis_storage = []
prompts_storage = {
    "coach": {
        "system": "أنت كوتش ذكي متخصص في تحفيز موظفي شركة د10 للتسويق الرقمي. شخصيتك ودودة ومحترفة، تتكلم بلهجة سعودية خفيفة. خبرتك في الإنتاجية وإدارة الأهداف. اكتب ≤3 جمل فقط واستخدم إيموجي واحد أو اثنين. ركز على خطوة واحدة واضحة يمكن تنفيذها اليوم. تجنب الانتقاد المباشر والتركيز على الحلول.",
        "user_template": "معلومات الموظف: الاسم: {name}, القسم: {department}, مستوى الأداء: {performance_level}, الملخص: {summary}, الوقت الحالي: {current_time}, اليوم: {current_day}"
    },
    "orchestrator": {
        "system": "أنت منسق مشاريع ذكي متخصص في تفكيك الأهداف الكبيرة إلى مهام قابلة للتنفيذ. لا تتجاوز 6 مهام في التفكيك الأول. كل مهمة يجب أن تكون قابلة للإنجاز خلال 1-7 أيام. استخدم أسماء واضحة ومحددة للمهام. راعي التسلسل المنطقي (مهمة أ قبل مهمة ب).",
        "user_template": "الهدف/المشروع المطلوب: {goal_text}. معلومات إضافية: الجدول الزمني: {timeline}, الأقسام المتاحة: {available_departments}"
    }
}

# Schemas
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

class PromptUpdate(BaseModel):
    template: str
    variables: Optional[Dict[str, Any]] = {}

class GoalExpand(BaseModel):
    goal_text: str
    timeline: Optional[str] = "أسبوعين"
    available_departments: Optional[str] = "sales,marketing,tech,sondos"

class CoordinationRequest(BaseModel):
    coordination_type: str
    data: Dict[str, Any]

# دالة استدعاء OpenAI
async def call_openai(messages: list, max_tokens: int = 200) -> Optional[str]:
    """استدعاء OpenAI مع معالجة الأخطاء"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.acreate(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None

# المسارات الأساسية
@app.get("/")
async def root():
    return {"message": "مرحباً بك في Siyadah Ops AI 🚀 - النسخة مع Agent Manager"}

@app.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    return {"status": "ok", "message": "Siyadah Ops AI with Agent Manager is running", "openai": "connected", "mongodb": "in-memory"}

# مسارات المهام
@app.post("/tasks")
async def create_task(task_data: TaskCreate):
    """إنشاء مهمة جديدة"""
    task = {
        "id": f"task_{len(tasks_storage) + 1}",
        "title": task_data.title,
        "assignee_email": task_data.assignee_email,
        "due_date": task_data.due_date or "2025-09-20",
        "status": "open",
        "source": "api",
        "created_at": datetime.now().isoformat(),
        "description": task_data.description
    }
    tasks_storage.append(task)
    
    logger.info(f"Task created: {task['id']}")
    return task

@app.get("/tasks")
async def get_tasks(assignee_email: Optional[str] = None):
    """جلب المهام"""
    if assignee_email:
        filtered_tasks = [t for t in tasks_storage if t["assignee_email"] == assignee_email]
        return filtered_tasks
    return tasks_storage

# مسارات KPIs
@app.post("/kpis/upsert")
async def upsert_kpi(kpi_data: KPIUpsert):
    """تحديث أو إنشاء KPI"""
    target = kpi_data.target
    actual = kpi_data.actual
    drift = max(0.0, (target - actual) / target) if target > 0 else 0.0
    
    performance_level = "excellent" if drift < 0.15 else "good" if drift < 0.25 else "needs_improvement" if drift < 0.35 else "critical"
    
    kpi = {
        "id": f"kpi_{len(kpis_storage) + 1}",
        "user_email": kpi_data.user_email,
        "month": kpi_data.month,
        "target": target,
        "actual": actual,
        "drift": drift,
        "performance_level": performance_level,
        "updated_at": datetime.now().isoformat()
    }
    
    # تحديث أو إضافة
    existing = next((k for k in kpis_storage if k["user_email"] == kpi_data.user_email and k["month"] == kpi_data.month), None)
    if existing:
        existing.update(kpi)
        kpi = existing
    else:
        kpis_storage.append(kpi)
    
    logger.info(f"KPI upserted: {kpi['id']}")
    return kpi

@app.get("/kpis/performance/{user_email}")
async def get_user_performance(user_email: str):
    """جلب أداء المستخدم"""
    user_kpis = [k for k in kpis_storage if k["user_email"] == user_email]
    if not user_kpis:
        return {
            "user_email": user_email,
            "department": "general",
            "drift": 0.0,
            "performance_level": "no_data"
        }
    
    latest_kpi = max(user_kpis, key=lambda x: x["updated_at"])
    return latest_kpi

# مسارات الكوتش مع Agent Manager
@app.post("/coach/ping")
async def coach_ping(ping_data: CoachPing):
    """الحصول على رسالة تحفيز من الكوتش الذكي مع Agent Manager"""
    try:
        from app.ai.agent_manager import agent_manager
    except ImportError:
        # Fallback إذا فشل استيراد Agent Manager
        return await coach_ping_fallback(ping_data)
    
    # إعداد بيانات المستخدم
    user_data = {
        "name": ping_data.user_email.split("@")[0],
        "department": ping_data.department,
        "summary": ping_data.summary or "أداء جيد"
    }
    
    # جلب أداء المستخدم
    performance_data = await get_user_performance(ping_data.user_email)
    user_data.update(performance_data)
    
    # استخدام Agent Manager
    result = await agent_manager.execute_agent_task("coach", "generate_message", user_data=user_data)
    
    if result["success"]:
        return {
            "message": result["result"].get("message", ""),
            "performance_level": result["result"].get("performance_level", "good"),
            "should_send": result["result"].get("should_send", True),
            "drift": user_data.get("drift", 0.0),
            "ai_source": "agent_manager",
            "execution_time": result["execution_time"]
        }
    else:
        return {
            "message": "واصل شغلك الرائع! 🚀 اليوم ركز على هدف واحد واضح",
            "performance_level": "good",
            "should_send": True,
            "drift": user_data.get("drift", 0.0),
            "ai_source": "fallback",
            "error": result["error"]
        }

# مسارات الـ Prompts
@app.get("/prompts/{agent_type}")
async def get_agent_prompts(agent_type: str):
    """عرض prompts للـ agent"""
    if agent_type not in prompts_storage:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    prompts = []
    for prompt_name, template in prompts_storage[agent_type].items():
        prompts.append({
            "id": f"{agent_type}_{prompt_name}",
            "agent_type": agent_type,
            "prompt_name": prompt_name,
            "template": template,
            "variables": {
                "{name}": "اسم الموظف",
                "{department}": "القسم",
                "{performance_level}": "مستوى الأداء",
                "{summary}": "ملخص الأداء"
            },
            "is_active": True,
            "updated_at": datetime.now().isoformat()
        })
    
    return prompts

@app.put("/prompts/{agent_type}/{prompt_name}")
async def update_prompt(agent_type: str, prompt_name: str, prompt_data: PromptUpdate):
    """تحديث prompt"""
    if agent_type not in prompts_storage:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    if prompt_name not in prompts_storage[agent_type]:
        raise HTTPException(status_code=404, detail="Prompt name not found")
    
    # تحديث الـ prompt
    prompts_storage[agent_type][prompt_name] = prompt_data.template
    
    logger.info(f"Prompt updated: {agent_type}/{prompt_name}")
    
    return {
        "id": f"{agent_type}_{prompt_name}",
        "agent_type": agent_type,
        "prompt_name": prompt_name,
        "template": prompt_data.template,
        "variables": prompt_data.variables or {},
        "is_active": True,
        "updated_at": datetime.now().isoformat(),
        "message": "تم تحديث الـ prompt بنجاح"
    }

# مسار تفكيك الأهداف مع Agent Manager
@app.post("/orchestrator/expand")
async def expand_goal(goal_data: GoalExpand):
    """تفكيك الهدف إلى مهام باستخدام Agent Manager"""
    from app.ai.agent_manager import agent_manager
    
    # استخدام Agent Manager
    result = await agent_manager.execute_agent_task(
        "orchestrator", 
        "expand_goal", 
        goal_text=goal_data.goal_text,
        timeline=goal_data.timeline,
        available_departments=goal_data.available_departments
    )
    
    if result["success"]:
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {goal_data.goal_text}",
            "type": "goal_expanded",
            "ai_response": str(result["result"]),
            "ai_source": "agent_manager",
            "execution_time": result["execution_time"]
        }
    else:
        return {
            "success": False,
            "message": "عذراً، حدث خطأ في تحليل الهدف",
            "error": result["error"],
            "ai_source": "fallback"
        }

# مسارات Agent Manager
@app.get("/agents/status")
async def get_agents_status():
    """جلب حالة جميع الـ Agents"""
    from app.ai.agent_manager import agent_manager
    status = await agent_manager.get_agent_status()
    return {
        "success": True,
        "agents_status": status,
        "total_agents": len(status)
    }

@app.get("/agents/health")
async def get_agents_health():
    """فحص صحة جميع الـ Agents"""
    from app.ai.agent_manager import agent_manager
    health = await agent_manager.get_agent_health()
    return {
        "success": True,
        "health_status": health
    }

@app.get("/agents/stats")
async def get_agents_stats():
    """جلب إحصائيات مفصلة لجميع الـ Agents"""
    from app.ai.agent_manager import agent_manager
    stats = {}
    for agent_type in agent_manager.agent_stats:
        agent_stats = agent_manager.agent_stats[agent_type]
        
        # حساب معدل النجاح
        success_rate = 0
        if agent_stats["total_requests"] > 0:
            success_rate = (agent_stats["successful_requests"] / agent_stats["total_requests"]) * 100
        
        stats[agent_type] = {
            "total_requests": agent_stats["total_requests"],
            "successful_requests": agent_stats["successful_requests"],
            "failed_requests": agent_stats["failed_requests"],
            "success_rate": round(success_rate, 2),
            "average_response_time": round(agent_stats["average_response_time"], 3),
            "last_activity": agent_stats["last_activity"].isoformat() if agent_stats["last_activity"] else None
        }
    
    return {
        "success": True,
        "agents_stats": stats,
        "summary": {
            "total_agents": len(stats),
            "total_requests": sum(s["total_requests"] for s in stats.values()),
            "overall_success_rate": round(
                sum(s["success_rate"] for s in stats.values()) / len(stats) if stats else 0, 2
            )
        }
    }

@app.post("/agents/coordinate")
async def coordinate_agents(coordination_request: CoordinationRequest):
    """تنسيق بين الـ Agents لمهمة معقدة"""
    from app.ai.agent_manager import agent_manager
    
    result = await agent_manager.coordinate_agents(
        coordination_request.coordination_type, 
        coordination_request.data
    )
    
    return {
        "success": result["success"],
        "coordination_result": result,
        "coordination_type": coordination_request.coordination_type
    }

# مسارات التقارير
@app.post("/digests/manager")
async def send_manager_digest(data: Dict[str, str]):
    """إرسال تقرير يومي للمدير"""
    manager_email = data.get("manager_email", "manager@d10.sa")
    
    # بناء التقرير
    team_tasks = [t for t in tasks_storage if t["status"] == "open"]
    team_kpis = kpis_storage
    
    content = f"""
    <h2>تقرير يومي - {datetime.now().strftime('%Y-%m-%d')}</h2>
    <p>مرحباً {manager_email.split('@')[0]}،</p>
    <p>إليك ملخص أداء فريقك اليوم:</p>
    
    <h3>📊 ملخص الأداء</h3>
    <ul>
        <li>إجمالي المهام المفتوحة: {len(team_tasks)}</li>
        <li>إجمالي KPIs المسجلة: {len(team_kpis)}</li>
    </ul>
    
    <h3>📋 المهام المعلقة</h3>
    <p>راجع المهام المعلقة لفريقك في النظام.</p>
    
    <h3>💡 توصيات</h3>
    <p>ركز على الأعضاء الذين يحتاجون دعم إضافي.</p>
    """
    
    logger.info(f"Manager digest sent to {manager_email}")
    
    return {
        "sent": True,
        "preview": f"تقرير يومي لـ {manager_email} - ملخص أداء الفريق",
        "recipients": [manager_email],
        "content": content
    }

# مسارات Slack
@app.post("/slack/mock")
async def slack_mock(data: SlackMock):
    """اختبار رسائل Slack مع Agent Manager"""
    text = data.text
    user = data.user
    
    if text.startswith("مهمة:"):
        task_title = text.replace("مهمة:", "").strip()
        
        # إنشاء المهمة
        task = {
            "id": f"slack_task_{len(tasks_storage) + 1}",
            "title": task_title,
            "assignee_email": f"{user}@slack.local",
            "due_date": "2025-09-20",
            "status": "open",
            "source": "slack",
            "created_at": datetime.now().isoformat()
        }
        tasks_storage.append(task)
        
        logger.info(f"Slack task created: {task['id']}")
        
        return {
            "success": True,
            "message": f"✅ تم إنشاء المهمة: {task_title}",
            "type": "task_created",
            "task_id": task["id"]
        }
        
    elif text.startswith("هدف:"):
        goal_text = text.replace("هدف:", "").strip()
        
        # استخدام Agent Manager لتفكيك الهدف
        from app.ai.agent_manager import agent_manager
        
        result = await agent_manager.execute_agent_task(
            "orchestrator", 
            "expand_goal", 
            goal_text=goal_text
        )
        
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {goal_text}",
            "type": "goal_expanded",
            "ai_response": str(result.get("result", "")),
            "ai_source": "agent_manager" if result["success"] else "fallback"
        }
        
    else:
        return {
            "success": True,
            "message": "مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'",
            "type": "help"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 بدء تشغيل Siyadah Ops AI - النسخة مع Agent Manager...")
    print("🌐 النظام متاح على: http://127.0.0.1:8004")
    print("📚 الوثائق متاحة على: http://127.0.0.1:8004/docs")
    print("🔧 تعديل الـ Prompts: http://127.0.0.1:8004/prompts/coach/edit")
    print("🤖 Agent Manager: http://127.0.0.1:8004/agents/status")
    print("📊 Agent Stats: http://127.0.0.1:8004/agents/stats")
    print("🏥 Agent Health: http://127.0.0.1:8004/agents/health")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="127.0.0.1", port=8004, reload=False)
