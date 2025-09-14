#!/bin/bash

# أوامر فحص النظام السريعة

echo "🚀 فحص النظام الأساسي..."
curl -s http://127.0.0.1:8000/healthz | jq .

echo -e "\n📋 اختبار إنشاء مهمة..."
curl -s -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Fix homepage bug","assignee_email":"sahar.n@d10.sa","due_date":"2025-09-20"}' | jq .

echo -e "\n📊 اختبار KPIs..."
curl -s -X POST http://127.0.0.1:8000/kpis/upsert \
  -H "Content-Type: application/json" \
  -d '{"user_email":"amina.br@d10.sa","month":"2025-09","target":10,"actual":6}' | jq .

echo -e "\n🤖 اختبار الكوتش الذكي..."
curl -s -X POST http://127.0.0.1:8000/coach/ping \
  -H "Content-Type: application/json" \
  -d '{"user_email":"amina.br@d10.sa","department":"sales","summary":"أنجزت 6/10"}' | jq .

echo -e "\n📝 عرض الـ Prompts..."
curl -s http://127.0.0.1:8000/prompts/coach | jq .

echo -e "\n🔧 اختبار تعديل Prompt..."
curl -s -X PUT http://127.0.0.1:8000/prompts/coach/system \
  -H "Content-Type: application/json" \
  -d '{"template": "🚀 يلا {name}! أداؤك ممتاز في {department}! استمر على هذا المستوى الرائع! 💪"}' | jq .

echo -e "\n📧 اختبار الـ Digests..."
curl -s -X POST http://127.0.0.1:8000/digests/manager \
  -H "Content-Type: application/json" \
  -d '{"manager_email":"manager@d10.sa"}' | jq .

echo -e "\n💬 اختبار Slack Mock..."
curl -s -X POST http://127.0.0.1:8000/slack/mock \
  -H "Content-Type: application/json" \
  -d '{"text":"مهمة: إصلاح خطأ في النظام","user":"test_user"}' | jq .

echo -e "\n🎯 اختبار تفكيك الهدف..."
curl -s -X POST http://127.0.0.1:8000/slack/mock \
  -H "Content-Type: application/json" \
  -d '{"text":"هدف: إطلاق موقع جديد للشركة","user":"test_user"}' | jq .

echo -e "\n✅ انتهت جميع الاختبارات!"
