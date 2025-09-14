#!/usr/bin/env python3
"""تشغيل النظام الكامل"""
import subprocess
import sys
import os

# تفعيل البيئة الافتراضية وتشغيل النظام
venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
main_file = os.path.join(os.getcwd(), "main_working.py")

if os.path.exists(venv_python) and os.path.exists(main_file):
    print("🚀 بدء تشغيل Siyadah Ops AI...")
    print("🌐 النظام متاح على: http://127.0.0.1:8000")
    print("📚 الوثائق متاحة على: http://127.0.0.1:8000/docs")
    print("🔧 تعديل الـ Prompts: http://127.0.0.1:8000/prompts/coach")
    print("\n" + "="*50)
    
    subprocess.run([venv_python, main_file])
else:
    print("❌ خطأ: لم يتم العثور على الملفات المطلوبة")
    print(f"Python: {venv_python} - {'موجود' if os.path.exists(venv_python) else 'غير موجود'}")
    print(f"Main: {main_file} - {'موجود' if os.path.exists(main_file) else 'غير موجود'}")
