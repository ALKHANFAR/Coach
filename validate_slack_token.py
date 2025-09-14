#!/usr/bin/env python3
"""
🔑 SLACK TOKEN VALIDATION TOOL
Quick tool to validate and test Slack tokens
"""

import os
import requests
import json
from dotenv import load_dotenv

def validate_slack_token(token=None):
    """Validate a Slack token"""
    if not token:
        load_dotenv()
        token = os.getenv("SLACK_BOT_TOKEN")
    
    if not token:
        print("❌ No token provided")
        return False
    
    print(f"🔑 Testing token: {token[:20]}...")
    
    # Check format
    if not token.startswith("xoxb-"):
        print("❌ Token format incorrect - should start with 'xoxb-'")
        return False
    
    print("✅ Token format correct")
    
    # Test API connection
    try:
        url = "https://slack.com/api/auth.test"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Token is VALID!")
            print(f"   Bot Name: {result.get('user')}")
            print(f"   Team: {result.get('team')}")
            print(f"   Bot ID: {result.get('bot_id')}")
            return True
        else:
            print(f"❌ Token is INVALID: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {str(e)}")
        return False

def test_bot_permissions(token=None):
    """Test bot permissions"""
    if not token:
        load_dotenv()
        token = os.getenv("SLACK_BOT_TOKEN")
    
    if not token:
        print("❌ No token provided")
        return False
    
    print("\n🔍 Testing bot permissions...")
    
    # Test chat.postMessage permission
    try:
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "channel": "#general",  # This will fail if no permission, but that's OK
            "text": "Test message"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print("✅ chat:write permission - OK")
        else:
            error = result.get("error")
            if error == "channel_not_found":
                print("✅ chat:write permission - OK (channel not found is expected)")
            elif error == "not_in_channel":
                print("✅ chat:write permission - OK (not in channel is expected)")
            else:
                print(f"⚠️ chat:write permission - {error}")
                
    except Exception as e:
        print(f"❌ Error testing permissions: {str(e)}")
    
    # Test app_mentions:read permission
    try:
        url = "https://slack.com/api/conversations.list"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print("✅ channels:read permission - OK")
        else:
            print(f"⚠️ channels:read permission - {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing permissions: {str(e)}")

def generate_token_guide():
    """Generate guide for getting a new token"""
    guide = """
# 🔑 HOW TO GET A NEW SLACK TOKEN

## Step 1: Go to Slack API Apps
1. Visit: https://api.slack.com/apps
2. Sign in to your Slack workspace

## Step 2: Select Your App
1. Find "Siyadah Ops AI" in your apps list
2. Click on it to open the app settings

## Step 3: Get Bot Token
1. Go to "OAuth & Permissions" in the left sidebar
2. Look for "Bot User OAuth Token"
3. Copy the token (starts with xoxb-)

## Step 4: Check Permissions
Make sure your bot has these scopes:
- ✅ app_mentions:read
- ✅ chat:write
- ✅ channels:read
- ✅ users:read

## Step 5: Install Bot
1. If not already installed, click "Install to Workspace"
2. Authorize the bot
3. Copy the new token

## Step 6: Update Environment
1. Open your .env file
2. Update SLACK_BOT_TOKEN with the new token
3. Save the file

## Step 7: Test Token
Run: python validate_slack_token.py
"""
    
    with open("SLACK_TOKEN_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("📄 Token guide created: SLACK_TOKEN_GUIDE.md")

if __name__ == "__main__":
    print("🔑 SLACK TOKEN VALIDATION TOOL")
    print("="*50)
    
    # Validate current token
    is_valid = validate_slack_token()
    
    if is_valid:
        test_bot_permissions()
        print("\n🎉 Your token is working perfectly!")
    else:
        print("\n🚨 Your token is invalid or expired!")
        print("📋 Follow these steps to get a new token:")
        generate_token_guide()
        print("\n📄 See SLACK_TOKEN_GUIDE.md for detailed instructions")
    
    print("\n" + "="*50)
