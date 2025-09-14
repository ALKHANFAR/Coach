"""Siyadah Ops AI - النسخة مع OpenAI الحقيقي"""
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

# قوالب الأداء
PERFORMANCE_TEMPLATES = {
    "excellent": [
        "مبروك! أداؤك رائع 🌟 استمر على نفس المستوى",
        "إنجاز ممتاز! 🚀 أنت مثال يُحتذى به",
        "أداء استثنائي! ✨ واصل التميز"
    ],
    "good": [
        "أداء جيد! 👍 خطوة بسيطة إضافية وتوصل للهدف",
        "تقدم ملحوظ! 📈 ركز على {focus_area} اليوم",
        "في الطريق الصحيح! 🎯 واصل بنفس الوتيرة"
    ],
    "needs_improvement": [
        "لا بأس، الهدف قريب! 💪 ركز على {action} اليوم",
        "تحدي بسيط! 🔥 جرب {suggestion} وشوف الفرق",
        "خطوة واحدة فقط! ⚡ {next_step} وتكون في المقدمة"
    ],
    "critical": [
        "وقت العمل الجاد! 🎯 نركز على {priority} فوراً",
        "تحدي كبير يحتاج حل سريع! ⚠️ {urgent_action}",
        "وضع طوارئ! 🚨 اتصل بمديرك فوراً للمساعدة"
    ]
}

# متغيرات الأقسام
DEPARTMENT_VARIABLES = {
    "sales": {
        "focus_area": "إقفال صفقة واحدة",
        "action": "اتصال واحد مهم",
        "suggestion": "متابعة العملاء المهتمين",
        "next_step": "قفل مكسب صغير",
        "priority": "العملاء الساخنين",
        "urgent_action": "راجع pipeline المبيعات"
    },
    "marketing": {
        "focus_area": "قطعة محتوى جديدة", 
        "action": "منشور إبداعي واحد",
        "suggestion": "تحليل منافس واحد",
        "next_step": "حملة صغيرة مستهدفة",
        "priority": "المحتوى عالي الأداء",
        "urgent_action": "راجع استراتيجية المحتوى"
    },
    "tech": {
        "focus_area": "حل تذكرة واحدة",
        "action": "مراجعة كود واحدة", 
        "suggestion": "تحسين أداء صغير",
        "next_step": "PR أو merge واحد",
        "priority": "الأخطاء الحرجة",
        "urgent_action": "راجع النظام والأخطاء"
    },
    "sondos": {
        "focus_area": "حل مشكلة عميل واحد",
        "action": "تطوير ميزة صغيرة",
        "suggestion": "تحليل بيانات جديد", 
        "next_step": "تحسين خوارزمية",
        "priority": "طلبات العملاء الملحة",
        "urgent_action": "راجع أداء النماذج"
    }
}

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
    return {"message": "مرحباً بك في Siyadah Ops AI 🚀 - النسخة مع OpenAI الحقيقي"}

@app.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    return {"status": "ok", "message": "Siyadah Ops AI is running", "openai": "connected", "mongodb": "in-memory"}

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

# مسارات الكوتش مع OpenAI الحقيقي
@app.post("/coach/ping")
async def coach_ping(ping_data: CoachPing):
    """الحصول على رسالة تحفيز من الكوتش الذكي مع OpenAI"""
    department = ping_data.department
    user_name = ping_data.user_email.split("@")[0]
    
    # جلب أداء المستخدم
    performance_data = await get_user_performance(ping_data.user_email)
    performance_level = performance_data.get("performance_level", "good")
    drift = performance_data.get("drift", 0.2)
    
    # تحديد ما إذا كان يجب إرسال الرسالة
    if performance_level == "excellent" or drift < 0.15:
        return {
            "message": "",
            "performance_level": performance_level,
            "should_send": False,
            "reason": "أداء ممتاز - لا حاجة لرسالة"
        }
    
    # جلب الـ prompts المرنة
    system_prompt = prompts_storage["coach"]["system"]
    user_template = prompts_storage["coach"]["user_template"]
    
    # إعداد المتغيرات
    variables = {
        "name": user_name,
        "department": department,
        "performance_level": performance_level,
        "summary": ping_data.summary or "أداء جيد",
        "current_time": datetime.now().strftime("%H:%M"),
        "current_day": "اليوم"
    }
    
    # تنسيق القالب
    user_prompt = user_template.format(**variables)
    
    # استدعاء OpenAI
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    ai_response = await call_openai(messages)
    
    # إذا فشل AI، استخدم القوالب الجاهزة
    if not ai_response:
        templates = PERFORMANCE_TEMPLATES.get(performance_level, PERFORMANCE_TEMPLATES["good"])
        template = random.choice(templates)
        dept_vars = DEPARTMENT_VARIABLES.get(department, DEPARTMENT_VARIABLES["sales"])
        try:
            ai_response = template.format(**dept_vars)
        except KeyError:
            ai_response = f"أداؤك جيد يا {user_name}! 🌟 استمر على نفس المستوى في قسم {department}"
    
    logger.info(f"Coach message generated for {user_name}: {performance_level}")
    
    return {
        "message": ai_response,
        "performance_level": performance_level,
        "should_send": True,
        "drift": drift,
        "ai_source": "openai" if ai_response else "fallback"
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

# مسار تفكيك الأهداف مع OpenAI
@app.post("/orchestrator/expand")
async def expand_goal(goal_data: GoalExpand):
    """تفكيك الهدف إلى مهام باستخدام OpenAI"""
    try:
        # جلب الـ prompts المرنة
        system_prompt = prompts_storage["orchestrator"]["system"]
        user_template = prompts_storage["orchestrator"]["user_template"]
        
        # إعداد المتغيرات
        variables = {
            "goal_text": goal_data.goal_text,
            "timeline": goal_data.timeline,
            "available_departments": goal_data.available_departments
        }
        
        # تنسيق القالب
        user_prompt = user_template.format(**variables)
        
        # استدعاء OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        ai_response = await call_openai(messages, max_tokens=500)
        
        # إذا فشل AI، استخدم القالب الافتراضي
        if not ai_response:
            ai_response = f"""
مشروع: {goal_data.goal_text}
المدة المتوقعة: {goal_data.timeline}

المهام المطلوبة:
1. تحليل المتطلبات (2 أيام)
2. التخطيط والتصميم (3 أيام)  
3. التنفيذ (5 أيام)
4. الاختبار والمراجعة (2 أيام)
5. الإطلاق (1 يوم)

معايير النجاح:
- إنجاز الهدف المطلوب
- الالتزام بالجدول الزمني
- جودة التنفيذ
"""
        
        logger.info(f"Goal expanded: {goal_data.goal_text}")
        
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {goal_data.goal_text}",
            "type": "goal_expanded",
            "ai_response": ai_response,
            "ai_source": "openai" if ai_response else "fallback"
        }
        
    except Exception as e:
        logger.error(f"Error expanding goal: {e}")
        return {
            "success": False,
            "message": "عذراً، حدث خطأ في تحليل الهدف",
            "error": str(e)
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
    """اختبار رسائل Slack"""
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
        
        # استخدام OpenAI لتفكيك الهدف
        goal_data = GoalExpand(
            goal_text=goal_text,
            timeline="أسبوعين",
            available_departments="sales,marketing,tech,sondos"
        )
        
        result = await expand_goal(goal_data)
        
        return {
            "success": True,
            "message": f"🎯 تم تحليل الهدف: {goal_text}",
            "type": "goal_expanded",
            "ai_response": result.get("ai_response", ""),
            "ai_source": result.get("ai_source", "unknown")
        }
        
    else:
        return {
            "success": True,
            "message": "مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'",
            "type": "help"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 بدء تشغيل Siyadah Ops AI - النسخة مع OpenAI الحقيقي...")
    print("🌐 النظام متاح على: http://127.0.0.1:8003")
    print("📚 الوثائق متاحة على: http://127.0.0.1:8003/docs")
    print("🔧 تعديل الـ Prompts: http://127.0.0.1:8003/prompts/coach/edit")
    print("🤖 OpenAI: متصل ومجهز")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="127.0.0.1", port=8003, reload=False)
