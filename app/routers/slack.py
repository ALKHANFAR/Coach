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
