import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# =======================================
# إعدادات المالك والمطورين (آمنة)
# =======================================

# قائمة المطورين الأساسيين
OWNER = [os.getenv("OWNER_USERNAME", "AAAKP")]
OWNER_ID = [int(os.getenv("OWNER_ID", "985612253"))]

# اسم المطور
OWNER_NAME = os.getenv("OWNER_NAME", "𝐷𝑟. 𝐾ℎ𝑎𝑦𝑎𝑙 𓏺")

# اسم السورس الذي سيظهر على الصور
infophoto = os.getenv("SOURCE_NAME", "LoL Music")

# =======================================
# البيانات الحساسة (من متغيرات البيئة)
# =======================================

# توكن البوت (يجب أن يكون في متغيرات البيئة)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في متغيرات البيئة! يرجى إضافته في ملف .env")

# رابط قاعدة البيانات (يجب أن يكون في متغيرات البيئة)
DATABASE = os.getenv("MONGO_DB_URL")
if not DATABASE:
    raise ValueError("❌ MONGO_DB_URL غير موجود في متغيرات البيئة! يرجى إضافته في ملف .env")

# =======================================
# روابط السورس والقنوات
# =======================================

# قناة السورس
CHANNEL = os.getenv("CHANNEL", "https://t.me/K55DD")

# كروب السورس
GROUP = os.getenv("GROUP", "https://t.me/YMMYN")

# فيديو السورس
VIDEO = os.getenv("VIDEO", "https://t.me/MusicxXxYousef/91")

# صورة السورس
PHOTO = os.getenv("PHOTO", "https://t.me/MusicxXxYousef/90")

# =======================================
# مجموعة السجلات
# =======================================

# مجموعة السجلات (يوزر أو ID)
LOGS = os.getenv("LOGS", "xjjfjfhh")

# =======================================
# مطورين إضافيين (اختياري)
# =======================================

# إضافة مطورين إضافيين من متغيرات البيئة
additional_devs = os.getenv("ADDITIONAL_DEVS", "")
if additional_devs:
    try:
        additional_dev_ids = [int(dev_id.strip()) for dev_id in additional_devs.split(",") if dev_id.strip()]
        OWNER_ID.extend(additional_dev_ids)
    except ValueError:
        print("⚠️ تحذير: خطأ في تحويل ADDITIONAL_DEVS إلى أرقام")

# =======================================
# التحقق من البيانات المطلوبة
# =======================================

def validate_config():
    """التحقق من وجود جميع البيانات المطلوبة"""
    required_vars = {
        "BOT_TOKEN": BOT_TOKEN,
        "MONGO_DB_URL": DATABASE,
        "OWNER_ID": OWNER_ID[0] if OWNER_ID else None,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        error_msg = f"❌ المتغيرات التالية مفقودة من ملف .env:\n" + "\n".join(f"- {var}" for var in missing_vars)
        raise ValueError(error_msg)
    
    print("✅ تم تحميل جميع الإعدادات بنجاح")
    return True

# تشغيل التحقق عند استيراد الملف
if __name__ != "__main__":
    validate_config()
 
 
