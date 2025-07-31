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
from config import API_ID, API_HASH, MONGO_DB_URL, OWNER, OWNER_ID, OWNER_NAME, CHANNEL, GROUP, PHOTO, VIDEO

Bots = []
off = True
# استخراج اسم القناة من الرابط
ch = CHANNEL.replace("https://t.me/", "").replace("@", "")
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
        if msg.chat.id not in OWNER_ID:
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
                f"**≭︰التنصيب المجاني معطل، راسل المبرمج ↫ @{OWNER_NAME}**"
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

        # الحصول على معرف المطور من OWNER_ID
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

    # إنشاء المجلد أولاً قبل النسخ
    os.makedirs(f"Maked/{id}", exist_ok=True)

    # نسخ ملفات AnonXMusic الكاملة للحصول على جميع الوظائف
    os.system(f"cp -r Make/AnonXMusic Maked/{id}/")
    os.system(f"cp -r Make/strings Maked/{id}/")
    os.system(f"cp -r Make/cookies Maked/{id}/")
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

        
        # إنشاء بوت موسيقي مستقل بدلاً من نسخ الملفات المعقدة
        import shutil
        
        # تحديث ملف config.py بالمعلومات الجديدة
        config_update = f"""import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"

# Get your token from @BotFather on Telegram.
BOT_TOKEN = "{TOKEN}"

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{id}_db?retryWrites=true&w=majority&appName=Cluster0"

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# Chat id of a group for logging bot's activities
LOGGER_ID = {loger.id}

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = {Dev}

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
# Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/K55DD")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/YMMYN")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", "True"))

# ============================================
# إعدادات النظام الذكي الجديد
# ============================================

# قناة التخزين الذكي (للتخزين في قناة تيليجرام)
CACHE_CHANNEL_USERNAME = getenv("CACHE_CHANNEL_USERNAME", "mccckc")

# تحويل يوزر القناة إلى الشكل المناسب
CACHE_CHANNEL_ID = {loger.id}
if CACHE_CHANNEL_USERNAME:
    # إذا كان ID رقمي، نحوله للصيغة الصحيحة
    if CACHE_CHANNEL_USERNAME.isdigit() or (CACHE_CHANNEL_USERNAME.startswith('-') and CACHE_CHANNEL_USERNAME[1:].isdigit()):
        try:
            channel_id = int(CACHE_CHANNEL_USERNAME)
            if not str(channel_id).startswith('-100') and channel_id > 0:
                CACHE_CHANNEL_ID = f"-100{{channel_id}}"
            else:
                CACHE_CHANNEL_ID = str(channel_id)
        except ValueError:
            CACHE_CHANNEL_ID = {loger.id}
    # إذا كان يوزر، نتركه كما هو
    elif CACHE_CHANNEL_USERNAME.startswith('@') or not CACHE_CHANNEL_USERNAME.startswith('-'):
        # إزالة @ إن وجدت
        username = CACHE_CHANNEL_USERNAME.replace('@', '')
        CACHE_CHANNEL_ID = f"@{{username}}"
    else:
        # صيغة ID مباشرة
        CACHE_CHANNEL_ID = CACHE_CHANNEL_USERNAME

# ============================================
# YouTube Data API Keys (متعددة للتدوير)
# ============================================
YT_API_KEYS_ENV = getenv("YT_API_KEYS", "[]")
try:
    import json
    YT_API_KEYS = json.loads(YT_API_KEYS_ENV) if YT_API_KEYS_ENV != "[]" else []
except:
    YT_API_KEYS = []

# مفاتيح افتراضية (تحديث مطلوب)
if not YT_API_KEYS:
    YT_API_KEYS = [
        "AIzaSyA3x5N5DNYzd5j7L7JMn9XsUYil32Ak77U", "AIzaSyDw09GqGziUHXZ3FjugOypSXD7tedWzIzQ"
        # أضف مفاتيحك هنا
    ]

# ============================================
# خوادم Invidious الأفضل (محدثة 2025)
# ============================================
INVIDIOUS_SERVERS_ENV = getenv("INVIDIOUS_SERVERS", "[]")
try:
    import json
    INVIDIOUS_SERVERS = json.loads(INVIDIOUS_SERVERS_ENV) if INVIDIOUS_SERVERS_ENV != "[]" else []
except:
    INVIDIOUS_SERVERS = []

# خوادم افتراضية محدثة (مجربة ديسمبر 2024 - يناير 2025)
if not INVIDIOUS_SERVERS:
    INVIDIOUS_SERVERS = [
        "https://inv.nadeko.net",           # 🥇 الأفضل - 99.666% uptime
        "https://invidious.nerdvpn.de",     # 🥈 ممتاز - 100% uptime  
        "https://yewtu.be",                 # 🥉 جيد - 89.625% uptime
        "https://invidious.f5.si",          # ⚡ سريع - Cloudflare
        "https://invidious.materialio.us",  # 🌟 موثوق
        "https://invidious.reallyaweso.me", # 🚀 سريع
        "https://iteroni.com",              # ⚡ جيد
        "https://iv.catgirl.cloud",         # 😸 ممتاز
        "https://youtube.alt.tyil.nl",      # 🇳🇱 هولندا
    ]

# ============================================
# إعدادات ملفات الكوكيز المتعددة
# ============================================
COOKIES_FILES_ENV = getenv("COOKIES_FILES", "[]")
try:
    import json
    COOKIES_FILES = json.loads(COOKIES_FILES_ENV) if COOKIES_FILES_ENV != "[]" else []
except:
    COOKIES_FILES = []

# مسارات افتراضية لملفات الكوكيز
if not COOKIES_FILES:
    import os
    cookies_dir = "cookies"
    if os.path.exists(cookies_dir):
        COOKIES_FILES = [
            f"{{cookies_dir}}/cookies1.txt",
            f"{{cookies_dir}}/cookies2.txt", 
            f"{{cookies_dir}}/cookies3.txt",
            f"{{cookies_dir}}/cookies4.txt",
            f"{{cookies_dir}}/cookies5.txt"
        ]
        # فلترة الملفات الموجودة فقط
        COOKIES_FILES = [f for f in COOKIES_FILES if os.path.exists(f)]
    else:
        # ملف واحد افتراضي للتوافق
        COOKIES_FILES = ["cookies.txt"] if os.path.exists("cookies.txt") else []

# ============================================
# إعدادات الكوكيز (التوافق مع الكود القديم)
# ============================================
COOKIE_METHOD = "browser"
COOKIE_FILE = COOKIES_FILES[0] if COOKIES_FILES else "cookies.txt"

# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes

# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = "{SESSION}"
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

BANNED_USERS = filters.user()
adminlist = {{}}
lyrical = {{}}
votemode = {{}}
autoclean = []
confirmer = {{}}

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

DURATION_LIMIT = int(time_to_seconds(f"{{DURATION_LIMIT_MIN}}:00"))

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
        print(f"🚀 بدء تشغيل البوت {id}...")
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
           os.system(f"pkill -f 'Maked/{bot}'")
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
   os.system(f"pkill -f 'Maked/{bot}'")
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
        return await message.reply_text("** ≭︰هذا الامر يخص المطور **")
    
    n = 0
    response_message = "** ≭︰قائمة الاسكرينات المفتوحه **\n\n"
    try:
        for screen in os.listdir("/var/run/screen/S-root"):
            n += 1
            response_message += f"{n} - ( `{screen}` )\n"
        await message.reply_text(response_message)
    except:
        await message.reply_text("** ≭︰لا يوجد اسكرينات مفتوحه **")


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
        # البحث عن العملية باستخدام طرق متعددة
        # 1. البحث في مجلد البوت
        output1 = subprocess.check_output(f"ps aux | grep 'Maked/{name}' | grep -v grep", shell=True)
        if len(output1.strip()) > 0:
            return True
        
        # 2. البحث عن اسم البوت في العملية
        output2 = subprocess.check_output(f"ps aux | grep '{name}' | grep python3 | grep -v grep", shell=True)
        if len(output2.strip()) > 0:
            return True
            
        return False
    except subprocess.CalledProcessError:
        return False

@Client.on_message(filters.command("❲ ايقاف بوت ❳", ""))
async def stop_specific_bot(c, message):
    if not is_dev(message.from_user.id):
        return await message.reply_text("** ≭︰هذا الامر يخص المطور فقط **")
        
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
            os.system(f'pkill -f "Maked/{folder}"')
            await message.reply_text(f"** ≭︰تم ايقاف البوت @{bot_username} بنجاح **")
            break

    if not bot_found:
        await message.reply_text(f"** ≭︰لم يتم العثور على البوت @{bot_username} **")

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
            # إيقاف البوت باستخدام pkill بدلاً من screen
            result = os.system(f'pkill -f "Maked/{folder}"')
            if result == 0:
                n += 1
    if n == 0:
        await message.reply_text("** ≭︰لم يتم ايقاف أي بوتات **")
    else:
        await message.reply_text(f"** ≭︰تم ايقاف {n} بوت بنجاح **")       