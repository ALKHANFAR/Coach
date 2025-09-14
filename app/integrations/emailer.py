"""خدمة الإيميل"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import structlog

logger = structlog.get_logger()

class EmailService:
    """خدمة إرسال الإيميلات"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_pass = settings.smtp_pass
    
    async def send_email(self, to: str, subject: str, body: str) -> dict:
        """إرسال إيميل"""
        try:
            # إنشاء الرسالة
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to
            msg['Subject'] = subject
            
            # إضافة المحتوى
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # إرسال الإيميل
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to}")
            return {"sent": True, "recipient": to}
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            # في حالة فشل الإرسال، اطبع المحتوى في اللوغ
            logger.info(f"Email preview for {to}: {body[:200]}...")
            return {
                "sent": False, 
                "preview": body[:200] + "...",
                "error": str(e)
            }
    
    def create_html_template(self, title: str, content: str) -> str:
        """إنشاء قالب HTML للإيميل"""
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                .content {{ line-height: 1.6; color: #555; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>تم إرسال هذا التقرير من نظام سيادة الذكي</p>
                </div>
            </div>
        </body>
        </html>
        """
