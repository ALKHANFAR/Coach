"""Digests endpoints"""
from fastapi import APIRouter, HTTPException
from app.schemas import ManagerDigestRequest, ExecutiveDigestRequest, DigestResponse
from app.services.digest_service import DigestService
from app.integrations.emailer import EmailService
from app.config import settings
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/digests", tags=["Digests"])

digest_service = DigestService()
email_service = EmailService()

@router.post("/manager", response_model=DigestResponse)
async def send_manager_digest(request: ManagerDigestRequest):
    """إرسال تقرير يومي للمدير"""
    try:
        # إنشاء التقرير
        content = await digest_service.build_manager_digest(request.manager_email)
        
        # إنشاء HTML
        html_content = email_service.create_html_template(
            "تقرير يومي - فريقك",
            content
        )
        
        # إرسال الإيميل
        result = await email_service.send_email(
            to=request.manager_email,
            subject=f"تقرير يومي - {request.manager_email}",
            body=html_content
        )
        
        return DigestResponse(
            sent=result["sent"],
            preview=result.get("preview", content[:200]),
            recipients=[request.manager_email]
        )
        
    except Exception as e:
        logger.error(f"Error sending manager digest: {e}")
        raise HTTPException(status_code=500, detail="Failed to send manager digest")

@router.post("/executive", response_model=DigestResponse)
async def send_executive_digest(request: ExecutiveDigestRequest):
    """إرسال تقرير أسبوعي للإدارة التنفيذية"""
    try:
        # إنشاء التقرير التنفيذي
        content = await digest_service.build_executive_digest()
        
        # إنشاء HTML
        html_content = email_service.create_html_template(
            "تقرير أسبوعي تنفيذي",
            content
        )
        
        # إرسال الإيميل للإدارة التنفيذية
        result = await email_service.send_email(
            to=settings.executive_email,
            subject="تقرير أسبوعي تنفيذي - سيادة الذكي",
            body=html_content
        )
        
        return DigestResponse(
            sent=result["sent"],
            preview=result.get("preview", content[:200]),
            recipients=[settings.executive_email]
        )
        
    except Exception as e:
        logger.error(f"Error sending executive digest: {e}")
        raise HTTPException(status_code=500, detail="Failed to send executive digest")
