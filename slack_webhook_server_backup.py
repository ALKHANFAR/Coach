#!/usr/bin/env python3
"""
خادم Slack Webhook مع دعم تحقق URL
"""
from fastapi import FastAPI, Request
import json
import uvicorn
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Slack Webhook Server")

@app.post("/slack/events")
async def slack_events(request: Request):
    """معالجة أحداث Slack مع دعم تحقق URL"""
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
        
        logger.info(f"App mention from {user_id} in {channel}: {text}")
        
        # هنا يمكنك إضافة منطق معالجة الرسائل
        # مثل إنشاء المهام أو تفكيك الأهداف
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")
        return {"error": "Processing failed"}

@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {"status": "healthy", "service": "slack-webhook-server"}

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Slack Webhook Server",
        "endpoints": {
            "slack_events": "/slack/events",
            "health": "/health"
        },
        "status": "running"
    }

if __name__ == "__main__":
    print("🚀 تشغيل خادم Slack Webhook...")
    print("📡 سيتم تشغيل الخادم على: http://127.0.0.1:8000")
    print("🔗 استخدم ngrok لتعريض الخادم للإنترنت")
    print("📋 الخطوات:")
    print("1. شغل هذا الملف: python slack_webhook_server.py")
    print("2. في terminal آخر: ngrok http 8000")
    print("3. انسخ ngrok URL إلى Slack Event Subscriptions")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
