#!/usr/bin/env python3
"""
اختبار سريع لـ MongoDB Atlas
"""
import os
import asyncio
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

async def test_atlas_connection():
    """اختبار الاتصال مع MongoDB Atlas"""
    print("🔍 اختبار الاتصال مع MongoDB Atlas...")
    
    try:
        from app.db import get_db
        
        db = await get_db()
        
        # اختبار ping
        await db.admin.command('ping')
        print("✅ الاتصال مع MongoDB Atlas ناجح!")
        
        # اختبار إنشاء قاعدة البيانات
        test_doc = {"test": "atlas_connection", "timestamp": "2024-01-01"}
        result = await db.test_collection.insert_one(test_doc)
        print(f"✅ تم إنشاء مستند تجريبي: {result.inserted_id}")
        
        # اختبار البحث
        found_doc = await db.test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ تم العثور على المستند بنجاح")
        
        # اختبار الحذف
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ تم حذف المستند التجريبي")
        
        # اختبار إنشاء فهارس
        await db.test_collection.create_index("test_field")
        print("✅ تم إنشاء فهرس تجريبي")
        
        print("\n🎉 MongoDB Atlas يعمل بشكل مثالي!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في MongoDB Atlas: {e}")
        print("\n📝 حلول محتملة:")
        print("1. تأكد من إضافة IP address في Network Access")
        print("2. تأكد من صحة username/password")
        print("3. تأكد من صحة connection string")
        return False

async def test_openai():
    """اختبار OpenAI"""
    print("\n🔍 اختبار OpenAI...")
    
    try:
        from app.ai.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def _get_default_prompt(self, prompt_name: str) -> str:
                return "أنت مساعد ذكي"
            
            def _get_fallback_response(self) -> str:
                return "رد احتياطي"
        
        agent = TestAgent("test")
        
        # اختبار استدعاء OpenAI
        messages = [
            {"role": "system", "content": "أنت مساعد ذكي"},
            {"role": "user", "content": "اكتب رسالة تحفيز قصيرة للموظفين"}
        ]
        
        response = await agent.call_openai(messages, max_tokens=100)
        
        if response:
            print(f"✅ OpenAI يعمل بشكل مثالي!")
            print(f"📝 الرد: {response}")
            return True
        else:
            print("❌ OpenAI لا يعمل - لا يوجد رد")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في OpenAI: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار MongoDB Atlas و OpenAI")
    print("=" * 50)
    
    # اختبار MongoDB Atlas
    atlas_ok = await test_atlas_connection()
    
    # اختبار OpenAI
    openai_ok = await test_openai()
    
    # النتائج النهائية
    print("\n" + "=" * 50)
    print("📊 نتائج الاختبارات:")
    print("=" * 50)
    
    print(f"MongoDB Atlas: {'✅ نجح' if atlas_ok else '❌ فشل'}")
    print(f"OpenAI: {'✅ نجح' if openai_ok else '❌ فشل'}")
    
    if atlas_ok and openai_ok:
        print("\n🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام!")
        print("\n🚀 للبدء:")
        print("   python run_atlas.py")
    elif atlas_ok:
        print("\n⚠️ MongoDB Atlas يعمل، لكن OpenAI لا يعمل")
        print("📝 تأكد من صحة OPENAI_API_KEY في ملف .env")
    elif openai_ok:
        print("\n⚠️ OpenAI يعمل، لكن MongoDB Atlas لا يعمل")
        print("📝 تأكد من إعدادات MongoDB Atlas")
    else:
        print("\n❌ كلا النظامين لا يعملان")
        print("📝 راجع إعدادات النظام")

if __name__ == "__main__":
    asyncio.run(main())
