#!/usr/bin/env python3
"""
اختبار شامل للنظام - MongoDB و OpenAI
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

async def test_mongodb():
    """اختبار MongoDB"""
    print("🔍 اختبار MongoDB...")
    
    try:
        from app.db import get_db, init_db
        
        # اختبار الاتصال
        db = await get_db()
        
        # اختبار إنشاء فهرس
        await db.test_collection.create_index("test_field")
        
        # اختبار إدراج بيانات
        test_doc = {"test_field": "test_value", "timestamp": "2024-01-01"}
        result = await db.test_collection.insert_one(test_doc)
        
        # اختبار البحث
        found_doc = await db.test_collection.find_one({"_id": result.inserted_id})
        
        # اختبار الحذف
        await db.test_collection.delete_one({"_id": result.inserted_id})
        
        print("✅ MongoDB يعمل بشكل مثالي!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB لا يعمل: {e}")
        return False

async def test_openai():
    """اختبار OpenAI"""
    print("🔍 اختبار OpenAI...")
    
    try:
        from app.ai.base_agent import BaseAgent
        
        # إنشاء agent تجريبي
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
        print(f"❌ OpenAI لا يعمل: {e}")
        return False

async def test_coach_ai():
    """اختبار CoachAI"""
    print("🔍 اختبار CoachAI...")
    
    try:
        from app.ai.coach import CoachAI
        
        coach = CoachAI()
        
        # بيانات تجريبية
        user_data = {
            "name": "أحمد",
            "department": "sales",
            "drift": 0.3,
            "summary": "أداء جيد لكن يحتاج تحسين"
        }
        
        result = await coach.generate_coach_message(user_data)
        
        if result.get("message"):
            print(f"✅ CoachAI يعمل بشكل مثالي!")
            print(f"📝 الرسالة: {result['message']}")
            return True
        else:
            print("❌ CoachAI لا يعمل - لا يوجد رسالة")
            return False
            
    except Exception as e:
        print(f"❌ CoachAI لا يعمل: {e}")
        return False

async def test_orchestrator_ai():
    """اختبار OrchestratorAI"""
    print("🔍 اختبار OrchestratorAI...")
    
    try:
        from app.ai.orchestrator import OrchestratorAI
        
        orchestrator = OrchestratorAI()
        
        # اختبار تفكيك الهدف
        goal_text = "إطلاق موقع جديد للشركة"
        result = await orchestrator.expand_goal_to_tasks(goal_text)
        
        if result and result.get("tasks"):
            print(f"✅ OrchestratorAI يعمل بشكل مثالي!")
            print(f"📝 المشروع: {result['project_title']}")
            print(f"📋 عدد المهام: {len(result['tasks'])}")
            return True
        else:
            print("❌ OrchestratorAI لا يعمل - لا يوجد مهام")
            return False
            
    except Exception as e:
        print(f"❌ OrchestratorAI لا يعمل: {e}")
        return False

async def test_slack_integration():
    """اختبار تكامل Slack"""
    print("🔍 اختبار تكامل Slack...")
    
    try:
        from app.integrations.slack_bot import app as slack_app
        
        if slack_app:
            print("✅ Slack Bot integration محمل بنجاح!")
            return True
        else:
            print("❌ Slack Bot integration غير محمل")
            return False
            
    except Exception as e:
        print(f"❌ Slack Bot integration لا يعمل: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار شامل لنظام Siyadah Ops AI")
    print("=" * 60)
    
    # قائمة الاختبارات
    tests = [
        ("MongoDB", test_mongodb),
        ("OpenAI", test_openai),
        ("CoachAI", test_coach_ai),
        ("OrchestratorAI", test_orchestrator_ai),
        ("Slack Integration", test_slack_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 اختبار {test_name}...")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
            results[test_name] = False
    
    # عرض النتائج النهائية
    print("\n" + "=" * 60)
    print("📊 نتائج الاختبارات:")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 النتيجة النهائية: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام!")
    elif passed >= 3:
        print("⚠️ معظم الاختبارات نجحت. النظام يعمل بشكل جزئي.")
    else:
        print("❌ معظم الاختبارات فشلت. النظام يحتاج إصلاح.")
    
    return passed == total

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ عام: {e}")
        sys.exit(1)
