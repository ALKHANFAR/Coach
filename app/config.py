"""إعدادات النظام"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # قاعدة البيانات
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "siyadah_ops_ai")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Slack
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    
    # الإيميل
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.mailtrap.io")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    executive_email: str = os.getenv("EXECUTIVE_EMAIL", "a@d10.sa")
    
    # الوقت
    timezone: str = os.getenv("TIMEZONE", "Asia/Riyadh")

settings = Settings()
