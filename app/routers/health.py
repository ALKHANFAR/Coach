"""Health check endpoint"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """فحص صحة النظام"""
    return {"status": "ok", "message": "Siyadah Ops AI is running"}
