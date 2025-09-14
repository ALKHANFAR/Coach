"""Coach AI endpoints"""
from fastapi import APIRouter, HTTPException
from app.schemas import CoachPing, CoachResponse
from app.services.kpi_service import KPIService
from app.ai.coach import CoachAI
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/coach", tags=["Coach AI"])

kpi_service = KPIService()
coach_ai = CoachAI()

@router.post("/ping", response_model=CoachResponse)
async def coach_ping(ping_data: CoachPing):
    """الحصول على رسالة تحفيز من الكوتش الذكي"""
    try:
        # جلب أداء المستخدم
        performance_data = await kpi_service.get_user_performance(ping_data.user_email)
        
        if "error" in performance_data:
            raise HTTPException(status_code=404, detail=performance_data["error"])
        
        # إعداد بيانات المستخدم للكوتش
        user_data = {
            "name": ping_data.user_email.split("@")[0],
            "department": ping_data.department,
            "role": "employee",
            "drift": performance_data.get("drift", 0.0),
            "summary": ping_data.summary or f"أداء في قسم {ping_data.department}"
        }
        
        # إنشاء رسالة الكوتش
        coach_result = await coach_ai.generate_coach_message(user_data)
        
        return CoachResponse(
            message=coach_result["message"],
            performance_level=coach_result["performance_level"],
            should_send=coach_result["should_send"]
        )
        
    except Exception as e:
        logger.error(f"Error in coach ping: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate coach message")
