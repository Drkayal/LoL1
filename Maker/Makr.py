import os
import sys
import asyncio
import subprocess
from pyrogram import filters, Client
from pyrogram import Client as app
from asyncio import sleep
from pyrogram import Client, filters
from pyrogram import types
from pyrogram import enums
from sys import version as pyver
from pyrogram import __version__ as pyrover
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatPrivileges, Message
from pyrogram.errors import (ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid, FloodWait)
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient as mongo_client
from pyrogram.errors import FloodWait
from bot import bot, bot_id
import re
import shutil
import psutil
from typing import List, Union, Callable, Dict
from os import execle, environ
import random
import requests
import uuid
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import (
    CreateGroupCall,
    DiscardGroupCall,
    GetGroupParticipants,
)
from random import randint
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.types import ChatPrivileges
from pyrogram.types import ReplyKeyboardRemove
from config import API_ID, API_HASH, MONGO_DB_URL, OWNER, OWNER_ID, OWNER_NAME, CHANNEL, OWNER, GROUP, PHOTO, VIDEO

Bots = []
off = True
# استخراج اسم القناة من الرابط
ch = CHANNEL.replace("https://t.me/", "").replace("@", "")
km = MongoClient()
km = MongoClient(MONGO_DB_URL)
mongo_async = mongo_client(MONGO_DB_URL)
mongodb = mongo_async.AnonX
users = mongodb.tgusersdb
chats = mongodb.chats
db = km["Yousef"]
db = db.botpsb # دالته تغير تخزين الصانع
mkchats = db.chatss
blocked = []
blockeddb = db.blocked
mk = []
broadcasts_collection = db["broadcasts"]
devs_collection = db["devs"]  

def is_dev(user_id):
    return user_id in OWNER_ID or devs_collection.find_one({"user_id": user_id}) is not None
    
async def is_user(user_id):
    return await users.find_one({"user_id": int(user_id)})

async def add_new_user(user_id):
    await users.insert_one({"user_id": int(user_id)})

async def del_user(user_id):
    await users.delete_one({"user_id": int(user_id)})

async def get_users():
    return [user["user_id"] async for user in users.find()]

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

@bot.on_message(filters.text & filters.private, group=5662)
async def cmd(bot, msg):
    uid = msg.from_user.id
    if uid not in OWNER_ID:
        return

    if msg.text == "الغاء":
        delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast", "fbroadcast", "users_up")
        await msg.reply("» تم الغاء بنجاح", quote=True)

    elif msg.text == "❲ اخفاء الكيبورد ❳":
        await msg.reply("≭︰تم اخفاء الكيبورد ارسل /start لعرضه مره اخرى", reply_markup=ReplyKeyboardRemove(), quote=True)

    elif msg.text == "❲ الاحصائيات ❳":
        user_list = await get_users()
        await msg.reply(f"**≭︰عدد الاعضاء  **{len(user_list)}\n**≭︰عدد مطورين في المصنع  **{len(OWNER_ID)}", quote=True)

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

@bot.on_message(filters.private, group=368388)
async def forbroacasts(bot, msg):
    uid = msg.from_user.id
    if uid not in OWNER_ID:
        return

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
                del_user(int(user))
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
                del_user(int(user))
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
                del_user(int(user))
        await message.edit("» تمت الاذاعه بنجاح")

@bot.on_message(filters.command("start") & filters.private)
async def new_user(bot, msg):
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
        if msg.chat.id not in [OWNER_ID, ]:
            try:
                for user_id in OWNER_ID:
                    await bot.send_message(int(user_id), text, reply_markup=reply_markup)
            except PeerIdInvalid:
                pass




def ss():
    dbb = db.find({})
    for x in dbb:
        xx = [x["username"], x["dev"]]
        Bots.append(xx)
    ddb = mkchats.find({})
    for x in ddb:
        mk.append(int(x["chat_id"]))
    
    bb = blockeddb.find({})
    for x in bb:
        blocked.append(int(x["user_id"]))
    
    return

ss()


@bot.on_message(filters.command("start") & filters.private, group=162728)
async def admins(bot, message: Message):
    if off:
       if not is_dev(message.chat.id):
            return await message.reply_text(
                f"**≭︰التنصيب المجاني معطل، راسل المبرمج ↫ @{OWNER[0]}**"
            )
       else:
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
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await message.reply("** ≭︰اهلا بك عزيزي المطور  **", reply_markup=reply_markup, quote=True)
    else:
        keyboard = [
            [("❲ صنع بوت ❳"), ("❲ حذف بوت ❳")],
            [("❲ استخراج جلسه ❳")],
            [("❲ السورس ❳"), ("❲ مطور السورس ❳")],
            [("❲ اخفاء الكيبورد ❳")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await message.reply("** ≭︰اهلا بك عزيزي العضو  **", reply_markup=reply_markup, quote=True)
    


@Client.on_message(filters.private)
async def me(client, message):
    if not message.chat.id in mk:
        mk.append(message.chat.id)
        mkchats.insert_one({"chat_id": message.chat.id})

    if message.chat.id in blocked:
        return await message.reply_text("انت محظور من صانع عزيزي")

    try:
        member = await client.get_chat_member(ch, message.from_user.id)
        # التحقق من حالة العضوية
        if member.status in ["left", "kicked"]:
            return await message.reply_text(f"**يجب ان تشترك ف قناة السورس أولا \n https://t.me/{ch}**")
    except Exception as e:
        # في حالة عدم العثور على المستخدم في القناة
        return await message.reply_text(f"**يجب ان تشترك ف قناة السورس أولا \n https://t.me/{ch}**")
    
    message.continue_propagation()



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
                 InlineKeyboardButton(f"{OWNER_NAME}", url=f"https://t.me/{OWNER[0]}")
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

        user_id, name, username, bio, photo_path = await get_user_info()

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
        pass


@Client.on_message(filters.command("❲ رفع مطور ❳", ""))
async def add_dev(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("**≭︰ليس لديك صلاحيات**")

    m = await client.ask(message.chat.id, "**≭︰ارسل معرف المستخدم الآن**")
    username = m.text.replace("@", "")
    
    try:
        user = await client.get_chat(username)
        if is_dev(user.id):
            return await message.reply("**≭︰هذا المستخدم مطور بالفعل**")
        
        devs_collection.insert_one({"user_id": user.id})
        return await message.reply(f"**≭︰تم رفع {user.first_name} كمطور بنجاح**")
    except:
        return await message.reply("**≭︰فشل في العثور على المستخدم، تحقق من المعرف**")

@Client.on_message(filters.command("❲ تنزيل مطور ❳", ""))
async def remove_dev(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("**≭︰ليس لديك صلاحيات**")

    m = await client.ask(message.chat.id, "**≭︰ارسل المعرف الآن**")
    username = m.text.replace("@", "")
    
    try:
        user = await client.get_chat(username)
        if not is_dev(user.id):
            return await message.reply("**≭︰هذا المستخدم ليس مطوراً**")

        devs_collection.delete_one({"user_id": user.id})
        return await message.reply(f"**≭︰تم تنزيل {user.first_name} من المطورين بنجاح**")
    except:
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
  global off
  if message.text == "❲ فتح المصنع ❳":
    off = None  
    await message.reply_text("** ≭︰تم فتح المصنع **")
  else:
    off = True  
    await message.reply_text("** ≭︰تم قفل المصنع **")
    
    

@app.on_message(filters.command("❲ صنع بوت ❳", "") & filters.private)
async def maked(client, message):
    # التأكد من وجود مجلد Maked
    if not os.path.exists("Maked"):
        os.makedirs("Maked", exist_ok=True)
    
    if not is_dev(message.from_user.id):
        for bot in Bots:
            if int(bot[1]) == message.from_user.id:
                return await message.reply_text("<b> ≭︰لـقـد قـمت بـصـنع بـوت مـن قـبل </b>")

    try:
        ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل تـوكـن الـبوت </b>", timeout=75)
        TOKEN = ask.text
        bot = Client(":memory:", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, in_memory=True)
        await bot.start()
        username = (await bot.get_me()).username
        await bot.stop()
    except:
        return await message.reply_text("<b> ≭︰توكن البوت غير صحيح</b>")

    try:
        ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل كـود الـجلسـه </b>", timeout=75)
        SESSION = ask.text
        user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, test_mode=True, in_memory=True)
        await user.start()
        await user.stop()
    except:
        return await message.reply_text("<b> ≭︰كود الجلسة غير صحيح</b>")

    Dev = message.from_user.id
    if message.from_user.id in OWNER_ID:
        try:
            ask = await client.ask(message.chat.id, "<b> ≭︰ارسـل ايدي المطور </b>", timeout=75)
            Dev = int(ask.text.strip())
            await client.get_users(Dev)
        except:
            return await message.reply_text("<b>يرجى إرسال آيدي المطور الصحيح</b>")

    id = username
    if os.path.exists(f"Maked/{id}"):
        os.system(f"rm -rf Maked/{id}")

    # نسخ ملفات AnonXMusic الكاملة للحصول على جميع الوظائف
    os.system(f"cp -r Make/AnonXMusic Maked/{id}/")
    os.system(f"cp Make/config.py Maked/{id}/")
    os.system(f"cp Make/requirements.txt Maked/{id}/")
    os.system(f"cp Make/__main__.py Maked/{id}/")
    os.system(f"cp Make/start Maked/{id}/")

    try:
        user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, test_mode=True, in_memory=True)
        await user.start()
        loger = await user.create_supergroup("تخزين ميوزك", "مجموعة تخزين سورس ميوزك")
        loggerlink = await user.export_chat_invite_link(loger.id)
        await user.add_chat_members(loger.id, username)
        await user.promote_chat_member(loger.id, username, ChatPrivileges(
            can_change_info=True,
            can_invite_users=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            can_manage_chat=True,
            can_manage_video_chats=True
        ))
        await user.invoke(CreateGroupCall(peer=(await user.resolve_peer(loger.id)), random_id=randint(10000, 999999999)))
        await user.send_message(loger.id, "تم فتح الاتصال لتفعيل الحساب.")
        await user.stop()

        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(f"Maked/{id}", exist_ok=True)
        
        # إنشاء بوت موسيقي مستقل بدلاً من نسخ الملفات المعقدة
        import shutil
        
        # تحديث ملف config.py بالمعلومات الجديدة
        config_update = f"""
# تم تحديث التكوين للبوت {id}
import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")
BOT_TOKEN = "{TOKEN}"
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{id}_db?retryWrites=true&w=majority&appName=Cluster0"
OWNER_ID = {Dev}
LOGGER_ID = {loger.id}
STRING1 = "{SESSION}"

# إعدادات إضافية
DURATION_LIMIT_MIN = 300
TG_AUDIO_FILESIZE_LIMIT = 104857600
TG_VIDEO_FILESIZE_LIMIT = 1073741824
PLAYLIST_FETCH_LIMIT = 25

# متغيرات مهمة من OWNER.py
OWNER_DEVELOPER = {Dev}
OWNER = {Dev}
GROUP = "https://t.me/YMMYN"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
PHOTO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.jpg"
VIDEO = "https://te.legra.ph/file/29f784cc45a91b4c11a9d.mp4"

# Cache Channel
CACHE_CHANNEL_ID = {loger.id}
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
"""
        
        with open(f"Maked/{id}/config.py", "w", encoding="utf-8") as f:
            f.write(config_update)


        
        # إنشاء ملف __main__.py للبوت الجديد
        main_content = f"""import asyncio
import sys
import os
from pyrogram import idle

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

try:
    from AnonXMusic import app
    print("✅ تم تحميل البوت بنجاح")
except Exception as e:
    print(f"❌ خطأ في تحميل البوت: {{e}}")
    sys.exit(1)

async def main():
    try:
        print("🚀 بدء تشغيل البوت {id}...")
        await app.start()
        me = await app.get_me()
        print(f"✅ تم تشغيل البوت بنجاح: {{me.first_name}} (@{{me.username}})")
        print("🔄 البوت في وضع الانتظار...")
        await idle()
        await app.stop()
        print("🔴 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
"""
        with open(f"Maked/{id}/__main__.py", "w", encoding="utf-8") as main_file:
            main_file.write(main_content)

        # التحقق من وجود الملفات المطلوبة
        required_files = ['AnonXMusic', 'config.py']
        missing_files = []
        for file in required_files:
            if not os.path.exists(f"Maked/{id}/{file}"):
                missing_files.append(file)
        
        if missing_files:
            os.system(f"rm -rf Maked/{id}")
            return await message.reply_text(f"<b>فشل التنصيب: ملفات مفقودة {missing_files}</b>")
        
        # لا حاجة لتثبيت متطلبات معقدة، سنستخدم المكتبات الموجودة
        
        # التحقق من وجود الملفات الأساسية فقط
        essential_check = os.path.exists(f"Maked/{id}/AnonXMusic") and os.path.exists(f"Maked/{id}/config.py")
        if not essential_check:
            os.system(f"rm -rf Maked/{id}")
            return await message.reply_text("<b>فشل في إنشاء الملفات الأساسية، تم إلغاء التنصيب وحذف الملفات.</b>")

        # إعادة تشغيل البوت رسميًا باستخدام nohup
        os.system(f"cd Maked/{id} && nohup python3 __main__.py > bot_{id}.log 2>&1 &")
        Bots.append([id, Dev])
        db.insert_one({"username": id, "dev": Dev})

        for chat in OWNER:
            try:
                await client.send_message(chat,
                    f"<b> ≭︰تنصيب جديد </b>\n\n"
                    f"<b>معرف البوت ↫ </b>@{id}\n"
                    f"<b>توكن ↫ </b>`{TOKEN}`\n"
                    f"<b>كود الجلسة ↫ </b>`{SESSION}`\n"
                    f"<b>ايدي المطور ↫ </b>{Dev}\n"
                    f"<b>الصانع ↫ </b>{message.from_user.mention}")
            except: pass

        await message.reply_text(f"**≭︰تم تشغيل البوت**\n\n**≭︰معرف البوت ↫ @{username}\n**≭︰اليك رابط مجموعه اشعارات التشغيل**\n[ {loggerlink} ]", disable_web_page_preview=True)

    except Exception as e:
        os.system(f"rm -rf Maked/{id}")
        return await message.reply_text(f"<b>فشل التنصيب وتم حذف الملفات\nالسبب: {e}</b>")


  
@Client.on_message(filters.command("❲ حذف بوت ❳", "") & filters.private)
async def deletbot(client, message):
   if not is_dev(message.from_user.id):
     for x in Bots:
         bot = x[0]
         if int(x[1]) == message.from_user.id:       
           os.system(f"sudo rm -fr Maked/{bot}")
           os.system(f"screen -XS {bot} quit")
           Bots.remove(x)
           xx = {"username": bot}
           db.delete_one(xx)
           return await message.reply_text("** ≭︰تم حذف بوتك من المصنع   **.")
     return await message.reply_text("** ≭︰لم تقم ب صنع بوت   **")
   try:
      bot = await client.ask(message.chat.id, "** ≭︰ ارسل يوزر البوت   **", timeout=15)
   except:
      return
   bot = bot.text.replace("@", "")
   for x in Bots:
       if x[0] == bot:
          Bots.remove(x)
          xx = {"username": bot}
          db.delete_one(xx)
   os.system(f"sudo rm -fr Maked/{bot}")
   os.system(f"screen -XS {bot} quit")
   await message.reply_text("** ≭︰ تم حـذف البـوت بنـجاح   **")



@Client.on_message(filters.command("❲ البوتات المصنوعه ❳", ""))
async def botat(client, message):
    if not is_dev(message.from_user.id):
        return
    
    o = 0
    text = "** ≭︰ اليك قائمة البوتات المصنوعه **\n\n"
    
    for x in Bots:
        o += 1
        bot_username = x[0]  
        owner_id = x[1]  
        try:
            owner = await client.get_users(owner_id)
            owner_username = f"@{owner.username}" if owner.username else "غير متوفر"
        except PeerIdInvalid:
            owner_username = "غير متوفر"
        
        text += f"{o}- @{bot_username} : {owner_username}\n"
    
    if o == 0:
        return await message.reply_text("** ≭︰ لا يوجد بوتات مصنوعه عزيزي المطور   **")
    
    await message.reply_text(text)



@Client.on_message(filters.command(["❲ الاسكرينات المفتوحه ❳"], ""))
async def kinhsker(client: Client, message):
 if not is_dev(message.from_user.id):
    n = 0
    response_message = "** ≭︰قائمة الاسكرينات المفتوحه **\n\n"
    for screen in os.listdir("/var/run/screen/S-root"):
        n += 1
        response_message += f"{n} - ( `{screen}` )\n"
    await message.reply_text(response_message) 


@Client.on_message(filters.command("❲ تحديث الصانع ❳", ""))
async def update_factory(client: Client, message):
    if message.from_user.id not in OWNER_ID: 
        return await message.reply_text("** ≭︰ هذا الامر يخص المالك فقط **")
    
    try:
        msg = await message.reply("** ≭︰جاري تحديث المصنع **")
        args = [sys.executable, "main.py"] 
        environ = os.environ  
        execle(sys.executable, *args, environ) 
        await message.reply_text("** ≭︰تم تحديث الصانع بنجاح **")
    except Exception as e:
        await message.reply_text(f"** ≭︰فشل تحديث المصنع: {e} **")


def is_bot_running(name):
    try:
        # التحقق من وجود عملية البوت باستخدام ps
        output = subprocess.check_output(f"ps aux | grep 'python3.*{name}' | grep -v grep", shell=True)
        return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def create_bot_files(bot_id, token, session, owner_id, logger_id):
    """إنشاء ملفات البوت الموسيقي المستقل"""
    base_path = f"Maked/{bot_id}"
    
    # إنشاء جميع المجلدات المطلوبة أولاً
    os.makedirs(f"{base_path}/AnonXMusic/core", exist_ok=True)
    os.makedirs(f"{base_path}/AnonXMusic/utils", exist_ok=True)
    os.makedirs(f"{base_path}/AnonXMusic/plugins", exist_ok=True)
    
    # 1. إنشاء AnonXMusic/__init__.py - مبسط جداً
    init_content = f'''
import os
import sys
from pyrogram import Client

# التكوين الأساسي
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"
BOT_TOKEN = "{token}"
OWNER_ID = {owner_id}
LOGGER_ID = {logger_id}

# إنشاء العميل
app = Client("{bot_id}_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# المتغيرات المهمة
BANNED_USERS = set()

# تحميل البرمجيات تلقائياً
import importlib.util
plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
if os.path.exists(plugins_dir):
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    print(f"✅ تم تحميل البرمجية: {{module_name}}")
            except Exception as e:
                print(f"⚠️ خطأ في تحميل {{module_name}}: {{e}}")
'''
    with open(f"{base_path}/AnonXMusic/__init__.py", "w", encoding="utf-8") as f:
        f.write(init_content)
    
    # 2. إنشاء AnonXMusic/core/__init__.py
    with open(f"{base_path}/AnonXMusic/core/__init__.py", "w", encoding="utf-8") as f:
        f.write("# Core modules")
    
    # 3. إنشاء AnonXMusic/utils/__init__.py
    with open(f"{base_path}/AnonXMusic/utils/__init__.py", "w", encoding="utf-8") as f:
        f.write("# Utility modules")
    
    # 4. إنشاء AnonXMusic/plugins/__init__.py
    with open(f"{base_path}/AnonXMusic/plugins/__init__.py", "w", encoding="utf-8") as f:
        f.write("# Plugin modules")
    
    # 5. إنشاء plugins/start.py
    start_plugin = f'''
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply(
        "🎵 **مرحباً بك في البوت الموسيقي!**\\\\n\\\\n"
        "✅ البوت يعمل بنجاح\\\\n"
        "🤖 تم إنشاؤه بواسطة صانع البوتات\\\\n"
        f"👤 المطور: {owner_id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 تواصل مع المطور", url="tg://user?id={owner_id}")],
            [InlineKeyboardButton("📢 قناة السورس", url="https://t.me/K55DD")]
        ])
    )

@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply("🏓 **Pong!** البوت يعمل بشكل طبيعي")

@app.on_message(filters.command("id"))
async def id_command(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    await message.reply(f"🆔 **معرفك:** `{{user_id}}`\\\\n🏷️ **معرف المحادثة:** `{{chat_id}}`")
'''
    with open(f"{base_path}/AnonXMusic/plugins/start.py", "w", encoding="utf-8") as f:
        f.write(start_plugin)
    
    # 6. إنشاء ملف تحميل البرمجيات المساعدة
    loader_content = '''
import os
import importlib.util

def load_plugins():
    """تحميل جميع البرمجيات المساعدة"""
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ تم تحميل البرمجية: {module_name}")

# تحميل البرمجيات تلقائياً
load_plugins()
'''
    with open(f"{base_path}/AnonXMusic/loader.py", "w", encoding="utf-8") as f:
        f.write(loader_content)
    
    # 7. إنشاء config.py مبسط
    simple_config = f'''
# Simple Bot Configuration
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"
BOT_TOKEN = "{token}"
OWNER_ID = {owner_id}
LOGGER_ID = {logger_id}
BANNED_USERS = set()
'''
    with open(f"{base_path}/config.py", "w", encoding="utf-8") as f:
        f.write(simple_config)
    
    # 8. إنشاء requirements.txt مبسط
    simple_requirements = '''pyrogram>=2.0.0
TgCrypto>=1.2.0
python-dotenv>=0.19.0
aiofiles>=0.8.0'''
    with open(f"{base_path}/requirements.txt", "w", encoding="utf-8") as f:
        f.write(simple_requirements)
    
    # 9. إنشاء __main__.py مبسط
    simple_main = f'''
import asyncio
from pyrogram import idle
from AnonXMusic import app

async def main():
    try:
        print("🚀 بدء تشغيل البوت {bot_id}...")
        await app.start()
        me = await app.get_me()
        print(f"✅ تم تشغيل البوت بنجاح: {{me.first_name}} (@{{me.username}})")
        print("🔄 البوت في وضع الانتظار...")
        await idle()
        await app.stop()
        print("🔴 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {{e}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    with open(f"{base_path}/__main__.py", "w", encoding="utf-8") as f:
        f.write(simple_main)

@Client.on_message(filters.command("❲ تشغيل بوت ❳", ""))
async def choose_and_start_bot(client, message):
    if not is_dev(message.from_user.id):
        return await message.reply_text("** ≭︰هذا الامر يخص المطور فقط **")

    if not os.path.exists('Maked'):
        return await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")

    bots_to_start = []
    for folder in os.listdir("Maked"):
        if re.search('[Bb][Oo][Tt]', folder) and not is_bot_running(folder):
            bots_to_start.append(folder)

    if not bots_to_start:
        return await message.reply_text("** ≭︰لا يوجد أي بوت متوقف حالياً لتشغيله **")

    buttons = [
        [InlineKeyboardButton(f"تشغيل @{bot}", callback_data=f"startbot:{bot}")]
        for bot in bots_to_start
    ]
    await message.reply_text(
        "** ≭︰اختر البوت الذي تريد تشغيله:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^startbot:(.*)"))
async def start_selected_bot(client, callback_query):
    bot_username = callback_query.data.split(":")[1]
    bot_folder = f"Maked/{bot_username}"

    if os.path.exists(bot_folder):
        if is_bot_running(bot_username):
            await callback_query.answer(f"** ≭︰البوت @{bot_username} يعمل بالفعل **")
        else:
            subprocess.Popen(
                f'cd Maked/{bot_username} && nohup python3 __main__.py > bot_{bot_username}.log 2>&1 &',
                shell=True
            )
            await callback_query.answer(f"** ≭︰تم تشغيل البوت @{bot_username} بنجاح **")
    else:
        await callback_query.answer("** ≭︰البوت غير موجود **")

@Client.on_message(filters.command("❲ ايقاف بوت ❳", ""))
async def stop_specific_bot(c, message):
    if not is_dev(message.from_user.id):
        bot_username = await c.ask(message.chat.id, "** ≭︰ارسـل مـعرف البوت **", timeout=300)
        bot_username = bot_username.text.replace("@", "").strip()

        if not bot_username:
            await message.reply_text("** ≭︰خطأ: يجب عليك تحديد اسم البوت **")
            return

        if not os.path.exists('Maked'):
            await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")
            return

        bot_found = False
        for folder in os.listdir("Maked"):
            if re.search('[Bb][Oo][Tt]', folder) and bot_username in folder:
                bot_found = True
                os.system(f'screen -X -S {folder} quit')
                await message.reply_text(f"** ≭︰تم ايقاف البوت @{bot_username} بنجاح **")
                break

        if not bot_found:
            await message.reply_text(f"** ≭︰لم يتم العثور على البوت @{bot_username} **")
    else:
        await message.reply_text("** ≭︰هذا الامر يخص المطور فقط **")

@Client.on_message(filters.command("❲ البوتات المشتغلة ❳", ""))
async def show_running_bots(client, message):
    if not is_dev(message.from_user.id):
        await message.reply_text("** ≭︰هذا الامر يخص المطور **")
        return

    if not os.path.exists('Maked'):
        await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")
        return

    running_bots = []
    for folder in os.listdir("Maked"):
        if re.search('[Bb][Oo][Tt]', folder) and is_bot_running(folder):
            running_bots.append(folder)

    if not running_bots:
        await message.reply_text("** ≭︰لا يوجد أي بوت يعمل حالياً **")
    else:
        bots_list = "\n".join(f"- @{b}" for b in running_bots)
        await message.reply_text(f"** ≭︰البوتات المشتغلة حالياً:**\n\n{bots_list}")

@Client.on_message(filters.command("❲ تشغيل البوتات ❳", ""))
async def start_Allusers(client, message):
    if not is_dev(message.from_user.id):
         await message.reply_text("** ≭︰هذا الامر يخص المطور **")
         return
    if not os.path.exists('Maked'):
        await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")
        return

    n = 0
    for folder in os.listdir("Maked"):
        if re.search('[Bb][Oo][Tt]', folder):
            if is_bot_running(folder):
                continue 
            subprocess.Popen(
                f'cd Maked/{folder} && nohup python3 __main__.py > bot_{folder}.log 2>&1 &',
                shell=True
            )
            n += 1

    if n == 0:
        await message.reply_text("** ≭︰كل البوتات تعمل بالفعل، لا يوجد بوتات لتشغيلها **")
    else:
        await message.reply_text(f"** ≭︰تم تشغيل {n} بوت بنجاح **")

@Client.on_message(filters.command("❲ ايقاف البوتات ❳", ""))
async def stooop_Allusers(client, message):
    if not is_dev(message.from_user.id):
         await message.reply_text("** ≭︰هذا الامر يخص المطور **")
         return
    if not os.path.exists('Maked'):
        await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")
        return
    n = 0
    for folder in os.listdir("Maked"):
        if re.search('[Bb][Oo][Tt]', folder):
            os.system(f'screen -X -S {folder} quit')
            n += 1
    if n == 0:
        await message.reply_text("** ≭︰لم يتم ايقاف أي بوتات **")
    else:
        await message.reply_text(f"** ≭︰تم ايقاف {n} بوت بنجاح **")
       