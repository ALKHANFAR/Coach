"""Base class لجميع الـ AI agents مع دعم الـ prompts المرنة"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.config import settings
import structlog
import os

logger = structlog.get_logger()

# متغير تعطيل الذكاء الاصطناعي
DISABLE_AI = os.getenv("DISABLE_AI", "false").lower() == "true"

class BaseAgent(ABC):
    """Base class لجميع الـ AI agents مع دعم الـ prompts المرنة"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.client = None
        
        # التحقق من متغير تعطيل الذكاء الاصطناعي
        if DISABLE_AI:
            logger.info(f"⚠️ AI initialization disabled by DISABLE_AI flag for {agent_type}")
            return
        
        try:
            if not settings.openai_api_key:
                logger.warning(f"OpenAI API key not configured for {agent_type}")
                return
                
            # استيراد OpenAI بطريقة آمنة
            try:
                import openai
                # إنشاء عميل OpenAI مع المعاملات الأساسية فقط
                self.client = openai.OpenAI(
                    api_key=settings.openai_api_key
                )
                logger.info(f"OpenAI client initialized successfully for {agent_type}")
            except ImportError:
                logger.error(f"OpenAI package not available for {agent_type}")
            except Exception as import_error:
                logger.error(f"OpenAI import error for {agent_type}: {import_error}")
                # محاولة بديلة مع httpx مباشرة
                try:
                    import httpx
                    self.client = httpx.Client()
                    logger.info(f"Using HTTP client as fallback for {agent_type}")
                except:
                    logger.error(f"No HTTP client available for {agent_type}")
                
        except Exception as e:
            logger.error(f"OpenAI client initialization failed for {agent_type}: {e}")
            self.client = None
    
    async def get_prompt_template(self, prompt_name: str) -> Optional[str]:
        """جلب prompt من قاعدة البيانات أو الملف"""
        from app.db import get_db
        
        # جرب جلب من قاعدة البيانات أولاً
        db = await get_db()
        prompt_doc = await db.ai_prompts.find_one({
            "agent_type": self.agent_type,
            "prompt_name": prompt_name,
            "is_active": True
        })
        
        if prompt_doc:
            return prompt_doc["template"]
        
        # إذا لم توجد، ارجع للملف الافتراضي
        return self._get_default_prompt(prompt_name)
    
    @abstractmethod
    def _get_default_prompt(self, prompt_name: str) -> str:
        """جلب الـ prompt الافتراضي من الملف"""
        pass
    
    async def call_openai(self, messages: list, **kwargs) -> Optional[str]:
        """استدعاء OpenAI مع معالجة الأخطاء"""
        try:
            if not self.client:
                logger.warning(f"OpenAI client not available for {self.agent_type}")
                return self._get_fallback_response()
            
            # التحقق من نوع العميل
            if hasattr(self.client, 'chat'):
                # عميل OpenAI عادي
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=kwargs.get('max_tokens', 200),
                    temperature=kwargs.get('temperature', 0.7)
                )
                
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content.strip()
                else:
                    logger.warning(f"No response content from OpenAI for {self.agent_type}")
                    return self._get_fallback_response()
            else:
                # عميل HTTP بديل - إرجاع رسالة احتياطية
                logger.warning(f"Using fallback response for {self.agent_type} (no OpenAI client)")
                return self._get_fallback_response()
                
        except Exception as e:
            logger.error(f"OpenAI error for {self.agent_type}: {e}")
            return self._get_fallback_response()
    
    @abstractmethod
    def _get_fallback_response(self) -> str:
        """رسالة احتياطية عند فشل OpenAI"""
        pass
    
    def format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """تنسيق القالب مع المتغيرات"""
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable {e} in template")
            return template
