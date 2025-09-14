#!/usr/bin/env python3
"""
تشغيل البوت مع إصلاح جميع المشاكل
"""
import os
import sys
import socket
import asyncio
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def find_free_port(start_port=8000, max_port=8020):
    """البحث عن منفذ متاح"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

async def test_mongodb_atlas():
    """اختبار MongoDB Atlas"""
    try:
        from app.db import get_db
        
        db = await get_db()
        
        # اختبار الاتصال مع Atlas
        await db.admin.command('ping')
        print("✅ MongoDB Atlas متصل ويعمل")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas غير متصل: {e}")
        return False

async def test_openai():
    """اختبار OpenAI"""
    try:
        from app.ai.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def _get_default_prompt(self, prompt_name: str) -> str:
                return "أنت مساعد ذكي"
            
            def _get_fallback_response(self) -> str:
                return "رد احتياطي"
        
        agent = TestAgent("test")
        
        # اختبار استدعاء OpenAI
        messages = [{"role": "user", "content": "مرحبا"}]
        response = agent.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50
        )
        
        if response.choices[0].message.content:
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
    print("🚀 بدء تشغيل Siyadah Ops AI مع إصلاح المشاكل...")
    print("=" * 70)
    
    # فحص متغيرات البيئة
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    mongo_uri = os.getenv("MONGO_URI")
    
    if not all([slack_token, openai_key, mongo_uri]):
        print("❌ متغيرات البيئة غير مكتملة!")
        return
    
    print("✅ متغيرات البيئة صحيحة")
    
    # البحث عن منفذ متاح
    port = find_free_port()
    if not port:
        print("❌ لا توجد منافذ متاحة!")
        return
    
    print(f"🌐 بدء تشغيل الخادم على المنفذ {port}...")
    
    # فحص النظام
    async def check_system():
        atlas_ok = await test_mongodb_atlas()
        openai_ok = await test_openai()
        
        if atlas_ok and openai_ok:
            print("✅ جميع الأنظمة تعمل بشكل مثالي!")
            return True
        elif openai_ok:
            print("⚠️ OpenAI يعمل، لكن MongoDB Atlas لا يعمل")
            print("📝 سيتم تشغيل النسخة بدون قاعدة بيانات")
            return False
        else:
            print("❌ معظم الأنظمة لا تعمل")
            return False
    
    # تشغيل الفحص
    try:
        system_ok = asyncio.run(check_system())
        
        if not system_ok:
            # تشغيل النسخة بدون قاعدة بيانات
            print("\n🔄 تشغيل النسخة بدون قاعدة بيانات...")
            print("=" * 70)
            
            try:
                from run_bot_no_db import app
                import uvicorn
                
                print(f"🚀 النظام متاح على: http://127.0.0.1:{port}")
                print(f"📚 الوثائق: http://127.0.0.1:{port}/docs")
                print(f"🔍 فحص الصحة: http://127.0.0.1:{port}/health")
                print(f"📡 Slack Webhook: http://127.0.0.1:{port}/slack/events")
                print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 70)
                
                uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
                
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
                
                print(f"🚀 النظام متاح على: http://127.0.0.1:{port}")
                print(f"📚 الوثائق: http://127.0.0.1:{port}/docs")
                print(f"🔍 فحص الصحة: http://127.0.0.1:{port}/health")
                print(f"📡 Slack Webhook: http://127.0.0.1:{port}/slack/events")
                print("\n💡 اختبر البوت بكتابة: @Siyadah Ops AI مهمة: اختبار")
                print("=" * 70)
                
                uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل النظام: {e}")
                return
                
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    main()
