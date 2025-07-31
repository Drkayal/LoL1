import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "7557280783:AAF44S35fdkcURM4j4Rp5-OOkASZ3_uCSR4")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", -1002034990746))

# ============================================
# إعدادات النظام الذكي الجديد
# ============================================

# قناة التخزين الذكي (للتخزين في قناة تيليجرام)
CACHE_CHANNEL_USERNAME = getenv("CACHE_CHANNEL_USERNAME", "mccckc")

# تحويل يوزر القناة إلى الشكل المناسب
CACHE_CHANNEL_ID = None
if CACHE_CHANNEL_USERNAME:
    # إذا كان ID رقمي، نحوله للصيغة الصحيحة
    if CACHE_CHANNEL_USERNAME.isdigit() or (CACHE_CHANNEL_USERNAME.startswith('-') and CACHE_CHANNEL_USERNAME[1:].isdigit()):
        try:
            channel_id = int(CACHE_CHANNEL_USERNAME)
            if not str(channel_id).startswith('-100') and channel_id > 0:
                CACHE_CHANNEL_ID = f"-100{channel_id}"
            else:
                CACHE_CHANNEL_ID = str(channel_id)
        except ValueError:
            CACHE_CHANNEL_ID = None
    # إذا كان يوزر، نتركه كما هو
    elif CACHE_CHANNEL_USERNAME.startswith('@') or not CACHE_CHANNEL_USERNAME.startswith('-'):
        # إزالة @ إن وجدت
        username = CACHE_CHANNEL_USERNAME.replace('@', '')
        CACHE_CHANNEL_ID = f"@{username}"
    else:
        # صيغة ID مباشرة
        CACHE_CHANNEL_ID = CACHE_CHANNEL_USERNAME

# ============================================
# YouTube Data API Keys (متعددة للتدوير)
# ============================================
YT_API_KEYS_ENV = getenv("YT_API_KEYS", "[]")
try:
    import json
    YT_API_KEYS = json.loads(YT_API_KEYS_ENV) if YT_API_KEYS_ENV != "[]" else []
except:
    YT_API_KEYS = []

# مفاتيح افتراضية (تحديث مطلوب)
if not YT_API_KEYS:
    YT_API_KEYS = [
        "AIzaSyA3x5N5DNYzd5j7L7JMn9XsUYil32Ak77U", "AIzaSyDw09GqGziUHXZ3FjugOypSXD7tedWzIzQ"
        # أضف مفاتيحك هنا
    ]

# ============================================
# خوادم Invidious الأفضل (محدثة 2025)
# ============================================
INVIDIOUS_SERVERS_ENV = getenv("INVIDIOUS_SERVERS", "[]")
try:
    import json
    INVIDIOUS_SERVERS = json.loads(INVIDIOUS_SERVERS_ENV) if INVIDIOUS_SERVERS_ENV != "[]" else []
except:
    INVIDIOUS_SERVERS = []

# خوادم افتراضية محدثة (مجربة ديسمبر 2024 - يناير 2025)
if not INVIDIOUS_SERVERS:
    INVIDIOUS_SERVERS = [
        "https://inv.nadeko.net",           # 🥇 الأفضل - 99.666% uptime
        "https://invidious.nerdvpn.de",     # 🥈 ممتاز - 100% uptime  
        "https://yewtu.be",                 # 🥉 جيد - 89.625% uptime
        "https://invidious.f5.si",          # ⚡ سريع - Cloudflare
        "https://invidious.materialio.us",  # 🌟 موثوق
        "https://invidious.reallyaweso.me", # 🚀 سريع
        "https://iteroni.com",              # ⚡ جيد
        "https://iv.catgirl.cloud",         # 😸 ممتاز
        "https://youtube.alt.tyil.nl",      # 🇳🇱 هولندا
    ]

# ============================================
# إعدادات ملفات الكوكيز المتعددة
# ============================================
COOKIES_FILES_ENV = getenv("COOKIES_FILES", "[]")
try:
    import json
    COOKIES_FILES = json.loads(COOKIES_FILES_ENV) if COOKIES_FILES_ENV != "[]" else []
except:
    COOKIES_FILES = []

# مسارات افتراضية لملفات الكوكيز
if not COOKIES_FILES:
    import os
    cookies_dir = "cookies"
    if os.path.exists(cookies_dir):
        COOKIES_FILES = [
            f"{cookies_dir}/cookies1.txt",
            f"{cookies_dir}/cookies2.txt", 
            f"{cookies_dir}/cookies3.txt",
            f"{cookies_dir}/cookies4.txt",
            f"{cookies_dir}/cookies5.txt"
        ]
        # فلترة الملفات الموجودة فقط
        COOKIES_FILES = [f for f in COOKIES_FILES if os.path.exists(f)]
    else:
        # ملف واحد افتراضي للتوافق
        COOKIES_FILES = ["cookies.txt"] if os.path.exists("cookies.txt") else []

# ============================================
# إعدادات الكوكيز (التوافق مع الكود القديم)
# ============================================
COOKIE_METHOD = "browser"
COOKIE_FILE = COOKIES_FILES[0] if COOKIES_FILES else "cookies.txt"

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", 985612253))
OWNER_DEVELOPER = 985612253  # Single developer ID

# Additional owner settings from OWNER.py
OWNER = []
OWNER__ID = 985612253
OWNER_NAME = "𝐷𝑟. 𝐾ℎ𝑎𝑦𝑎𝑙 𓏺"
GROUP = "https://t.me/YMMYN"
YOUTUBE_IMG_URL = "https://t.me/MusicxXxYousef/90"
PHOTO = "https://t.me/MusicxXxYousef/90"
VIDEO = "https://t.me/MusicxXxYousef/91"

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
# Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = "https://t.me/K55DD"
SUPPORT_CHAT = "https://t.me/YMMYN"

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", "True"))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", "BQGhGkAAU-dreEVif7ijsuGD5E_xJA88HGUu0nv__Fj_-AKxfbnYNOp2DjFvYlNuzm0H9nRC1dTV1VeSYbmYCOZgmXGpcrHjJ8h6bDBDnC8xkJr_DzzWQYqNX4hsKxJ1BCiCuB32impJYYkTIAmflZ-9PD7UfxFng6etAUli7_H3k2gSTmDGpnpL9W1nNbSE92VwLhadWBVjcMCdeNsJgOV4Wm6oxAcfefLCAn7EoB3ehyV-5xl9k7yV4JrblpETpXmEeE11KzGq1caJ7ECCKNjjXCnBBnxEYL7fnGkknQycsbD2Nd64rv9bvnScwJMHOsSd5boX2L8SmtrQdXmCvAhPW1dnTQAAAAGyOTEEAA")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://te.legra.ph/file/25efe6aa029c6baea73ea.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://te.legra.ph/file/b8a0c1a00db3e57522b53.jpg"
)
PLAYLIST_IMG_URL = "https://te.legra.ph/file/4ec5ae4381dffb039b4ef.jpg"
STATS_IMG_URL = "https://te.legra.ph/file/e906c2def5afe8a9b9120.jpg"
TELEGRAM_AUDIO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
)
