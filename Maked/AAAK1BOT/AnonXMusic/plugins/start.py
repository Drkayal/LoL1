
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply(
        "🎵 **مرحباً بك في البوت الموسيقي!**\\n\\n"
        "✅ البوت يعمل بنجاح\\n"
        "🤖 تم إنشاؤه بواسطة صانع البوتات\\n"
        f"👤 المطور: 985612253",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 تواصل مع المطور", url="tg://user?id=985612253")],
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
    await message.reply(f"🆔 **معرفك:** `{user_id}`\\n🏷️ **معرف المحادثة:** `{chat_id}`")
