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

# استيراد الوحدات المتقدمة الجديدة
try:
    from core.monitoring import monitoring_dashboard
    from core.ui_manager import ui_manager
    from core.notification_system import notification_system, NotificationLevel, NotificationType
    ADVANCED_FEATURES_AVAILABLE = True
    print("✅ تم تحميل الميزات المتقدمة بنجاح")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"⚠️ لم يتم تحميل الميزات المتقدمة: {e}")

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
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                # الحصول على بيانات لوحة المراقبة
                dashboard_data = monitoring_dashboard.generate_dashboard_data()
                
                # تنسيق الرسالة باستخدام واجهة المستخدم المحسنة
                stats_text = ui_manager.format_stats_message(dashboard_data)
                
                # إنشاء لوحة مفاتيح الإحصائيات
                keyboard = ui_manager.create_stats_keyboard()
                
                await msg.reply(stats_text, reply_markup=keyboard, quote=True)
                
            except Exception as e:
                print(f"خطأ في عرض الإحصائيات المتقدمة: {e}")
                # العودة للإحصائيات البسيطة
                user_list = await get_users()
                await msg.reply(f"**≭︰عدد الاعضاء  **{len(user_list)}\n**≭︰عدد مطورين في المصنع  **{len(OWNER_ID)}", quote=True)
        else:
            # الإحصائيات التقليدية
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
    user_id = message.chat.id
    user_name = message.from_user.first_name
    is_developer = is_dev(user_id)
    
    if off:
       if not is_developer:
            return await message.reply_text(
                f"**≭︰التنصيب المجاني معطل، راسل المبرمج ↫ @{OWNER_NAME}**"
            )
       else:
            # استخدام الواجهة المحسنة إذا كانت متاحة
            if ADVANCED_FEATURES_AVAILABLE:
                # تعيين عميل الإشعارات
                notification_system.set_client(bot)
                
                # اشتراك المطورين في الإشعارات
                notification_system.subscribe(user_id, [
                    NotificationLevel.INFO,
                    NotificationLevel.WARNING,
                    NotificationLevel.ERROR,
                    NotificationLevel.CRITICAL,
                    NotificationLevel.SUCCESS
                ])
                
                # تنسيق رسالة الترحيب المحسنة
                welcome_text = ui_manager.format_welcome_message(user_name, True)
                reply_markup = ui_manager.create_main_keyboard(True)
                
                # بدء نظام المراقبة إذا لم يكن مفعلاً
                if not monitoring_dashboard.monitoring_active:
                    try:
                        from core.process_manager import process_manager
                        asyncio.create_task(monitoring_dashboard.start_monitoring(process_manager))
                    except ImportError:
                        pass
                
            else:
                # الواجهة التقليدية
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
                welcome_text = "** ≭︰اهلا بك عزيزي المطور  **"
            
            await message.reply(welcome_text, reply_markup=reply_markup, quote=True)
    else:
        # للمستخدمين العاديين
        if ADVANCED_FEATURES_AVAILABLE:
            welcome_text = ui_manager.format_welcome_message(user_name, False)
            reply_markup = ui_manager.create_main_keyboard(False)
        else:
            keyboard = [
                [("❲ صنع بوت ❳"), ("❲ حذف بوت ❳")],
                [("❲ استخراج جلسه ❳")],
                [("❲ السورس ❳"), ("❲ مطور السورس ❳")],
                [("❲ اخفاء الكيبورد ❳")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            welcome_text = "** ≭︰اهلا بك عزيزي العضو  **"
        
        await message.reply(welcome_text, reply_markup=reply_markup, quote=True)
    


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
    """دالة صناعة البوتات المحسنة"""
    
    # استيراد الوحدات المحسنة
    try:
        from core.bot_factory import BotFactory, BotCreationError
        from core.process_manager import process_manager
    except ImportError as e:
        logger.error(f"خطأ في استيراد الوحدات المحسنة: {e}")
        return await message.reply_text("❌ خطأ في تحميل وحدات النظام")
    
    # التأكد من وجود مجلد Maked
    if not os.path.exists("Maked"):
        os.makedirs("Maked", exist_ok=True)
    
    # التحقق من صلاحيات المستخدم
    user_id = message.from_user.id
    if not is_dev(user_id):
        for bot in Bots:
            if int(bot[1]) == user_id:
                return await message.reply_text("**≭︰لـقـد قـمت بـصـنع بـوت مـن قـبل**")

    # إنشاء مصنع البوتات
    bot_factory = BotFactory(
        api_id=API_ID,
        api_hash=API_HASH,
        mongo_url=MONGO_DB_URL
    )
    
    progress_msg = None
    
    async def update_progress(status: str):
        """تحديث رسالة التقدم"""
        nonlocal progress_msg
        try:
            if progress_msg:
                await progress_msg.edit_text(f"**🔄 جاري إنشاء البوت...**\n\n{status}")
            else:
                progress_msg = await message.reply_text(f"**🔄 جاري إنشاء البوت...**\n\n{status}")
        except:
            pass
    
    try:
        # طلب توكن البوت
        await update_progress("⏳ في انتظار توكن البوت...")
        ask = await client.ask(
            message.chat.id, 
            "**≭︰ أرسل توكن البوت**\n\n"
            "💡 يمكنك الحصول على التوكن من @BotFather\n"
            "⚠️ تأكد من صحة التوكن قبل الإرسال", 
            timeout=120
        )
        bot_token = ask.text.strip()
        
        # طلب كود الجلسة
        await update_progress("⏳ في انتظار كود الجلسة...")
        ask = await client.ask(
            message.chat.id, 
            "**≭︰ أرسل كود الجلسة**\n\n"
            "💡 يمكنك الحصول على الجلسة من @StringFatherBot\n"
            "⚠️ تأكد من صحة الجلسة قبل الإرسال", 
            timeout=120
        )
        session_string = ask.text.strip()
        
        # تحديد المطور
        owner_id = user_id
        if user_id in OWNER_ID:
            try:
                ask = await client.ask(
                    message.chat.id, 
                    "**≭︰ أرسل معرف المطور**\n\n"
                    "💡 أرسل معرف المطور الذي سيملك البوت\n"
                    "⚠️ أو اتركه فارغاً لتكون أنت المالك", 
                    timeout=60
                )
                if ask.text.strip().isdigit():
                    owner_id = int(ask.text.strip())
                    # التحقق من صحة المعرف
                    await client.get_users(owner_id)
            except:
                pass  # استخدام المعرف الافتراضي
        
        # بدء عملية إنشاء البوت
        success, bot_info, error_msg = await bot_factory.create_bot(
            bot_token=bot_token,
            session_string=session_string,
            owner_id=owner_id,
            progress_callback=update_progress
        )
        
        if success and bot_info:
            # إضافة البوت لقائمة البوتات
            Bots.append([bot_info['username'], owner_id])
            db.insert_one({"username": bot_info['username'], "dev": owner_id})
            
            # إرسال رسالة النجاح
            success_text = f"""**✅ تم إنشاء البوت بنجاح!**

🤖 **معرف البوت:** @{bot_info['username']}
👑 **المطور:** {owner_id}
📝 **مجموعة السجلات:** {bot_info['logger_group']['invite_link']}
🎵 **نوع البوت:** موسيقى متقدم
⚡ **الحالة:** يعمل الآن

**🎉 البوت جاهز للاستخدام!**
**يمكنك الآن إضافته لمجموعاتك والاستمتاع بالموسيقى**"""
            
            if progress_msg:
                await progress_msg.edit_text(success_text)
            else:
                await message.reply_text(success_text)
                
            # إرسال إشعار للمطورين
            for owner in OWNER:
                try:
                    await client.send_message(
                        owner,
                        f"**🔔 تنصيب جديد**\n\n"
                        f"**البوت:** @{bot_info['username']}\n"
                        f"**المطور:** {owner_id}\n"
                        f"**المنشئ:** {message.from_user.mention}\n"
                        f"**الوقت:** {asyncio.get_event_loop().time()}"
                    )
                except:
                    pass
                    
        else:
            # فشل في الإنشاء
            error_text = f"**❌ فشل في إنشاء البوت**\n\n**السبب:** {error_msg or 'خطأ غير معروف'}"
            if progress_msg:
                await progress_msg.edit_text(error_text)
            else:
                await message.reply_text(error_text)
                
    except BotCreationError as e:
        error_text = f"**❌ خطأ في صناعة البوت**\n\n**التفاصيل:** {str(e)}"
        if progress_msg:
            await progress_msg.edit_text(error_text)
        else:
            await message.reply_text(error_text)
            
    except asyncio.TimeoutError:
        error_text = "**⏰ انتهت مهلة الانتظار**\n\nيرجى المحاولة مرة أخرى والإجابة في الوقت المحدد"
        if progress_msg:
            await progress_msg.edit_text(error_text)
        else:
            await message.reply_text(error_text)
            
    except Exception as e:
        logger.error(f"خطأ غير متوقع في صناعة البوت: {e}")
        error_text = f"**❌ خطأ غير متوقع**\n\n**التفاصيل:** {str(e)}"
        if progress_msg:
            await progress_msg.edit_text(error_text)
        else:
            await message.reply_text(error_text)

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
    
    # التأكد من صحة ملف Youtube.py بعد النسخ
    try:
        import ast
        with open(f'Maked/{id}/AnonXMusic/platforms/Youtube.py', 'r') as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ تم نسخ Youtube.py بنجاح للبوت {id}")
    except SyntaxError as e:
        print(f"❌ خطأ في Youtube.py للبوت {id}: {e}")
        # إعادة نسخ الملف مرة أخرى
        os.system(f"cp Make/AnonXMusic/platforms/Youtube.py Maked/{id}/AnonXMusic/platforms/Youtube.py")
        print(f"🔄 تم إعادة نسخ Youtube.py للبوت {id}")
    except Exception as e:
        print(f"❌ خطأ آخر في فحص Youtube.py: {e}")
    
    # التأكد من صحة ملف Youtube.py بعد النسخ
    try:
        import ast
        with open(f'Maked/{id}/AnonXMusic/platforms/Youtube.py', 'r') as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ تم نسخ Youtube.py بنجاح للبوت {id}")
    except SyntaxError as e:
        print(f"❌ خطأ في Youtube.py للبوت {id}: {e}")
        # إعادة نسخ الملف مرة أخرى
        os.system(f"cp Make/AnonXMusic/platforms/Youtube.py Maked/{id}/AnonXMusic/platforms/Youtube.py")
        print(f"🔄 تم إعادة نسخ Youtube.py للبوت {id}")
    except Exception as e:
        print(f"❌ خطأ آخر في فحص Youtube.py: {e}")
    os.system(f"cp -r Make/strings Maked/{id}/")
    os.system(f"cp -r Make/cookies Maked/{id}/")
    os.system(f"cp Make/config.py Maked/{id}/")
    os.system(f"cp Make/requirements.txt Maked/{id}/")
    os.system(f"cp Make/__main__.py Maked/{id}/")
    os.system(f"cp Make/start Maked/{id}/")

    try:
        user = Client("user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, in_memory=True)
        await user.start()
        loger = await user.create_supergroup("تخزين ميوزك", "مجموعة تخزين سورس ميوزك")
        
        # طباعة معرف المجموعة للتأكد
        print(f"🆔 معرف مجموعة السجل: {loger.id}")
        print(f"📝 سيتم حفظ LOGGER_ID كـ: {loger.id}")
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
        
        # إنشاء قالب config.py محسن وآمن
        config_template = f"""import re
import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# تحميل متغيرات البيئة
load_dotenv()

# =======================================
# إعدادات قاعدة البيانات
# =======================================
MONGO_DB_URI = "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/{id}_db?retryWrites=true&w=majority&appName=Cluster0"

# =======================================
# إعدادات Telegram API
# =======================================
API_ID = int(getenv("API_ID", "17490746"))
API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")

# =======================================
# إعدادات البوت
# =======================================
BOT_TOKEN = "{{BOT_TOKEN}}"

# مدة الحد الأقصى للمقاطع (بالدقائق)
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))

# معرف مجموعة السجلات
LOGGER_ID = {{LOGGER_ID}}

# معرف المالك
OWNER_ID = {Dev}

# =======================================
# التحقق من البيانات الحرجة
# =======================================
if not BOT_TOKEN or BOT_TOKEN == "{{BOT_TOKEN}}":
    raise ValueError("❌ BOT_TOKEN غير محدد بشكل صحيح")

if not LOGGER_ID or LOGGER_ID == "{{LOGGER_ID}}":
    raise ValueError("❌ LOGGER_ID غير محدد بشكل صحيح")

if not OWNER_ID:
    raise ValueError("❌ OWNER_ID غير محدد بشكل صحيح")

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
STRING1 = "{SESSION}"
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
            # استبدال المتغيرات في القالب بشكل آمن
            try:
                final_config = config_template.replace("{{BOT_TOKEN}}", TOKEN)
                final_config = final_config.replace("{{LOGGER_ID}}", str(loger.id))
                final_config = final_config.replace("{SESSION}", SESSION)
                
                # التحقق من نجاح الاستبدال
                if "{{BOT_TOKEN}}" in final_config or "{{LOGGER_ID}}" in final_config:
                    raise ValueError("فشل في استبدال المتغيرات في قالب التكوين")
                
                f.write(final_config)
                print(f"✅ تم إنشاء ملف config.py للبوت {id} بنجاح")
                print(f"   🔑 BOT_TOKEN: {TOKEN[:20]}...")
                print(f"   📝 LOGGER_ID: {loger.id}")
                print(f"   👑 OWNER_ID: {Dev}")
                
            except Exception as e:
                raise Exception(f"خطأ في إنشاء ملف config.py: {e}")


        
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

# أمر التنبيهات الجديد
@Client.on_message(filters.command("❲ التنبيهات ❳", ""))
async def show_notifications(client, message):
    """عرض التنبيهات الأخيرة"""
    if not is_dev(message.from_user.id):
        await message.reply_text("**≭︰هذا الامر يخص المطور**")
        return
    
    if not ADVANCED_FEATURES_AVAILABLE:
        await message.reply_text("**≭︰نظام التنبيهات غير متاح**")
        return
    
    try:
        # الحصول على التنبيهات الأخيرة للمستخدم
        user_notifications = notification_system.get_user_notifications(message.from_user.id, limit=10)
        
        if not user_notifications:
            await message.reply_text("**📢 لا توجد تنبيهات حالياً**")
            return
        
        notifications_text = "**🔔 التنبيهات الأخيرة:**\n\n"
        
        for i, notification in enumerate(user_notifications, 1):
            alert_message = ui_manager.format_alert_message({
                'level': notification.level.value,
                'title': notification.title,
                'message': notification.message,
                'timestamp': notification.timestamp,
                'bot_username': notification.bot_username
            })
            
            notifications_text += f"**{i}.** {alert_message}\n\n"
            
            # تحديد الإشعار كمقروء
            notification_system.mark_notification_read(notification.id, message.from_user.id)
        
        # إحصائيات الإشعارات
        stats = notification_system.get_statistics()
        notifications_text += f"**📊 الإحصائيات:**\n"
        notifications_text += f"▪️ المجموع: {stats['total_notifications']}\n"
        notifications_text += f"▪️ غير المقروءة: {stats['unread_notifications']}\n"
        
        await message.reply_text(notifications_text)
        
    except Exception as e:
        print(f"خطأ في عرض التنبيهات: {e}")
        if ADVANCED_FEATURES_AVAILABLE:
            error_text = ui_manager.format_error_message("خطأ في عرض التنبيهات", str(e))
            await message.reply_text(error_text)
        else:
            await message.reply_text(f"**❌ خطأ في عرض التنبيهات:** {e}")

@Client.on_message(filters.command("❲ البوتات المشتغلة ❳", ""))
async def show_running_bots(client, message):
    """عرض البوتات المشغلة باستخدام مدير العمليات المحسن"""
    if not is_dev(message.from_user.id):
        await message.reply_text("**≭︰هذا الامر يخص المطور**")
        return

    try:
        from core.process_manager import process_manager
        
        # الحصول على إحصائيات البوتات
        stats = process_manager.get_bot_stats()
        running_bots = process_manager.get_running_bots()
        
        if not running_bots:
            await message.reply_text("**≭︰لا يوجد أي بوت يعمل حالياً**")
            return
        
        # إنشاء قائمة مفصلة بالبوتات المشغلة
        bots_text = "**📊 البوتات المشغلة حالياً:**\n\n"
        
        for i, bot in enumerate(running_bots, 1):
            uptime = ""
            if bot.start_time:
                uptime_seconds = time.time() - bot.start_time
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                uptime = f"{uptime_hours}h {uptime_minutes}m"
            
            bots_text += f"**{i}.** @{bot.username}\n"
            bots_text += f"   💾 الذاكرة: {bot.memory_usage:.1f} MB\n"
            bots_text += f"   ⚡ المعالج: {bot.cpu_usage:.1f}%\n"
            bots_text += f"   ⏱️ وقت التشغيل: {uptime}\n"
            bots_text += f"   👑 المالك: {bot.owner_id}\n\n"
        
        # إضافة الإحصائيات العامة
        bots_text += f"**📈 الإحصائيات العامة:**\n"
        bots_text += f"🟢 مشغل: {stats['running_bots']}\n"
        bots_text += f"🔴 متوقف: {stats['stopped_bots']}\n"
        bots_text += f"📊 المجموع: {stats['total_bots']}\n"
        bots_text += f"💾 إجمالي الذاكرة: {stats['total_memory_usage']:.1f} MB\n"
        bots_text += f"⚡ إجمالي المعالج: {stats['total_cpu_usage']:.1f}%"
        
        await message.reply_text(bots_text)
        
    except ImportError:
        # العودة للطريقة القديمة في حالة عدم وجود الوحدة
        if not os.path.exists('Maked'):
            await message.reply_text("**~ خطأ: لا يوجد مجلد Maked.**")
            return

        running_bots = []
        for folder in os.listdir("Maked"):
            if re.search('[Bb][Oo][Tt]', folder) and is_bot_running(folder):
                running_bots.append(folder)

        if not running_bots:
            await message.reply_text("**≭︰لا يوجد أي بوت يعمل حالياً**")
        else:
            bots_list = "\n".join(f"- @{b}" for b in running_bots)
            await message.reply_text(f"**≭︰البوتات المشتغلة حالياً:**\n\n{bots_list}")
            
    except Exception as e:
        logger.error(f"خطأ في عرض البوتات المشغلة: {e}")
        await message.reply_text(f"**❌ خطأ في عرض البوتات:** {e}")

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