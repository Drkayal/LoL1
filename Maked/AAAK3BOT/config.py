
import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Basic Configuration
API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = "7519388401:AAF60Wj1Xq6vgcDDFDblZw5pdjZPio7ajlY"
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/AAAK3BOT_db?retryWrites=true&w=majority&appName=Cluster0")
OWNER_ID = int("985612253")
LOGGER_ID = int("-1002689749562")
STRING1 = "BAGhGkAASbIvCxWXaryrEi6Cif7eT2PFQDnOK7MposDHD17RXHy3Id4FfoOP1TXPxM3mme7KfS9Ras3hkBDGOleks1acrSG2PWM67Gim0Fagl2q4Z0gkCarnwsCk1sxDES6LGaAPdbv8EubZ20V1PE_hJ9FyZKrqRIUIi96_6t3t8wF4UX2X5RYI0WrzdnrNFsnjAFQHp9H2m8RAWWySkQ3TK41LGKsncBcYKgrskzZMrJuxrlzpnouKDnWDJdp6EtJghmw5Oe-feoPSUJ5TfrXgKRbogFDnSG9hSxaD9A_cM8H50e25J7AmntU58NLSZs-4tb2wHzi8GKebHAvTEb_fxb_NsQAAAAGkQYkQAA"

# Additional Configuration
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Heroku Configuration (Optional)
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", None)
HEROKU_API_KEY = getenv("HEROKU_API_KEY", None)

# Additional Sessions (Optional)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

# Other Configuration
BANNED_USERS = set()
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/K55DD")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "https://t.me/YMMYN")
