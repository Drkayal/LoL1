import asyncio
import sys
import os
from pyrogram import idle

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

try:
    from AnonXMusic import app
    print("✅ تم تحميل البوت بنجاح")
except Exception as e:
    print(f"❌ خطأ في تحميل البوت: {e}")
    sys.exit(1)

async def main():
    try:
        print("🚀 بدء تشغيل البوت AAAK3BOT...")
        await app.start()
        me = await app.get_me()
        print(f"✅ تم تشغيل البوت بنجاح: {me.first_name} (@{me.username})")
        print("🔄 البوت في وضع الانتظار...")
        await idle()
        await app.stop()
        print("🔴 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
