import asyncio
from pyrogram import Client, idle, filters
from pyrogram.types import Message

# التكوين الأساسي
API_ID = 17490746
API_HASH = "ed923c3d59d699018e79254c6f8b6671"
BOT_TOKEN = "7519388401:AAHhwC5R5pY8C_v1qsKlKZLt8E4-Kl1HCGQ"

# إنشاء العميل
app = Client("SimpleBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply(
        "🎵 **مرحباً بك في البوت الموسيقي!**\n\n"
        "✅ البوت يعمل بنجاح\n"
        "🤖 تم إنشاؤه بواسطة صانع البوتات"
    )

@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply("🏓 **Pong!** البوت يعمل بشكل طبيعي")

async def main():
    print("🚀 بدء تشغيل البوت البسيط...")
    await app.start()
    me = await app.get_me()
    print(f"✅ تم تشغيل البوت: {me.first_name} (@{me.username})")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
