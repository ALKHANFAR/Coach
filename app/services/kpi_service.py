"""خدمة إدارة KPIs وحساب الـ drift"""
from typing import Optional
from app.db import get_db
from app.models import KPI, User
import structlog

logger = structlog.get_logger()

class KPIService:
    """خدمة إدارة KPIs"""
    
    async def compute_drift(self, user_id: str) -> float:
        """حساب الـ drift للمستخدم"""
        try:
            db = await get_db()
            
            # جلب أحدث KPI للمستخدم
            kpi_doc = await db.kpis.find_one(
                {"user_id": user_id},
                sort=[("month", -1)]
            )
            
            if not kpi_doc:
                return 0.0
            
            target = kpi_doc.get("target", 0)
            actual = kpi_doc.get("actual", 0)
            
            if target == 0:
                return 0.0
            
            # حساب الـ drift: max(0, (target - actual) / target)
            drift = max(0.0, (target - actual) / target)
            
            # تحديث الـ drift في قاعدة البيانات
            await db.kpis.update_one(
                {"_id": kpi_doc["_id"]},
                {"$set": {"drift": drift}}
            )
            
            return drift
            
        except Exception as e:
            logger.error(f"Error computing drift for user {user_id}: {e}")
            return 0.0
    
    async def upsert_kpi(self, user_email: str, month: str, target: int, actual: int) -> dict:
        """تحديث أو إنشاء KPI جديد"""
        try:
            db = await get_db()
            
            # البحث عن المستخدم
            user = await db.users.find_one({"email": user_email})
            if not user:
                # إنشاء مستخدم جديد إذا لم يوجد
                user = User(
                    email=user_email,
                    name=user_email.split("@")[0],
                    role="employee",
                    department="general"
                )
                await db.users.insert_one(user.dict(by_alias=True))
            
            # البحث عن KPI موجود
            existing_kpi = await db.kpis.find_one({
                "user_id": user["_id"],
                "month": month
            })
            
            # حساب الـ drift
            drift = max(0.0, (target - actual) / target) if target > 0 else 0.0
            
            if existing_kpi:
                # تحديث موجود
                await db.kpis.update_one(
                    {"_id": existing_kpi["_id"]},
                    {
                        "$set": {
                            "target": target,
                            "actual": actual,
                            "drift": drift
                        }
                    }
                )
                kpi_id = existing_kpi["_id"]
            else:
                # إنشاء جديد
                kpi = KPI(
                    user_id=user["_id"],
                    department=user.get("department", "general"),
                    month=month,
                    target=target,
                    actual=actual,
                    drift=drift
                )
                result = await db.kpis.insert_one(kpi.dict(by_alias=True))
                kpi_id = result.inserted_id
            
            return {
                "id": str(kpi_id),
                "user_email": user_email,
                "department": user.get("department", "general"),
                "month": month,
                "target": target,
                "actual": actual,
                "drift": drift
            }
            
        except Exception as e:
            logger.error(f"Error upserting KPI: {e}")
            raise
    
    async def get_user_performance(self, user_email: str) -> dict:
        """جلب أداء المستخدم"""
        try:
            db = await get_db()
            
            user = await db.users.find_one({"email": user_email})
            if not user:
                return {"error": "User not found"}
            
            # جلب أحدث KPI
            kpi_doc = await db.kpis.find_one(
                {"user_id": user["_id"]},
                sort=[("month", -1)]
            )
            
            if not kpi_doc:
                return {
                    "user_email": user_email,
                    "department": user.get("department", "general"),
                    "drift": 0.0,
                    "performance_level": "no_data"
                }
            
            drift = kpi_doc.get("drift", 0.0)
            performance_level = self._get_performance_level(drift)
            
            return {
                "user_email": user_email,
                "department": user.get("department", "general"),
                "drift": drift,
                "performance_level": performance_level,
                "target": kpi_doc.get("target", 0),
                "actual": kpi_doc.get("actual", 0),
                "month": kpi_doc.get("month", "")
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance: {e}")
            return {"error": str(e)}
    
    def _get_performance_level(self, drift: float) -> str:
        """تحديد مستوى الأداء بناءً على الـ drift"""
        if drift < 0.15:
            return "excellent"
        elif drift < 0.25:
            return "good"
        elif drift < 0.35:
            return "needs_improvement"
        else:
            return "critical"
