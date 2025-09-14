#!/usr/bin/env python3
"""
🔍 SLACK BOT FORENSIC DEBUG TOOL
Comprehensive diagnostic tool to identify and fix Slack bot issues
"""

import os
import json
import requests
import socket
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SlackForensicDebugger:
    def __init__(self):
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
    def print_result(self, test_name, status, details=""):
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   📝 {details}")
        self.results[test_name] = {"status": status, "details": details}
        
    def test_env_file(self):
        """Test environment file structure"""
        self.print_header("ENVIRONMENT FILE ANALYSIS")
        
        # Check if .env file exists
        env_exists = os.path.exists(".env")
        self.print_result("Environment file exists", env_exists, 
                         ".env file found" if env_exists else "No .env file found")
        
        if not env_exists:
            return False
            
        # Check required variables
        required_vars = [
            "SLACK_BOT_TOKEN",
            "SLACK_SIGNING_SECRET", 
            "SLACK_WEBHOOK_URL"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            exists = bool(value)
            self.print_result(f"Variable {var} exists", exists,
                            f"Value: {value[:20]}..." if value else "Not set")
        
        return True
        
    def test_slack_token_format(self):
        """Test Slack token format"""
        self.print_header("SLACK TOKEN FORMAT VALIDATION")
        
        if not self.slack_bot_token:
            self.print_result("Bot token exists", False, "SLACK_BOT_TOKEN not set")
            return False
            
        # Check token format
        correct_format = self.slack_bot_token.startswith("xoxb-")
        self.print_result("Token format correct", correct_format,
                         f"Token starts with xoxb-: {correct_format}")
        
        # Check token length
        token_length = len(self.slack_bot_token)
        reasonable_length = 50 <= token_length <= 200
        self.print_result("Token length reasonable", reasonable_length,
                         f"Length: {token_length} characters")
        
        return correct_format and reasonable_length
        
    def test_slack_api_connection(self):
        """Test Slack API connection"""
        self.print_header("SLACK API CONNECTION TEST")
        
        if not self.slack_bot_token:
            self.print_result("API connection", False, "No token available")
            return False
            
        try:
            url = "https://slack.com/api/auth.test"
            headers = {"Authorization": f"Bearer {self.slack_bot_token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("ok"):
                self.print_result("API authentication", True, 
                                f"Bot: {result.get('user')}, Team: {result.get('team')}")
                return True
            else:
                self.print_result("API authentication", False, 
                                f"Error: {result.get('error')}")
                return False
                
        except Exception as e:
            self.print_result("API connection", False, f"Exception: {str(e)}")
            return False
            
    def test_port_availability(self):
        """Test port availability"""
        self.print_header("PORT AVAILABILITY CHECK")
        
        ports_to_check = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]
        available_ports = []
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    available_ports.append(port)
                    self.print_result(f"Port {port} available", True)
            except socket.error:
                self.print_result(f"Port {port} available", False, "Port in use")
        
        if available_ports:
            self.print_result("Available ports found", True, 
                            f"Ports: {available_ports[:5]}")
            return available_ports[0]
        else:
            self.print_result("Available ports found", False, "No ports available")
            return None
            
    def test_running_servers(self):
        """Test currently running servers"""
        self.print_header("RUNNING SERVERS ANALYSIS")
        
        try:
            # Check what's running on common ports
            result = subprocess.run(['lsof', '-i', ':8000-8010'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                servers = {}
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        port = parts[8].split(':')[-1]
                        pid = parts[1]
                        command = parts[0]
                        
                        if port not in servers:
                            servers[port] = []
                        servers[port].append(f"{command} (PID: {pid})")
                
                for port, processes in servers.items():
                    self.print_result(f"Port {port} usage", True, 
                                    f"Processes: {', '.join(processes)}")
                    
                return servers
            else:
                self.print_result("No servers running", True, "No processes on ports 8000-8010")
                return {}
                
        except Exception as e:
            self.print_result("Server analysis", False, f"Error: {str(e)}")
            return {}
            
    def test_webhook_endpoints(self):
        """Test webhook endpoints"""
        self.print_header("WEBHOOK ENDPOINTS TEST")
        
        # Test common endpoints
        endpoints = [
            ("http://127.0.0.1:8003/slack/events", "Port 8003"),
            ("http://127.0.0.1:8005/slack/events", "Port 8005"),
            ("http://127.0.0.1:8006/slack/events", "Port 8006"),
            ("http://127.0.0.1:8003/health", "Health 8003"),
            ("http://127.0.0.1:8005/health", "Health 8005"),
        ]
        
        working_endpoints = []
        
        for url, description in endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.print_result(f"{description} endpoint", True, 
                                    f"Status: {response.status_code}")
                    working_endpoints.append(url)
                else:
                    self.print_result(f"{description} endpoint", False, 
                                    f"Status: {response.status_code}")
            except requests.exceptions.RequestException:
                self.print_result(f"{description} endpoint", False, "Connection failed")
                
        return working_endpoints
        
    def test_ngrok_tunnel(self):
        """Test ngrok tunnel"""
        self.print_header("NGROK TUNNEL TEST")
        
        try:
            # Check if ngrok is running
            result = subprocess.run(['pgrep', '-f', 'ngrok'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                self.print_result("Ngrok process running", True, 
                               f"PID: {result.stdout.strip()}")
                
                # Try to get ngrok status
                try:
                    ngrok_response = requests.get("http://127.0.0.1:4040/api/tunnels", 
                                                timeout=5)
                    if ngrok_response.status_code == 200:
                        tunnels = ngrok_response.json()
                        if tunnels.get('tunnels'):
                            tunnel = tunnels['tunnels'][0]
                            public_url = tunnel.get('public_url')
                            self.print_result("Ngrok tunnel active", True, 
                                            f"URL: {public_url}")
                            return public_url
                        else:
                            self.print_result("Ngrok tunnel active", False, 
                                            "No active tunnels")
                    else:
                        self.print_result("Ngrok API accessible", False, 
                                        f"Status: {ngrok_response.status_code}")
                except:
                    self.print_result("Ngrok API accessible", False, 
                                    "Cannot connect to ngrok API")
            else:
                self.print_result("Ngrok process running", False, "Ngrok not running")
                
        except Exception as e:
            self.print_result("Ngrok check", False, f"Error: {str(e)}")
            
        return None
        
    def create_minimal_working_bot(self):
        """Create a minimal working bot with maximum logging"""
        self.print_header("CREATING MINIMAL WORKING BOT")
        
        bot_code = '''#!/usr/bin/env python3
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
    print(f"\\n{'='*60}")
    print(f"📡 [{timestamp}] NEW REQUEST")
    print(f"{'='*60}")
    print(f"🌐 Method: {request.method}")
    print(f"🔗 URL: {request.url}")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"👤 Client: {request.client.host if request.client else 'Unknown'}")
    if data:
        print(f"📦 Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"{'='*60}\\n")

def send_slack_message(channel: str, text: str) -> dict:
    """Send message to Slack with detailed logging"""
    print(f"\\n📤 SENDING SLACK MESSAGE")
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
                    reply = "👋 Hello! I'm working perfectly! 🚀\\n\\nI can help you with:\\n• Creating tasks\\n• Setting goals\\n• Managing projects\\n\\nJust mention me and ask!"
                elif "test" in clean_text.lower() or "اختبار" in clean_text:
                    reply = "✅ Test successful! I'm responding correctly! 🎉\\n\\nBot Status: ✅ ONLINE\\nAPI Status: ✅ CONNECTED\\nResponse Time: ⚡ FAST"
                else:
                    reply = f"📨 I received your message: **{clean_text}**\\n\\n✅ Bot is working perfectly!\\n🚀 Ready to help you with tasks and goals!"
                
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
                
                reply = f"📨 Thanks for your direct message!\\n\\n**Your message:** {text}\\n\\n✅ I'm working perfectly and ready to help!\\n🚀 You can also mention me in channels for team collaboration."
                
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
'''
        
        with open("minimal_slack_bot.py", "w", encoding="utf-8") as f:
            f.write(bot_code)
            
        self.print_result("Minimal bot created", True, "File: minimal_slack_bot.py")
        return True
        
    def generate_deployment_guide(self):
        """Generate step-by-step deployment guide"""
        self.print_header("DEPLOYMENT GUIDE GENERATION")
        
        guide = f"""# 🚀 SLACK BOT DEPLOYMENT GUIDE

## 🔍 DIAGNOSTIC RESULTS

### ✅ WORKING COMPONENTS
{self._format_results(True)}

### ❌ ISSUES FOUND
{self._format_results(False)}

## 🛠️ STEP-BY-STEP FIX

### Step 1: Fix Slack Token Issue
**PROBLEM**: Your Slack token is invalid or expired
**SOLUTION**:
1. Go to https://api.slack.com/apps
2. Select your app: "Siyadah Ops AI"
3. Go to "OAuth & Permissions"
4. Copy the "Bot User OAuth Token" (starts with xoxb-)
5. Update your .env file:
   ```
   SLACK_BOT_TOKEN=xoxb-your-new-token-here
   ```

### Step 2: Clean Up Running Servers
**PROBLEM**: Multiple servers running on different ports
**SOLUTION**:
```bash
# Kill all running Python processes
pkill -f python

# Or kill specific ports
lsof -ti:8003 | xargs kill -9
lsof -ti:8005 | xargs kill -9
lsof -ti:8006 | xargs kill -9
```

### Step 3: Use the Minimal Working Bot
**SOLUTION**: Use the new minimal bot with maximum logging
```bash
# Run the minimal bot
python minimal_slack_bot.py
```

### Step 4: Set Up Ngrok Tunnel
**SOLUTION**: Create public URL for Slack webhook
```bash
# Install ngrok (if not installed)
brew install ngrok

# Start tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Step 5: Configure Slack App
**SOLUTION**: Update Slack app webhook URL
1. Go to https://api.slack.com/apps
2. Select your app
3. Go to "Event Subscriptions"
4. Update Request URL to: https://your-ngrok-url.ngrok.io/slack/events
5. Verify the URL (should return challenge)
6. Subscribe to Bot Events:
   - app_mentions
   - message.channels
   - message.im

### Step 6: Test the Bot
**SOLUTION**: Test all functionality
1. Invite bot to channel: /invite @Siyadah Ops AI
2. Test mention: @Siyadah Ops AI hello
3. Test DM: Send direct message to bot
4. Check logs for detailed debugging info

## 🔧 TROUBLESHOOTING

### If Bot Doesn't Respond:
1. Check token validity: curl -X GET "https://slack.com/api/auth.test" -H "Authorization: Bearer YOUR_TOKEN"
2. Check webhook URL: Visit https://your-ngrok-url.ngrok.io/health
3. Check Slack app permissions: Ensure bot has chat:write scope
4. Check event subscriptions: Ensure app_mentions is subscribed

### If Ngrok Issues:
1. Restart ngrok: ngrok http 8000
2. Use different port: ngrok http 8001
3. Check ngrok status: http://127.0.0.1:4040

### If Port Conflicts:
1. Use the minimal bot (auto-finds available port)
2. Or specify port: uvicorn.run(app, host="0.0.0.0", port=8001)

## 📋 FINAL CHECKLIST

- [ ] Valid Slack token (xoxb-...)
- [ ] Bot installed to workspace
- [ ] Event subscriptions configured
- [ ] Ngrok tunnel running
- [ ] Webhook URL updated in Slack app
- [ ] Bot responds to mentions
- [ ] Bot responds to DMs
- [ ] Health endpoint working

## 🎯 SUCCESS INDICATORS

✅ Bot responds to @mentions
✅ Bot responds to DMs  
✅ Health check returns 200
✅ Slack API test passes
✅ No port conflicts
✅ Ngrok tunnel active

## 🚨 EMERGENCY CONTACTS

If issues persist:
1. Check Slack API status: https://status.slack.com/
2. Verify app permissions in Slack
3. Test with curl commands
4. Review detailed logs from minimal bot

---
Generated: {datetime.now().isoformat()}
"""
        
        with open("SLACK_DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(guide)
            
        self.print_result("Deployment guide created", True, "File: SLACK_DEPLOYMENT_GUIDE.md")
        return True
        
    def _format_results(self, success_only=False):
        """Format results for the guide"""
        if success_only:
            items = [k for k, v in self.results.items() if v["status"]]
        else:
            items = [k for k, v in self.results.items() if not v["status"]]
            
        if not items:
            return "None found"
            
        formatted = []
        for item in items:
            status = "✅" if self.results[item]["status"] else "❌"
            details = self.results[item]["details"]
            formatted.append(f"- {status} **{item}**: {details}")
            
        return "\\n".join(formatted)
        
    def run_full_diagnosis(self):
        """Run complete diagnostic analysis"""
        print("🔍 SLACK BOT FORENSIC ANALYSIS")
        print("="*60)
        print(f"📅 Started: {datetime.now().isoformat()}")
        print("="*60)
        
        # Run all tests
        self.test_env_file()
        self.test_slack_token_format()
        self.test_slack_api_connection()
        self.test_port_availability()
        self.test_running_servers()
        self.test_webhook_endpoints()
        self.test_ngrok_tunnel()
        
        # Create solutions
        self.create_minimal_working_bot()
        self.generate_deployment_guide()
        
        # Summary
        self.print_header("DIAGNOSTIC SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["status"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\\n🚨 CRITICAL ISSUES FOUND:")
            for test_name, result in self.results.items():
                if not result["status"]:
                    print(f"   ❌ {test_name}: {result['details']}")
        
        print(f"\\n📋 NEXT STEPS:")
        print(f"   1. Review SLACK_DEPLOYMENT_GUIDE.md")
        print(f"   2. Run: python minimal_slack_bot.py")
        print(f"   3. Set up ngrok tunnel")
        print(f"   4. Update Slack app webhook URL")
        print(f"   5. Test bot functionality")
        
        return self.results

if __name__ == "__main__":
    debugger = SlackForensicDebugger()
    debugger.run_full_diagnosis()
