
import os
import sys
sys.path.insert(0, '/workspace')

# محاكاة إنشاء بوت جديد
id = 'TESTBOT'
TOKEN = '7174411191:AAG1jd-KAOH0OR5UNHKHHrW-CEFDgnVxNLg'
SESSION = 'test_session'
Dev = 985612253
loger = -1002728178540

# إنشاء المجلد
os.makedirs(f'test_creation/{id}', exist_ok=True)

# نسخ الملفات (محاكاة)
os.system(f'cp -r Make/AnonXMusic test_creation/{id}/')

# إنشاء config.py باستخدام النموذج المُحدث
config_update = f'''
# تم تحديث التكوين للبوت {id}
import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = "{TOKEN}"
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{id}_db?retryWrites=true&w=majority&appName=Cluster0"
OWNER_ID = {Dev}
LOGGER_ID = {loger}
STRING1 = "{SESSION}"

# إعدادات إضافية مطلوبة
DURATION_LIMIT_MIN = 300
TG_AUDIO_FILESIZE_LIMIT = 104857600
TG_VIDEO_FILESIZE_LIMIT = 1073741824
PLAYLIST_FETCH_LIMIT = 25

# متغيرات Heroku
HEROKU_API_KEY = None
HEROKU_APP_NAME = None

# متغيرات مهمة من OWNER.py
OWNER_DEVELOPER = {Dev}
OWNER = {Dev}
GROUP = "https://t.me/YMMYN"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PHOTO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
VIDEO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.mp4"

# Cache Channel
CACHE_CHANNEL_ID = {loger}
CACHE_CHANNEL_USERNAME = None

# Advanced Settings
YT_API_KEYS = []
INVIDIOUS_SERVERS = []
COOKIES_FILES = []
COOKIE_METHOD = "chrome"
COOKIE_FILE = None

# Additional Variables
BANNED_USERS = set()
SUPPORT_CHANNEL = "https://t.me/K55DD"
SUPPORT_GROUP = "https://t.me/YMMYN"
UPSTREAM_REPO = "https://github.com/AnonymousX1025/AnonXMusic"
UPSTREAM_BRANCH = "master"
GIT_TOKEN = None
SUPPORT_CHAT = "https://t.me/YMMYN"

# String Sessions
STRING2 = None
STRING3 = None
STRING4 = None  
STRING5 = None

# Additional Settings
AUTO_LEAVING_ASSISTANT = True
CLEANMODE_DELETE_MINS = 5
PRIVATE_BOT_MODE = False
SPOTIFY_CLIENT_ID = None
SPOTIFY_CLIENT_SECRET = None
SET_CMDS = True

# Dictionary Variables
adminlist = {{}}
lyrical = {{}}
confirmer = {{}}

# Image URLs
START_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PING_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PLAY_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
STATS_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
TELEGRAM_AUDIO_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
SPOTIFY_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
CHANNEL_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"

# Additional Settings
AUTO_DOWNLOADS_CLEAR = True
YOUTUBE_DOWNLOAD_EDIT_RM_TIME = 3
ASSISTANT_NAME = "مساعد الموسيقى"
ASSISTANT_USERNAME = None
ASSISTANT_ID = None
AUTO_SUGGESTION_MODE = True
AUTO_SUGGESTION_TIME = 5
'''

with open(f'test_creation/{id}/config.py', 'w', encoding='utf-8') as f:
    f.write(config_update)

print('✅ تم إنشاء ملف config.py بنجاح')

# اختبار استيراد config.py
import sys
sys.path.insert(0, f'test_creation/{id}')
try:
    import config
    print('✅ تم استيراد config.py بنجاح')
    print(f'BOT_TOKEN: {config.BOT_TOKEN[:20]}...')
    print(f'LOGGER_ID: {config.LOGGER_ID}')
    print(f'HEROKU_API_KEY: {config.HEROKU_API_KEY}')
    print(f'SUPPORT_CHAT: {config.SUPPORT_CHAT}')
except Exception as e:
    print(f'❌ خطأ في استيراد config.py: {e}')

