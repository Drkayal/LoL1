"""
وحدة صناعة البوتات المحسنة
تحتوي على جميع الوظائف المطلوبة لإنشاء وإدارة البوتات الموسيقية
"""

import os
import re
import asyncio
import logging
from typing import Dict, Optional, Tuple, List
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, 
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid,
    FloodWait, PeerIdInvalid
)
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.types import ChatPrivileges
from random import randint

# إعداد الـ logging
logger = logging.getLogger(__name__)

class BotCreationError(Exception):
    """استثناء خاص بأخطاء صناعة البوتات"""
    pass

class BotFactory:
    """مصنع البوتات المحسن"""
    
    def __init__(self, api_id: int, api_hash: str, mongo_url: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.mongo_url = mongo_url
        self.created_bots: List[Dict] = []
        
    async def validate_bot_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        التحقق من صحة توكن البوت
        
        Returns:
            tuple: (is_valid, bot_info)
        """
        try:
            # تنظيف التوكن
            token = token.strip()
            
            # التحقق من صيغة التوكن
            if not re.match(r'^\d+:[A-Za-z0-9_-]{35}$', token):
                return False, None
            
            # اختبار التوكن
            test_bot = Client(
                ":memory:", 
                api_id=self.api_id, 
                api_hash=self.api_hash, 
                bot_token=token, 
                in_memory=True
            )
            
            await test_bot.start()
            bot_info = await test_bot.get_me()
            await test_bot.stop()
            
            bot_data = {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot
            }
            
            if not bot_data['is_bot']:
                return False, None
                
            logger.info(f"✅ توكن صحيح للبوت: @{bot_data['username']}")
            return True, bot_data
            
        except FloodWait as e:
            logger.error(f"FloodWait: انتظار {e.value} ثانية")
            raise BotCreationError(f"يجب الانتظار {e.value} ثانية قبل المحاولة مرة أخرى")
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من التوكن: {e}")
            return False, None
    
    async def validate_session_string(self, session: str) -> Tuple[bool, Optional[Dict]]:
        """
        التحقق من صحة كود الجلسة
        
        Returns:
            tuple: (is_valid, user_info)
        """
        try:
            # تنظيف كود الجلسة
            session = session.strip()
            
            # التحقق من طول كود الجلسة (تقريبي)
            if len(session) < 100:
                return False, None
            
            # اختبار الجلسة
            test_user = Client(
                ":memory:", 
                api_id=self.api_id, 
                api_hash=self.api_hash, 
                session_string=session, 
                in_memory=True
            )
            
            await test_user.start()
            user_info = await test_user.get_me()
            await test_user.stop()
            
            user_data = {
                'id': user_info.id,
                'username': user_info.username,
                'first_name': user_info.first_name,
                'is_bot': user_info.is_bot
            }
            
            if user_data['is_bot']:
                return False, None
                
            logger.info(f"✅ جلسة صحيحة للمستخدم: @{user_data['username'] or user_data['first_name']}")
            return True, user_data
            
        except FloodWait as e:
            logger.error(f"FloodWait: انتظار {e.value} ثانية")
            raise BotCreationError(f"يجب الانتظار {e.value} ثانية قبل المحاولة مرة أخرى")
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الجلسة: {e}")
            return False, None
    
    async def create_logger_group(self, session: str, bot_username: str) -> Tuple[bool, Optional[Dict]]:
        """
        إنشاء مجموعة السجلات للبوت
        
        Returns:
            tuple: (success, group_info)
        """
        try:
            user_client = Client(
                ":memory:", 
                api_id=self.api_id, 
                api_hash=self.api_hash, 
                session_string=session, 
                in_memory=True
            )
            
            await user_client.start()
            
            # إنشاء المجموعة
            group_title = f"تخزين {bot_username}"
            group_description = f"مجموعة تخزين وسجلات البوت @{bot_username}"
            
            logger_group = await user_client.create_supergroup(
                title=group_title,
                description=group_description
            )
            
            # الحصول على رابط الدعوة
            invite_link = await user_client.export_chat_invite_link(logger_group.id)
            
            # إضافة البوت للمجموعة
            try:
                await user_client.add_chat_members(logger_group.id, bot_username)
                
                # رفع البوت كمشرف
                await user_client.promote_chat_member(
                    logger_group.id, 
                    bot_username, 
                    ChatPrivileges(
                        can_change_info=True,
                        can_invite_users=True,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_pin_messages=True,
                        can_promote_members=True,
                        can_manage_chat=True,
                        can_manage_video_chats=True
                    )
                )
                
                logger.info(f"✅ تم رفع البوت @{bot_username} كمشرف في المجموعة")
                
            except Exception as e:
                logger.warning(f"تحذير: لم يتم رفع البوت كمشرف: {e}")
            
            # إنشاء مكالمة صوتية لتفعيل الحساب
            try:
                await user_client.invoke(
                    CreateGroupCall(
                        peer=(await user_client.resolve_peer(logger_group.id)), 
                        random_id=randint(10000, 999999999)
                    )
                )
                await user_client.send_message(
                    logger_group.id, 
                    f"🎵 تم إنشاء البوت @{bot_username} بنجاح!\n🔊 تم فتح الاتصال لتفعيل الحساب."
                )
                logger.info("✅ تم إنشاء مكالمة صوتية وتفعيل الحساب")
                
            except Exception as e:
                logger.warning(f"تحذير: لم يتم إنشاء المكالمة الصوتية: {e}")
                await user_client.send_message(
                    logger_group.id, 
                    f"🎵 تم إنشاء البوت @{bot_username} بنجاح!"
                )
            
            await user_client.stop()
            
            group_info = {
                'id': logger_group.id,
                'title': group_title,
                'invite_link': invite_link,
                'username': getattr(logger_group, 'username', None)
            }
            
            logger.info(f"✅ تم إنشاء مجموعة السجلات: {group_info['id']}")
            return True, group_info
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجموعة السجلات: {e}")
            return False, None
    
    def generate_bot_config(self, bot_token: str, logger_id: int, session: str, owner_id: int, bot_username: str) -> str:
        """
        توليد ملف التكوين للبوت الجديد
        """
        config_content = f'''import re
import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# تحميل متغيرات البيئة
load_dotenv()

# =======================================
# إعدادات قاعدة البيانات
# =======================================
MONGO_DB_URI = "{self.mongo_url.replace('cluster0.', f'cluster0.')}/{bot_username}_db?retryWrites=true&w=majority&appName=Cluster0"

# =======================================
# إعدادات Telegram API
# =======================================
API_ID = int(getenv("API_ID", "{self.api_id}"))
API_HASH = getenv("API_HASH", "{self.api_hash}")

# =======================================
# إعدادات البوت
# =======================================
BOT_TOKEN = "{bot_token}"

# مدة الحد الأقصى للمقاطع (بالدقائق)
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# معرف مجموعة السجلات
LOGGER_ID = {logger_id}

# معرف المالك
OWNER_ID = {owner_id}

# =======================================
# إعدادات الجلسات
# =======================================
STRING1 = "{session}"
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

# =======================================
# إعدادات إضافية
# =======================================
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/BLAKAQ/a")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/K55DD")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/YMMYN")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", "True"))

# إعدادات Spotify
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

# حدود الملفات
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

# فلاتر المحظورين
BANNED_USERS = filters.user()
adminlist = {{}}
lyrical = {{}}
votemode = {{}}
autoclean = []
confirmer = {{}}

# روابط الصور
START_IMG_URL = getenv("START_IMG_URL", "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/645af9b1cc12cc0a6dfc8.jpg")
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

# دالة تحويل الوقت
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{{DURATION_LIMIT_MIN}}:00"))

# التحقق من الروابط
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://")

# =======================================
# التحقق النهائي من البيانات
# =======================================
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير محدد")

if not LOGGER_ID:
    raise ValueError("❌ LOGGER_ID غير محدد")

if not OWNER_ID:
    raise ValueError("❌ OWNER_ID غير محدد")

print("✅ تم تحميل تكوين البوت بنجاح")
print(f"🤖 البوت: @{bot_username}")
print(f"📝 مجموعة السجلات: {LOGGER_ID}")
print(f"👑 المالك: {OWNER_ID}")
'''
        return config_content
    
    def copy_bot_files(self, bot_username: str) -> bool:
        """
        نسخ ملفات البوت الأساسية
        """
        try:
            bot_dir = f"Maked/{bot_username}"
            
            # إنشاء المجلد الرئيسي
            os.makedirs(bot_dir, exist_ok=True)
            
            # قائمة الملفات والمجلدات المطلوبة للنسخ
            files_to_copy = [
                ("Make/AnonXMusic", f"{bot_dir}/AnonXMusic"),
                ("Make/strings", f"{bot_dir}/strings"),
                ("Make/cookies", f"{bot_dir}/cookies"),
                ("Make/requirements.txt", f"{bot_dir}/requirements.txt"),
                ("Make/__main__.py", f"{bot_dir}/__main__.py"),
                ("Make/start", f"{bot_dir}/start"),
                ("Make/Dockerfile", f"{bot_dir}/Dockerfile"),
                ("Make/Procfile", f"{bot_dir}/Procfile"),
                ("Make/app.json", f"{bot_dir}/app.json"),
                ("Make/runtime.txt", f"{bot_dir}/runtime.txt"),
                ("Make/heroku.yml", f"{bot_dir}/heroku.yml"),
                ("Make/.dockerignore", f"{bot_dir}/.dockerignore"),
                ("Make/.gitignore", f"{bot_dir}/.gitignore"),
            ]
            
            # نسخ الملفات
            for source, destination in files_to_copy:
                if os.path.exists(source):
                    if os.path.isdir(source):
                        # نسخ مجلد
                        os.system(f"cp -r '{source}' '{destination}'")
                    else:
                        # نسخ ملف
                        os.system(f"cp '{source}' '{destination}'")
                    logger.info(f"✅ تم نسخ: {source} -> {destination}")
                else:
                    logger.warning(f"⚠️ الملف غير موجود: {source}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في نسخ ملفات البوت: {e}")
            return False
    
    def create_main_file(self, bot_username: str) -> bool:
        """
        إنشاء ملف __main__.py محسن للبوت
        """
        try:
            main_content = f'''import asyncio
import sys
import os
from pyrogram import idle

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

# إعداد الـ logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bot_{bot_username}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from AnonXMusic import app
    logger.info("✅ تم تحميل البوت بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في تحميل البوت: {{e}}")
    sys.exit(1)

async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    try:
        logger.info(f"🚀 بدء تشغيل البوت @{bot_username}...")
        
        await app.start()
        me = await app.get_me()
        
        logger.info(f"✅ تم تشغيل البوت بنجاح:")
        logger.info(f"   🤖 الاسم: {{me.first_name}}")
        logger.info(f"   📱 المعرف: @{{me.username}}")
        logger.info(f"   🆔 الـ ID: {{me.id}}")
        logger.info("🔄 البوت في وضع الانتظار...")
        
        await idle()
        
    except KeyboardInterrupt:
        logger.info("🔴 تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {{e}}")
        sys.exit(1)
    finally:
        try:
            await app.stop()
            logger.info("🔴 تم إيقاف البوت")
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {{e}}")
        sys.exit(1)
'''
            
            with open(f"Maked/{bot_username}/__main__.py", "w", encoding="utf-8") as f:
                f.write(main_content)
            
            logger.info(f"✅ تم إنشاء ملف __main__.py للبوت @{bot_username}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف __main__.py: {e}")
            return False
    
    async def create_bot(
        self, 
        bot_token: str, 
        session_string: str, 
        owner_id: int,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        إنشاء بوت جديد بشكل كامل
        
        Args:
            bot_token: توكن البوت
            session_string: كود الجلسة
            owner_id: معرف المالك
            progress_callback: دالة لإرسال تحديثات التقدم
            
        Returns:
            tuple: (success, bot_info, error_message)
        """
        try:
            if progress_callback:
                await progress_callback("🔍 التحقق من توكن البوت...")
            
            # التحقق من التوكن
            token_valid, bot_info = await self.validate_bot_token(bot_token)
            if not token_valid:
                return False, None, "توكن البوت غير صحيح"
            
            if progress_callback:
                await progress_callback("🔐 التحقق من كود الجلسة...")
            
            # التحقق من الجلسة
            session_valid, user_info = await self.validate_session_string(session_string)
            if not session_valid:
                return False, None, "كود الجلسة غير صحيح"
            
            bot_username = bot_info['username']
            
            if progress_callback:
                await progress_callback(f"📁 إنشاء مجلد البوت @{bot_username}...")
            
            # حذف المجلد إذا كان موجوداً
            if os.path.exists(f"Maked/{bot_username}"):
                os.system(f"rm -rf Maked/{bot_username}")
            
            # نسخ ملفات البوت
            if not self.copy_bot_files(bot_username):
                return False, None, "فشل في نسخ ملفات البوت"
            
            if progress_callback:
                await progress_callback("🏗️ إنشاء مجموعة السجلات...")
            
            # إنشاء مجموعة السجلات
            group_created, group_info = await self.create_logger_group(session_string, bot_username)
            if not group_created:
                return False, None, "فشل في إنشاء مجموعة السجلات"
            
            if progress_callback:
                await progress_callback("⚙️ إنشاء ملف التكوين...")
            
            # إنشاء ملف التكوين
            config_content = self.generate_bot_config(
                bot_token, 
                group_info['id'], 
                session_string, 
                owner_id, 
                bot_username
            )
            
            with open(f"Maked/{bot_username}/config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            
            # إنشاء ملف __main__.py محسن
            if not self.create_main_file(bot_username):
                return False, None, "فشل في إنشاء ملف التشغيل"
            
            if progress_callback:
                await progress_callback("🚀 تشغيل البوت...")
            
            # تشغيل البوت
            bot_dir = f"Maked/{bot_username}"
            start_command = f"cd {bot_dir} && nohup python3 __main__.py > bot_{bot_username}.log 2>&1 &"
            os.system(start_command)
            
            # معلومات البوت المكتمل
            complete_bot_info = {
                'username': bot_username,
                'bot_id': bot_info['id'],
                'owner_id': owner_id,
                'logger_group': group_info,
                'user_info': user_info,
                'created_at': asyncio.get_event_loop().time()
            }
            
            self.created_bots.append(complete_bot_info)
            
            if progress_callback:
                await progress_callback("✅ تم إنشاء البوت بنجاح!")
            
            logger.info(f"✅ تم إنشاء البوت @{bot_username} بنجاح")
            return True, complete_bot_info, None
            
        except BotCreationError as e:
            logger.error(f"خطأ في صناعة البوت: {e}")
            return False, None, str(e)
        except Exception as e:
            logger.error(f"خطأ غير متوقع في صناعة البوت: {e}")
            return False, None, f"خطأ غير متوقع: {e}"
    
    def cleanup_failed_bot(self, bot_username: str) -> bool:
        """
        تنظيف ملفات البوت في حالة فشل الإنشاء
        """
        try:
            bot_dir = f"Maked/{bot_username}"
            if os.path.exists(bot_dir):
                os.system(f"rm -rf {bot_dir}")
                logger.info(f"✅ تم تنظيف ملفات البوت الفاشل: @{bot_username}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تنظيف ملفات البوت: {e}")
            return False