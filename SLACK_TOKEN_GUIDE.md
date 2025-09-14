
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
