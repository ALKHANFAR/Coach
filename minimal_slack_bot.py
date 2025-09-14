#!/usr/bin/env python3
"""
🚀 MINIMAL SLACK BOT WITH MAXIMUM LOGGING
Bulletproof Slack bot implementation
"""

import os
import json
import requests
import socket
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Minimal Slack Bot", version="1.0.0")

# Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def log_request(request: Request, data: dict = None):
    """Log all incoming requests"""
    timestamp = datetime.now().isoformat()
    print(f"\n{'='*60}")
    print(f"📡 [{timestamp}] NEW REQUEST")
    print(f"{'='*60}")
    print(f"🌐 Method: {request.method}")
    print(f"🔗 URL: {request.url}")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"👤 Client: {request.client.host if request.client else 'Unknown'}")
    if data:
        print(f"📦 Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"{'='*60}\n")

def send_slack_message(channel: str, text: str) -> dict:
    """Send message to Slack with detailed logging"""
    print(f"\n📤 SENDING SLACK MESSAGE")
    print(f"📺 Channel: {channel}")
    print(f"💬 Text: {text}")
    
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
        print(f"🔗 URL: {url}")
        print(f"📋 Headers: {headers}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Body: {json.dumps(result, indent=2)}")
        
        if result.get("ok"):
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Slack API Error: {result.get('error')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Exception sending message: {str(e)}")
        return {"error": str(e)}

@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events with maximum logging"""
    try:
        # Get request body
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        # Log the request
        log_request(request, data)
        
        # Handle URL verification challenge
        if data.get("type") == "url_verification":
            challenge = data.get("challenge")
            print(f"✅ URL VERIFICATION CHALLENGE: {challenge}")
            return {"challenge": challenge}
        
        # Handle events
        if "event" in data:
            event = data["event"]
            event_type = event.get("type")
            
            print(f"🎯 EVENT TYPE: {event_type}")
            print(f"📋 FULL EVENT: {json.dumps(event, indent=2, ensure_ascii=False)}")
            
            # Skip bot messages to avoid loops
            if event.get("bot_id"):
                print("🤖 Skipping bot message to avoid loops")
                return {"status": "ignored_bot_message"}
            
            # Handle app mentions
            if event_type == "app_mention":
                print("📱 APP MENTION DETECTED!")
                
                channel = event.get("channel")
                text = event.get("text", "")
                user_id = event.get("user")
                
                print(f"📺 Channel: {channel}")
                print(f"👤 User: {user_id}")
                print(f"💬 Text: {text}")
                
                # Clean the text (remove mention)
                clean_text = text
                if user_id:
                    clean_text = text.replace(f"<@{user_id}>", "").strip()
                
                print(f"🧹 Clean text: {clean_text}")
                
                # Generate response
                if "hello" in clean_text.lower() or "مرحبا" in clean_text:
                    reply = "👋 Hello! I'm working perfectly! 🚀\n\nI can help you with:\n• Creating tasks\n• Setting goals\n• Managing projects\n\nJust mention me and ask!"
                elif "test" in clean_text.lower() or "اختبار" in clean_text:
                    reply = "✅ Test successful! I'm responding correctly! 🎉\n\nBot Status: ✅ ONLINE\nAPI Status: ✅ CONNECTED\nResponse Time: ⚡ FAST"
                else:
                    reply = f"📨 I received your message: **{clean_text}**\n\n✅ Bot is working perfectly!\n🚀 Ready to help you with tasks and goals!"
                
                # Send response
                result = send_slack_message(channel, reply)
                
                if result.get("ok"):
                    print("✅ Response sent successfully!")
                    return {"status": "message_sent"}
                else:
                    print(f"❌ Failed to send response: {result}")
                    return {"status": "send_failed", "error": result.get("error")}
            
            # Handle direct messages
            elif event_type == "message" and event.get("channel_type") == "im":
                print("📨 DIRECT MESSAGE DETECTED!")
                
                channel = event.get("channel")
                text = event.get("text", "")
                
                reply = f"📨 Thanks for your direct message!\n\n**Your message:** {text}\n\n✅ I'm working perfectly and ready to help!\n🚀 You can also mention me in channels for team collaboration."
                
                result = send_slack_message(channel, reply)
                
                if result.get("ok"):
                    print("✅ DM response sent successfully!")
                    return {"status": "dm_sent"}
                else:
                    print(f"❌ Failed to send DM: {result}")
                    return {"status": "dm_failed", "error": result.get("error")}
        
        print("✅ Event processed successfully")
        return {"status": "ok"}
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON DECODE ERROR: {str(e)}")
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
    except Exception as e:
        print(f"❌ GENERAL ERROR: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "slack_token": "✅ configured" if SLACK_BOT_TOKEN else "❌ missing",
        "signing_secret": "✅ configured" if SLACK_SIGNING_SECRET else "❌ missing",
        "message": "🚀 Minimal Slack Bot is running perfectly!"
    }

@app.get("/test-slack")
async def test_slack():
    """Test Slack API connection"""
    if not SLACK_BOT_TOKEN:
        return {"error": "SLACK_BOT_TOKEN not configured"}
    
    try:
        url = "https://slack.com/api/auth.test"
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "✅ SUCCESS",
                "bot_name": result.get("user"),
                "team_name": result.get("team"),
                "bot_id": result.get("bot_id"),
                "message": "Slack API connection is working perfectly!"
            }
        else:
            return {
                "status": "❌ FAILED",
                "error": result.get("error"),
                "message": "Slack API connection failed"
            }
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "error": str(e),
            "message": "Exception occurred while testing Slack API"
        }

def find_available_port(start_port=8000):
    """Find an available port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except socket.error:
            continue
    raise RuntimeError("No available port found")

if __name__ == "__main__":
    print("🚀 STARTING MINIMAL SLACK BOT")
    print("="*60)
    
    # Check configuration
    if not SLACK_BOT_TOKEN:
        print("❌ ERROR: SLACK_BOT_TOKEN not found in environment")
        print("📝 Please add SLACK_BOT_TOKEN to your .env file")
        exit(1)
    
    if not SLACK_BOT_TOKEN.startswith("xoxb-"):
        print("❌ ERROR: SLACK_BOT_TOKEN format is incorrect")
        print("📝 Token should start with 'xoxb-'")
        exit(1)
    
    # Find available port
    port = find_available_port(8000)
    
    print(f"✅ Configuration: OK")
    print(f"🔑 Token: {SLACK_BOT_TOKEN[:20]}...")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: http://127.0.0.1:{port}")
    print(f"📡 Webhook: http://127.0.0.1:{port}/slack/events")
    print(f"🏥 Health: http://127.0.0.1:{port}/health")
    print(f"🧪 Test: http://127.0.0.1:{port}/test-slack")
    print("="*60)
    print("🚀 Bot is ready! Waiting for Slack events...")
    print("💡 Test with: @YourBot hello")
    print("="*60)
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
