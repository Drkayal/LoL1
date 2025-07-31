import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Basic Configuration
API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = "7659739618:AAEEvi8sAm2cBV7KHH_sTjB9ffn5bvjKo6U"
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/AAAK1BOT_db?retryWrites=true&w=majority&appName=Cluster0"
OWNER_ID = 985612253
LOGGER_ID = -1002557222253
STRING1 = "BAGhGkAASbIvCxWXaryrEi6Cif7eT2PFQDnOK7MposDHD17RXHy3Id4FfoOP1TXPxM3mme7KfS9Ras3hkBDGOleks1acrSG2PWM67Gim0Fagl2q4Z0gkCarnwsCk1sxDES6LGaAPdbv8EubZ20V1PE_hJ9FyZKrqRIUIi96_6t3t8wF4UX2X5RYI0WrzdnrNFsnjAFQHp9H2m8RAWWySkQ3TK41LGKsncBcYKgrskzZMrJuxrlzpnouKDnWDJdp6EtJghmw5Oe-feoPSUJ5TfrXgKRbogFDnSG9hSxaD9A_cM8H50e25J7AmntU58NLSZs-4tb2wHzi8GKebHAvTEb_fxb_NsQAAAAGkQYkQAA"

# إعدادات إضافية
DURATION_LIMIT_MIN = 300
TG_AUDIO_FILESIZE_LIMIT = 104857600
TG_VIDEO_FILESIZE_LIMIT = 1073741824
PLAYLIST_FETCH_LIMIT = 25

# متغيرات مهمة من OWNER.py
OWNER_DEVELOPER = 985612253
OWNER = 985612253
GROUP = "https://t.me/YMMYN"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PHOTO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
VIDEO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.mp4"

# Cache Channel
CACHE_CHANNEL_ID = -1002557222253
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

# All missing session strings
STRING2 = None
STRING3 = None
STRING4 = None
STRING5 = None

# Additional missing variables
HEROKU_API_KEY = None
HEROKU_APP_NAME = None
AUTO_LEAVING_ASSISTANT = True
CLEANMODE_DELETE_MINS = 5
UPSTREAM_REPO = 'https://github.com/AnonymousX1025/AnonXMusic'
UPSTREAM_BRANCH = 'master'
GIT_TOKEN = None
PRIVATE_BOT_MODE = False
SPOTIFY_CLIENT_ID = None
SPOTIFY_CLIENT_SECRET = None
SET_CMDS = True

# Duration calculation
def time_to_seconds(stringt):
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SUPPORT_CHAT = 'https://t.me/YMMYN'

# More missing variables
adminlist = {}
lyrical = {}
START_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
PING_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
STATS_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
TELEGRAM_AUDIO_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
TELEGRAM_VIDEO_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
STREAM_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
SOUNCLOUD_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
YOUTUBE_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
SPOTIFY_ARTIST_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
SPOTIFY_ALBUM_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'
SPOTIFY_PLAYLIST_IMG_URL = 'https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg'

confirmer = {}
