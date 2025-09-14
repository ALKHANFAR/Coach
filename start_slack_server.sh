#!/bin/bash

echo "🚀 بدء تشغيل خادم Slack Webhook"
echo "=================================="

# التحقق من وجود ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok غير مثبت"
    echo "📥 تثبيت ngrok: brew install ngrok"
    exit 1
fi

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    exit 1
fi

echo "✅ جميع المتطلبات متوفرة"
echo ""

# تشغيل الخادم في الخلفية
echo "🖥️  تشغيل خادم Slack Webhook..."
python3 slack_webhook_server.py &
SERVER_PID=$!

# انتظار قليل لبدء الخادم
sleep 3

# تشغيل ngrok
echo "🌐 تشغيل ngrok..."
ngrok http 8000 &
NGROK_PID=$!

# انتظار قليل لبدء ngrok
sleep 5

echo ""
echo "🎉 تم تشغيل الخادم بنجاح!"
echo "📡 الخادم المحلي: http://127.0.0.1:8000"
echo "🌐 ngrok URL: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
echo "📋 الخطوات التالية:"
echo "1. اذهب إلى: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "2. انسخ ngrok URL (مثل: https://abc123.ngrok.io)"
echo "3. أضف URL إلى Slack Event Subscriptions"
echo "4. أضف /slack/events في نهاية URL"
echo ""
echo "🔍 لمراقبة السجلات:"
echo "tail -f logs/slack.log"
echo ""
echo "⏹️  لإيقاف الخادم: اضغط Ctrl+C"

# انتظار إشارة الإيقاف
trap "echo '🛑 إيقاف الخادم...'; kill $SERVER_PID $NGROK_PID; exit" INT

# انتظار
wait
