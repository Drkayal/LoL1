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

# استيراد دوال قاعدة البيانات من مجلد db
from db import (
    # Database Manager
    db_manager,
    get_sync_db,
    get_async_db,
    close_connections,
    
    # Utility Functions
    clear_bot_cache,
    clear_factory_cache,
    get_database_stats,
    set_collections as set_db_collections
)

# استيراد دوال المصنع من مجلد factory
from factory import (
    # Settings Functions
    get_factory_state,
    set_factory_state,
    set_collections as set_factory_collections
)

# استيراد دوال البوتات من مجلد bots
from bots import (
    # Logic Functions
    start_bot_process,
    stop_bot_process,
    initialize_factory,
    
    # Model Functions
    get_bot_info,
    save_bot_info,
    update_bot_status,
    delete_bot_info,
    get_all_bots,
    get_running_bots,
    set_collections as set_bots_collections
)

# استيراد معالجات الأوامر من مجلد handlers
from handlers import (
    # Command Handlers
    cmd_handler,
    new_user_handler,
    admins_handler,
    user_count_callback_handler,
    alivehi_handler,
    you_handler,
    add_dev_handler,
    remove_dev_handler,
    list_devs_handler,
    onoff_handler,
    botat_handler,
    kinhsker_handler,
    update_factory_handler,
    show_running_bots_handler,
    start_Allusers_handler,
    stooop_Allusers_handler,
    
    # Broadcast Handlers
    forbroacasts_handler
)

# استيراد دوال البث من مجلد broadcast
from broadcast import (
    # Status Functions
    set_broadcast_status,
    get_broadcast_status,
    delete_broadcast_status,
    set_collections as set_broadcast_collections
)

# استخراج اسم القناة من الرابط
ch = CHANNEL.replace("https://t.me/", "").replace("@", "")

# أنواع الأخطاء المخصصة تم نقلها إلى utils/errors.py

# مدير التخزين المؤقت تم نقله إلى utils/cache.py

# مدير قاعدة البيانات تم نقله إلى db/manager.py

# مدير الملفات المؤقتة تم نقله إلى utils/tempfiles.py

# مدير التأخير تم نقله إلى utils/rate_limit.py

# تهيئة المجموعات باستخدام مدير قاعدة البيانات الجديد
db = None
mongodb = None

users = None
chats = None
mkchats = None
blocked = []
blockeddb = None
broadcasts_collection = None
devs_collection = None
bots_collection = None
factory_settings = None

# حالة المصنع الافتراضية
off = True
mk = []  # قائمة المحادثات

# وظائف التحقق من المدخلات مع أنواع الأخطاء المخصصة
# دوال التحقق من المدخلات تم نقلها إلى users/validation.py

# دوال إدارة المستخدمين تم نقلها إلى users/logic.py

# دوال البث تم نقلها إلى db/models.py

# دوال إدارة البوتات والمصنع تم نقلها إلى db/models.py

# دوال إدارة العمليات تم نقلها إلى bots/logic.py

# ================================================
# ============== HANDLERS START HERE =============
# ================================================

# معالج الأوامر الرئيسية تم نقله إلى handlers/commands.py

# باقي معالجات الأوامر تم نقلها إلى handlers/commands.py

# معالج البث تم نقله إلى handlers/broadcast.py

# جميع المعالجات تم نقلها إلى مجلد handlers

# معالج السورس تم نقله إلى handlers/commands.py

# معالج مطور السورس تم نقله إلى handlers/commands.py

# معالج رفع مطور تم نقله إلى handlers/commands.py




# دالة إغلاق اتصالات قاعدة البيانات وتنظيف الملفات المؤقتة
def cleanup_database_connections():
    """إغلاق اتصالات قاعدة البيانات وتنظيف الملفات المؤقتة بشكل آمن"""
    try:
        # إغلاق اتصالات قاعدة البيانات
        close_connections()
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

# تعيين المجموعات لمجلد db
set_db_collections(broadcasts_collection, bots_collection, factory_settings)

# تعيين المجموعات لمجلد bots
set_bots_collections(bots_collection, factory_settings)

# تعيين المجموعات لمجلد broadcast
set_broadcast_collections(broadcasts_collection)

# تعيين المجموعات لمجلد factory
set_factory_collections(factory_settings)

# تعيين التبعيات لمعالجات الأوامر
from handlers.commands import set_dependencies as set_commands_dependencies
from handlers.broadcast import set_dependencies as set_broadcast_dependencies

set_commands_dependencies(OWNER_ID, bots_collection)
set_broadcast_dependencies(bots_collection)
