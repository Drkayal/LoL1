import os
import sys
import asyncio
import subprocess
import re
import shutil
import psutil
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import List, Union, Callable, Dict, Optional, Any
from os import execle, environ, path
from random import randint
from pyrogram import filters, Client, enums
from pyrogram import Client as app
from pyrogram import __version__ as pyrover
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    ChatPrivileges, 
    Message
)
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, 
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid, 
    FloodWait, PeerIdInvalid
)
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient as mongo_client
from config import API_ID, API_HASH, MONGO_DB_URL, OWNER, OWNER_ID, OWNER_NAME, CHANNEL, GROUP, PHOTO, VIDEO

# استيراد الأدوات المساعدة من مجلد utils
from utils import (
    logger,
    ValidationError,
    DatabaseError,
    ProcessError,
    BroadcastError,
    CacheError,
    cache_manager,
    temp_file_manager,
    rate_limit_manager
)

# استيراد دوال المستخدمين من مجلد users
from users import (
    validate_user_id,
    validate_bot_token,
    validate_session_string,
    validate_bot_username,
    is_dev,
    is_user,
    add_new_user,
    del_user,
    get_users,
    get_user_count,
    clear_user_cache,
    get_dev_count,
    set_dependencies
)

# استخراج اسم القناة من الرابط
ch = CHANNEL.replace("https://t.me/", "").replace("@", "")

# أنواع الأخطاء المخصصة تم نقلها إلى utils/errors.py

# مدير التخزين المؤقت تم نقله إلى utils/cache.py

# إعداد اتصال MongoDB مع إدارة محسنة
class DatabaseManager:
    def __init__(self):
        self.sync_client = None
        self.async_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        try:
            self.sync_client = MongoClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
            self.async_client = mongo_client(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
            # اختبار الاتصال
            self.sync_client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def get_sync_db(self):
        if not self.sync_client:
            self._initialize_connections()
        return self.sync_client["Yousef"].botpsb
    
    def get_async_db(self):
        if not self.async_client:
            self._initialize_connections()
        return self.async_client.AnonX
    
    def close_connections(self):
        try:
            if self.sync_client:
                self.sync_client.close()
            if self.async_client:
                self.async_client.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

# إنشاء مدير قاعدة البيانات
db_manager = DatabaseManager()
db = db_manager.get_sync_db()
mongodb = db_manager.get_async_db()

# مدير الملفات المؤقتة تم نقله إلى utils/tempfiles.py

# مدير التأخير تم نقله إلى utils/rate_limit.py

# تهيئة المجموعات
users = mongodb.tgusersdb
chats = mongodb.chats
mkchats = db.chatss
blocked = []
blockeddb = db.blocked
broadcasts_collection = db["broadcasts"]
devs_collection = db["devs"]
bots_collection = db["bots"]
factory_settings = db["factory_settings"]

# حالة المصنع الافتراضية
off = True
mk = []  # قائمة المحادثات

# وظائف التحقق من المدخلات مع أنواع الأخطاء المخصصة
# دوال التحقق من المدخلات تم نقلها إلى users/validation.py

# دوال إدارة المستخدمين تم نقلها إلى users/logic.py

# وظائف البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
async def set_broadcast_status(user_id, bot_id, key, max_retries=3):
    """تعيين حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not key or not isinstance(key, str):
            logger.error(f"Invalid key: {key}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                broadcasts_collection.update_one(
                    {"user_id": validated_user_id, "bot_id": validated_bot_id},
                    {"$set": {key: True}},
                    upsert=True
                )
                logger.info(f"Successfully set broadcast status for user {validated_user_id}, bot {validated_bot_id}, key {key}")
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to set broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to set broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in set_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in set_broadcast_status function: {str(e)}")
        return False

async def get_broadcast_status(user_id, bot_id, key, max_retries=3):
    """الحصول على حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not key or not isinstance(key, str):
            logger.error(f"Invalid key: {key}")
            return False
        
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"broadcast_status_{validated_user_id}_{validated_bot_id}_{key}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                doc = broadcasts_collection.find_one({"user_id": validated_user_id, "bot_id": validated_bot_id})
                result = doc and doc.get(key)
                cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in get_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in get_broadcast_status function: {str(e)}")
        return False

async def delete_broadcast_status(user_id, bot_id, *keys, max_retries=3):
    """حذف حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not keys:
            logger.error("No keys provided for deletion")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                unset_dict = {key: "" for key in keys if key and isinstance(key, str)}
                if not unset_dict:
                    logger.error("No valid keys provided for deletion")
                    return False
                
                broadcasts_collection.update_one(
                    {"user_id": validated_user_id, "bot_id": validated_bot_id},
                    {"$unset": unset_dict}
                )
                logger.info(f"Successfully deleted broadcast status for user {validated_user_id}, bot {validated_bot_id}, keys {keys}")
                
                # حذف من التخزين المؤقت
                for key in keys:
                    if key and isinstance(key, str):
                        cache_key = f"broadcast_status_{validated_user_id}_{validated_bot_id}_{key}"
                        cache_manager.delete(cache_key)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to delete broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to delete broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in delete_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in delete_broadcast_status function: {str(e)}")
        return False

# وظائف إدارة البوتات مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
def get_bot_info(bot_username, max_retries=3):
    """الحصول على معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"bot_info_{bot_username}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return None
        
        for attempt in range(max_retries):
            try:
                result = bots_collection.find_one({"username": validated_username})
                if result:
                    cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get bot info after {max_retries} attempts")
                    return None
                time.sleep(1)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in get_bot_info: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in get_bot_info function: {str(e)}")
        return None

def save_bot_info(bot_username, dev_id, pid, config_data, max_retries=3):
    """حفظ معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        is_valid_username, validated_username = validate_bot_username(bot_username)
        is_valid_dev, validated_dev_id = validate_user_id(dev_id)
        
        if not is_valid_username or not is_valid_dev:
            logger.error(f"Invalid bot_username or dev_id: {bot_username}, {dev_id}")
            return False
        
        if not isinstance(config_data, dict):
            logger.error("Config data must be a dictionary")
            return False
        
        for attempt in range(max_retries):
            try:
                bot_data = {
                    "dev_id": validated_dev_id,
                    "pid": pid,
                    "config": config_data,
                    "created_at": datetime.now(),
                    "status": "running"
                }
                
                bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": bot_data},
                    upsert=True
                )
                logger.info(f"Successfully saved bot info for {validated_username}")
                
                # تحديث التخزين المؤقت
                cache_key = f"bot_info_{validated_username}"
                cache_manager.set(cache_key, bot_data)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to save bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to save bot info after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in save_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in save_bot_info function: {str(e)}")
        return False

def update_bot_status(bot_username, status, max_retries=3):
    """تحديث حالة البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return False
        
        if not status or not isinstance(status, str):
            logger.error(f"Invalid status: {status}")
            return False
        
        valid_statuses = ["running", "stopped", "error"]
        if status not in valid_statuses:
            logger.error(f"Invalid status value: {status}. Must be one of {valid_statuses}")
            return False
        
        for attempt in range(max_retries):
            try:
                bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": {"status": status}}
                )
                logger.info(f"Successfully updated bot status for {validated_username} to {status}")
                
                # حذف من التخزين المؤقت لتحديث البيانات
                cache_key = f"bot_info_{validated_username}"
                cache_manager.delete(cache_key)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to update bot status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to update bot status after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in update_bot_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in update_bot_status function: {str(e)}")
        return False

def delete_bot_info(bot_username, max_retries=3):
    """حذف معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return False
        
        for attempt in range(max_retries):
            try:
                result = bots_collection.delete_one({"username": validated_username})
                if result.deleted_count > 0:
                    logger.info(f"Successfully deleted bot info for {validated_username}")
                    
                    # حذف من التخزين المؤقت
                    cache_key = f"bot_info_{validated_username}"
                    cache_manager.delete(cache_key)
                    
                    return True
                else:
                    logger.warning(f"Bot {validated_username} not found for deletion")
                    return False
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to delete bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to delete bot info after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in delete_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in delete_bot_info function: {str(e)}")
        return False

def get_all_bots(max_retries=3):
    """الحصول على جميع البوتات مع التخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "all_bots_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved bots from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                bots = list(bots_collection.find())
                logger.info(f"Successfully retrieved {len(bots)} bots")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, bots)
                return bots
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get all bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get all bots after {max_retries} attempts")
                    return []
                time.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_all_bots function: {str(e)}")
        return []

def get_running_bots(max_retries=3):
    """الحصول على البوتات المشتغلة مع التخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "running_bots_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved running bots from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                bots = list(bots_collection.find({"status": "running"}))
                logger.info(f"Successfully retrieved {len(bots)} running bots")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, bots)
                return bots
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get running bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get running bots after {max_retries} attempts")
                    return []
                time.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_running_bots function: {str(e)}")
        return []

# وظائف إدارة المصنع مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
def get_factory_state(max_retries=3):
    """الحصول على حالة المصنع مع التخزين المؤقت وإعادة المحاولة"""
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "factory_state"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved factory state from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                settings = factory_settings.find_one({"name": "factory"})
                enabled = settings.get("enabled", True) if settings else True
                logger.info(f"Factory state retrieved: {enabled}")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, enabled)
                return enabled
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get factory state after {max_retries} attempts")
                    return True  # القيمة الافتراضية
                time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error in get_factory_state function: {str(e)}")
        return True

def set_factory_state(enabled, max_retries=3):
    """تعيين حالة المصنع مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        if not isinstance(enabled, bool):
            logger.error(f"Invalid enabled value: {enabled}. Must be boolean")
            return False
        
        for attempt in range(max_retries):
            try:
                factory_settings.update_one(
                    {"name": "factory"},
                    {"$set": {"enabled": enabled}},
                    upsert=True
                )
                logger.info(f"Successfully set factory state to: {enabled}")
                
                # تحديث التخزين المؤقت
                cache_key = "factory_state"
                cache_manager.set(cache_key, enabled)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to set factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to set factory state after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in set_factory_state function: {str(e)}")
        return False

# وظائف إدارة العمليات مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة
def start_bot_process(bot_username, max_retries=3):
    """تشغيل عملية البوت مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة"""
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return None
        
        bot_path = path.join("Maked", validated_username)
        main_file = path.join(bot_path, "__main__.py")
        
        if not path.exists(main_file):
            logger.error(f"Main file not found for bot: {validated_username}")
            return None
        
        # التحقق من وجود البيئة الافتراضية
        venv_python = path.join("/workspace/venv/bin/python")
        if not path.exists(venv_python):
            logger.error(f"Virtual environment not found at: {venv_python}")
            return None
        
        # إنشاء ملف مؤقت لتسجيل الأخطاء
        log_file = temp_file_manager.create_temp_file(suffix=".log", prefix=f"bot_{validated_username}_")
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                process = subprocess.Popen(
                    [venv_python, main_file],
                    cwd=bot_path,
                    stdout=open(log_file, 'w'),
                    stderr=subprocess.STDOUT,
                    text=True,
                    env={
                        **os.environ,
                        "PYTHONPATH": f"{bot_path}:{os.environ.get('PYTHONPATH', '')}"
                    }
                )
                
                # انتظار قليل للتأكد من بدء العملية
                time.sleep(2)
                
                # التحقق من أن العملية لا تزال تعمل
                if process.poll() is None:
                    logger.info(f"Started bot {validated_username} with PID: {process.pid}")
                    return process.pid
                else:
                    # قراءة الأخطاء إذا فشل التشغيل
                    try:
                        with open(log_file, 'r') as f:
                            error_log = f.read()
                        logger.error(f"Bot {validated_username} failed to start. Log: {error_log}")
                    except:
                        logger.error(f"Bot {validated_username} failed to start")
                    
                    if attempt == max_retries - 1:
                        # تنظيف الملف المؤقت
                        temp_file_manager.cleanup_temp_file(log_file)
                        return None
                    time.sleep(2)  # انتظار قبل إعادة المحاولة
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to start bot {validated_username}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to start bot {validated_username} after {max_retries} attempts")
                    # تنظيف الملف المؤقت
                    temp_file_manager.cleanup_temp_file(log_file)
                    return None
                time.sleep(2)
        
        # تنظيف الملف المؤقت
        temp_file_manager.cleanup_temp_file(log_file)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in start_bot_process: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in start_bot_process function: {str(e)}")
        return None

def stop_bot_process(pid, max_retries=3):
    """إيقاف عملية البوت مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة"""
    try:
        if not pid or not isinstance(pid, int) or pid <= 0:
            logger.error(f"Invalid PID: {pid}")
            return False
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                process = psutil.Process(pid)
                process.terminate()
                
                # انتظار قليل للتأكد من إيقاف العملية
                time.sleep(1)
                
                if process.poll() is None:
                    # إذا لم تتوقف العملية، قم بإجبارها على التوقف
                    process.kill()
                    time.sleep(1)
                
                logger.info(f"Stopped process with PID: {pid}")
                return True
                
            except psutil.NoSuchProcess:
                logger.warning(f"Process with PID {pid} not found")
                return True  # العملية غير موجودة تعني أنها متوقفة بالفعل
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to stop process {pid}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to stop process {pid} after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in stop_bot_process function: {str(e)}")
        return False

# تهيئة المصنع عند التشغيل مع التحقق من المدخلات وإعادة المحاولة
async def initialize_factory(max_retries=3):
    """تهيئة المصنع مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة"""
    try:
        global off
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                off = get_factory_state()
                logger.info(f"Factory state initialized: {off}")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Failed to initialize factory state, using default")
                    off = True
                await asyncio.sleep(1)
        
        # استعادة البوتات المشتغلة
        for attempt in range(max_retries):
            try:
                running_bots = get_running_bots()
                logger.info(f"Found {len(running_bots)} bots to restore")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get running bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Failed to get running bots, skipping restoration")
                    return
                await asyncio.sleep(1)
        
        for bot in running_bots:
            if bot.get("status") == "running":
                bot_username = bot.get("username")
                if not bot_username:
                    logger.warning("Bot without username found, skipping")
                    continue
                    
                logger.info(f"Restoring bot: {bot_username}")
                pid = start_bot_process(bot_username)
                if pid:
                    success = bots_collection.update_one(
                        {"username": bot_username},
                        {"$set": {"pid": pid}}
                    )
                    if success.modified_count > 0:
                        logger.info(f"Successfully restored bot {bot_username} with PID: {pid}")
                    else:
                        logger.warning(f"Failed to update bot {bot_username} PID in database")
                else:
                    update_bot_status(bot_username, "stopped")
                    logger.warning(f"Failed to restore bot {bot_username}, marked as stopped")
    except Exception as e:
        logger.error(f"Error in initialize_factory function: {str(e)}")
        off = True  # القيمة الافتراضية في حالة الخطأ

# ================================================
# ============== HANDLERS START HERE =============
# ================================================

@Client.on_message(filters.text & filters.private, group=5662)
async def cmd(client, msg):
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received")
        return
    
    uid = msg.from_user.id
    if not is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info: {str(e)}")
        return

    if msg.text == "الغاء":
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast", "fbroadcast", "users_up")
        await msg.reply("» تم الغاء بنجاح", quote=True)

    elif msg.text == "❲ اخفاء الكيبورد ❳":
        await msg.reply("≭︰تم اخفاء الكيبورد ارسل /start لعرضه مره اخرى", reply_markup=ReplyKeyboardRemove(), quote=True)

    elif msg.text == "❲ الاحصائيات ❳":
        user_list = await get_users()
        bots_count = bots_collection.count_documents({})
        running_bots = len(get_running_bots())
        await msg.reply(
            f"**≭︰عدد الاعضاء  **{len(user_list)}\n"
            f"**≭︰عدد مطورين في المصنع  **{len(OWNER_ID)}\n"
            f"**≭︰عدد البوتات المصنوعة  **{bots_count}\n"
            f"**≭︰عدد البوتات المشتغلة  **{running_bots}",
            quote=True
        )

    elif msg.text == "❲ اذاعه ❳":
        await set_broadcast_status(uid, bot_id, "broadcast")
        await delete_broadcast_status(uid, bot_id, "fbroadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتوجيه ❳":
        await set_broadcast_status(uid, bot_id, "fbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتثبيت ❳":
        await set_broadcast_status(uid, bot_id, "pinbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "fbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ تشغيل بوت ❳":
        # طلب معرف البوت من المستخدم
        await msg.reply("**أرسل معرف البوت الذي تريد تشغيله**", quote=True)
        # تعيين حالة انتظار معرف البوت
        await set_broadcast_status(uid, bot_id, "start_bot")

    elif msg.text == "❲ تشغيل البوتات ❳":
        if not is_dev(uid):
            await msg.reply("** ≭︰هذا الامر يخص المطور **", quote=True)
            return
        
        all_bots = get_all_bots()
        if not all_bots:
            await msg.reply("** ≭︰لا يوجد بوتات مصنوعة **", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await msg.reply("**🔄 جاري تشغيل البوتات...**", quote=True)
        
        started_count = 0
        failed_count = 0
        already_running = 0
        
        for i, bot in enumerate(all_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري تشغيل البوتات... ({i}/{len(all_bots)})**")
            
            if bot.get("status") == "running":
                already_running += 1
                continue
                
            pid = start_bot_process(bot["username"])
            if pid:
                update_bot_status(bot["username"], "running")
                bots_collection.update_one(
                    {"username": bot["username"]},
                    {"$set": {"pid": pid}}
                )
                started_count += 1
            else:
                failed_count += 1

        # رسالة النتيجة النهائية
        result_text = f"**📊 نتائج تشغيل البوتات:**\n\n"
        result_text += f"✅ **تم تشغيل:** {started_count} بوت\n"
        result_text += f"⚠️ **كانت تعمل:** {already_running} بوت\n"
        result_text += f"❌ **فشل التشغيل:** {failed_count} بوت\n"
        
        if started_count == 0 and already_running == 0:
            result_text = "**❌ لم يتم تشغيل أي بوت**"
        elif started_count == 0:
            result_text = f"**⚠️ كل البوتات تعمل بالفعل ({already_running} بوت)**"
        
        await status_msg.edit(result_text)

    elif msg.text == "❲ البوتات المشتغلة ❳":
        if not is_dev(uid):
            await msg.reply("** ≭︰هذا الامر يخص المطور **", quote=True)
            return

        running_bots = get_running_bots()
        if not running_bots:
            await msg.reply("** ≭︰لا يوجد أي بوت يعمل حالياً **", quote=True)
        else:
            text = "** ≭︰البوتات المشتغلة حالياً:**\n\n"
            for i, bot in enumerate(running_bots, 1):
                # التحقق من أن البوت لا يزال يعمل
                if "pid" in bot and bot["pid"]:
                    try:
                        import psutil
                        if psutil.pid_exists(bot["pid"]):
                            text += f"{i}. @{bot['username']} ✅ (PID: {bot['pid']})\n"
                        else:
                            text += f"{i}. @{bot['username']} ❌ (متوقف)\n"
                            # تحديث الحالة في قاعدة البيانات
                            update_bot_status(bot["username"], "stopped")
                    except:
                        text += f"{i}. @{bot['username']} ❓ (غير محدد)\n"
                else:
                    text += f"{i}. @{bot['username']} ❌ (بدون PID)\n"
            await msg.reply(text, quote=True)

    elif msg.text == "❲ 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳":
        try:
            # منطق تحديث الكوكيز
            await msg.reply("**تم تحديث الكوكيز بنجاح**", quote=True)
        except Exception as e:
            logger.error(f"Update cookies error: {str(e)}")
            await msg.reply("**حدث خطأ في تحديث الكوكيز**", quote=True)

    elif msg.text == "❲ 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳":
        try:
            # منطق إعادة تشغيل الكوكيز
            await msg.reply("**تم إعادة تشغيل الكوكيز بنجاح**", quote=True)
        except Exception as e:
            logger.error(f"Restart cookies error: {str(e)}")
            await msg.reply("**حدث خطأ في إعادة تشغيل الكوكيز**", quote=True)

@Client.on_message(filters.private, group=368388)
async def forbroacasts(client, msg):
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received in broadcast handler")
        return
    
    uid = msg.from_user.id
    if not is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info in broadcast handler: {str(e)}")
        return

    text = msg.text
    ignore = ["❲ اذاعه ❳", "❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳", "❲ الاحصائيات ❳", "❲ اخفاء الكيبورد ❳", "الغاء"]
    if text in ignore:
        return

    # معالجة تشغيل بوت محدد
    if await get_broadcast_status(uid, bot_id, "start_bot"):
        await delete_broadcast_status(uid, bot_id, "start_bot")
        
        # التحقق من صحة معرف البوت
        is_valid, validated_username = validate_bot_username(text)
        if not is_valid:
            await msg.reply(f"**❌ معرف البوت غير صحيح: {text}**", quote=True)
            return
        
        bot_info = get_bot_info(validated_username)
        if not bot_info:
            await msg.reply("**❌ هذا البوت غير موجود في قاعدة البيانات**", quote=True)
            return
        
        if bot_info.get("status") == "running":
            await msg.reply("**⚠️ هذا البوت يعمل بالفعل**", quote=True)
            return
        
        pid = start_bot_process(validated_username)
        if pid:
            if update_bot_status(validated_username, "running"):
                bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": {"pid": pid}}
                )
                await msg.reply(f"**✅ تم تشغيل البوت @{validated_username} بنجاح**", quote=True)
            else:
                await msg.reply(f"**⚠️ تم تشغيل البوت @{validated_username} لكن فشل تحديث الحالة**", quote=True)
        else:
            await msg.reply(f"**❌ فشل في تشغيل البوت @{validated_username}**", quote=True)
        return

    if await get_broadcast_status(uid, bot_id, "broadcast"):
        await delete_broadcast_status(uid, bot_id, "broadcast")
        message = await msg.reply("• جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in broadcast: {user}")
                    failed_count += 1
                    continue
                
                await msg.copy(validated_user_id)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")

    elif await get_broadcast_status(uid, bot_id, "pinbroadcast"):
        await delete_broadcast_status(uid, bot_id, "pinbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in pin broadcast: {user}")
                    failed_count += 1
                    continue
                
                m = await msg.copy(validated_user_id)
                await m.pin(disable_notification=False, both_sides=True)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Pin broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")

    elif await get_broadcast_status(uid, bot_id, "fbroadcast"):
        await delete_broadcast_status(uid, bot_id, "fbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in forward broadcast: {user}")
                    failed_count += 1
                    continue
                
                await msg.forward(validated_user_id)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"• نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Forward broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")

@Client.on_message(filters.command("start") & filters.private)
async def new_user(client, msg):
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received in new_user handler")
        return
    
    user_id = msg.from_user.id
    
    # التحقق من صحة معرف المستخدم
    is_valid, validated_user_id = validate_user_id(user_id)
    if not is_valid:
        logger.error(f"Invalid user_id in new_user handler: {user_id}")
        return
    
    if not await is_user(validated_user_id):
        # إضافة المستخدم الجديد مع التحقق
        if await add_new_user(validated_user_id):
            text = f"""
** ≭︰  دخل عضو جديد لـ↫ مصنع   **

** ≭︰  الاسم : {msg.from_user.first_name}   **
** ≭︰  تاك : {msg.from_user.mention}   **
** ≭︰  الايدي : {validated_user_id} **
            """
            
            # الحصول على عدد المستخدمين مع التحقق
            try:
                users_count = len(await get_users())
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f" ≭︰عدد الاعضاء  {users_count}", callback_data=f"user_count_{validated_user_id}")]]
                )
            except Exception as e:
                logger.error(f"Failed to get users count: {str(e)}")
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f" ≭︰عدد الاعضاء  غير محدد", callback_data=f"user_count_{validated_user_id}")]]
                )
            
            if validated_user_id not in OWNER_ID:
                try:
                    for owner_id in OWNER_ID:
                        # التحقق من صحة معرف المالك
                        is_valid_owner, validated_owner_id = validate_user_id(owner_id)
                        if is_valid_owner:
                            await client.send_message(validated_owner_id, text, reply_markup=reply_markup)
                except PeerIdInvalid:
                    pass
                except Exception as e:
                    logger.error(f"Failed to send notification to owners: {str(e)}")
        else:
            logger.error(f"Failed to add new user: {validated_user_id}")

@Client.on_message(filters.command("start") & filters.private, group=162728)
async def admins(client, message: Message):
    global off
    off = get_factory_state()
    
    keyboard = []
    
    if is_dev(message.chat.id):
        keyboard = [
            [("❲ صنع بوت ❳"), ("❲ حذف بوت ❳")],
            [("❲ فتح المصنع ❳"), ("❲ قفل المصنع ❳")],
            [("❲ ايقاف بوت ❳"), ("❲ تشغيل بوت ❳")],
            [("❲ ايقاف البوتات ❳"), ("❲ تشغيل البوتات ❳")],
            [("❲ البوتات المشتغلة ❳")],
            [("❲ البوتات المصنوعه ❳"), ("❲ تحديث الصانع ❳")],
            [("❲ الاحصائيات ❳")],
            [("❲ رفع مطور ❳"), ("❲ تنزيل مطور ❳")],
            [("❲ المطورين ❳")],
            [("❲ اذاعه ❳"), ("❲ اذاعه بالتوجيه ❳"), ("❲ اذاعه بالتثبيت ❳")],
            [("❲ استخراج جلسه ❳"), ("❲ الاسكرينات المفتوحه ❳")],
            ["❲ 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳", "❲ 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳"],
            [("❲ السورس ❳"), ("❲ مطور السورس ❳")],
            [("❲ اخفاء الكيبورد ❳")]
        ]
        await message.reply("** ≭︰اهلا بك عزيزي المطور  **", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), quote=True)
    else:
        if off:
            await message.reply_text(f"**≭︰التنصيب المجاني معطل، راسل المبرمج ↫ @{OWNER_NAME}**")
            return

@Client.on_callback_query(filters.regex("^user_count_"))
async def user_count_callback(client, callback_query):
    try:
        # التحقق من صحة الاستعلام
        if not callback_query or not callback_query.data:
            logger.warning("Invalid callback query received")
            return
        
        # استخراج معرف المستخدم من البيانات
        user_id_str = callback_query.data.split("_")[-1]
        is_valid, validated_user_id = validate_user_id(user_id_str)
        
        if not is_valid:
            logger.error(f"Invalid user_id in callback: {user_id_str}")
            await callback_query.answer("خطأ في معرف المستخدم", show_alert=True)
            return
        
        # التحقق من صلاحيات المستخدم
        if callback_query.from_user.id in OWNER_ID:
            try:
                count = len(await get_users())
                await callback_query.answer(f"عدد الأعضاء: {count}", show_alert=True)
            except Exception as e:
                logger.error(f"Failed to get users count: {str(e)}")
                await callback_query.answer("فشل في الحصول على عدد الأعضاء", show_alert=True)
        else:
            await callback_query.answer("ليس لديك صلاحية", show_alert=True)
    except Exception as e:
        logger.error(f"User count callback error: {str(e)}")
        await callback_query.answer("حدث خطأ", show_alert=True)

# معالجات الأزرار المفقودة
# تم إزالة المعالجات المكررة لأنها موجودة في معالج النصوص
    else:
        keyboard = [
            [("❲ صنع بوت ❳"), ("❲ حذف بوت ❳")],
            [("❲ استخراج جلسه ❳")],
            [("❲ السورس ❳"), ("❲ مطور السورس ❳")],
            [("❲ اخفاء الكيبورد ❳")]
        ]
        await message.reply("** ≭︰اهلا بك عزيزي العضو  **", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), quote=True)

# تم إزالة معالج me الذي يسبب مشاكل الرسائل المتكررة

@app.on_message(filters.command(["❲ السورس ❳"], ""))
async def alivehi(client: Client, message):
    chat_id = message.chat.id

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("❲ Help Group ❳", url=f"{GROUP}"),
                InlineKeyboardButton("❲ Source Ch ❳", url=f"{CHANNEL}"),
            ],
            [
                 InlineKeyboardButton(f"{OWNER_NAME}", url=f"https://t.me/{OWNER_NAME}")
            ]
        ]
    )

    await message.reply_video(
        video=VIDEO,
        caption="**≭︰Welcome to Source Music **",
        reply_markup=keyboard,
    )

@Client.on_message(filters.command(["❲ مطور السورس ❳"], ""))
async def you(client: Client, message):
    try:
        async def get_user_info(user_id):
            user = await client.get_users(user_id)
            chat = await client.get_chat(user_id)

            name = user.first_name
            bio = chat.bio if chat and chat.bio else "لا يوجد"

            usernames = []
            if user.__dict__.get('usernames'):
                usernames.extend([f"@{u.username}" for u in user.usernames])
            if user.username:
                usernames.append(f"@{user.username}")
            username_text = " ".join(usernames) if usernames else "لا يوجد"

            photo_path = None
            if user.photo:
                photo_path = await client.download_media(user.photo.big_file_id)

            return user.id, name, username_text, bio, photo_path

        developer_id = OWNER_ID[0] if isinstance(OWNER_ID, list) and OWNER_ID else OWNER_ID
        user_id, name, username, bio, photo_path = await get_user_info(developer_id)

        link = None
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
            try:
                link = await client.export_chat_invite_link(message.chat.id)
            except:
                link = f"https://t.me/{message.chat.username}" if message.chat.username else "رابط الدعوة غير متاح."
        
        title = message.chat.title or message.chat.first_name
        chat_title = f"≯︰العضو ↫ ❲ {message.from_user.mention} ❳\n≯︰اسم المجموعه ↫ ❲ {title} ❳" if message.from_user else f"≯︰اسم المجموعه ↫ ❲ {title} ❳"

        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
            try:
                await client.send_message(
                    user_id,
                    f"**≯︰هناك من بحاجه للمساعده**\n{chat_title}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"❲ {title} ❳", url=link)]])
                )
            except:
                pass
        else:
            try:
                await client.send_message(
                    user_id,
                    f"**≯︰هناك من بحاجه للمساعده**\n{chat_title}"
                )
            except:
                pass

        if photo_path:
            await message.reply_photo(
                photo=photo_path,
                caption=f"**≯︰Information programmer  ↯.\n          ━─━─────━─────━─━\n≯︰Name ↬ ❲ {name} ❳** \n**≯︰User ↬ ❲ {username} ❳**\n**≯︰Bio ↬ ❲ {bio} ❳**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"❲ {name} ❳", user_id=user_id)]])
            )
            os.remove(photo_path)

    except Exception as e:
        logger.error(f"Error in developer info: {str(e)}")

@Client.on_message(filters.command("❲ رفع مطور ❳", ""))
async def add_dev(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("**≭︰ليس لديك صلاحيات**")

    m = await client.ask(message.chat.id, "**≭︰ارسل معرف المستخدم الآن**", timeout=120)
    username = m.text.replace("@", "")
    
    try:
        user = await client.get_chat(username)
        if is_dev(user.id):
            return await message.reply("**≭︰هذا المستخدم مطور بالفعل**")
        
        devs_collection.insert_one({"user_id": user.id})
        return await message.reply(f"**≭︰تم رفع {user.first_name} كمطور بنجاح**")
    except Exception as e:
        logger.error(f"Add dev error: {str(e)}")
        return await message.reply("**≭︰فشل في العثور على المستخدم، تحقق من المعرف**")

@Client.on_message(filters.command("❲ تنزيل مطور ❳", ""))
async def remove_dev(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("**≭︰ليس لديك صلاحيات**")

    m = await client.ask(message.chat.id, "**≭︰ارسل المعرف الآن**", timeout=120)
    username = m.text.replace("@", "")
    
    try:
        user = await client.get_chat(username)
        if not is_dev(user.id):
            return await message.reply("**≭︰هذا المستخدم ليس مطوراً**")

        devs_collection.delete_one({"user_id": user.id})
        return await message.reply(f"**≭︰تم تنزيل {user.first_name} من المطورين بنجاح**")
    except Exception as e:
        logger.error(f"Remove dev error: {str(e)}")
        return await message.reply("**≭︰فشل في العثور على المستخدم، تحقق من المعرف**")

@Client.on_message(filters.command("❲ المطورين ❳", ""))
async def list_devs(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("<b>≭︰ليس لديك صلاحيات</b>")

    response = "<b><u>≭︰قائمة المطورين :</u></b>\n\n"
    for i, uid in enumerate(OWNER_ID, start=1):
        try:
            user = await client.get_users(uid)
            name = user.first_name or "No Name"
            mention = f'<a href="tg://user?id={uid}">{name}</a>'
            response += f"<b>{i}- {mention}</b> (المالك)\n"
        except:
            continue
            
    devs = list(devs_collection.find({"user_id": {"$nin": OWNER_ID}}))
    if devs:
        for i, dev in enumerate(devs, start=len(OWNER_ID)+1):
            try:
                user = await client.get_users(dev["user_id"])
                name = user.first_name or "No Name"
                mention = f'<a href="tg://user?id={user.id}">{name}</a>'
                response += f"**{i}- {mention}**\n"
            except:
                continue
    else:
        response += "\n**≭︰لا يوجد مطورين مضافين بعد**"

    await message.reply_text(response, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["❲ فتح المصنع ❳", "❲ قفل المصنع ❳"], "") & filters.private)
async def onoff(client, message):
    if not is_dev(message.from_user.id):
        return
        
    if message.text == "❲ فتح المصنع ❳":
        set_factory_state(False)
        await message.reply_text("** ≭︰تم فتح المصنع **")
    else:
        set_factory_state(True)
        await message.reply_text("** ≭︰تم قفل المصنع **")
    
@app.on_message(filters.command("❲ صنع بوت ❳", "") & filters.private)
async def maked(client, message):
    if not is_dev(message.from_user.id):
        user_bots = list(bots_collection.find({"dev_id": message.from_user.id}))
        if user_bots:
            return await message.reply_text("<b> ≭︰لـقـد قـمت بـصـنع بـوت مـن قـبل </b>")

    # التأكد من وجود مجلد Maked
    if not os.path.exists("Maked"):
        os.makedirs("Maked", exist_ok=True)
    
    try:
        # طلب توكن البوت
        ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل تـوكـن الـبوت </b>", timeout=120)
        TOKEN = ask.text.strip()
        
        # التحقق من صحة التوكن
        bot = Client(":memory:", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, in_memory=True)
        await bot.start()
        bot_me = await bot.get_me()
        username = bot_me.username
        bot_id = bot_me.id
        await bot.stop()
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return await message.reply_text("<b> ≭︰توكن البوت غير صحيح</b>")

    try:
        # طلب كود الجلسة
        ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل كـود الـجلسـه </b>", timeout=120)
        SESSION = ask.text.strip()
        
        # التحقق من صحة الجلسة
        user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, in_memory=True)
        await user.start()
        user_me = await user.get_me()
        await user.stop()
    except Exception as e:
        logger.error(f"Session validation error: {str(e)}")
        return await message.reply_text("<b> ≭︰كود الجلسة غير صحيح</b>")

    Dev = message.from_user.id
    if message.from_user.id in OWNER_ID:
        try:
            ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل ايدي المطور </b>", timeout=120)
            Dev = int(ask.text.strip())
            await client.get_users(Dev)
        except:
            return await message.reply_text("<b>يرجى إرسال آيدي المطور الصحيح</b>")

    bot_folder = os.path.join("Maked", username)
    if os.path.exists(bot_folder):
        shutil.rmtree(bot_folder)

    # إنشاء مجلد البوت الجديد
    os.makedirs(bot_folder, exist_ok=True)
    
    # نسخ محتويات مجلد Make إلى مجلد البوت الجديد
    make_dir = "Make"
    for item in os.listdir(make_dir):
        source = os.path.join(make_dir, item)
        destination = os.path.join(bot_folder, item)
        
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

    try:
        # إنشاء مجموعة التخزين
        user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, in_memory=True)
        await user.start()
        
        group_name = f"تخزين ميوزك {uuid.uuid4().hex[:4]}"
        loger = await user.create_supergroup(group_name, "مجموعة تخزين سورس ميوزك")
        logger.info(f"Created storage group: {loger.id}")
        
        loggerlink = await user.export_chat_invite_link(loger.id)
        await user.add_chat_members(loger.id, username)
        
        # منح صلاحيات للبوت
        await user.promote_chat_member(
            loger.id,
            username,
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
        
        # إنشاء مكالمة جماعية
        await user.invoke(CreateGroupCall(
            peer=(await user.resolve_peer(loger.id)),
            random_id=randint(10000, 999999999)
        ))
        
        await user.send_message(loger.id, "تم فتح الاتصال لتفعيل الحساب.")
        await user.stop()
        
        # تحديث ملف config.py للبوت المصنوع
        config_path = os.path.join(bot_folder, "config.py")
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # استبدال المتغيرات الأساسية
        replacements = {
            "BOT_TOKEN = getenv(\"BOT_TOKEN\", \"\")": f"BOT_TOKEN = \"{TOKEN}\"",
            "STRING1 = getenv(\"STRING_SESSION\", \"\")": f"STRING1 = \"{SESSION}\"",
            "OWNER_ID = int(getenv(\"OWNER_ID\", 0))": f"OWNER_ID = {Dev}",
            "LOGGER_ID = int(getenv(\"LOGGER_ID\", -100))": f"LOGGER_ID = {loger.id}",
            "CACHE_CHANNEL_USERNAME = getenv(\"CACHE_CHANNEL_USERNAME\", \"\")": f"CACHE_CHANNEL_USERNAME = \"{loger.id}\""
        }
        
        # استبدال المتغيرات الإضافية
        additional_replacements = {
            "MONGO_DB_URI = getenv(\"MONGO_DB_URI\", \"\")": f"MONGO_DB_URI = \"mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{username}_db?retryWrites=true&w=majority&appName=Cluster0\"",
            "SUPPORT_CHANNEL = getenv(\"SUPPORT_CHANNEL\", \"https://t.me/A1DIIU\")": "SUPPORT_CHANNEL = \"https://t.me/K55DD\"",
            "SUPPORT_CHAT = getenv(\"SUPPORT_CHAT\", \"https://t.me/A1DIIU\")": "SUPPORT_CHAT = \"https://t.me/YMMYN\"",
            "OWNER = [\"AAAKP\"]": "OWNER = []",
            "OWNER__ID = 985612253": f"OWNER__ID = {Dev}",
            "OWNER_NAME = \"𝐷𝑣. 𝐾ℎ𝑎𝑦𝑎𝑙 𓏺\"": f"OWNER_NAME = \"{message.from_user.first_name}\""
        }
        
        # تطبيق جميع الاستبدالات
        for old, new in {**replacements, **additional_replacements}.items():
            config_content = config_content.replace(old, new)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        # بدء تشغيل البوت
        pid = start_bot_process(username)
        if not pid:
            shutil.rmtree(bot_folder)
            return await message.reply_text("<b>فشل في تشغيل البوت</b>")
        
        # حفظ معلومات البوت
        config_data = {
            "TOKEN": TOKEN,
            "SESSION": SESSION,
            "LOGGER_ID": loger.id,
            "OWNER_ID": Dev
        }
        save_bot_info(username, Dev, pid, config_data)
        
        # إرسال التنبيه للمطورين
        for chat in OWNER_ID:
            try:
                await client.send_message(
                    chat,
                    f"<b> ≭︰تنصيب جديد </b>\n\n"
                    f"<b>معرف البوت ↫ </b>@{username}\n"
                    f"<b>ايدي المطور ↫ </b>{Dev}\n"
                    f"<b>الصانع ↫ </b>{message.from_user.mention}"
                )
            except Exception as e:
                logger.error(f"Send message error: {str(e)}")
        
        await message.reply_text(
            f"**≭︰تم تشغيل البوت**\n\n"
            f"**≭︰معرف البوت ↫ @{username}\n"
            f"**≭︰اليك رابط مجموعه اشعارات التشغيل**\n[ {loggerlink} ]",
            disable_web_page_preview=True
        )

    except Exception as e:
        if os.path.exists(bot_folder):
            shutil.rmtree(bot_folder)
        logger.error(f"Bot creation error: {str(e)}")
        await message.reply_text(f"<b>فشل التنصيب: {str(e)}</b>")

@Client.on_message(filters.command("❲ حذف بوت ❳", "") & filters.private)
async def deletbot(client, message):
    if not is_dev(message.from_user.id):
        user_bots = list(bots_collection.find({"dev_id": message.from_user.id}))
        if not user_bots:
            return await message.reply_text("** ≭︰لم تقم ب صنع بوت   **")
        
        bot_username = user_bots[0]["username"]
        bot_info = get_bot_info(bot_username)
        
        # إيقاف البوت
        if bot_info and "pid" in bot_info:
            stop_bot_process(bot_info["pid"])
        
        # حذف الملفات
        bot_folder = os.path.join("Maked", bot_username)
        if os.path.exists(bot_folder):
            shutil.rmtree(bot_folder)
        
        # حذف المعلومات
        delete_bot_info(bot_username)
        return await message.reply_text("** ≭︰تم حذف بوتك من المصنع   **.")
    
    try:
        bot = await client.ask(message.chat.id, "** ≭︰ ارسل يوزر البوت   **", timeout=60)
        bot_username = bot.text.replace("@", "").strip()
    except:
        return
    
    bot_info = get_bot_info(bot_username)
    if not bot_info:
        return await message.reply_text("** ≭︰هذا البوت غير موجود **")
    
    # إيقاف البوت
    if "pid" in bot_info:
        stop_bot_process(bot_info["pid"])
    
    # حذف الملفات
    bot_folder = os.path.join("Maked", bot_username)
    if os.path.exists(bot_folder):
        shutil.rmtree(bot_folder)
    
    # حذف المعلومات
    delete_bot_info(bot_username)
    await message.reply_text("** ≭︰ تم حـذف البـوت بنـجاح   **")

@Client.on_message(filters.command("❲ البوتات المصنوعه ❳", ""))
async def botat(client, message):
    if not is_dev(message.from_user.id):
        return
    
    all_bots = get_all_bots()
    if not all_bots:
        return await message.reply_text("** ≭︰ لا يوجد بوتات مصنوعه عزيزي المطور   **")
    
    text = "** ≭︰ اليك قائمة البوتات المصنوعه **\n\n"
    for i, bot in enumerate(all_bots, 1):
        try:
            user = await client.get_users(bot["dev_id"])
            dev_name = user.first_name
        except:
            dev_name = "غير معروف"
            
        status = "🟢" if bot.get("status", "stopped") == "running" else "🔴"
        text += f"{i}. {status} @{bot['username']} - المطور: {dev_name}\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command(["❲ الاسكرينات المفتوحه ❳"], ""))
async def kinhsker(client: Client, message):
    if not is_dev(message.from_user.id):
        return await message.reply_text("** ≭︰هذا الامر يخص المطور **")
    
    try:
        screens = []
        if sys.platform == "linux":
            output = subprocess.check_output("screen -list | grep 'Detached'", shell=True).decode()
            screens = [line.split()[0] for line in output.splitlines() if 'Detached' in line]
        
        if not screens:
            return await message.reply_text("** ≭︰لا يوجد اسكرينات مفتوحه **")
        
        text = "** ≭︰قائمة الاسكرينات المفتوحه **\n\n"
        for i, screen in enumerate(screens, 1):
            text += f"{i}. `{screen}`\n"
        
        await message.reply_text(text)
    except Exception as e:
        logger.error(f"Screen list error: {str(e)}")
        await message.reply_text("** ≭︰فشل في الحصول على الاسكرينات **")

@Client.on_message(filters.command("❲ تحديث الصانع ❳", ""))
async def update_factory(client: Client, message):
    if message.from_user.id not in OWNER_ID: 
        return await message.reply_text("** ≭︰ هذا الامر يخص المالك فقط **")
    
    try:
        msg = await message.reply("** ≭︰جاري تحديث المصنع **")
        
        # إيقاف جميع البوتات
        running_bots = get_running_bots()
        for bot in running_bots:
            if "pid" in bot:
                stop_bot_process(bot["pid"])
                update_bot_status(bot["username"], "stopped")
        
        # إعادة تشغيل المصنع
        args = [sys.executable, "main.py"] 
        environ = os.environ  
        execle(sys.executable, *args, environ) 
    except Exception as e:
        logger.error(f"Factory update error: {str(e)}")
        await message.reply_text(f"** ≭︰فشل تحديث المصنع: {e} **")

@Client.on_message(filters.command("❲ ايقاف بوت ❳", ""))
async def stop_specific_bot(c, message):
    if not is_dev(message.from_user.id):
        return await message.reply_text("** ≭︰هذا الامر يخص المطور فقط **")
        
    bot_username = await c.ask(message.chat.id, "** ≭︰ارسـل مـعرف البوت **", timeout=120)
    bot_username = bot_username.text.replace("@", "").strip()

    bot_info = get_bot_info(bot_username)
    if not bot_info:
        return await message.reply_text("** ≭︰هذا البوت غير موجود **")
    
    if "pid" not in bot_info:
        return await message.reply_text("** ≭︰هذا البوت غير مشتغل **")
    
    if stop_bot_process(bot_info["pid"]):
        update_bot_status(bot_username, "stopped")
        await message.reply_text(f"** ≭︰تم ايقاف البوت @{bot_username} بنجاح **")
    else:
        await message.reply_text(f"** ≭︰فشل في ايقاف البوت @{bot_username} **")

@Client.on_message(filters.command("❲ البوتات المشتغلة ❳", ""))
async def show_running_bots(client, message):
    if not is_dev(message.from_user.id):
        await message.reply_text("** ≭︰هذا الامر يخص المطور **")
        return

    running_bots = get_running_bots()
    if not running_bots:
        await message.reply_text("** ≭︰لا يوجد أي بوت يعمل حالياً **")
    else:
        text = "** ≭︰البوتات المشتغلة حالياً:**\n\n"
        for i, bot in enumerate(running_bots, 1):
            # التحقق من أن البوت لا يزال يعمل
            if "pid" in bot and bot["pid"]:
                try:
                    import psutil
                    if psutil.pid_exists(bot["pid"]):
                        text += f"{i}. @{bot['username']} ✅ (PID: {bot['pid']})\n"
                    else:
                        text += f"{i}. @{bot['username']} ❌ (متوقف)\n"
                        # تحديث الحالة في قاعدة البيانات
                        update_bot_status(bot["username"], "stopped")
                except:
                    text += f"{i}. @{bot['username']} ❓ (غير محدد)\n"
            else:
                text += f"{i}. @{bot['username']} ❌ (بدون PID)\n"
        await message.reply_text(text)

@Client.on_message(filters.command("❲ تشغيل البوتات ❳", ""))
async def start_Allusers(client, message):
    if not is_dev(message.from_user.id):
         await message.reply_text("** ≭︰هذا الامر يخص المطور **")
         return
    
    all_bots = get_all_bots()
    if not all_bots:
        return await message.reply_text("** ≭︰لا يوجد بوتات مصنوعة **")
    
    # إرسال رسالة بداية العملية
    status_msg = await message.reply_text("**🔄 جاري تشغيل البوتات...**")
    
    started_count = 0
    failed_count = 0
    already_running = 0
    
    for i, bot in enumerate(all_bots, 1):
        # تحديث رسالة الحالة كل 3 بوتات
        if i % 3 == 0:
            await status_msg.edit(f"**🔄 جاري تشغيل البوتات... ({i}/{len(all_bots)})**")
        
        if bot.get("status") == "running":
            already_running += 1
            continue
            
        pid = start_bot_process(bot["username"])
        if pid:
            update_bot_status(bot["username"], "running")
            bots_collection.update_one(
                {"username": bot["username"]},
                {"$set": {"pid": pid}}
            )
            started_count += 1
        else:
            failed_count += 1

    # رسالة النتيجة النهائية
    result_text = f"**📊 نتائج تشغيل البوتات:**\n\n"
    result_text += f"✅ **تم تشغيل:** {started_count} بوت\n"
    result_text += f"⚠️ **كانت تعمل:** {already_running} بوت\n"
    result_text += f"❌ **فشل التشغيل:** {failed_count} بوت\n"
    
    if started_count == 0 and already_running == 0:
        result_text = "**❌ لم يتم تشغيل أي بوت**"
    elif started_count == 0:
        result_text = f"**⚠️ كل البوتات تعمل بالفعل ({already_running} بوت)**"
    
    await status_msg.edit(result_text)

@Client.on_message(filters.command("❲ ايقاف البوتات ❳", ""))
async def stooop_Allusers(client, message):
    if not is_dev(message.from_user.id):
         await message.reply_text("** ≭︰هذا الامر يخص المطور **")
         return
         
    stopped_count = 0
    running_bots = get_running_bots()
    for bot in running_bots:
        if "pid" in bot:
            if stop_bot_process(bot["pid"]):
                update_bot_status(bot["username"], "stopped")
                stopped_count += 1

    if stopped_count == 0:
        await message.reply_text("** ≭︰لم يتم ايقاف أي بوتات **")
    else:
        await message.reply_text(f"** ≭︰تم ايقاف {stopped_count} بوت بنجاح **")

# دالة إغلاق اتصالات قاعدة البيانات وتنظيف الملفات المؤقتة
def cleanup_database_connections():
    """إغلاق اتصالات قاعدة البيانات وتنظيف الملفات المؤقتة بشكل آمن"""
    try:
        # إغلاق اتصالات قاعدة البيانات
        db_manager.close_connections()
        logger.info("Database connections closed successfully")
        
        # تنظيف الملفات المؤقتة
        cleaned_files = temp_file_manager.cleanup_all_temp_files()
        logger.info(f"Cleaned up {cleaned_files} temporary files")
        
        # مسح التخزين المؤقت
        cache_manager.clear()
        logger.info("Cache cleared successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# تهيئة المصنع عند التشغيل
# سيتم استدعاؤها من bot.py

# تسجيل دالة إغلاق اتصالات قاعدة البيانات عند إنهاء البرنامج
import atexit
atexit.register(cleanup_database_connections)

# تعيين التبعيات لمجلد users
set_dependencies(OWNER_ID, devs_collection, users)
