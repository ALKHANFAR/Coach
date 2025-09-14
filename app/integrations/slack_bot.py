"""Slack Bot integration"""
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from app.db import get_db
from app.models import Task, User
from app.ai.orchestrator import OrchestratorAI
from app.config import settings
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()

# إنشاء تطبيق Slack
app = App(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret
)

orchestrator_ai = OrchestratorAI()

@app.event("app_mention")
async def handle_mention(event, say):
    """معالجة ذكر البوت"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        
        logger.info(f"Slack mention from {user_id}: {text}")
        
        if text.startswith("مهمة:"):
            await handle_task_creation(text, user_id, say)
        elif text.startswith("هدف:"):
            await handle_goal_expansion(text, user_id, say)
        else:
            await say("مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'")
            
    except Exception as e:
        logger.error(f"Error handling Slack mention: {e}")
        await say("عذراً، حدث خطأ في معالجة طلبك")

async def handle_task_creation(text: str, user_id: str, say):
    """معالجة إنشاء مهمة من Slack"""
    try:
        # استخراج عنوان المهمة
        task_title = text.replace("مهمة:", "").strip()
        
        if not task_title:
            await say("يرجى كتابة عنوان المهمة بعد 'مهمة:'")
            return
        
        # البحث عن المستخدم في قاعدة البيانات
        db = await get_db()
        slack_user = await db.users.find_one({"slack_user_id": user_id})
        
        if not slack_user:
            # إنشاء مستخدم جديد إذا لم يوجد
            slack_user = User(
                email=f"{user_id}@slack.local",
                name=f"Slack User {user_id}",
                role="employee",
                department="general",
                slack_user_id=user_id
            )
            await db.users.insert_one(slack_user.dict(by_alias=True))
        
        # إنشاء المهمة
        task = Task(
            title=task_title,
            description=f"مهمة منشأة من Slack بواسطة {slack_user['name']}",
            assignee_user_id=slack_user["_id"],
            due_date=datetime.utcnow().replace(hour=18),  # نهاية اليوم
            created_by_user_id=slack_user["_id"],
            source="slack"
        )
        
        result = await db.tasks.insert_one(task.dict(by_alias=True))
        
        await say(f"✅ تم إنشاء المهمة: {task_title}\n🆔 معرف المهمة: {result.inserted_id}")
        
    except Exception as e:
        logger.error(f"Error creating task from Slack: {e}")
        await say("عذراً، حدث خطأ في إنشاء المهمة")

async def handle_goal_expansion(text: str, user_id: str, say):
    """معالجة تفكيك الهدف إلى مهام"""
    try:
        # استخراج نص الهدف
        goal_text = text.replace("هدف:", "").strip()
        
        if not goal_text:
            await say("يرجى كتابة وصف الهدف بعد 'هدف:'")
            return
        
        await say("🤔 جاري تحليل الهدف وإنشاء خطة العمل...")
        
        # استخدام OrchestratorAI لتفكيك الهدف
        project_data = await orchestrator_ai.expand_goal_to_tasks(goal_text)
        
        # إرسال النتيجة
        response = f"🎯 *{project_data['project_title']}*\n\n"
        response += f"📝 *الوصف:* {project_data['project_description']}\n"
        response += f"⏱️ *المدة المتوقعة:* {project_data['estimated_duration']}\n\n"
        response += "📋 *المهام المطلوبة:*\n"
        
        for task in project_data['tasks']:
            response += f"• {task['title']} ({task['department']}) - {task['estimated_days']} أيام\n"
        
        response += f"\n🎯 *معايير النجاح:*\n"
        for criterion in project_data['success_criteria']:
            response += f"• {criterion}\n"
        
        await say(response)
        
    except Exception as e:
        logger.error(f"Error expanding goal from Slack: {e}")
        await say("عذراً، حدث خطأ في تحليل الهدف")

# معالج الطلبات
handler = SlackRequestHandler(app)

# endpoint للـ Slack events
async def slack_events(request):
    """معالجة أحداث Slack"""
    try:
        # الحصول على البيانات من الطلب
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        # التحقق من نوع الطلب
        if data.get("type") == "url_verification":
            # إرجاع قيمة challenge للتحقق من URL
            challenge = data.get("challenge")
            logger.info(f"Slack URL verification challenge: {challenge}")
            return {"challenge": challenge}
        
        # معالجة الأحداث الأخرى باستخدام SlackRequestHandler
        return await handler.handle(request)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Slack request")
        return {"error": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Error handling Slack request: {e}")
        return {"error": "Internal server error"}
