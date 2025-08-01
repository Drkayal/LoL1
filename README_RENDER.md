# 🚀 دليل نشر مصنع البوتات على Render.com

## 📋 المتطلبات المسبقة

1. **حساب على Render.com** - [إنشاء حساب](https://render.com)
2. **مستودع GitHub** يحتوي على الكود
3. **توكن البوت من @BotFather**
4. **API ID و API Hash من my.telegram.org**

## 🔧 خطوات النشر

### **الخطوة 1: ربط المستودع بـ Render**

1. اذهب إلى [Render Dashboard](https://dashboard.render.com)
2. اضغط على **"New +"** ثم اختر **"Web Service"**
3. اختر **"Connect a repository"**
4. اختر مستودع GitHub الخاص بك
5. اختر الفرع (عادة `main`)

### **الخطوة 2: إعداد الخدمة**

1. **اسم الخدمة:** `bot-factory` (أو أي اسم تريده)
2. **نوع الخدمة:** `Worker` (مهم جداً!)
3. **الفرع:** `main`
4. **أمر البناء:** `pip install --upgrade pip && pip install -r requirements-minimal.txt`
5. **أمر التشغيل:** `chmod +x start.sh && ./start.sh`

### **الخطوة 3: إعداد متغيرات البيئة**

أضف المتغيرات التالية في قسم **"Environment Variables"**:

```bash
API_ID=17490746
API_HASH=ed923c3d59d699018e79254c6f8b6671
BOT_TOKEN=8020231543:AAHFLDS8a77eqGA045YZFV8uQjvr34IvWrM
MONGO_DB_URI=mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/bot_factory?retryWrites=true&w=majority&appName=Cluster0
OWNER_ID=985612253
OWNER_NAME=Dr. Khayal
CHANNEL=https://t.me/K55DD
GROUP=https://t.me/YMMYN
PHOTO=https://t.me/MusicxXxYousef/90
VIDEO=https://t.me/MusicxXxYousef/91
LOGS=xjjfjfhh
PYTHON_VERSION=3.11.0
```

### **الخطوة 4: النشر**

1. اضغط على **"Create Web Service"**
2. انتظر حتى يكتمل البناء والتشغيل
3. تحقق من السجلات للتأكد من عدم وجود أخطاء

## ⚠️ ملاحظات مهمة

### **لماذا نستخدم Worker بدلاً من Web Service؟**

- **Web Service** يتطلب فتح منفذ للاستقبال
- **Worker** يعمل في الخلفية بدون الحاجة لمنفذ
- بوتات Telegram لا تحتاج لاستقبال طلبات HTTP

### **مشاكل شائعة وحلولها**

1. **"No open ports detected"**
   - **الحل:** تأكد من استخدام `type: worker` في `render.yaml`

2. **"Build failed"**
   - **الحل:** تحقق من `requirements-minimal.txt` و `Dockerfile`

3. **"Bot not responding"**
   - **الحل:** تحقق من `BOT_TOKEN` و `API_ID` و `API_HASH`

4. **"Database connection failed"**
   - **الحل:** تحقق من `MONGO_DB_URI`

## 📊 مراقبة البوت

### **السجلات (Logs)**
- اذهب إلى صفحة الخدمة في Render
- اضغط على **"Logs"** لمراقبة السجلات

### **الحالة (Status)**
- **Running:** البوت يعمل بشكل طبيعي
- **Failed:** هناك خطأ، تحقق من السجلات
- **Stopped:** البوت متوقف

## 🔄 التحديثات

عند تحديث الكود:

1. ادفع التحديثات إلى GitHub
2. Render سيكتشف التحديثات تلقائياً
3. سيبدأ البناء الجديد
4. سيتم إعادة تشغيل البوت

## 🆘 الدعم

إذا واجهت مشاكل:

1. تحقق من السجلات في Render
2. تأكد من صحة متغيرات البيئة
3. تحقق من اتصال قاعدة البيانات
4. تأكد من صحة توكن البوت

---

**🎉 تهانينا! بوتك يعمل الآن على Render.com**