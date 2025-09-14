"""KPIs management endpoints"""
from fastapi import APIRouter, HTTPException
from app.schemas import KPIUpsert, KPIResponse
from app.services.kpi_service import KPIService
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/kpis", tags=["KPIs"])

kpi_service = KPIService()

@router.post("/upsert", response_model=KPIResponse)
async def upsert_kpi(kpi_data: KPIUpsert):
    """تحديث أو إنشاء KPI جديد"""
    try:
        result = await kpi_service.upsert_kpi(
            user_email=kpi_data.user_email,
            month=kpi_data.month,
            target=kpi_data.target,
            actual=kpi_data.actual
        )
        
        return KPIResponse(**result)
        
    except Exception as e:
        logger.error(f"Error upserting KPI: {e}")
        raise HTTPException(status_code=500, detail="Failed to upsert KPI")

@router.get("/performance/{user_email}")
async def get_user_performance(user_email: str):
    """جلب أداء المستخدم"""
    try:
        result = await kpi_service.get_user_performance(user_email)
        return result
        
    except Exception as e:
        logger.error(f"Error getting user performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user performance")
