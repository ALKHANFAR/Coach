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

# إنشاء تطبيق Slack مع معالجة الأخطاء
try:
    if not settings.slack_bot_token or not settings.slack_signing_secret:
        logger.error("❌ Slack credentials not configured!")
        logger.error(f"SLACK_BOT_TOKEN: {'SET' if settings.slack_bot_token else 'MISSING'}")
        logger.error(f"SLACK_SIGNING_SECRET: {'SET' if settings.slack_signing_secret else 'MISSING'}")
        raise ValueError("Slack credentials not configured")
    
    app = App(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret
    )
    logger.info("✅ Slack app initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Slack app: {e}")
    # إنشاء تطبيق وهمي للاختبار
    app = None

orchestrator_ai = OrchestratorAI()

def register_slack_events():
    """تسجيل أحداث Slack فقط إذا كان التطبيق متاحاً"""
    if app is None:
        logger.warning("⚠️ Slack app not initialized - events not registered")
        return
    
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

# تسجيل الأحداث
register_slack_events()

async def handle_task_creation(text: str, user_id: str, say):
    """معالجة إنشاء مهمة من Slack"""
    try:
        # استخراج عنوان المهمة
        task_title = text.replace("مهمة:", "").strip()
        
        if not task_title:
            await say("يرجى كتابة عنوان المهمة بعد 'مهمة:'")
            return
        
        # البحث عن المستخدم في قاعدة البيانات مع معالجة الأخطاء
        try:
            db = await get_db()
            slack_user = await db.users.find_one({"slack_user_id": user_id})
        except Exception as db_error:
            logger.error(f"Database error in task creation: {db_error}")
            await say("عذراً، حدث خطأ في الاتصال بقاعدة البيانات")
            return
        
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
        
        # استخدام OrchestratorAI لتفكيك الهدف مع معالجة الأخطاء
        try:
            project_data = await orchestrator_ai.expand_goal_to_tasks(goal_text)
        except Exception as ai_error:
            logger.error(f"AI error in goal expansion: {ai_error}")
            await say("عذراً، حدث خطأ في تحليل الهدف بواسطة الذكاء الاصطناعي")
            return
        
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

# معالج الطلبات مع معالجة الأخطاء
handler = None
if app is not None:
    handler = SlackRequestHandler(app)
    logger.info("✅ Slack request handler initialized")
else:
    logger.warning("⚠️ Slack request handler not initialized - app is None")

# endpoint للـ Slack events
async def slack_events(request):
    """معالجة أحداث Slack مع معالجة شاملة للأخطاء"""
    try:
        # الحصول على البيانات من الطلب
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        logger.info(f"📨 Received Slack event: {data.get('type', 'unknown')}")
        
        # التحقق من نوع الطلب
        if data.get("type") == "url_verification":
            # إرجاع قيمة challenge للتحقق من URL
            challenge = data.get("challenge")
            logger.info(f"✅ Slack URL verification challenge: {challenge}")
            return {"challenge": challenge}
        
        # التحقق من وجود المعالج
        if handler is None:
            logger.error("❌ Slack handler not available - credentials not configured")
            return {"error": "Slack bot not configured", "status": "error"}
        
        # معالجة الأحداث الأخرى باستخدام SlackRequestHandler
        logger.info("🔄 Processing Slack event with handler...")
        result = await handler.handle(request)
        logger.info("✅ Slack event processed successfully")
        return result
        
    except json.JSONDecodeError as json_error:
        logger.error(f"❌ Invalid JSON in Slack request: {json_error}")
        return {"error": "Invalid JSON", "status": "error"}
    except Exception as e:
        logger.error(f"❌ Error handling Slack request: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return {"error": "Internal server error", "status": "error", "details": str(e)}
