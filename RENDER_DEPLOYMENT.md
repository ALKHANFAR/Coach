# 🚀 دليل النشر على Render

## المتطلبات الأساسية

### 1. متغيرات البيئة المطلوبة
```bash
MONGO_URI=mongodb+srv://USER:PASS@CLUSTER/dbname?retryWrites=true&w=majority
DB_NAME=siyadah_ops_ai
OPENAI_API_KEY=sk-...
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
EXECUTIVE_EMAIL=a@d10.sa
TIMEZONE=Asia/Riyadh
```

### 2. خطوات النشر

1. **إنشاء حساب على Render**
   - اذهب إلى [render.com](https://render.com)
   - سجل حساب جديد

2. **إنشاء Web Service جديد**
   - اختر "New" → "Web Service"
   - اربط حساب GitHub الخاص بك
   - اختر هذا المستودع

3. **إعدادات الخدمة**
   ```
   Name: siyadah-ops-ai
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: (اتركه فارغ)
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **إضافة متغيرات البيئة**
   - اذهب إلى "Environment" tab
   - أضف جميع المتغيرات المطلوبة من القائمة أعلاه

5. **إنشاء قاعدة بيانات MongoDB**
   - اذهب إلى "New" → "MongoDB"
   - اختر الخطة المناسبة
   - انسخ connection string وأضفه إلى `MONGO_URI`

## ✅ التحقق من النشر

بعد النشر، يجب أن ترى:
- ✅ "Build successful"
- ✅ "Deploy successful"
- ✅ الخدمة تعمل على الرابط المقدم

## 🔧 استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في OpenAI**
   ```
   ❌ OpenAI client initialization failed
   ```
   **الحل**: تأكد من صحة `OPENAI_API_KEY`

2. **خطأ في MongoDB**
   ```
   ❌ Database initialization failed
   ```
   **الحل**: تأكد من صحة `MONGO_URI`

3. **خطأ في المنفذ**
   ```
   ❌ Port already in use
   ```
   **الحل**: تأكد من استخدام `$PORT` وليس رقم ثابت

## 📊 مراقبة الأداء

- استخدم "Logs" tab لمراقبة الـ logs
- استخدم "Metrics" tab لمراقبة الأداء
- تأكد من أن الـ logs تظهر الرسائل التالية:
  ```
  🚀 Starting Siyadah Ops AI...
  ✅ Database initialized successfully
  ✅ System initialized successfully
  ```

## 🔄 التحديثات المستقبلية

للتحديث:
1. ادفع التغييرات إلى GitHub
2. Render سيقوم بإعادة النشر تلقائياً
3. راقب الـ logs للتأكد من نجاح التحديث
