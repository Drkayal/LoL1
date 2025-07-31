# AnonXMusic Bot - Simplified Version for Generated Bots
import os
import sys
from pyrogram import Client

# إضافة المسار الحالي والمسار الرئيسي إلى sys.path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# استيراد التكوين
try:
    from config import API_ID, API_HASH, BOT_TOKEN, STRING1, OWNER_ID, LOGGER_ID
except ImportError as e:
    print(f"خطأ في استيراد التكوين: {e}")
    # في حالة عدم وجود config.py، استخدم القيم الافتراضية
    API_ID = 17490746
    API_HASH = "ed923c3d59d699018e79254c6f8b6671"
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    STRING1 = ""
    OWNER_ID = 0
    LOGGER_ID = 0

# إنشاء عميل البوت
app = Client("GeneratedMusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تصدير المتغيرات المهمة
__all__ = ["app", "API_ID", "API_HASH", "BOT_TOKEN", "OWNER_ID", "LOGGER_ID"]

print(f"✅ تم تهيئة البوت المُولد بنجاح - BOT_TOKEN: {BOT_TOKEN[:10]}...")
