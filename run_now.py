#!/usr/bin/env python3
import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.getcwd())

# تشغيل النظام الكامل
if __name__ == "__main__":
    try:
        from main_working import app
        import uvicorn
        
        print("🚀 بدء تشغيل Siyadah Ops AI...")
        print("🌐 النظام متاح على: http://127.0.0.1:8000")
        print("📚 الوثائق متاحة على: http://127.0.0.1:8000/docs")
        print("🔧 تعديل الـ Prompts: http://127.0.0.1:8000/prompts/coach")
        print("\n" + "="*50)
        
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 جاري تشغيل النسخة البسيطة...")
        
        # النسخة البسيطة كبديل
        from test_simple import app
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
