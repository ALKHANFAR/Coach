#!/usr/bin/env python3
"""
تشغيل البوت مع MongoDB - حل كامل ومضمون
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

async def check_mongodb():
    """فحص MongoDB"""
    try:
        from app.db import get_db
        db = await get_db()
        
        # اختبار الاتصال
        await db.admin.command('ping')
        print("✅ MongoDB متصل ويعمل")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB غير متصل: {e}")
        print("📝 تأكد من تشغيل MongoDB:")
        print("   brew services start mongodb-community")
        print("   أو")
        print("   mongod --config /usr/local/etc/mongod.conf")
        return False

async def check_openai():
    """فحص OpenAI"""
    try:
        from app.ai.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def _get_default_prompt(self, prompt_name: str) -> str:
                return "أنت مساعد ذكي"
            
            def _get_fallback_response(self) -> str:
                return "رد احتياطي"
        
        agent = TestAgent("test")
        
        # اختبار سريع
        messages = [{"role": "user", "content": "مرحبا"}]
        response = await agent.call_openai(messages, max_tokens=50)
        
        if response:
            print("✅ OpenAI يعمل")
            return True
        else:
            print("❌ OpenAI لا يعمل")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI لا يعمل: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل Siyadah Ops AI مع MongoDB...")
    print("=" * 60)
    
    # فحص متغيرات البيئة
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not slack_token or not openai_key:
        print("❌ متغيرات البيئة غير مكتملة!")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    
    # فحص MongoDB و OpenAI
    async def check_system():
        mongodb_ok = await check_mongodb()
        openai_ok = await check_openai()
        
        if not mongodb_ok:
            print("\n❌ MongoDB غير متصل!")
            print("📝 حلول MongoDB:")
            print("   1. شغل MongoDB: brew services start mongodb-community")
            print("   2. أو استخدم النسخة بدون قاعدة بيانات: python run_bot_no_db.py")
            return False
        
        if not openai_ok:
            print("\n❌ OpenAI لا يعمل!")
            print("📝 تأكد من صحة OPENAI_API_KEY في ملف .env")
            return False
        
        print("\n✅ جميع الأنظمة تعمل بشكل مثالي!")
        return True
    
    # تشغيل الفحص
    try:
        system_ok = asyncio.run(check_system())
        
        if not system_ok:
            print("\n🔄 جاري تشغيل النسخة بدون قاعدة بيانات...")
            print("=" * 60)
            
            # تشغيل النسخة بدون قاعدة بيانات
            try:
                from run_bot_no_db import app
                import uvicorn
                
                print("🚀 النظام متاح على: http://127.0.0.1:8002")
                print("📡 Slack Webhook: http://127.0.0.1:8002/slack/events")
                print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 60)
                
                uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل النظام: {e}")
                return
        
        else:
            # تشغيل النسخة الكاملة مع MongoDB
            print("\n🚀 تشغيل النسخة الكاملة مع MongoDB...")
            print("=" * 60)
            
            try:
                from app import app
                import uvicorn
                
                print("🚀 النظام متاح على: http://127.0.0.1:8000")
                print("📚 الوثائق: http://127.0.0.1:8000/docs")
                print("🔍 فحص الصحة: http://127.0.0.1:8000/health")
                print("📡 Slack Webhook: http://127.0.0.1:8000/slack/events")
                print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 60)
                
                uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل النظام: {e}")
                return
                
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    main()
