from pyrogram import Client, idle
from pyromod import listen
from config import API_ID, API_HASH, BOT_TOKEN

# استخدام in_memory=True لتجنب مشاكل قاعدة البيانات المُقفلة
bot = Client(
    "bot_maker",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Maker"),
    in_memory=True
)

bot_id = None

async def start_bot():
    global bot_id
    await bot.start()
    me = await bot.get_me()
    bot_id = me.id
    print(f"✅ بوت الصانع يعمل: {me.first_name} (@{me.username})")
    print(f"🆔 معرف البوت: {me.id}")
    await idle()
    await bot.stop()
    