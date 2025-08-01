# 🚀 دليل النشر - Bot Factory Maker

## 📋 المنصات المدعومة

### 1. Railway.com
```bash
# 1. رفع المشروع إلى GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. ربط المشروع بـ Railway
# - اذهب إلى railway.app
# - اربط حساب GitHub
# - اختر المشروع
# - أضف المتغيرات البيئية
```

### 2. Render.com
```bash
# 1. رفع المشروع إلى GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. ربط المشروع بـ Render
# - اذهب إلى render.com
# - اربط حساب GitHub
# - اختر "New Web Service"
# - اختر المشروع
# - أضف المتغيرات البيئية
```

### 3. Heroku
```bash
# 1. تثبيت Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. تسجيل الدخول
heroku login

# 3. إنشاء تطبيق جديد
heroku create your-app-name

# 4. إضافة المتغيرات البيئية
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set MONGO_DB_URI=your_mongodb_uri
heroku config:set OWNER_ID=your_owner_id

# 5. رفع المشروع
git push heroku main
```

### 4. Docker
```bash
# 1. بناء الصورة
docker build -t bot-factory .

# 2. تشغيل الحاوية
docker run -d \
  --name bot-factory \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e MONGO_DB_URI=your_mongodb_uri \
  -e OWNER_ID=your_owner_id \
  bot-factory
```

### 5. Docker Compose
```bash
# 1. إنشاء ملف .env
cp .env.example .env
# ثم عدل المتغيرات في ملف .env

# 2. تشغيل المشروع
docker-compose up -d
```

## 🔧 المتغيرات البيئية المطلوبة

| المتغير | الوصف | مطلوب |
|---------|-------|-------|
| `API_ID` | Telegram API ID من my.telegram.org | ✅ |
| `API_HASH` | Telegram API Hash من my.telegram.org | ✅ |
| `BOT_TOKEN` | توكن البوت من @BotFather | ✅ |
| `MONGO_DB_URI` | رابط قاعدة بيانات MongoDB | ✅ |
| `OWNER_ID` | معرف المطور (رقم) | ✅ |
| `CHANNEL` | رابط قناة السورس | ❌ |
| `GROUP` | رابط مجموعة السورس | ❌ |
| `PHOTO` | رابط صورة السورس | ❌ |
| `VIDEO` | رابط فيديو السورس | ❌ |
| `LOGS` | معرف قناة السجلات | ❌ |

## 📁 هيكل الملفات

```
bot-factory/
├── main.py                 # نقطة الدخول الرئيسية
├── config.py              # إعدادات البوت
├── OWNER.py               # معلومات المطور
├── requirements.txt       # متطلبات Python
├── railway.json          # إعدادات Railway
├── render.yaml           # إعدادات Render
├── app.json              # إعدادات Heroku
├── Dockerfile            # إعدادات Docker
├── docker-compose.yml    # إعدادات Docker Compose
├── Procfile              # إعدادات Heroku
├── runtime.txt           # إصدار Python
├── start.sh              # سكريبت التشغيل
├── .env.example          # مثال للمتغيرات البيئية
├── .dockerignore         # استبعاد ملفات Docker
├── Make/                 # قالب البوتات
├── Maked/                # البوتات المنشأة
├── utils/                # الأدوات المساعدة
├── users/                # إدارة المستخدمين
├── db/                   # قاعدة البيانات
├── bots/                 # إدارة البوتات
├── broadcast/            # البث
├── factory/              # إعدادات المصنع
└── handlers/             # معالجات الأوامر
```

## 🚀 خطوات النشر السريع

### Railway.com
1. ارفع المشروع إلى GitHub
2. اربط المشروع بـ Railway
3. أضف المتغيرات البيئية
4. انتظر النشر التلقائي

### Render.com
1. ارفع المشروع إلى GitHub
2. اربط المشروع بـ Render
3. أضف المتغيرات البيئية
4. انتظر النشر التلقائي

### Heroku
1. ارفع المشروع إلى GitHub
2. اربط المشروع بـ Heroku
3. أضف المتغيرات البيئية
4. ارفع المشروع: `git push heroku main`

## 🔍 استكشاف الأخطاء

### مشاكل شائعة:
1. **خطأ في المتغيرات البيئية**: تأكد من صحة جميع المتغيرات
2. **خطأ في قاعدة البيانات**: تأكد من صحة رابط MongoDB
3. **خطأ في التوكن**: تأكد من صحة توكن البوت
4. **خطأ في المكتبات**: تأكد من تحديث requirements.txt

### سجلات الأخطاء:
- **Railway**: اذهب إلى "Deployments" ثم "View Logs"
- **Render**: اذهب إلى "Logs" في لوحة التحكم
- **Heroku**: استخدم `heroku logs --tail`

## 📞 الدعم

إذا واجهت أي مشاكل في النشر، يمكنك:
1. مراجعة سجلات الأخطاء
2. التحقق من المتغيرات البيئية
3. التأكد من صحة الإعدادات
4. التواصل للحصول على المساعدة