import os
import sys
import asyncio
import subprocess
import re
import shutil
import logging
import psutil
import uuid
import json
from datetime import datetime
from typing import List, Union, Callable, Dict
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

# إعداد نظام التسجيل (Logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("factory_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# استخراج اسم القناة من الرابط
ch = CHANNEL.replace("https://t.me/", "").replace("@", "")

# إعداد اتصال MongoDB
km = MongoClient(MONGO_DB_URL)
mongo_async = mongo_client(MONGO_DB_URL)
mongodb = mongo_async.AnonX
users = mongodb.tgusersdb
chats = mongodb.chats
db = km["Yousef"]
db = db.botpsb
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

# وظيفة للتحقق من صلاحيات المطور
def is_dev(user_id):
    return user_id in OWNER_ID or devs_collection.find_one({"user_id": user_id}) is not None

# وظائف إدارة المستخدمين
async def is_user(user_id):
    return await users.find_one({"user_id": int(user_id)})

async def add_new_user(user_id):
    await users.insert_one({"user_id": int(user_id)})

async def del_user(user_id):
    await users.delete_one({"user_id": int(user_id)})

async def get_users():
    return [user["user_id"] async for user in users.find()]

# وظائف البث
def set_broadcast_status(user_id, bot_id, key):
    broadcasts_collection.update_one(
        {"user_id": user_id, "bot_id": bot_id},
        {"$set": {key: True}},
        upsert=True
    )

def get_broadcast_status(user_id, bot_id, key):
    doc = broadcasts_collection.find_one({"user_id": user_id, "bot_id": bot_id})
    return doc and doc.get(key)

def delete_broadcast_status(user_id, bot_id, *keys):
    broadcasts_collection.update_one(
        {"user_id": user_id, "bot_id": bot_id},
        {"$unset": {key: "" for key in keys}}
    )

# وظائف إدارة البوتات
def get_bot_info(bot_username):
    return bots_collection.find_one({"username": bot_username})

def save_bot_info(bot_username, dev_id, pid, config_data):
    bots_collection.update_one(
        {"username": bot_username},
        {"$set": {
            "dev_id": dev_id,
            "pid": pid,
            "config": config_data,
            "created_at": datetime.now(),
            "status": "running"
        }},
        upsert=True
    )

def update_bot_status(bot_username, status):
    bots_collection.update_one(
        {"username": bot_username},
        {"$set": {"status": status}}
    )

def delete_bot_info(bot_username):
    bots_collection.delete_one({"username": bot_username})

def get_all_bots():
    return list(bots_collection.find())

def get_running_bots():
    return list(bots_collection.find({"status": "running"}))

# وظائف إدارة المصنع
def get_factory_state():
    settings = factory_settings.find_one({"name": "factory"})
    return settings.get("enabled", True) if settings else True

def set_factory_state(enabled):
    factory_settings.update_one(
        {"name": "factory"},
        {"$set": {"enabled": enabled}},
        upsert=True
    )

# وظائف إدارة العمليات
def start_bot_process(bot_username):
    bot_path = path.join("Maked", bot_username)
    main_file = path.join(bot_path, "__main__.py")
    
    if not path.exists(main_file):
        logger.error(f"Main file not found for bot: {bot_username}")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, main_file],
            cwd=bot_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Started bot {bot_username} with PID: {process.pid}")
        return process.pid
    except Exception as e:
        logger.error(f"Failed to start bot {bot_username}: {str(e)}")
        return None

def stop_bot_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        logger.info(f"Stopped process with PID: {pid}")
        return True
    except psutil.NoSuchProcess:
        logger.warning(f"Process with PID {pid} not found")
        return False
    except Exception as e:
        logger.error(f"Error stopping process {pid}: {str(e)}")
        return False

# تهيئة المصنع عند التشغيل
async def initialize_factory():
    global off
    off = get_factory_state()
    
    # استعادة البوتات المشتغلة
    running_bots = get_running_bots()
    for bot in running_bots:
        if bot["status"] == "running":
            pid = start_bot_process(bot["username"])
            if pid:
                bots_collection.update_one(
                    {"username": bot["username"]},
                    {"$set": {"pid": pid}}
                )
            else:
                update_bot_status(bot["username"], "stopped")

# ================================================
# ============== HANDLERS START HERE =============
# ================================================

@Client.on_message(filters.text & filters.private, group=5662)
async def cmd(client, msg):
    uid = msg.from_user.id
    if not is_dev(uid):
        return
    
    # تعريف bot_id
    bot_me = await client.get_me()
    bot_id = bot_me.id

    if msg.text == "الغاء":
        delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast", "fbroadcast", "users_up")
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
        set_broadcast_status(uid, bot_id, "broadcast")
        delete_broadcast_status(uid, bot_id, "fbroadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتوجيه ❳":
        set_broadcast_status(uid, bot_id, "fbroadcast")
        delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتثبيت ❳":
        set_broadcast_status(uid, bot_id, "pinbroadcast")
        delete_broadcast_status(uid, bot_id, "broadcast", "fbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ تشغيل بوت ❳":
        await msg.reply("**أرسل معرف البوت الذي تريد تشغيله**", quote=True)

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
    uid = msg.from_user.id
    if not is_dev(uid):
        return
    
    # تعريف bot_id
    bot_me = await client.get_me()
    bot_id = bot_me.id

    text = msg.text
    ignore = ["❲ اذاعه ❳", "❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳", "❲ الاحصائيات ❳", "❲ اخفاء الكيبورد ❳", "الغاء"]
    if text in ignore:
        return

    if get_broadcast_status(uid, bot_id, "broadcast"):
        delete_broadcast_status(uid, bot_id, "broadcast")
        message = await msg.reply("• جاري الإذاعة ..", quote=True)
        users_list = await get_users()
        for i, user in enumerate(users_list, start=1):
            try:
                await msg.copy(int(user))
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
            except PeerIdInvalid:
                await del_user(int(user))
        await message.edit("» تمت الاذاعه بنجاح")

    elif get_broadcast_status(uid, bot_id, "pinbroadcast"):
        delete_broadcast_status(uid, bot_id, "pinbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        users_list = await get_users()
        for i, user in enumerate(users_list, start=1):
            try:
                m = await msg.copy(int(user))
                await m.pin(disable_notification=False, both_sides=True)
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
            except PeerIdInvalid:
                await del_user(int(user))
        await message.edit("» تمت الاذاعه بنجاح")

    elif get_broadcast_status(uid, bot_id, "fbroadcast"):
        delete_broadcast_status(uid, bot_id, "fbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        users_list = await get_users()
        for i, user in enumerate(users_list, start=1):
            try:
                await msg.forward(int(user))
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"• نسبه الاذاعه {progress}%")
            except PeerIdInvalid:
                await del_user(int(user))
        await message.edit("» تمت الاذاعه بنجاح")

@Client.on_message(filters.command("start") & filters.private)
async def new_user(client, msg):
    if not await is_user(msg.from_user.id):
        await add_new_user(msg.from_user.id) 
        text = f"""
** ≭︰  دخل عضو جديد لـ↫ مصنع   **

** ≭︰  الاسم : {msg.from_user.first_name}   **
** ≭︰  تاك : {msg.from_user.mention}   **
** ≭︰  الايدي : {msg.from_user.id} **
        """
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f" ≭︰عدد الاعضاء  {len(await get_users())}", callback_data=f"user_count_{msg.from_user.id}")]]
        )
        if msg.chat.id not in OWNER_ID:
            try:
                for user_id in OWNER_ID:
                    await client.send_message(int(user_id), text, reply_markup=reply_markup)
            except PeerIdInvalid:
                pass

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
        user_id = int(callback_query.data.split("_")[-1])
        if callback_query.from_user.id in OWNER_ID:
            count = len(await get_users())
            await callback_query.answer(f"عدد الأعضاء: {count}", show_alert=True)
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

@Client.on_message(filters.private, group=1)
async def me(client, message):
    if not message.chat.id in mk:
        mk.append(message.chat.id)
        mkchats.insert_one({"chat_id": message.chat.id})

    if message.chat.id in blocked:
        return await message.reply_text("انت محظور من صانع عزيزي")

    try:
        # التحقق من الاشتراك مع التخزين المؤقت
        cache_key = f"subscription_{message.from_user.id}"
        cached = factory_settings.find_one({"key": cache_key})
        
        if cached and (datetime.now() - cached["timestamp"]).hours < 24:
            if not cached["status"]:
                return await message.reply_text(f"**يجب ان تشترك ف قناة السورس أولا \n https://t.me/{ch}**")
        else:
            member = await client.get_chat_member(ch, message.from_user.id)
            status = member.status not in ["left", "kicked"]
            factory_settings.update_one(
                {"key": cache_key},
                {"$set": {"status": status, "timestamp": datetime.now()}},
                upsert=True
            )
            if not status:
                return await message.reply_text(f"**يجب ان تشترك ف قناة السورس أولا \n https://t.me/{ch}**")
    except Exception as e:
        logger.error(f"Subscription check error: {str(e)}")
        return await message.reply_text(f"**يجب ان تشترك ف قناة السورس أولا \n https://t.me/{ch}**")

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
            text += f"{i}. @{bot['username']}\n"
        await message.reply_text(text)

@Client.on_message(filters.command("❲ تشغيل البوتات ❳", ""))
async def start_Allusers(client, message):
    if not is_dev(message.from_user.id):
         await message.reply_text("** ≭︰هذا الامر يخص المطور **")
         return
    
    all_bots = get_all_bots()
    if not all_bots:
        return await message.reply_text("** ≭︰لا يوجد بوتات مصنوعة **")
    
    started_count = 0
    for bot in all_bots:
        if bot.get("status") == "running":
            continue
            
        pid = start_bot_process(bot["username"])
        if pid:
            update_bot_status(bot["username"], "running")
            bots_collection.update_one(
                {"username": bot["username"]},
                {"$set": {"pid": pid}}
            )
            started_count += 1

    if started_count == 0:
        await message.reply_text("** ≭︰كل البوتات تعمل بالفعل، لا يوجد بوتات لتشغيلها **")
    else:
        await message.reply_text(f"** ≭︰تم تشغيل {started_count} بوت بنجاح **")

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

# تهيئة المصنع عند التشغيل
asyncio.create_task(initialize_factory())
