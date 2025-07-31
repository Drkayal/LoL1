
# تم تحديث التكوين للبوت SP1bot
import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = "7174411191:AAG1jd-KAOH0OR5UNHKHHrW-CEFDgnVxNLg"
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/SP1bot_db?retryWrites=true&w=majority&appName=Cluster0"
OWNER_ID = 985612253
LOGGER_ID = {
    "_": "Chat",
    "id": -1002500508557,
    "type": "ChatType.SUPERGROUP",
    "is_verified": false,
    "is_restricted": false,
    "is_creator": true,
    "is_scam": false,
    "is_fake": false,
    "title": "تخزين ميوزك",
    "has_protected_content": false,
    "permissions": {
        "_": "ChatPermissions",
        "can_send_messages": true,
        "can_send_media_messages": true,
        "can_send_other_messages": true,
        "can_send_polls": true,
        "can_add_web_page_previews": true,
        "can_change_info": false,
        "can_invite_users": false,
        "can_pin_messages": false
    }
}
STRING1 = "BAGhGkAASbIvCxWXaryrEi6Cif7eT2PFQDnOK7MposDHD17RXHy3Id4FfoOP1TXPxM3mme7KfS9Ras3hkBDGOleks1acrSG2PWM67Gim0Fagl2q4Z0gkCarnwsCk1sxDES6LGaAPdbv8EubZ20V1PE_hJ9FyZKrqRIUIi96_6t3t8wF4UX2X5RYI0WrzdnrNFsnjAFQHp9H2m8RAWWySkQ3TK41LGKsncBcYKgrskzZMrJuxrlzpnouKDnWDJdp6EtJghmw5Oe-feoPSUJ5TfrXgKRbogFDnSG9hSxaD9A_cM8H50e25J7AmntU58NLSZs-4tb2wHzi8GKebHAvTEb_fxb_NsQAAAAGkQYkQAA"

# إعدادات إضافية مطلوبة
DURATION_LIMIT_MIN = 300
TG_AUDIO_FILESIZE_LIMIT = 104857600
TG_VIDEO_FILESIZE_LIMIT = 1073741824
PLAYLIST_FETCH_LIMIT = 25

# متغيرات Heroku
HEROKU_API_KEY = None
HEROKU_APP_NAME = None

# متغيرات مهمة من OWNER.py
OWNER_DEVELOPER = 985612253
OWNER = 985612253
GROUP = "https://t.me/YMMYN"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PHOTO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
VIDEO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.mp4"

# Cache Channel
CACHE_CHANNEL_ID = {
    "_": "Chat",
    "id": -1002500508557,
    "type": "ChatType.SUPERGROUP",
    "is_verified": false,
    "is_restricted": false,
    "is_creator": true,
    "is_scam": false,
    "is_fake": false,
    "title": "تخزين ميوزك",
    "has_protected_content": false,
    "permissions": {
        "_": "ChatPermissions",
        "can_send_messages": true,
        "can_send_media_messages": true,
        "can_send_other_messages": true,
        "can_send_polls": true,
        "can_add_web_page_previews": true,
        "can_change_info": false,
        "can_invite_users": false,
        "can_pin_messages": false
    }
}
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
adminlist = {}
lyrical = {}
confirmer = {}

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
