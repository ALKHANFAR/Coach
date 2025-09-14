#!/usr/bin/env python3
"""
تشغيل البوت بدون قاعدة بيانات - حل جذري ومضمون
"""
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
import json
import random

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
    description="نظام إدارة العمليات الذكي مع تكامل Slack - بدون قاعدة بيانات",
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

# تخزين مؤقت في الذاكرة
tasks_storage = []
users_storage = []

# Schemas
class TaskCreate(BaseModel):
    title: str
    assignee_email: str
    due_date: Optional[str] = None
    description: Optional[str] = None

class SlackEvent(BaseModel):
    type: str
    text: Optional[str] = None
    user: Optional[str] = None
    channel: Optional[str] = None
    challenge: Optional[str] = None

# المسارات الأساسية
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "مرحباً بك في Siyadah Ops AI 🚀",
        "status": "running",
        "slack_bot": "active",
        "version": "1.0.0",
        "database": "in-memory"
    }

@app.get("/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "slack_bot": "active",
        "database": "in-memory",
        "tasks_count": len(tasks_storage),
        "users_count": len(users_storage)
    }

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

# مسارات Slack
@app.post("/slack/events")
async def slack_webhook(request):
    """webhook لاستقبال أحداث Slack"""
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
        
        # معالجة الأحداث الأخرى
        if data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")
            
            if event_type == "app_mention":
                await handle_app_mention(event)
            elif event_type == "message":
                await handle_message(event)
        
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Slack request")
        return {"error": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Error handling Slack request: {e}")
        return {"error": "Internal server error"}

async def handle_app_mention(event):
    """معالجة ذكر البوت"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        channel = event.get("channel")
        
        logger.info(f"Slack mention from {user_id}: {text}")
        
        if text.startswith("مهمة:"):
            await handle_task_creation(text, user_id, channel)
        elif text.startswith("هدف:"):
            await handle_goal_expansion(text, user_id, channel)
        else:
            await send_slack_message(channel, "مرحباً! يمكنني مساعدتك في:\n- إنشاء مهام: اكتب 'مهمة: عنوان المهمة'\n- تفكيك الأهداف: اكتب 'هدف: وصف الهدف'")
            
    except Exception as e:
        logger.error(f"Error handling Slack mention: {e}")

async def handle_message(event):
    """معالجة الرسائل العادية"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        channel = event.get("channel")
        
        # تجاهل الرسائل من البوت نفسه
        if event.get("bot_id"):
            return
        
        logger.info(f"Slack message from {user_id}: {text}")
        
        # معالجة الرسائل التي تبدأ بـ "مهمة:" أو "هدف:"
        if text.startswith("مهمة:"):
            await handle_task_creation(text, user_id, channel)
        elif text.startswith("هدف:"):
            await handle_goal_expansion(text, user_id, channel)
            
    except Exception as e:
        logger.error(f"Error handling Slack message: {e}")

async def handle_task_creation(text: str, user_id: str, channel: str):
    """معالجة إنشاء مهمة من Slack"""
    try:
        # استخراج عنوان المهمة
        task_title = text.replace("مهمة:", "").strip()
        
        if not task_title:
            await send_slack_message(channel, "يرجى كتابة عنوان المهمة بعد 'مهمة:'")
            return
        
        # إنشاء المهمة
        task = {
            "id": f"slack_task_{len(tasks_storage) + 1}",
            "title": task_title,
            "assignee_email": f"{user_id}@slack.local",
            "due_date": "2025-09-20",
            "status": "open",
            "source": "slack",
            "created_at": datetime.now().isoformat(),
            "description": f"مهمة منشأة من Slack بواسطة {user_id}"
        }
        tasks_storage.append(task)
        
        await send_slack_message(channel, f"✅ تم إنشاء المهمة: {task_title}\n🆔 معرف المهمة: {task['id']}")
        
    except Exception as e:
        logger.error(f"Error creating task from Slack: {e}")
        await send_slack_message(channel, "عذراً، حدث خطأ في إنشاء المهمة")

async def handle_goal_expansion(text: str, user_id: str, channel: str):
    """معالجة تفكيك الهدف إلى مهام"""
    try:
        # استخراج نص الهدف
        goal_text = text.replace("هدف:", "").strip()
        
        if not goal_text:
            await send_slack_message(channel, "يرجى كتابة وصف الهدف بعد 'هدف:'")
            return
        
        await send_slack_message(channel, "🤔 جاري تحليل الهدف وإنشاء خطة العمل...")
        
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
                    "title": "وضع الخطة",
                    "description": "وضع خطة تنفيذية مفصلة",
                    "department": "general",
                    "estimated_days": 3,
                    "priority": "high"
                },
                {
                    "id": 3,
                    "title": "التنفيذ",
                    "description": "تنفيذ المهام المطلوبة",
                    "department": "general",
                    "estimated_days": 5,
                    "priority": "medium"
                },
                {
                    "id": 4,
                    "title": "المراجعة والاختبار",
                    "description": "مراجعة النتائج واختبار الجودة",
                    "department": "general",
                    "estimated_days": 2,
                    "priority": "medium"
                }
            ],
            "success_criteria": ["إنجاز الهدف المطلوب", "تحقيق الجودة المطلوبة"],
            "potential_risks": ["عدم وضوح المتطلبات", "تأخير في التنفيذ"]
        }
        
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
        
        await send_slack_message(channel, response)
        
    except Exception as e:
        logger.error(f"Error expanding goal from Slack: {e}")
        await send_slack_message(channel, "عذراً، حدث خطأ في تحليل الهدف")

async def send_slack_message(channel: str, text: str):
    """إرسال رسالة إلى Slack"""
    try:
        import requests
        
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        if not slack_token:
            logger.error("SLACK_BOT_TOKEN not found")
            return
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        data = {
            "channel": channel,
            "text": text
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info(f"Message sent to {channel}")
            else:
                logger.error(f"Slack API error: {result.get('error')}")
        else:
            logger.error(f"HTTP error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending Slack message: {e}")

# مسارات إضافية
@app.get("/tasks/count")
async def get_tasks_count():
    """عدد المهام"""
    return {"count": len(tasks_storage)}

@app.get("/users/count")
async def get_users_count():
    """عدد المستخدمين"""
    return {"count": len(users_storage)}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """حذف مهمة"""
    global tasks_storage
    tasks_storage = [t for t in tasks_storage if t["id"] != task_id]
    return {"message": "Task deleted", "task_id": task_id}

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل Siyadah Ops AI - Slack Bot (بدون قاعدة بيانات)...")
    print("=" * 70)
    
    # فحص متغيرات البيئة الأساسية
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_secret = os.getenv("SLACK_SIGNING_SECRET")
    
    if not slack_token or not slack_secret:
        print("❌ متغيرات البيئة غير مكتملة!")
        print("📝 تأكد من إعداد ملف .env")
        return
    
    if not slack_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح!")
        print("📝 يجب أن يبدأ بـ xoxb-")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    print("🌐 بدء تشغيل الخادم على المنفذ 8002...")
    
    # تشغيل النظام
    try:
        import uvicorn
        
        print("🚀 النظام متاح على: http://127.0.0.1:8002")
        print("📚 الوثائق: http://127.0.0.1:8002/docs")
        print("🔍 فحص الصحة: http://127.0.0.1:8002/health")
        print("📡 Slack Webhook: http://127.0.0.1:8002/slack/events")
        print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
        print("=" * 70)
        
        uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        print("📝 تأكد من تثبيت جميع المتطلبات: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
