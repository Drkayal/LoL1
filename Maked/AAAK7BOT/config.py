import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/AAAK7BOT_db?retryWrites=true&w=majority&appName=Cluster0"

# Get this value from my.telegram.org/apps
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"

# Get your token from @BotFather on Telegram.
BOT_TOKEN = "7618405088:AAEikRuG-UXaLYqcrqGjgxf5k4V23U9kcAA"

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = {LOGGER_ID}

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = 985612253

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

# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = "BAGhGkAASbIvCxWXaryrEi6Cif7eT2PFQDnOK7MposDHD17RXHy3Id4FfoOP1TXPxM3mme7KfS9Ras3hkBDGOleks1acrSG2PWM67Gim0Fagl2q4Z0gkCarnwsCk1sxDES6LGaAPdbv8EubZ20V1PE_hJ9FyZKrqRIUIi96_6t3t8wF4UX2X5RYI0WrzdnrNFsnjAFQHp9H2m8RAWWySkQ3TK41LGKsncBcYKgrskzZMrJuxrlzpnouKDnWDJdp6EtJghmw5Oe-feoPSUJ5TfrXgKRbogFDnSG9hSxaD9A_cM8H50e25J7AmntU58NLSZs-4tb2wHzi8GKebHAvTEb_fxb_NsQAAAAGkQYkQAA"
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv(
    "START_IMG_URL", "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg"
)
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
