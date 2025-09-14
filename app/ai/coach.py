"""CoachAI - مدرب سيادة الذكي"""
from typing import Dict, Any, Optional
from datetime import datetime
import random
from app.ai.base_agent import BaseAgent
from app.ai.prompts.coach_prompts import (
    COACH_AI_SYSTEM_PROMPT, 
    COACH_USER_TEMPLATE,
    PERFORMANCE_TEMPLATES,
    DEPARTMENT_VARIABLES
)
from app.utils.quiet_mode import QuietMode
import structlog

logger = structlog.get_logger()

class CoachAI(BaseAgent):
    """مدرب ذكي متخصص في تحفيز الموظفين"""
    
    def __init__(self):
        super().__init__("coach")
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """جلب الـ prompt الافتراضي من الملف"""
        if prompt_name == "system":
            return COACH_AI_SYSTEM_PROMPT
        elif prompt_name == "user_template":
            return COACH_USER_TEMPLATE
        return ""
    
    def _get_fallback_response(self) -> str:
        """رسالة احتياطية عند فشل OpenAI"""
        return "واصل شغلك الرائع! 🚀 اليوم ركز على هدف واحد واضح"
    
    def _determine_performance_level(self, drift: float) -> str:
        """تحديد مستوى الأداء بناءً على الـ drift"""
        if drift < 0.15:
            return "excellent"
        elif drift < 0.25:
            return "good"
        elif drift < 0.35:
            return "needs_improvement"
        else:
            return "critical"
    
    def _should_send_message(self, performance_level: str, last_message_time: datetime = None) -> bool:
        """تحديد ما إذا كان يجب إرسال رسالة"""
        # لا ترسل للأداء الممتاز
        if performance_level == "excellent":
            return False
        
        # استخدام QuietMode للتحقق من الوقت والتكرار
        return QuietMode.should_send_message(last_message_time)
    
    async def generate_coach_message(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء رسالة تحفيز مخصصة للموظف"""
        try:
            # جلب البيانات المطلوبة
            name = user_data.get("name", "عزيزي الموظف")
            department = user_data.get("department", "عام")
            drift = user_data.get("drift", 0.0)
            summary = user_data.get("summary", "")
            
            # تحديد مستوى الأداء
            performance_level = self._determine_performance_level(drift)
            
            # التحقق من الوقت الحالي
            now = datetime.now()
            
            # تحديد ما إذا كان يجب إرسال الرسالة
            should_send = self._should_send_message(performance_level)
            
            if not should_send:
                return {
                    "message": "",
                    "performance_level": performance_level,
                    "should_send": False
                }
            
            # جلب الـ prompts المرنة
            system_prompt = await self.get_prompt_template("system")
            user_template = await self.get_prompt_template("user_template")
            
            # إعداد المتغيرات
            variables = {
                "name": name,
                "department": department,
                "role": user_data.get("role", "موظف"),
                "performance_level": performance_level,
                "summary": summary,
                "current_time": now.strftime("%H:%M"),
                "current_day": "اليوم"  # مبسط
            }
            
            # تنسيق القالب
            user_prompt = self.format_template(user_template, variables)
            
            # استدعاء OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            ai_response = await self.call_openai(messages)
            
            # إذا فشل AI، استخدم القوالب الجاهزة
            if not ai_response:
                ai_response = self._get_template_message(performance_level, department)
            
            return {
                "message": ai_response,
                "performance_level": performance_level,
                "should_send": True
            }
            
        except Exception as e:
            logger.error(f"Error generating coach message: {e}")
            return {
                "message": self._get_fallback_response(),
                "performance_level": "good",
                "should_send": True
            }
    
    def _get_template_message(self, performance_level: str, department: str) -> str:
        """جلب رسالة من القوالب الجاهزة"""
        templates = PERFORMANCE_TEMPLATES.get(performance_level, PERFORMANCE_TEMPLATES["good"])
        template = random.choice(templates)
        
        # تطبيق متغيرات القسم
        dept_vars = DEPARTMENT_VARIABLES.get(department, DEPARTMENT_VARIABLES["sales"])
        
        try:
            return template.format(**dept_vars)
        except KeyError:
            return template
