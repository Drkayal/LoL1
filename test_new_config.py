
import os
import sys
sys.path.insert(0, '/workspace')

# اختبار نهائي بالملف الجديد
id = 'NEWTEST'
TOKEN = '7174411191:AAG1jd-KAOH0OR5UNHKHHrW-CEFDgnVxNLg'
SESSION = 'test_session'
Dev = 985612253

# محاكاة loger object
class MockLoger:
    def __init__(self):
        self.id = -1002500508557

loger = MockLoger()

# إنشاء المجلد
os.makedirs(f'new_test/{id}', exist_ok=True)

# نسخ الملفات
os.system(f'cp -r Make/AnonXMusic new_test/{id}/')

# إنشاء config.py بالنموذج الجديد الكامل
config_update = f'''import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = "{TOKEN}"

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{id}_db?retryWrites=true&w=majority&appName=Cluster0"

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = {loger.id}

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = {Dev}

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/BLAKAQ/a",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)  

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/K55DD")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/YMMYN")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", "True"))

CACHE_CHANNEL_ID = {loger.id}

# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = "{SESSION}"
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

BANNED_USERS = filters.user()
adminlist = {{}}
lyrical = {{}}
votemode = {{}}
autoclean = []
confirmer = {{}}

START_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
PING_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
PLAYLIST_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
STATS_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
SOUNCLOUD_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{{DURATION_LIMIT_MIN}}:00"))
'''

with open(f'new_test/{id}/config.py', 'w', encoding='utf-8') as f:
    f.write(config_update)

print('✅ تم إنشاء ملف config.py الجديد')

# اختبار شامل
import sys
sys.path.insert(0, f'new_test/{id}')
try:
    import config
    print('✅ تم استيراد config.py بنجاح')
    print(f'API_ID: {config.API_ID} (type: {type(config.API_ID)})')
    print(f'LOGGER_ID: {config.LOGGER_ID} (type: {type(config.LOGGER_ID)})')
    print(f'UPSTREAM_REPO: {config.UPSTREAM_REPO}')
    print(f'SPOTIFY_CLIENT_ID: {config.SPOTIFY_CLIENT_ID}')
    print('🔄 اختبار تحميل AnonXMusic...')
    
    from AnonXMusic import app
    print('🎉 تم تحميل AnonXMusic بنجاح بدون أي أخطاء!')
    print('✅ الإصلاح النهائي نجح تماماً!')
    
except Exception as e:
    print(f'❌ خطأ: {e}')
    import traceback
    traceback.print_exc()

