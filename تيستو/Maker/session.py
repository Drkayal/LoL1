import os
import asyncio
from os import getenv

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

from config import API_ID, API_HASH, CHANNEL, PHOTO


@Client.on_message(filters.command(["❲ استخراج جلسه ❳"], ""))
async def getsession(app, message: Message):
    try:
        num = await app.ask(message.chat.id, "**ا≯︰رسل رقم الهاتف**", timeout=60)
    except asyncio.TimeoutError:
        await app.send_message(message.chat.id, "**≯︰انتهى الوقت حاول مره اخرى..!!**")
        return

    phone_number = num.text

    client = Client(":memory:", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await client.connect()

    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await message.reply("**رقم الهاتف غير صحيح**")
        return

    try:
        phone_code_msg = await app.ask(
            message.chat.id,
            f"**تم ارسال كود ᴏᴛᴩ إلى رقم : {phone_number}**\n"
            "**│ تم ارساله بهذا الشكل : 12345**\n"
            "**من فضلك ارسله لي هكذا : 1 2 3 4 5**",
            filters=filters.text,
            timeout=60
        )
    except asyncio.TimeoutError:
        await message.reply("**انتهي الوقت حاول مره اخرى..!!**")
        return

    phone_code = phone_code_msg.text.replace(" ", "")

    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await message.reply("**الكود ᴏᴛᴩ غير صحيح حاول مره اخرى**")
        return
    except PhoneCodeExpired:
        await message.reply("**انتهت صلاحية الكود، ارسله بهذا الشكل : 1 2 3 4 5**")
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await app.ask(
                message.chat.id,
                "**من فضلك عزيزي، ارسل لي كلمه السر**",
                filters=filters.text,
                timeout=60
            )
        except asyncio.TimeoutError:
            await message.reply("**انتهي الوقت حاول مره اخرى..!!**")
            return

        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply("**كلمة السر غير صحيحة، حاول مجددًا**")
            return

    session = await client.export_session_string()

    await message.reply_photo(
        photo=PHOTO,
        caption=(
            f"**عزيزي : {message.from_user.mention}**\n"
            "**شكراً لك لثقتك بنا**\n"
            "**جلستك اصدار :**\n\n"
            f"`{session}`\n\n"
            "**اضغط للنسخ**"
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❲ Source Ch ❳", url=f"{CHANNEL}")]]
        )
    )