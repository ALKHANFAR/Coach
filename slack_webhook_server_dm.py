#!/usr/bin/env python3
"""
خادم Slack Webhook مع دعم الرسائل المباشرة (Direct Messages)
"""
from fastapi import FastAPI, Request
import json
import uvicorn
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Slack Webhook Server - Direct Messages")

@app.post("/slack/events")
async def slack_events(request: Request):
    """معالجة أحداث Slack مع دعم الرسائل المباشرة"""
    try:
        # الحصول على البيانات
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Received Slack event: {data}")
        
        # التحقق من نوع الطلب
        if data.get("type") == "url_verification":
            # إرجاع قيمة challenge للتحقق من URL
            challenge = data.get("challenge")
            logger.info(f"URL verification challenge: {challenge}")
            return {"challenge": challenge}
        
        # معالجة الأحداث الأخرى
        elif data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")
            
            logger.info(f"Processing event: {event_type}")
            
            # معالجة app_mention
            if event_type == "app_mention":
                await handle_app_mention(event)
            # معالجة message.channels
            elif event_type == "message":
                await handle_message(event)
            
            return {"status": "ok"}
        
        else:
            logger.warning(f"Unknown event type: {data.get('type')}")
            return {"status": "ignored"}
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        return {"error": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"error": "Internal server error"}

async def handle_app_mention(event):
    """معالجة ذكر البوت"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        channel = event.get("channel")
        
        logger.info(f"🎯 App mention from {user_id} in {channel}: {text}")
        
        # استخراج النص من الرسالة (إزالة ذكر البوت)
        clean_text = text
        if "<@" in text and ">" in text:
            # إزالة ذكر البوت من النص
            import re
            clean_text = re.sub(r'<@[^>]+>', '', text).strip()
        
        logger.info(f"📝 Clean text: {clean_text}")
        
        # معالجة أنواع مختلفة من الرسائل
        if clean_text.startswith("مهمة:"):
            await handle_task_creation(clean_text, user_id, channel)
        elif clean_text.startswith("هدف:"):
            await handle_goal_expansion(clean_text, user_id, channel)
        elif clean_text.startswith("مساعدة") or clean_text.startswith("help"):
            await handle_help_request(user_id, channel)
        else:
            await handle_general_message(clean_text, user_id, channel)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")
        return {"error": "Processing failed"}

async def handle_message(event):
    """معالجة الرسائل العامة والمباشرة"""
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        channel = event.get("channel")
        bot_id = event.get("bot_id")
        channel_type = event.get("channel_type", "unknown")
        
        # تجاهل الرسائل من البوت نفسه
        if bot_id:
            logger.info(f"🤖 Ignoring bot message: {text}")
            return {"status": "ignored"}
        
        # تحديد نوع القناة
        if channel_type == "im":
            logger.info(f"💬 Direct message from {user_id}: {text}")
            await handle_direct_message(text, user_id, channel)
        elif channel_type == "mpim":
            logger.info(f"👥 Group message from {user_id}: {text}")
            await handle_group_message(text, user_id, channel)
        else:
            # رسالة في قناة عامة
            if "<@" in text and ">" in text:
                logger.info(f"📢 Bot mentioned in channel message from {user_id}: {text}")
                await handle_app_mention(event)
            else:
                logger.info(f"📨 Regular channel message from {user_id}: {text}")
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return {"error": "Processing failed"}

async def handle_direct_message(text: str, user_id: str, channel: str):
    """معالجة الرسائل المباشرة"""
    try:
        logger.info(f"💬 Processing direct message from {user_id}: {text}")
        
        # معالجة أنواع مختلفة من الرسائل المباشرة
        if text.startswith("مهمة:"):
            await handle_task_creation(text, user_id, channel)
        elif text.startswith("هدف:"):
            await handle_goal_expansion(text, user_id, channel)
        elif text.startswith("مساعدة") or text.startswith("help"):
            await handle_help_request(user_id, channel)
        elif text.startswith("تقرير") or text.startswith("report"):
            await handle_report_request(user_id, channel)
        elif text.startswith("حالة") or text.startswith("status"):
            await handle_status_request(user_id, channel)
        else:
            await handle_general_message(text, user_id, channel)
        
        logger.info(f"✅ Direct message processed successfully")
        
    except Exception as e:
        logger.error(f"Error handling direct message: {e}")

async def handle_group_message(text: str, user_id: str, channel: str):
    """معالجة رسائل المجموعات"""
    try:
        logger.info(f"👥 Processing group message from {user_id}: {text}")
        
        # نفس معالجة الرسائل المباشرة
        await handle_direct_message(text, user_id, channel)
        
    except Exception as e:
        logger.error(f"Error handling group message: {e}")

async def handle_task_creation(text: str, user_id: str, channel: str):
    """معالجة إنشاء مهمة"""
    try:
        task_title = text.replace("مهمة:", "").strip()
        logger.info(f"✅ Task creation: {task_title} by {user_id}")
        
        # هنا يمكنك إضافة منطق إنشاء المهمة في قاعدة البيانات
        # await create_task_in_database(task_title, user_id)
        
        logger.info(f"📋 Task '{task_title}' created successfully")
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")

async def handle_goal_expansion(text: str, user_id: str, channel: str):
    """معالجة تفكيك الهدف"""
    try:
        goal_text = text.replace("هدف:", "").strip()
        logger.info(f"🎯 Goal expansion: {goal_text} by {user_id}")
        
        # هنا يمكنك إضافة منطق تفكيك الهدف باستخدام AI
        # await expand_goal_with_ai(goal_text, user_id)
        
        logger.info(f"📊 Goal '{goal_text}' expanded successfully")
        
    except Exception as e:
        logger.error(f"Error expanding goal: {e}")

async def handle_help_request(user_id: str, channel: str):
    """معالجة طلب المساعدة"""
    try:
        logger.info(f"❓ Help requested by {user_id}")
        
        # هنا يمكنك إرسال رسالة مساعدة
        # await send_help_message(channel)
        
        logger.info(f"📖 Help message sent to {channel}")
        
    except Exception as e:
        logger.error(f"Error handling help request: {e}")

async def handle_report_request(user_id: str, channel: str):
    """معالجة طلب التقرير"""
    try:
        logger.info(f"📊 Report requested by {user_id}")
        
        # هنا يمكنك إرسال تقرير
        # await send_report(channel)
        
        logger.info(f"📈 Report sent to {channel}")
        
    except Exception as e:
        logger.error(f"Error handling report request: {e}")

async def handle_status_request(user_id: str, channel: str):
    """معالجة طلب الحالة"""
    try:
        logger.info(f"📊 Status requested by {user_id}")
        
        # هنا يمكنك إرسال حالة النظام
        # await send_status(channel)
        
        logger.info(f"📈 Status sent to {channel}")
        
    except Exception as e:
        logger.error(f"Error handling status request: {e}")

async def handle_general_message(text: str, user_id: str, channel: str):
    """معالجة الرسائل العامة"""
    try:
        logger.info(f"💭 General message from {user_id}: {text}")
        
        # هنا يمكنك إضافة منطق معالجة الرسائل العامة
        # await process_general_message(text, user_id, channel)
        
        logger.info(f"🔄 General message processed")
        
    except Exception as e:
        logger.error(f"Error handling general message: {e}")

@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {"status": "healthy", "service": "slack-webhook-server-dm"}

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Slack Webhook Server - Direct Messages",
        "endpoints": {
            "slack_events": "/slack/events",
            "health": "/health"
        },
        "status": "running",
        "supported_events": ["app_mention", "message.channels", "message.im", "message.mpim"],
        "features": [
            "Direct messages (رسائل مباشرة)",
            "Group messages (رسائل المجموعات)",
            "Task creation (مهمة: ...)",
            "Goal expansion (هدف: ...)",
            "Help requests (مساعدة)",
            "Reports (تقرير)",
            "Status (حالة)",
            "General message handling"
        ]
    }

if __name__ == "__main__":
    print("🚀 تشغيل خادم Slack Webhook للرسائل المباشرة...")
    print("📡 سيتم تشغيل الخادم على: http://127.0.0.1:8000")
    print("🔗 استخدم ngrok لتعريض الخادم للإنترنت")
    print("📋 الخطوات:")
    print("1. شغل هذا الملف: python slack_webhook_server_dm.py")
    print("2. في terminal آخر: ngrok http 8000")
    print("3. انسخ ngrok URL إلى Slack Event Subscriptions")
    print("4. أضف Bot Events: message.im, message.mpim")
    print("5. ابدأ محادثة مع البوت: @Siyadah Ops AI")
    print("6. اختبر البوت: مهمة: اختبار")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
