import os
from os import getenv
from dotenv import load_dotenv

# تحميل متغيرات البيئة أولاً
load_dotenv()

# استيراد البيانات الآمنة من OWNER.py
try:
    from OWNER import (
        BOT_TOKEN, OWNER, OWNER_ID, infophoto, OWNER_NAME, 
        DATABASE, CHANNEL, GROUP, LOGS, PHOTO, VIDEO,
        validate_config
    )
    # التحقق من صحة التكوين
    validate_config()
except ImportError as e:
    raise ImportError(f"❌ خطأ في استيراد الإعدادات من OWNER.py: {e}")
except ValueError as e:
    raise ValueError(f"❌ خطأ في التكوين: {e}")

# =======================================
# إعدادات Telegram API
# =======================================

API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")

# التحقق من وجود API_ID و API_HASH
if not API_ID or not API_HASH:
    raise ValueError("❌ API_ID و API_HASH مطلوبان في متغيرات البيئة")

# =======================================
# إعدادات قاعدة البيانات
# =======================================

MONGO_DB_URL = DATABASE

# =======================================
# إعدادات المالك والمطورين
# =======================================

# تحويل OWNER_ID إلى قائمة إذا لم تكن كذلك
if not isinstance(OWNER_ID, list):
    OWNER_ID = [OWNER_ID]

# =======================================
# إعدادات إضافية
# =======================================

# مدة انتظار العمليات
OPERATION_TIMEOUT = int(getenv("OPERATION_TIMEOUT", "300"))

# وضع التطوير
DEBUG_MODE = getenv("DEBUG_MODE", "false").lower() == "true"

# =======================================
# طباعة معلومات التكوين (للتأكد)
# =======================================

if DEBUG_MODE:
    print("🔧 معلومات التكوين:")
    print(f"   📱 API_ID: {API_ID}")
    print(f"   🔑 API_HASH: {'*' * (len(API_HASH) - 4) + API_HASH[-4:] if API_HASH else 'غير محدد'}")
    print(f"   🤖 BOT_TOKEN: {'*' * 20 + BOT_TOKEN[-10:] if BOT_TOKEN else 'غير محدد'}")
    print(f"   👑 OWNER_ID: {OWNER_ID}")
    print(f"   📊 DATABASE: {'mongodb://*****' if DATABASE else 'غير محدد'}")
    print(f"   📺 CHANNEL: {CHANNEL}")
    print(f"   👥 GROUP: {GROUP}")
    print(f"   📝 LOGS: {LOGS}")
    print("✅ تم تحميل التكوين بنجاح")

# =======================================
# التحقق النهائي من البيانات الحرجة
# =======================================

def final_config_check():
    """التحقق النهائي من جميع البيانات الحرجة"""
    critical_vars = {
        "API_ID": API_ID,
        "API_HASH": API_HASH,
        "BOT_TOKEN": BOT_TOKEN,
        "MONGO_DB_URL": MONGO_DB_URL,
        "OWNER_ID": OWNER_ID
    }
    
    missing_critical = [var for var, value in critical_vars.items() if not value]
    
    if missing_critical:
        error_msg = f"❌ البيانات الحرجة التالية مفقودة:\n" + "\n".join(f"- {var}" for var in missing_critical)
        raise ValueError(error_msg)
    
    return True

# تشغيل التحقق النهائي
final_config_check()
