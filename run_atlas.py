#!/usr/bin/env python3
"""
تشغيل البوت مع MongoDB Atlas - حل كامل ومضمون
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

async def check_mongodb_atlas():
    """فحص MongoDB Atlas"""
    try:
        from app.db import get_db
        
        db = await get_db()
        
        # اختبار الاتصال مع Atlas
        await db.admin.command('ping')
        print("✅ MongoDB Atlas متصل ويعمل")
        
        # اختبار إنشاء قاعدة البيانات
        await db.test_collection.insert_one({"test": "connection"})
        await db.test_collection.delete_many({"test": "connection"})
        
        print("✅ قاعدة البيانات جاهزة للاستخدام")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas غير متصل: {e}")
        print("📝 تأكد من:")
        print("   1. صحة الـ connection string")
        print("   2. إضافة IP address في Network Access")
        print("   3. صحة username/password")
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

async def test_full_system():
    """اختبار النظام الكامل"""
    print("🔍 اختبار النظام الكامل...")
    
    try:
        # اختبار CoachAI
        from app.ai.coach import CoachAI
        coach = CoachAI()
        
        user_data = {
            "name": "أحمد",
            "department": "sales",
            "drift": 0.3,
            "summary": "أداء جيد"
        }
        
        result = await coach.generate_coach_message(user_data)
        if result.get("message"):
            print("✅ CoachAI يعمل")
        else:
            print("❌ CoachAI لا يعمل")
            return False
        
        # اختبار OrchestratorAI
        from app.ai.orchestrator import OrchestratorAI
        orchestrator = OrchestratorAI()
        
        project = await orchestrator.expand_goal_to_tasks("إطلاق موقع جديد")
        if project and project.get("tasks"):
            print("✅ OrchestratorAI يعمل")
        else:
            print("❌ OrchestratorAI لا يعمل")
            return False
        
        print("✅ جميع الـ AI agents تعمل بشكل مثالي!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النظام: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل Siyadah Ops AI مع MongoDB Atlas...")
    print("=" * 70)
    
    # فحص متغيرات البيئة
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    mongo_uri = os.getenv("MONGO_URI")
    
    if not all([slack_token, openai_key, mongo_uri]):
        print("❌ متغيرات البيئة غير مكتملة!")
        print("📝 تأكد من إعداد ملف .env")
        return
    
    if not slack_token.startswith("xoxb-"):
        print("❌ SLACK_BOT_TOKEN غير صحيح!")
        return
    
    if not mongo_uri.startswith("mongodb+srv://"):
        print("❌ MONGO_URI غير صحيح!")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    print(f"🌐 MongoDB Atlas: {mongo_uri[:20]}...")
    
    # فحص النظام
    async def check_system():
        atlas_ok = await check_mongodb_atlas()
        openai_ok = await check_openai()
        
        if not atlas_ok:
            print("\n❌ MongoDB Atlas غير متصل!")
            print("📝 حلول MongoDB Atlas:")
            print("   1. تأكد من إضافة IP address في Network Access")
            print("   2. تأكد من صحة username/password")
            print("   3. أو استخدم النسخة بدون قاعدة بيانات: python run_bot_no_db.py")
            return False
        
        if not openai_ok:
            print("\n❌ OpenAI لا يعمل!")
            print("📝 تأكد من صحة OPENAI_API_KEY في ملف .env")
            return False
        
        # اختبار النظام الكامل
        system_ok = await test_full_system()
        
        if system_ok:
            print("\n🎉 جميع الأنظمة تعمل بشكل مثالي!")
            return True
        else:
            print("\n⚠️ بعض الأنظمة لا تعمل بشكل مثالي")
            return False
    
    # تشغيل الفحص
    try:
        system_ok = asyncio.run(check_system())
        
        if not system_ok:
            print("\n🔄 جاري تشغيل النسخة بدون قاعدة بيانات...")
            print("=" * 70)
            
            # تشغيل النسخة بدون قاعدة بيانات
            try:
                from run_bot_no_db import app
                import uvicorn
                
                print("🚀 النظام متاح على: http://127.0.0.1:8002")
                print("📡 Slack Webhook: http://127.0.0.1:8002/slack/events")
                print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 70)
                
                uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل النظام: {e}")
                return
        
        else:
            # تشغيل النسخة الكاملة مع MongoDB Atlas
            print("\n🚀 تشغيل النسخة الكاملة مع MongoDB Atlas...")
            print("=" * 70)
            
            try:
                from app import app
                import uvicorn
                
                print("🚀 النظام متاح على: http://127.0.0.1:8000")
                print("📚 الوثائق: http://127.0.0.1:8000/docs")
                print("🔍 فحص الصحة: http://127.0.0.1:8000/health")
                print("📡 Slack Webhook: http://127.0.0.1:8000/slack/events")
                print("💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 70)
                
                uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل النظام: {e}")
                return
                
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    main()
