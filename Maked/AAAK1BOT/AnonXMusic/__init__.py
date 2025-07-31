
import os
import sys
from pyrogram import Client

# إعداد المسارات
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# التكوين
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"
BOT_TOKEN = "7659739618:AAEEvi8sAm2cBV7KHH_sTjB9ffn5bvjKo6U"
OWNER_ID = 985612253
LOGGER_ID = -1002557222253

# إنشاء العميل
app = Client("AAAK1BOT_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# المتغيرات المهمة
BANNED_USERS = set()

# تحميل البرمجيات المساعدة
try:
    import sys
    import os
    import importlib.util
    
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if os.path.exists(plugins_dir):
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(plugins_dir, filename)
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    print(f"✅ تم تحميل البرمجية: {module_name}")
except Exception as e:
    print(f"⚠️ خطأ في تحميل البرمجيات: {e}")
