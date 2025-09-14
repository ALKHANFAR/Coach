# 🚀 SLACK BOT DEPLOYMENT GUIDE

## 🔍 DIAGNOSTIC RESULTS

### ✅ WORKING COMPONENTS
- ✅ **Environment file exists**: .env file found\n- ✅ **Variable SLACK_BOT_TOKEN exists**: Value: xoxb-your-bot-token-...\n- ✅ **Variable SLACK_SIGNING_SECRET exists**: Value: 75b9f7acae0c4cfd3274...\n- ✅ **Variable SLACK_WEBHOOK_URL exists**: Value: https://webhook.site...\n- ✅ **Token format correct**: Token starts with xoxb-: True\n- ✅ **Port 8000 available**: \n- ✅ **Port 8002 available**: \n- ✅ **Port 8004 available**: \n- ✅ **Port 8007 available**: \n- ✅ **Port 8008 available**: \n- ✅ **Port 8009 available**: \n- ✅ **Port 8010 available**: \n- ✅ **Available ports found**: Ports: [8000, 8002, 8004, 8007, 8008]\n- ✅ **Port 8003 usage**: Processes: Python (PID: 47994)\n- ✅ **Port 8005 usage**: Processes: Python (PID: 51354), Python (PID: 55852), Python (PID: 55852)\n- ✅ **Port 8006 usage**: Processes: Python (PID: 53794), Python (PID: 55853), Python (PID: 55853)\n- ✅ **Port vcom-tunnel usage**: Processes: Python (PID: 64149)\n- ✅ **Health 8003 endpoint**: Status: 200\n- ✅ **Health 8005 endpoint**: Status: 200\n- ✅ **Ngrok process running**: PID: 54864\n- ✅ **Ngrok tunnel active**: URL: https://af1b4441cdf6.ngrok-free.app\n- ✅ **Minimal bot created**: File: minimal_slack_bot.py

### ❌ ISSUES FOUND
- ❌ **Token length reasonable**: Length: 24 characters\n- ❌ **API authentication**: Error: invalid_auth\n- ❌ **Port 8001 available**: Port in use\n- ❌ **Port 8003 available**: Port in use\n- ❌ **Port 8005 available**: Port in use\n- ❌ **Port 8006 available**: Port in use\n- ❌ **Port 8003 endpoint**: Status: 405\n- ❌ **Port 8005 endpoint**: Status: 405\n- ❌ **Port 8006 endpoint**: Status: 405

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
Generated: 2025-09-14T00:41:02.410353
