import asyncio
from pyrogram import idle
from AnonXMusic import app

async def main():
    print("🚀 بدء تشغيل البوت...")
    await app.start()
    print("✅ تم تشغيل البوت بنجاح!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
