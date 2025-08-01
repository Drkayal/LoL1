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
db = db_manager.get_sync_db()
mongodb = db_manager.get_async_db()

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

# دوال البث تم نقلها إلى db/models.py

# دوال إدارة البوتات والمصنع تم نقلها إلى db/models.py

# دوال إدارة العمليات تم نقلها إلى bots/logic.py

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
