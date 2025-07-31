import asyncio
from pyrogram import idle
import sys
import os

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from AnonXMusic import app
    print("✅ تم استيراد البوت بنجاح")
except Exception as e:
    print(f"❌ خطأ في استيراد البوت: {e}")
    sys.exit(1)

async def main():
    try:
        print("🚀 بدء تشغيل البوت المُولد...")
        await app.start()
        me = await app.get_me()
        print(f"✅ تم تشغيل البوت بنجاح: {me.first_name} (@{me.username})")
        await idle()
        await app.stop()
        print("🔴 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
