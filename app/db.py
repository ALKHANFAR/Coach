"""اتصال قاعدة البيانات MongoDB"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import structlog

logger = structlog.get_logger()

# عميل MongoDB
client = None
database = None

async def get_db():
    """الحصول على قاعدة البيانات"""
    global database
    if database is None:
        await init_db()
    return database

async def init_db():
    """تهيئة قاعدة البيانات والفهارس"""
    global client, database
    
    try:
        logger.info("🔗 Connecting to MongoDB...")
        
        # إنشاء العميل
        client = AsyncIOMotorClient(settings.mongo_uri)
        database = client[settings.db_name]
        
        # اختبار الاتصال أولاً
        await database.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        
        # إنشاء فهارس أساسية
        try:
            await database.users.create_index("email", unique=True)
            await database.tasks.create_index("assignee_user_id")
            await database.kpis.create_index([("user_id", 1), ("month", 1)])
            await database.ai_prompts.create_index([("agent_type", 1), ("prompt_name", 1)])
            logger.info("✅ Database indexes created successfully")
        except Exception as index_error:
            logger.warning(f"⚠️ Some indexes creation failed: {index_error}")
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # لا نوقف التطبيق إذا فشل MongoDB
        client = None
        database = None
        raise
