from fastapi import APIRouter, Request, BackgroundTasks
from starlette.responses import JSONResponse
import os
from slack_sdk import WebClient

router = APIRouter(prefix="/slack", tags=["slack"])

@router.post("/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    # URL Verification
    if body.get("type") == "url_verification":
        return JSONResponse({"challenge": body.get("challenge")}, status_code=200)

    # ACK fast (≤3s). Real work in background.
    background_tasks.add_task(process_event_safely, body)
    return JSONResponse({"ok": True}, status_code=200)

def process_event_safely(body: dict):
    try:
        event = (body or {}).get("event", {}) or {}
        etype = event.get("type")
        channel = event.get("channel")
        user = event.get("user")
        text = (event.get("text") or "").strip()

        # Ignore bot messages or missing channel
        if event.get("bot_id") or not channel:
            return

        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            return
        client = WebClient(token=token)

        # Reply on app mentions and DMs
        if etype in ("app_mention", "message", "message.im"):
            reply = "أنا جاهز ✅ — اكتب: `مهمة: ...` أو `هدف: ...`"
            client.chat_postMessage(channel=channel, text=reply)
    except Exception:
        return

@router.get("/status")
def slack_status():
    return {"ok": True}