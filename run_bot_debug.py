from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import requests
import socket
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

app = FastAPI()

# إعدادات Slack
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def find_available_port(start_port=8000, max_attempts=100):
    """البحث عن منفذ متاح"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                print(f"✅ تم العثور على منفذ متاح: {port}")
                return port
        except socket.error:
            print(f"❌ المنفذ {port} مستخدم، أبحث عن آخر...")
            continue
    raise RuntimeError("❌ لم يتم العثور على منفذ متاح!")

def send_slack_message(channel, text):
    """إرسال رسالة إلى Slack"""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except requests.RequestException as e:
        print(f"❌ خطأ في إرسال الرسالة: {e}")
        return {"error": str(e)}

@app.post("/slack/events")
async def handle_events(request: Request):
    # Log all incoming requests for debugging
    print(f"📡 Incoming request from: {request.client.host if request.client else 'Unknown'}")
    print(f"📡 Headers: {dict(request.headers)}")
    try:
        body = await request.body()
        data = json.loads(body)
        
        print("📥 تم استلام رسالة من Slack:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # رد على challenge للتحقق
        if "challenge" in data:
            print("✅ تم التحقق من URL بنجاح!")
            return {"challenge": data["challenge"]}
        
        # رد على الرسائل
        if "event" in data:
            event = data["event"]
            
            # تجنب الردود المتكررة من البوت نفسه
            if event.get("bot_id"):
                return {"status": "ignored_bot_message"}
            
            # رد على المنشن
            if event.get("type") == "app_mention":
                print("📱 البوت تم ذكره في رسالة!")
                channel = event.get("channel")
                user_text = event.get("text", "")
                user_id = event.get("user")
                
                # إزالة المنشن من النص
                clean_text = user_text
                if user_id:
                    clean_text = user_text.replace(f"<@{user_id}>", "").strip()
                
                print(f"🔤 النص المنظف: {clean_text}")
                
                # تحليل الرسالة والرد المناسب
                if "مهمة" in clean_text or "task" in clean_text.lower():
                    task_name = clean_text.replace("مهمة:", "").replace("task:", "").strip()
                    reply = f"✅ تم إنشاء مهمة جديدة: **{task_name}**\n\n🎯 تفاصيل المهمة:\n• الحالة: قيد التنفيذ\n• الأولوية: متوسطة\n• سأذكرك بالمتابعة قريباً!\n\n💪 بالتوفيق في تنفيذها!"
                elif "هدف" in clean_text or "goal" in clean_text.lower():
                    goal_name = clean_text.replace("هدف:", "").replace("goal:", "").strip()
                    reply = f"🎯 هدف رائع: **{goal_name}**\n\n📋 خطة التنفيذ المقترحة:\n• **المرحلة 1:** التخطيط والتحضير\n• **المرحلة 2:** البدء في التنفيذ\n• **المرحلة 3:** المراجعة والتطوير\n• **المرحلة 4:** الإنجاز والتقييم\n\n🚀 أنت قادر على تحقيقه! سأساعدك في كل خطوة."
                elif any(greeting in clean_text for greeting in ["مرحبا", "هلا", "السلام", "hello", "hi"]):
                    reply = "مرحباً وأهلاً بك! 👋\n\n**أنا مساعدك الذكي في إدارة المهام والأهداف**\n\n🎯 **يمكنني مساعدتك في:**\n✅ إنشاء وإدارة المهام\n🎯 تفكيك الأهداف الكبيرة\n📊 متابعة التقدم والإنجازات\n💪 التحفيز والدعم المستمر\n📈 تحليل الأداء\n\n**جرب الأمثلة التالية:**\n• `@Siyadah Ops AI مهمة: تطوير التطبيق`\n• `@Siyadah Ops AI هدف: إطلاق منتج جديد`\n\n🚀 أنا هنا لمساعدتك في تحقيق أهدافك!"
                elif "شكرا" in clean_text or "thanks" in clean_text.lower():
                    reply = "العفو! 😊 أنا سعيد لمساعدتك!\n\n🎯 لا تتردد في سؤالي عن أي شيء متعلق بالمهام والأهداف.\n💪 أنا هنا لدعمك دائماً!"
                else:
                    reply = f"📨 استلمت رسالتك: **{clean_text}**\n\n💡 **يمكنك استخدام الأوامر التالية:**\n\n🎯 **للمهام:**\n• `مهمة: وصف المهمة`\n• مثال: `مهمة: إنهاء التقرير الشهري`\n\n🎯 **للأهداف:**\n• `هدف: وصف الهدف`\n• مثال: `هدف: تطوير مهاراتي في البرمجة`\n\n🚀 أنا مستعد لمساعدتك في تحقيق النجاح!"
                
                # إرسال الرد
                result = send_slack_message(channel, reply)
                if "error" not in result:
                    print(f"✅ تم الرد بنجاح: {reply[:50]}...")
                else:
                    print(f"❌ فشل الرد: {result}")
                
            # رد على رسائل DM
            elif event.get("type") == "message" and event.get("channel_type") == "im":
                print("📨 رسالة DM مباشرة!")
                channel = event.get("channel")
                text = event.get("text", "")
                
                reply = f"شكراً لرسالتك المباشرة! 📨\n\n**رسالتك:** {text}\n\n🤝 سأعود إليك قريباً بالتفاصيل والمساعدة\n\n💡 **نصيحة:** يمكنك ذكري في أي قناة بكتابة `@Siyadah Ops AI` متبوعاً بطلبك\n\n🚀 أنا هنا لخدمتك!"
                
                result = send_slack_message(channel, reply)
                if "error" not in result:
                    print(f"✅ تم الرد على DM بنجاح")
                else:
                    print(f"❌ فشل الرد على DM: {result}")
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"❌ خطأ في معالجة الطلب: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "🚀 البوت جاهز ويعمل بكامل طاقته!",
        "slack_token": "✅ متصل" if SLACK_BOT_TOKEN else "❌ غير متصل",
        "features": [
            "استقبال والرد على المنشن",
            "معالجة رسائل DM",
            "إنشاء المهام",
            "تفكيك الأهداف",
            "الردود الذكية"
        ]
    }

@app.get("/")
async def root():
    return {
        "message": "🎯 Siyadah Ops AI - مساعدك الذكي لإدارة المهام",
        "version": "2.0 Enhanced",
        "status": "🚀 جاهز للخدمة!",
        "endpoints": {
            "health": "/health",
            "slack_events": "/slack/events",
            "docs": "/docs"
        }
    }

@app.get("/test-slack")
async def test_slack():
    """اختبار الاتصال مع Slack"""
    if not SLACK_BOT_TOKEN:
        return {"error": "SLACK_BOT_TOKEN غير موجود"}
    
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "✅ الاتصال مع Slack ناجح!",
                "bot_name": result.get("user"),
                "team_name": result.get("team")
            }
        else:
            return {"error": f"❌ خطأ في Slack: {result.get('error')}"}
    
    except Exception as e:
        return {"error": f"❌ فشل الاتصال: {str(e)}"}

if __name__ == "__main__":
    # البحث عن منفذ متاح
    try:
        # قائمة بالمنافذ المفضلة
        preferred_ports = [8003, 8004, 8005, 8010, 8020, 8030, 9000, 9001, 9002, 3001, 3002, 5000, 5001]
        
        available_port = None
        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    available_port = port
                    break
            except socket.error:
                continue
        
        # إذا لم نجد منفذ من القائمة المفضلة، ابحث تلقائياً
        if not available_port:
            available_port = find_available_port(start_port=8100)
        
        print("🚀 بدء تشغيل البوت المحسن مع منفذ ديناميكي...")
        print("=" * 70)
        print(f"🎯 المنفذ المختار: {available_port}")
        print(f"✅ SLACK_BOT_TOKEN: {'✓ موجود' if SLACK_BOT_TOKEN else '✗ مفقود'}")
        print(f"✅ SLACK_SIGNING_SECRET: {'✓ موجود' if SLACK_SIGNING_SECRET else '✗ مفقود'}")
        print("✅ البوت الآن يرد على جميع الرسائل بذكاء!")
        print(f"🌐 النظام متاح على: http://127.0.0.1:{available_port}")
        print(f"📚 الوثائق متاحة على: http://127.0.0.1:{available_port}/docs")  
        print(f"🔍 فحص الصحة: http://127.0.0.1:{available_port}/health")
        print(f"🧪 اختبار Slack: http://127.0.0.1:{available_port}/test-slack")
        print(f"📡 Slack Webhook: http://127.0.0.1:{available_port}/slack/events")
        print("=" * 70)
        print("✅ البوت جاهز لاستقبال الرسائل والرد عليها بذكاء!")
        print("🎯 أمثلة للاختبار:")
        print("   • @Siyadah Ops AI مرحبا")
        print("   • @Siyadah Ops AI مهمة: تطوير التطبيق")
        print("   • @Siyadah Ops AI هدف: إطلاق منتج جديد")
        print("=" * 70)
        print(f"🔗 لربط ngrok استخدم: ngrok http {available_port}")
        
        # تشغيل الخادم
        uvicorn.run(app, host="0.0.0.0", port=available_port, log_level="info")
        
    except Exception as e:
        print(f"❌ خطأ في بدء تشغيل الخادم: {e}")
        print("💡 جرب تشغيل البوت مرة أخرى")
        exit(1)