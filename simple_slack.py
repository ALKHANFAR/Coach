from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    data = json.loads(body.decode('utf-8'))
    
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Slack server running on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8002)
