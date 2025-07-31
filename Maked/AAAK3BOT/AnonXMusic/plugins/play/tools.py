from pyrogram import Client, filters
from colorama import init, Style
from pyrogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup as ikm, InlineKeyboardButton as ikb 
from AnonXMusic import app
from config import OWNER_ID, OWNER_DEVELOPER
from AnonXMusic.utils.database import get_served_chats, is_contact_enabled, toggle_contact, is_served_user, add_served_user, get_served_users, get_client, set_must, get_must, del_must, get_must_ch, set_must_ch, get_active_chats, remove_active_video_chat, remove_active_chat, set_bot_name, get_bot_name
import os 
from pyrogram.enums import ParseMode
import shutil
import asyncio
import random 
from asyncio import gather
import time
import logging
from PIL import Image
from pyrogram import client, filters
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic.utils.database import get_must, get_bot_name, set_auto_leave_status
import config
from AnonXMusic import app
from AnonXMusic.misc import _boot_
from AnonXMusic.utils.database import (
    add_served_chat,
    is_served_channel,
    is_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats, 
    get_served_users, 
    is_banned_user,
    is_on_off,
)
from AnonXMusic.plugins.tools.must_join import must_join_ch
from AnonXMusic.utils.formatters import get_readable_time
from config import BANNED_USERS
from strings import get_string
import logging
import os
import re
import textwrap
import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from pathlib import Path 
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import aiofiles
import aiohttp
from pyrogram.types import CallbackQuery
from config import OWNER, GROUP, YOUTUBE_IMG_URL, OWNER_DEVELOPER, OWNER_NAME, PHOTO, VIDEO
from AnonXMusic.plugins.play.start import devs
import aiohttp
from unidecode import unidecode
from AnonXMusic.plugins.play.filters import command
from pyrogram import filters
from pyrogram.types import Message
from unidecode import unidecode

from AnonXMusic import app
from AnonXMusic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)

BASE = "https://batbin.me/"

# دالة رفع النص إلى batbin
async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data

# تنسيق الرابط بعد الرفع
async def base(text):
    resp = await post(f"{BASE}api/v2/paste", data=text)
    if isinstance(resp, dict) and resp.get("success"):
        return BASE + resp["message"]
    return None
    
@app.on_message(filters.command("❲ المكالمات النشطه ❳", ""))
async def geetmeactive(client, message: Message):
    m = await message.reply_text("<b>≯︰انتظر قليلا ..</b>")

    active_chats = await get_active_chats()
    if not active_chats:
        if m.text != "<b>≯︰لا يوجد مكالمات قيد التشغيل</b>":
            return await m.edit("<b>≯︰لا يوجد مكالمات قيد التشغيل</b>")

    count = 0
    text = ""

    for chat_id in active_chats:
        try:
            chat = await app.get_chat(chat_id)
            count += 1
            if chat.username:
                text += f"<b>{count}- ❲ <a href='https://t.me/{chat.username}'>{chat.title}</a> ❳</b>\n"
            else:
                text += f"<b>{count}- ❲ {chat.title} ❳</b>\n"
        except Exception:
            continue

    if count == 0:
        if m.text != "<b>≯︰لا يوجد مكالمات قيد التشغيل</b>":
            return await m.edit("<b>≯︰لا يوجد مكالمات قيد التشغيل</b>")

    if len(text) > 4000:
        link = await base(text)
        if link:
            await message.reply_text(f"المحادثات النشطة هنا: {link}")
        else:
            await message.reply_text("حدث خطأ أثناء رفع القائمة.")
    else:
        await message.reply_text(f"<b>{text}</b>", disable_web_page_preview=True)

    return await m.delete()



@app.on_message(filters.command(["❲ قسم الاحصائيات ❳"], "") & filters.private & devs, group=2)
async def stats_bot(c, msg):
    await msg.reply(
        "<b> ≭︰اهلا بك عزيزي المطور بقسم الاحصائيات </b>",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["❲ المستخدمين ❳", "❲ الكروبات ❳"],
                ["❲ الاحصائيات ❳"],
                ["❲ رجوع للقائمة الرئيسية ❳"]
            ],
            resize_keyboard=True
        )
    )
    
@app.on_message(filters.command(["❲ قسم المساعد ❳"],"") & filters.private & devs, group = 2)    
async def asisstant_bot(c, msg):
    await msg.reply(
        "<b>≯︰اهلا بك عزيزي المطور بقسم حساب المساعد ◟</b>",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["❲ تغيير الاسم الاول ❳", "❲ تغيير الاسم الثاني ❳"],
                ["❲ تغيير البايو ❳"],
                ["❲ اضف صورة ❳", "❲ مسح الصورة ❳"],
                ["❲ اذاعة ❳"],
                ["❲ رجوع للقائمة الرئيسية ❳"]
            ],
            resize_keyboard=True
        )
    )

@app.on_message(filters.command(["❲ قسم الاشتراك الاجباري ❳"], "") & filters.private & devs, group=2)
async def force_sub_bot(c, msg):
    await msg.reply(
        "<b> ≭︰اهلا بك عزيزي المطور بقسم الاشتراك الاجباري </b>",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["❲ قناة الاشتراك ❳"],
                ["❲ اضف قناة ❳", "❲ حذف قناة الاشتراك ❳"],
                ["❲ تفعيل الاشتراك ❳", "❲ تعطيل الاشتراك ❳"],
                ["❲ رجوع للقائمة الرئيسية ❳"]
            ],
            resize_keyboard=True
        )
    )

@app.on_message(filters.command(["❲ قسم الاذاعه ❳"], "") & filters.private & devs, group=2)
async def broadcast_bot(c, msg):
    await msg.reply(
        "<b>≭︰اهلا بك عزيزي المطور بقسم الاذاعه</b>",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["❲ للكروبات ❳", "❲ للمستخدمين ❳"],
                ["❲ بالتوجيه للكروبات ❳", "❲ بالتوجيه للمستخدمين ❳"],
                ["❲ ترويج للبوت ❳"],
                ["❲ رجوع للقائمة الرئيسية ❳"]
            ],
            resize_keyboard=True
        )
    )


@app.on_message(filters.command(["❲ الكروبات ❳", "❲ المستخدمين ❳", "❲ الاحصائيات ❳"], "") & filters.private & devs, group=2)
async def stat_bot(c: Client, msg):
    served_users, served_chats = await gather(
        get_served_users(c),
        get_served_chats(c)
    )
    
    if msg.text == "❲ المستخدمين ❳":
        return await msg.reply(f"<b> ≭︰ عدد مستخدمين البوت : {len(served_users)}  </b>")
    elif msg.text == "❲ الكروبات ❳":
        return await msg.reply(f"<b> ≭︰عدد كروبات البوت : {len(served_chats)} </b>")
    elif msg.text == "❲ الاحصائيات ❳":
        return await msg.reply(
            f"<b> ≭︰عدد مستخدمين البوت : {len(served_users)}\n"
            f"≭︰عدد كروبات البوت : {len(served_chats)}</b>"
        )
        
        

@app.on_message(filters.command(["❲ تفعيل المغادرة ❳", "❲ تعطيل المغادرة ❳"], "") & filters.private & devs)
async def toggle_auto_leave(c, m: Message):
    if "تفعيل" in m.text:
        await set_auto_leave_status(True)
        await m.reply("≯ تم تفعيل نظام مغادرة المساعد التلقائي.")
    else:
        await set_auto_leave_status(False)
        await m.reply("≯ تم تعطيل نظام مغادرة المساعد التلقائي.")        
        
@app.on_message(
    filters.command([
        "❲ تغيير الاسم الاول ❳", 
        "❲ تغيير البايو ❳", 
        "❲ اضف صورة ❳", 
        "❲ تغيير الاسم الثاني ❳", 
        "❲ مسح الصورة ❳", 
        "❲ تفعيل المغادرة ❳", 
        "❲ تعطيل المغادرة ❳"
    ], "") & filters.private & devs, group=2
)
async def acc_bot(c, msg):
    client = await get_client(1)

    if msg.text == "❲ اضف صورة ❳":
        try:
            m = await c.ask(msg.chat.id, "<b>❲ قم بإرسال الصوره عزيزي المطور ◟</b>")
            if m.text == "❲ اضف صورة ❳":
                m = await c.ask(msg.chat.id, "<b> ≯︰عذرا قم بإرسال صورة عزيزي المطور ◟</b>")
            photo = await m.download()
            await client.set_profile_photo(photo=photo)
            await msg.reply("<b>≯︰تم تغيير الصورة بنجاح ◟</b>")
        except Exception as e:
            await msg.reply(f"- حدث خطا -> {e}")

    elif msg.text == "❲ تغيير البايو ❳":
        try:
            m = await c.ask(msg.chat.id, "<b>≯︰قم بإرسال البايو عزيزي المطور ◟</b>")
            if m.text == "❲ تغيير البايو ❳":
                m = await c.ask(msg.chat.id, "<b>≯︰عذرا قم بإرسال نص البايو عزيزي المطور ◟</b>")
            await client.update_profile(bio=m.text)
            await msg.reply("≯︰تم تغيير البايو بنجاح ◟")
        except Exception as e:
            await msg.reply(f"- حدث خطا -> {e}")

    elif msg.text == "❲ تغيير الاسم الاول ❳":
        try:
            m = await c.ask(msg.chat.id, "<b>≯︰قم بإرسال الاسم عزيزي المطور ◟</b>")
            if m.text == "❲ تغيير الاسم الاول ❳":
                m = await c.ask(msg.chat.id, "<b>≯︰عذرا قم بإرسال نص الاسم عزيزي المطور ◟</b>")
            await client.update_profile(first_name=m.text)
            await msg.reply("<b>❲ تم تغيير الاسم الاول بنجاح ◟</b>")
        except Exception as e:
            await msg.reply(f"- حدث خطا -> {e}")

    elif msg.text == "❲ تغيير الاسم الثاني ❳":
        try:
            m = await c.ask(msg.chat.id, "<b>≯︰قم بإرسال الاسم عزيزي المطور ◟</b>")
            if m.text == "❲ تغيير الاسم الثاني ❳":
                m = await c.ask(msg.chat.id, "<b>≯︰عذرا قم بإرسال نص الاسم عزيزي المطور ◟</b>")
            await client.update_profile(last_name=m.text)
            await msg.reply("<b>≯︰تم تغيير الاسم التاني بنجاح ◟</b>")
        except Exception as e:
            await msg.reply(f"- حدث خطا -> {e}")

    elif msg.text == "❲ مسح الصورة ❳":
        try:
            if (await client.get_me()).photo:
                async for photo in client.get_chat_photos("me", limit=1):
                    await client.delete_profile_photos(photo.file_id)
                await msg.reply("<b>≯︰تم حذف صورة من الحساب المساعد بنجاح ◟</b>")
            else:
                await msg.reply("≯︰لا يوجد صور لحذفها عزيزي المطور ◟")
        except Exception as e:
            await msg.reply(f"- حدث خطا -> {e}")

@app.on_message(filters.command(["❲ اذاعة ❳"],"") & filters.private & devs, group = 2)
async def broadcast_acc(c,msg):
    try:
        m = await c.ask(msg.chat.id, "≯︰قم بإرسال الرسالة المراد نشرها عزيزي المطور ◟")
        if m.text == "❲ اذاعة ❳":
            m = await c.ask(msg.chat.id, "≯︰عذرا قم بإرسال الرسالة المراد نشرها عزيزي المطور ◟")
        client = await get_client(1)
        x = 0
        async for ch in client.get_dialogs():
            try:
                if m.photo:
                    photo = await m.download()
                    await client.send_photo(ch.chat.id, photo=photo, caption=m.caption)
                elif m.video:
                    video = await m.download()
                    thumb = await app.download_media(m.video.thumbs[0].file_id)
                    await client.send_video(ch.chat.id, photo=video, caption=m.caption, duration=m.video.duration,thumb=thumb)
                else:
                    await client.send_message(ch.chat.id, text=m.text)
                x += 1
            except:
                pass
        await msg.reply(f"≯︰تم ارسال الى {x} شات")
    except Exception as e:
        await msg.reply(f"- حدث خطا -> {e}")


@app.on_message(filters.command(["❲ اضف قناة ❳"], "") & filters.private & devs, group=2)
async def add_must(c, msg):
    try:
        m = await c.ask(msg.chat.id, "<b>≯︰قم بارسال رابط القناه </b>")
        username_input = m.text.strip().replace("@", "").replace("https://t.me/", "")
        try:
            chat = await c.get_chat(username_input)
        except:
            return await msg.reply("<b> ≭︰ تأكد من صحة يوزر القناة وأن البوت مرفوع بها </b>")
        await set_must(c.me.username, chat.username)
        await msg.reply(f"<b> ≭︰ تم تعيين القناة بنجاح: https://t.me/{chat.username} </b>")
    except Exception as e:
        await msg.reply(f"- حدث خطأ -> {e}")

@app.on_message(filters.command(["❲ قناة الاشتراك ❳"], "") & filters.private & devs, group=2)
async def get_ch_must(c, msg):
    ch = await get_must(c.me.username)
    if ch:
        return await msg.reply(f"<b> ≭︰ قناة الاشتراك : {ch} </b>")
    else:
        return await msg.reply("<b> ≭︰ لا توجد قناة حالياً، استخدم ❲ اضف قناة ❳ أولاً </b>")


@app.on_message(filters.command(["❲ حذف قناة الاشتراك ❳"], "") & filters.private & devs, group=2)
async def rem_ch_must(c, msg):
    done = await del_must(c.me.username)
    if done:
        return await msg.reply("<b> ≭︰ تم حذف قناة الاشتراك الإجباري بنجاح </b>")
    else:
        return await msg.reply("<b> ≭︰ لا توجد قناة حالياً لحذفها </b>")

@app.on_message(filters.command(["❲ تفعيل الاشتراك ❳"], "") & filters.private & devs, group=2)
async def en_ch_must(c, msg):
    status = await get_must_ch(c.me.username)
    if status == "معطل":
        await set_must_ch(c.me.username, "enable")
        await msg.reply("<b> ≭︰ تم تفعيل الاشتراك الإجباري </b>")
    else:
        await msg.reply("<b> ≭︰ الاشتراك الإجباري مفعل بالفعل </b>")

@app.on_message(filters.command(["❲ تعطيل الاشتراك ❳"], "") & filters.private & devs, group=2)
async def dis_ch_must(c, msg):
    status = await get_must_ch(c.me.username)
    if status == "مفعل":
        await set_must_ch(c.me.username, "disable")
        await msg.reply("<b> ≭︰ تم تعطيل الاشتراك الإجباري </b>")
    else:
        await msg.reply("<b> ≭︰ الاشتراك الإجباري معطل بالفعل </b>")
        
@app.on_message(filters.command(["❲ للكروبات ❳","❲ للمستخدمين ❳"],"") & filters.private & devs, group = 2)
async def broadcast_gr(c,msg):
    try:
        m = await c.ask(msg.chat.id, "<b> ≭︰ قم بارسال الرسالة التي تريد نشرها  </b>")
        if m.text in ["❲ للكروبات ❳" ,"❲ للمستخدمين ❳"]:
            m = await c.ask(msg.chat.id, "<b> ≭︰عذرا قم بارسال الرسالة التي تريد نشرها  </b>")
        chats = await get_served_chats(c) if msg.text == "❲ للكروبات ❳" else await get_served_users(c)
        x = 0
        n = "chat_id" if msg.text == "❲ للكروبات ❳" else "user_id"
        for chat in chats:
            try:
                if m.photo:
                    photo = await m.download()
                    await app.send_photo(int(chat[n]), photo=photo, caption=m.caption)
                elif m.video:
                    video = await m.download()
                    thumb = await app.download_media(m.video.thumbs[0].file_id)
                    await app.send_video(int(chat[n]), photo=video, caption=m.caption, duration=m.video.duration,thumb=thumb)
                else:
                    await app.send_message(int(chat[n]), text=m.text)
                x += 1
                await asyncio.sleep(0.2)
            except:
                pass
        type = "كروب" if msg.text == "❲ للكروبات ❳" else "مستخدم"
        await msg.reply(f"≯︰تم ارسال الى {x} {type}")
    except Exception as e:
        await msg.reply(f"- حدث خطا -> {e}")    

@app.on_message(filters.command(["❲ بالتوجيه للكروبات ❳", "❲ بالتوجيه للمستخدمين ❳"],"") & filters.private & devs, group = 2)
async def broadcast_fr(c,msg):
    try:
        m = await c.ask(msg.chat.id, "<b> ≭︰ قم بارسال الرسالة التي تريد نشرها   </b>")
        if m.text in ["❲ بالتوجيه للكروبات ❳", "❲ بالتوجيه للمستخدمين ❳"]:
            m = await c.ask(msg.chat.id, "≯︰عذرا قم بارسال الرسالة التي تريد نشرها ◟")
        chats = await get_served_chats(c) if msg.text == "❲ بالتوجيه للكروبات ❳" else await get_served_users(c)
        x = 0
        n = "chat_id" if msg.text == "❲ بالتوجيه للكروبات ❳" else "user_id"
        for chat in chats:
            try:
                await m.forward(int(chat[n]))
                x += 1
                await asyncio.sleep(0.2)
            except:
                pass
        type = "كروب" if msg.text == "❲ بالتوجيه للكروبات ❳" else "مستخدم"
        await msg.reply(f"≯︰تم ارسال الى {x} {type}")
    except Exception as e:
        await msg.reply(f"- حدث خطا -> {e}")                