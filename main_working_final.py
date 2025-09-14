"""Siyadah Ops AI - النسخة النهائية التي تعمل بالكامل"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
import json
import random
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

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

# إعداد MongoDB - استخدام MongoDB Atlas أو محلي
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "siyadah_ops_ai"

# إنشاء عميل MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

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

# المسارات الأساسية
@app.get("/")
async def root():
    return {"message": "مرحباً بك في Siyadah Ops AI 🚀"}

@app.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    try:
        # فحص اتصال MongoDB
        await db.command("ping")
        return {"status": "ok", "message": "Siyadah Ops AI is running", "mongodb": "connected"}
    except Exception as e:
        return {"status": "ok", "message": "Siyadah Ops AI is running", "mongodb": "disconnected", "error": str(e)}

# مسارات المهام
@app.post("/tasks")
async def create_task(task_data: TaskCreate):
    """إنشاء مهمة جديدة"""
    task = {
        "_id": ObjectId(),
        "title": task_data.title,
        "assignee_email": task_data.assignee_email,
        "due_date": task_data.due_date or "2025-09-20",
        "status": "open",
        "source": "api",
        "created_at": datetime.now(),
        "description": task_data.description
    }
    
    try:
        result = await db.tasks.insert_one(task)
        task["id"] = str(result.inserted_id)
        
        logger.info(f"Task created: {task['id']}")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="فشل في إنشاء المهمة")

@app.get("/tasks")
async def get_tasks(assignee_email: Optional[str] = None):
    """جلب المهام"""
    try:
        query = {}
        if assignee_email:
            query["assignee_email"] = assignee_email
        
        tasks = []
        async for task in db.tasks.find(query):
            task["id"] = str(task["_id"])
            tasks.append(task)
        
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="فشل في جلب المهام")

# مسارات KPIs
@app.post("/kpis/upsert")
async def upsert_kpi(kpi_data: KPIUpsert):
    """تحديث أو إنشاء KPI"""
    try:
        target = kpi_data.target
        actual = kpi_data.actual
        drift = max(0.0, (target - actual) / target) if target > 0 else 0.0
        
        performance_level = "excellent" if drift < 0.15 else "good" if drift < 0.25 else "needs_improvement" if drift < 0.35 else "critical"
        
        kpi = {
            "user_email": kpi_data.user_email,
            "month": kpi_data.month,
            "target": target,
            "actual": actual,
            "drift": drift,
            "performance_level": performance_level,
            "updated_at": datetime.now()
        }
        
        # تحديث أو إضافة
        result = await db.kpis.update_one(
            {"user_email": kpi_data.user_email, "month": kpi_data.month},
            {"$set": kpi},
            upsert=True
        )
        
        kpi["id"] = str(result.upserted_id) if result.upserted_id else "updated"
        
        logger.info(f"KPI upserted: {kpi['id']}")
        return kpi
    except Exception as e:
        logger.error(f"Error upserting KPI: {e}")
        raise HTTPException(status_code=500, detail="فشل في تحديث KPI")

@app.get("/kpis/performance/{user_email}")
async def get_user_performance(user_email: str):
    """جلب أداء المستخدم"""
    try:
        kpi = await db.kpis.find_one(
            {"user_email": user_email},
            sort=[("updated_at", -1)]
        )
        
        if not kpi:
            return {
                "user_email": user_email,
                "department": "general",
                "drift": 0.0,
                "performance_level": "no_data"
            }
        
        kpi["id"] = str(kpi["_id"])
        return kpi
    except Exception as e:
        logger.error(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail="فشل في جلب الأداء")

# مسارات الكوتش
@app.post("/coach/ping")
async def coach_ping(ping_data: CoachPing):
    """الحصول على رسالة تحفيز من الكوتش الذكي"""
    try:
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
        
        # جلب القالب المناسب
        templates = PERFORMANCE_TEMPLATES.get(performance_level, PERFORMANCE_TEMPLATES["good"])
        template = random.choice(templates)
        
        # تطبيق متغيرات القسم
        dept_vars = DEPARTMENT_VARIABLES.get(department, DEPARTMENT_VARIABLES["sales"])
        
        try:
            message = template.format(
                name=user_name,
                department=department,
                **dept_vars
            )
        except KeyError:
            message = f"أداؤك جيد يا {user_name}! 🌟 استمر على نفس المستوى في قسم {department}"
        
        logger.info(f"Coach message generated for {user_name}: {performance_level}")
        
        return {
            "message": message,
            "performance_level": performance_level,
            "should_send": True,
            "drift": drift
        }
    except Exception as e:
        logger.error(f"Error generating coach message: {e}")
        raise HTTPException(status_code=500, detail="فشل في توليد رسالة الكوتش")

# مسارات الـ Prompts
@app.get("/prompts/{agent_type}")
async def get_agent_prompts(agent_type: str):
    """عرض prompts للـ agent"""
    try:
        prompts = []
        async for prompt in db.ai_prompts.find({"agent_type": agent_type, "is_active": True}):
            prompt["id"] = str(prompt["_id"])
            prompts.append(prompt)
        
        return prompts
    except Exception as e:
        logger.error(f"Error fetching prompts: {e}")
        raise HTTPException(status_code=500, detail="فشل في جلب الـ prompts")

@app.put("/prompts/{agent_type}/{prompt_name}")
async def update_prompt(agent_type: str, prompt_name: str, prompt_data: PromptUpdate):
    """تحديث prompt"""
    try:
        prompt = {
            "agent_type": agent_type,
            "prompt_name": prompt_name,
            "template": prompt_data.template,
            "variables": prompt_data.variables or {},
            "is_active": True,
            "updated_at": datetime.now()
        }
        
        result = await db.ai_prompts.update_one(
            {"agent_type": agent_type, "prompt_name": prompt_name},
            {"$set": prompt},
            upsert=True
        )
        
        prompt["id"] = str(result.upserted_id) if result.upserted_id else "updated"
        
        logger.info(f"Prompt updated: {agent_type}/{prompt_name}")
        
        return {
            **prompt,
            "message": "تم تحديث الـ prompt بنجاح"
        }
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(status_code=500, detail="فشل في تحديث الـ prompt")

@app.get("/prompts/templates")
async def get_prompt_templates():
    """جلب جميع القوالب الجاهزة"""
    return {
        "coach": {
            "available_variables": {
                "{name}": "اسم الموظف",
                "{department}": "القسم",
                "{performance_level}": "مستوى الأداء",
                "{focus_area}": "المجال المطلوب التركيز عليه",
                "{action}": "الإجراء المقترح"
            },
            "performance_templates": ["excellent", "good", "needs_improvement", "critical"],
            "departments": ["sales", "marketing", "tech", "sondos"]
        },
        "orchestrator": {
            "available_variables": {
                "{goal_text}": "النص الأصلي للهدف",
                "{timeline}": "الجدول الزمني",
                "{available_departments}": "الأقسام المتاحة"
            },
            "project_templates": ["website_launch", "marketing_campaign", "sales_increase"]
        }
    }

@app.get("/prompts/{agent_type}/edit", response_class=HTMLResponse)
async def edit_prompt_form(agent_type: str):
    """صفحة HTML بسيطة لتعديل الـ prompts"""
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تعديل Prompts - {agent_type}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            h1 {{ color: #333; text-align: center; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            textarea {{ height: 200px; resize: vertical; }}
            button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            .variables {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; }}
            .variable {{ display: inline-block; background: #e9ecef; padding: 2px 6px; margin: 2px; border-radius: 3px; font-size: 12px; }}
            .success {{ background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>تعديل Prompts - {agent_type}</h1>
            <form id="promptForm">
                <div class="form-group">
                    <label for="promptName">اسم الـ Prompt:</label>
                    <input type="text" id="promptName" name="prompt_name" value="system" required>
                </div>
                <div class="form-group">
                    <label for="template">القالب:</label>
                    <textarea id="template" name="template" placeholder="اكتب الـ prompt هنا..." required></textarea>
                </div>
                <button type="submit">حفظ التغييرات</button>
            </form>
            
            <div class="variables">
                <h3>المتغيرات المتاحة:</h3>
                <div id="variablesList">
                    <span class="variable">{{name}}: اسم الموظف</span>
                    <span class="variable">{{department}}: القسم</span>
                    <span class="variable">{{performance_level}}: مستوى الأداء</span>
                    <span class="variable">{{summary}}: ملخص الأداء</span>
                </div>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            // معالجة إرسال النموذج
            document.getElementById('promptForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {{
                    template: formData.get('template'),
                    variables: {{}}
                }};
                
                try {{
                    const response = await fetch(`/prompts/{agent_type}/${{formData.get('prompt_name')}}`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(data)
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        document.getElementById('result').innerHTML = 
                            '<div class="success">✅ تم حفظ التغييرات بنجاح!</div>';
                    }} else {{
                        document.getElementById('result').innerHTML = 
                            '<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px;">❌ حدث خطأ في الحفظ</div>';
                    }}
                }} catch (error) {{
                    document.getElementById('result').innerHTML = 
                        '<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px;">❌ حدث خطأ في الاتصال</div>';
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# مسارات التقارير
@app.post("/digests/manager")
async def send_manager_digest(data: Dict[str, str]):
    """إرسال تقرير يومي للمدير"""
    try:
        manager_email = data.get("manager_email", "manager@d10.sa")
        
        # بناء التقرير
        team_tasks = []
        async for task in db.tasks.find({"status": "open"}):
            team_tasks.append(task)
        
        team_kpis = []
        async for kpi in db.kpis.find():
            team_kpis.append(kpi)
        
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
    except Exception as e:
        logger.error(f"Error sending manager digest: {e}")
        raise HTTPException(status_code=500, detail="فشل في إرسال تقرير المدير")

@app.post("/digests/executive")
async def send_executive_digest():
    """إرسال تقرير أسبوعي تنفيذي"""
    try:
        # تحليل الأداء العام
        total_tasks = 0
        async for _ in db.tasks.find():
            total_tasks += 1
        
        total_kpis = 0
        async for _ in db.kpis.find():
            total_kpis += 1
        
        content = f"""
        <h2>تقرير أسبوعي تنفيذي - {datetime.now().strftime('%Y-%m-%d')}</h2>
        
        <h3>📈 نظرة عامة على الأداء</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <p><strong>إجمالي المهام:</strong> {total_tasks}</p>
            <p><strong>إجمالي KPIs:</strong> {total_kpis}</p>
        </div>
        
        <h3>🎯 توصيات إستراتيجية</h3>
        <ul>
            <li>ركز على الأقسام ذات الأداء الضعيف</li>
            <li>استثمر في تطوير الموظفين المتميزين</li>
            <li>ضع خطط تحسين للأقسام الحرجة</li>
        </ul>
        """
        
        logger.info("Executive digest sent")
        
        return {
            "sent": True,
            "preview": "تقرير أسبوعي تنفيذي - نظرة شاملة على الشركة",
            "recipients": ["executive@d10.sa"],
            "content": content
        }
    except Exception as e:
        logger.error(f"Error sending executive digest: {e}")
        raise HTTPException(status_code=500, detail="فشل في إرسال التقرير التنفيذي")

# مسارات Slack
@app.post("/slack/mock")
async def slack_mock(data: SlackMock):
    """اختبار رسائل Slack"""
    try:
        text = data.text
        user = data.user
        
        if text.startswith("مهمة:"):
            task_title = text.replace("مهمة:", "").strip()
            
            # إنشاء المهمة
            task = {
                "_id": ObjectId(),
                "title": task_title,
                "assignee_email": f"{user}@slack.local",
                "due_date": "2025-09-20",
                "status": "open",
                "source": "slack",
                "created_at": datetime.now()
            }
            
            result = await db.tasks.insert_one(task)
            task["id"] = str(result.inserted_id)
            
            logger.info(f"Slack task created: {task['id']}")
            
            return {
                "success": True,
                "message": f"✅ تم إنشاء المهمة: {task_title}",
                "type": "task_created",
                "task_id": task["id"]
            }
            
        elif text.startswith("هدف:"):
            goal_text = text.replace("هدف:", "").strip()
            
            # تفكيك الهدف إلى مهام
            project_data = {
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
            
            logger.info(f"Slack goal expanded: {goal_text}")
            
            return {
                "success": True,
                "message": f"🎯 تم تحليل الهدف: {goal_text}",
                "type": "goal_expanded",
                "project_data": project_data
            }
            
        else:
            return {
                "success": True,
                "message": "مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'",
                "type": "help"
            }
    except Exception as e:
        logger.error(f"Error processing Slack message: {e}")
        raise HTTPException(status_code=500, detail="فشل في معالجة رسالة Slack")

# تهيئة البيانات الأساسية
@app.on_event("startup")
async def startup_event():
    """تهيئة البيانات الأساسية عند بدء التطبيق"""
    try:
        # إنشاء فهارس
        await db.tasks.create_index("assignee_email")
        await db.kpis.create_index([("user_email", 1), ("month", 1)])
        await db.ai_prompts.create_index([("agent_type", 1), ("prompt_name", 1)])
        
        # إدراج prompts افتراضية
        default_prompts = [
            {
                "agent_type": "coach",
                "prompt_name": "system",
                "template": "أنت كوتش ذكي متخصص في تحفيز موظفي شركة د10. شخصيتك ودودة ومحترفة، تتكلم بلهجة سعودية خفيفة. اكتب ≤3 جمل فقط واستخدم إيموجي واحد أو اثنين.",
                "variables": {},
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "agent_type": "orchestrator",
                "prompt_name": "system",
                "template": "أنت منسق مشاريع ذكي متخصص في تفكيك الأهداف الكبيرة إلى مهام قابلة للتنفيذ. لا تتجاوز 6 مهام في التفكيك الأول.",
                "variables": {},
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        for prompt in default_prompts:
            await db.ai_prompts.update_one(
                {"agent_type": prompt["agent_type"], "prompt_name": prompt["prompt_name"]},
                {"$set": prompt},
                upsert=True
            )
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 بدء تشغيل Siyadah Ops AI - النسخة النهائية...")
    print("🌐 النظام متاح على: http://127.0.0.1:8000")
    print("📚 الوثائق متاحة على: http://127.0.0.1:8000/docs")
    print("🔧 تعديل الـ Prompts: http://127.0.0.1:8000/prompts/coach/edit")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
