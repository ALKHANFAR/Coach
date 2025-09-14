"""Slack integration endpoints"""
from fastapi import APIRouter, Request, HTTPException
from app.integrations.slack_bot import slack_events
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/slack", tags=["Slack Integration"])

@router.post("/events")
async def slack_webhook(request: Request):
    """webhook لاستقبال أحداث Slack"""
    try:
        return await slack_events(request)
    except Exception as e:
        logger.error(f"Error handling Slack webhook: {e}")
        raise HTTPException(status_code=500, detail="Slack webhook error")

@router.get("/status")
async def slack_status():
    """فحص حالة تكوين Slack Bot"""
    from app.config import settings
    from app.integrations.slack_bot import app, handler
    
    status = {
        "slack_configured": bool(settings.slack_bot_token and settings.slack_signing_secret),
        "bot_token_set": bool(settings.slack_bot_token),
        "signing_secret_set": bool(settings.slack_signing_secret),
        "app_initialized": app is not None,
        "handler_initialized": handler is not None,
        "bot_token_format": "valid" if settings.slack_bot_token and settings.slack_bot_token.startswith("xoxb-") else "invalid",
        "environment": {
            "SLACK_BOT_TOKEN": "SET" if settings.slack_bot_token else "MISSING",
            "SLACK_SIGNING_SECRET": "SET" if settings.slack_signing_secret else "MISSING"
        }
    }
    
    return status

@router.post("/mock")
async def mock_slack_message(message_data: dict):
    """اختبار رسائل Slack بدون token حقيقي"""
    try:
        text = message_data.get("text", "")
        user_id = message_data.get("user", "test_user")
        
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
                    "project_title": "مشروع تجريبي",
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
            
    except Exception as e:
        logger.error(f"Error in mock Slack: {e}")
        raise HTTPException(status_code=500, detail="Mock Slack error")
