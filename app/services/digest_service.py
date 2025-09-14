"""خدمة إنشاء التقارير اليومية والأسبوعية"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.db import get_db
from app.services.kpi_service import KPIService
import structlog

logger = structlog.get_logger()

class DigestService:
    """خدمة إنشاء التقارير"""
    
    def __init__(self):
        self.kpi_service = KPIService()
    
    async def build_manager_digest(self, manager_email: str) -> str:
        """إنشاء تقرير يومي للمدير"""
        try:
            db = await get_db()
            
            # جلب بيانات المدير
            manager = await db.users.find_one({"email": manager_email})
            if not manager:
                return "المدير غير موجود"
            
            # جلب فريق المدير
            team_members = []
            async for member in db.users.find({"manager_id": manager["_id"]}):
                team_members.append(member)
            
            if not team_members:
                return f"مرحباً {manager.get('name', 'المدير')}، لا يوجد أعضاء في فريقك حالياً."
            
            # بناء التقرير
            content = f"""
            <h2>تقرير يومي - {datetime.now().strftime('%Y-%m-%d')}</h2>
            <p>مرحباً {manager.get('name', 'المدير')}،</p>
            <p>إليك ملخص أداء فريقك اليوم:</p>
            
            <h3>📊 ملخص الأداء</h3>
            <ul>
            """
            
            # إضافة بيانات كل عضو في الفريق
            for member in team_members:
                performance = await self.kpi_service.get_user_performance(member["email"])
                
                if "error" not in performance:
                    drift = performance.get("drift", 0.0)
                    performance_level = performance.get("performance_level", "no_data")
                    
                    # تحديد الرمز حسب الأداء
                    emoji = "🟢" if performance_level == "excellent" else \
                           "🟡" if performance_level == "good" else \
                           "🟠" if performance_level == "needs_improvement" else "🔴"
                    
                    content += f"""
                    <li>{emoji} <strong>{member.get('name', member['email'])}</strong> 
                        - قسم {member.get('department', 'غير محدد')}
                        - الأداء: {performance_level}
                        - الهدف: {performance.get('target', 0)} | المحقق: {performance.get('actual', 0)}
                    </li>
                    """
            
            content += """
            </ul>
            
            <h3>📋 المهام المعلقة</h3>
            <p>راجع المهام المعلقة لفريقك في النظام.</p>
            
            <h3>💡 توصيات</h3>
            <p>ركز على الأعضاء الذين يحتاجون دعم إضافي.</p>
            """
            
            return content
            
        except Exception as e:
            logger.error(f"Error building manager digest: {e}")
            return f"خطأ في إنشاء التقرير: {str(e)}"
    
    async def build_executive_digest(self) -> str:
        """إنشاء تقرير أسبوعي للإدارة التنفيذية"""
        try:
            db = await get_db()
            
            # جلب جميع المستخدمين
            users = []
            async for user in db.users.find():
                users.append(user)
            
            if not users:
                return "لا يوجد مستخدمين في النظام"
            
            # تحليل الأداء العام
            total_users = len(users)
            excellent_count = 0
            good_count = 0
            needs_improvement_count = 0
            critical_count = 0
            
            department_performance = {}
            
            for user in users:
                performance = await self.kpi_service.get_user_performance(user["email"])
                
                if "error" not in performance:
                    performance_level = performance.get("performance_level", "no_data")
                    
                    if performance_level == "excellent":
                        excellent_count += 1
                    elif performance_level == "good":
                        good_count += 1
                    elif performance_level == "needs_improvement":
                        needs_improvement_count += 1
                    else:
                        critical_count += 1
                    
                    # تجميع حسب القسم
                    dept = user.get("department", "غير محدد")
                    if dept not in department_performance:
                        department_performance[dept] = {"total": 0, "excellent": 0, "good": 0, "needs_improvement": 0, "critical": 0}
                    
                    department_performance[dept]["total"] += 1
                    department_performance[dept][performance_level] += 1
            
            # بناء التقرير التنفيذي
            content = f"""
            <h2>تقرير أسبوعي تنفيذي - {datetime.now().strftime('%Y-%m-%d')}</h2>
            
            <h3>📈 نظرة عامة على الأداء</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p><strong>إجمالي الموظفين:</strong> {total_users}</p>
                <p><strong>الأداء الممتاز:</strong> {excellent_count} ({excellent_count/total_users*100:.1f}%)</p>
                <p><strong>الأداء الجيد:</strong> {good_count} ({good_count/total_users*100:.1f}%)</p>
                <p><strong>يحتاج تحسين:</strong> {needs_improvement_count} ({needs_improvement_count/total_users*100:.1f}%)</p>
                <p><strong>حرج:</strong> {critical_count} ({critical_count/total_users*100:.1f}%)</p>
            </div>
            
            <h3>🏢 أداء الأقسام</h3>
            """
            
            for dept, stats in department_performance.items():
                content += f"""
                <h4>{dept}</h4>
                <ul>
                    <li>إجمالي الموظفين: {stats['total']}</li>
                    <li>ممتاز: {stats['excellent']}</li>
                    <li>جيد: {stats['good']}</li>
                    <li>يحتاج تحسين: {stats['needs_improvement']}</li>
                    <li>حرج: {stats['critical']}</li>
                </ul>
                """
            
            content += """
            <h3>🎯 توصيات إستراتيجية</h3>
            <ul>
                <li>ركز على الأقسام ذات الأداء الضعيف</li>
                <li>استثمر في تطوير الموظفين المتميزين</li>
                <li>ضع خطط تحسين للأقسام الحرجة</li>
            </ul>
            """
            
            return content
            
        except Exception as e:
            logger.error(f"Error building executive digest: {e}")
            return f"خطأ في إنشاء التقرير التنفيذي: {str(e)}"
