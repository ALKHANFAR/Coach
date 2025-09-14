"""اختبار Slack endpoint بسيط"""
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/slack/events")
async def slack_events(request: Request):
    """معالجة أحداث Slack"""
    try:
        # الحصول على البيانات من الطلب
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        # التحقق من نوع الطلب
        if data.get("type") == "url_verification":
            # إرجاع قيمة challenge للتحقق من URL
            challenge = data.get("challenge")
            print(f"Slack URL verification challenge: {challenge}")
            return {"challenge": challenge}
        
        # معالجة الأحداث الأخرى
        print(f"Slack event received: {data}")
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        print("Invalid JSON in Slack request")
        return {"error": "Invalid JSON"}
    except Exception as e:
        print(f"Error handling Slack request: {e}")
        return {"error": "Internal server error"}

@app.get("/")
async def root():
    return {"message": "Slack test server is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 بدء تشغيل Slack test server...")
    print("🌐 النظام متاح على: http://127.0.0.1:8000")
    print("📡 Slack endpoint: http://127.0.0.1:8000/slack/events")
    uvicorn.run(app, host="127.0.0.1", port=8001)
