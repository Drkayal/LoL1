from pyrogram import Client, idle
from pyromod import listen
import os
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    "B7R",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Maker")
)

async def start_bot():
    print("[INFO]: جاري تشغيل البوت")
    await bot.start()
    print("[INFO]: بدأ تشغيل")
    await idle()


bot_id = BOT_TOKEN.split(":")[0]    
    