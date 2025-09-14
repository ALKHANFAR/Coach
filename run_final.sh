#!/bin/bash
echo "🚀 بدء تشغيل Siyadah Ops AI - النسخة النهائية..."
echo "🌐 النظام متاح على: http://127.0.0.1:8000"
echo "📚 الوثائق متاحة على: http://127.0.0.1:8000/docs"
echo "🔧 تعديل الـ Prompts: http://127.0.0.1:8000/prompts/coach/edit"
echo ""
echo "="*50
echo ""

source venv/bin/activate
python main_final.py
