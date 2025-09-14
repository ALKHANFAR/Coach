"""نظام Quiet Mode - منع الإزعاج خارج ساعات العمل"""
from datetime import datetime
import structlog

logger = structlog.get_logger()

class QuietMode:
    """إدارة الوضع الصامت"""
    
    @staticmethod
    def is_quiet_time() -> bool:
        """التحقق من كون الوقت حالياً ضمن Quiet Mode"""
        now = datetime.now()
        
        # نهاية الأسبوع (الخميس والجمعة)
        if now.weekday() in [3, 4]:  # الخميس=3, الجمعة=4
            return True
        
        # خارج ساعات العمل (9 صباحاً - 6 مساءً KSA)
        if now.hour < 9 or now.hour > 18:
            return True
        
        return False
    
    @staticmethod
    def get_quiet_reason() -> str:
        """الحصول على سبب تفعيل Quiet Mode"""
        now = datetime.now()
        
        if now.weekday() in [3, 4]:
            return "نهاية الأسبوع"
        
        if now.hour < 9:
            return "قبل ساعات العمل"
        
        if now.hour > 18:
            return "بعد ساعات العمل"
        
        return "غير مفعل"
    
    @staticmethod
    def should_send_message(last_message_time: datetime = None) -> bool:
        """التحقق من إمكانية إرسال رسالة"""
        # التحقق من Quiet Mode
        if QuietMode.is_quiet_time():
            logger.info(f"Quiet mode active: {QuietMode.get_quiet_reason()}")
            return False
        
        # التحقق من تكرار الرسائل (4 ساعات)
        if last_message_time:
            time_diff = datetime.now() - last_message_time
            if time_diff.total_seconds() < 4 * 3600:  # 4 ساعات
                logger.info("Message too soon after last message")
                return False
        
        return True
