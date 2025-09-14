# 📦 Siyadah Ops AI - نظام إدارة العمليات الذكي

نظام إدارة العمليات الذكي لشركة د10 للتسويق الرقمي، مع مرونة كاملة في تعديل سلوك الـ AI بدون الحاجة للكود.

## 🚀 المميزات الرئيسية

- **🤖 AI Prompts مرنة**: تعديل سلوك الـ AI من واجهة بسيطة
- **👨‍💼 CoachAI**: مدرب ذكي لتحفيز الموظفين حسب الأداء
- **📊 إدارة KPIs**: تتبع الأداء وحساب الـ drift تلقائياً
- **📋 إدارة المهام**: إنشاء ومتابعة المهام من مصادر متعددة
- **📧 Digests ذكية**: تقارير يومية وأسبوعية للمدراء
- **🔗 تكامل Slack**: استقبال الأوامر وتحويلها لمهام/مشاريع

## 🛠️ التثبيت والتشغيل

### الطريقة السريعة
```bash
./start.sh
```

### الطريقة اليدوية
```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. إعداد البيئة
cp env.example .env
# املأ ملف .env بالمعلومات المطلوبة

# 3. تشغيل النظام
uvicorn main:app --reload

# 4. فحص النظام
curl http://127.0.0.1:8000/healthz
```

### فحص شامل للنظام
```bash
./run_tests.sh
```

## 📡 API Endpoints الأساسية

### المهام
- `POST /tasks` - إنشاء مهمة جديدة
- `GET /tasks?assignee_email=...` - جلب المهام

### KPIs
- `POST /kpis/upsert` - تحديث أو إنشاء KPI

### الكوتش الذكي
- `POST /coach/ping` - الحصول على رسالة تحفيز

### KPIs
- `POST /kpis/upsert` - تحديث أو إنشاء KPI
- `GET /kpis/performance/{user_email}` - جلب أداء المستخدم

### التقارير والإيميل
- `POST /digests/manager` - إرسال تقرير يومي للمدير
- `POST /digests/executive` - إرسال تقرير أسبوعي تنفيذي

### تكامل Slack
- `POST /slack/events` - webhook لأحداث Slack
- `POST /slack/mock` - اختبار رسائل Slack بدون token

### إدارة الـ Prompts (الأهم!)
- `GET /prompts/{agent_type}` - عرض جميع prompts
- `PUT /prompts/{agent_type}/{prompt_name}` - تحديث prompt
- `GET /prompts/{agent_type}/edit` - واجهة تعديل بسيطة
- `GET /prompts/templates` - القوالب الجاهزة

## 🎯 مثال على تعديل الـ Prompts

### تغيير أسلوب الكوتش:
```bash
curl -X PUT http://127.0.0.1:8000/prompts/coach/system \
  -H "Content-Type: application/json" \
  -d '{"template": "🚀 يلا {name}! أداؤك ممتاز في {department}! استمر على هذا المستوى الرائع! 💪"}'
```

### اختبار الـ Prompt الجديد:
```bash
curl -X POST http://127.0.0.1:8000/coach/ping \
  -H "Content-Type: application/json" \
  -d '{"user_email":"test@d10.sa","department":"sales","summary":"أداء ممتاز"}'
```

## 🧪 اختبارات سريعة

### اختبار KPIs والكوتش:
```bash
# إضافة KPI للمستخدم
curl -X POST http://127.0.0.1:8000/kpis/upsert \
  -H "Content-Type: application/json" \
  -d '{"user_email":"amina.br@d10.sa","month":"2025-09","target":10,"actual":6}'

# الحصول على رسالة تحفيز
curl -X POST http://127.0.0.1:8000/coach/ping \
  -H "Content-Type: application/json" \
  -d '{"user_email":"amina.br@d10.sa","department":"sales","summary":"أنجزت 6/10"}'
```

### اختبار Slack Mock:
```bash
# إنشاء مهمة من Slack
curl -X POST http://127.0.0.1:8000/slack/mock \
  -H "Content-Type: application/json" \
  -d '{"text":"مهمة: إصلاح خطأ في النظام","user":"test_user"}'

# تفكيك هدف إلى مشروع
curl -X POST http://127.0.0.1:8000/slack/mock \
  -H "Content-Type: application/json" \
  -d '{"text":"هدف: إطلاق موقع جديد للشركة","user":"test_user"}'
```

### اختبار التقارير:
```bash
# تقرير مدير
curl -X POST http://127.0.0.1:8000/digests/manager \
  -H "Content-Type: application/json" \
  -d '{"manager_email":"manager@d10.sa"}'

# تقرير تنفيذي
curl -X POST http://127.0.0.1:8000/digests/executive \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🏗️ هيكل المشروع

```
siyadah_ops_ai/
├── app/
│   ├── ai/
│   │   ├── prompts/          # الـ prompts المرنة
│   │   │   ├── coach_prompts.py
│   │   │   └── orchestrator_prompts.py
│   │   ├── base_agent.py
│   │   └── coach.py
│   ├── routers/
│   │   ├── health.py
│   │   ├── tasks.py
│   │   └── prompts.py        # إدارة الـ prompts
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   └── schemas.py
├── main.py
├── requirements.txt
└── README.md
```

## 🔧 التخصيص السريع

### تعديل رسائل الكوتش:
1. اذهب إلى `/prompts/coach/edit`
2. عدل القالب حسب الحاجة
3. احفظ التغييرات
4. التغيير يطبق فوراً!

### المتغيرات المتاحة:
- `{name}` - اسم الموظف
- `{department}` - القسم
- `{performance_level}` - مستوى الأداء
- `{focus_area}` - المجال المطلوب التركيز عليه

## 📊 Business Rules

- **Quiet Mode**: لا إزعاج خارج ساعات العمل (9-18 KSA)
- **نهاية الأسبوع**: لا رسائل في الخميس والجمعة
- **حد الرسائل**: رسالة واحدة يومياً لكل موظف
- **تصعيد**: للمدير بعد 3 أيام من الأداء الضعيف

## 🚨 ملاحظات مهمة

- تأكد من ملء جميع المتغيرات في ملف `.env`
- الـ prompts محفوظة في قاعدة البيانات مع نسخ احتياطية
- النظام يدعم fallback responses عند فشل OpenAI
- جميع العمليات مسجلة بـ structlog

## 📞 الدعم

للمساعدة أو الاستفسارات، تواصل مع فريق التطوير.
