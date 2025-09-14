#!/bin/bash

echo "🚀 بدء تشغيل Siyadah Ops AI..."

# التحقق من وجود ملف البيئة
if [ ! -f ".env" ]; then
    echo "⚠️  ملف .env غير موجود، يتم نسخ من env.example..."
    cp env.example .env
    echo "📝 يرجى ملء ملف .env بالمعلومات المطلوبة"
fi

# تثبيت المتطلبات إذا لم تكن مثبتة
if [ ! -d "venv" ]; then
    echo "📦 إنشاء بيئة افتراضية..."
    python3 -m venv venv
fi

echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo "📥 تثبيت المتطلبات..."
pip install -r requirements.txt

echo "🎯 بدء تشغيل الخادم..."
echo "🌐 النظام متاح على: http://127.0.0.1:8000"
echo "📚 الوثائق متاحة على: http://127.0.0.1:8000/docs"
echo "🔧 تعديل الـ Prompts: http://127.0.0.1:8000/prompts/coach/edit"

uvicorn main:app --reload --host 0.0.0.0 --port 8000
