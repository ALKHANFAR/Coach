"""OrchestratorAI - منسق المشاريع الذكي"""
import json
from typing import Dict, Any, List
from app.ai.base_agent import BaseAgent
from app.ai.prompts.orchestrator_prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    ORCHESTRATOR_USER_TEMPLATE,
    PROJECT_TEMPLATES
)
import structlog

logger = structlog.get_logger()

class OrchestratorAI(BaseAgent):
    """منسق ذكي متخصص في تفكيك الأهداف إلى مهام"""
    
    def __init__(self):
        super().__init__("orchestrator")
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """جلب الـ prompt الافتراضي من الملف"""
        if prompt_name == "system":
            return ORCHESTRATOR_SYSTEM_PROMPT
        elif prompt_name == "user_template":
            return ORCHESTRATOR_USER_TEMPLATE
        return ""
    
    def _get_fallback_response(self) -> str:
        """رد احتياطي عند فشل OpenAI"""
        return json.dumps({
            "project_title": "مشروع جديد",
            "project_description": "مشروع تم إنشاؤه تلقائياً",
            "estimated_duration": "أسبوعين",
            "tasks": [
                {
                    "id": 1,
                    "title": "تحليل المتطلبات",
                    "description": "تحليل الهدف وتحديد المتطلبات",
                    "department": "general",
                    "suggested_assignee": None,
                    "priority": "high",
                    "estimated_days": 2,
                    "depends_on": None,
                    "deliverables": ["قائمة المتطلبات"]
                }
            ],
            "success_criteria": ["إنجاز الهدف المطلوب"],
            "potential_risks": ["عدم وضوح المتطلبات"],
            "recommended_timeline": "أسبوعين"
        }, ensure_ascii=False)
    
    async def expand_goal_to_tasks(self, goal_text: str, **kwargs) -> Dict[str, Any]:
        """تحويل الهدف إلى مشروع مع مهام مفصلة"""
        try:
            # جلب الـ prompts المرنة
            system_prompt = await self.get_prompt_template("system")
            user_template = await self.get_prompt_template("user_template")
            
            # إعداد المتغيرات
            variables = {
                "goal_text": goal_text,
                "timeline": kwargs.get("timeline", "غير محدد"),
                "available_departments": "مبيعات، تسويق، تقنية، سندس",
                "budget": kwargs.get("budget", "غير محدد"),
                "special_requirements": kwargs.get("special_requirements", "لا توجد")
            }
            
            # تنسيق القالب
            user_prompt = self.format_template(user_template, variables)
            
            # استدعاء OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            ai_response = await self.call_openai(messages, max_tokens=1000)
            
            # محاولة تحليل JSON
            try:
                result = json.loads(ai_response)
                return result
            except json.JSONDecodeError:
                # إذا فشل التحليل، استخدم القوالب الجاهزة
                return self._get_template_based_response(goal_text)
            
        except Exception as e:
            logger.error(f"Error expanding goal to tasks: {e}")
            return self._get_fallback_response()
    
    def _get_template_based_response(self, goal_text: str) -> Dict[str, Any]:
        """استخدام القوالب الجاهزة بناءً على نوع الهدف"""
        goal_lower = goal_text.lower()
        
        # تحديد نوع المشروع
        if any(word in goal_lower for word in ["موقع", "website", "web"]):
            template = PROJECT_TEMPLATES["website_launch"]
        elif any(word in goal_lower for word in ["حملة", "campaign", "تسويق", "marketing"]):
            template = PROJECT_TEMPLATES["marketing_campaign"]
        elif any(word in goal_lower for word in ["مبيعات", "sales", "زيادة", "increase"]):
            template = PROJECT_TEMPLATES["sales_increase"]
        else:
            # قالب عام
            template = {
                "title": "مشروع جديد",
                "common_tasks": [
                    {"title": "تحليل الهدف", "department": "general", "days": 2},
                    {"title": "وضع الخطة", "department": "general", "days": 3},
                    {"title": "التنفيذ", "department": "general", "days": 7},
                    {"title": "المراجعة", "department": "general", "days": 2}
                ]
            }
        
        # تحويل القالب إلى تنسيق JSON المطلوب
        tasks = []
        for i, task in enumerate(template["common_tasks"], 1):
            tasks.append({
                "id": i,
                "title": task["title"],
                "description": f"تنفيذ {task['title']}",
                "department": task["department"],
                "suggested_assignee": None,
                "priority": "medium",
                "estimated_days": task["days"],
                "depends_on": [i-1] if i > 1 else None,
                "deliverables": [f"إنجاز {task['title']}"]
            })
        
        return {
            "project_title": template["title"],
            "project_description": f"مشروع {template['title']} بناءً على الهدف: {goal_text}",
            "estimated_duration": f"{sum(task['days'] for task in template['common_tasks'])} أيام",
            "tasks": tasks,
            "success_criteria": ["إنجاز جميع المهام المطلوبة"],
            "potential_risks": ["عدم وضوح المتطلبات"],
            "recommended_timeline": f"{sum(task['days'] for task in template['common_tasks'])} أيام"
        }
