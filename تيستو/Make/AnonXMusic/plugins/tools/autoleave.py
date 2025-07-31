import asyncio
from datetime import datetime

from pyrogram.enums import ChatType

import config
from AnonXMusic import app
from AnonXMusic.core.call import Anony, autoend
from AnonXMusic.utils.database import get_client, is_active_chat, get_auto_leave_status



async def auto_leave():
    while True:
        await asyncio.sleep(900)  # كل 15 دقيقة
        if not await get_auto_leave_status():
            continue

        from AnonXMusic.core.userbot import assistants
        for num in assistants:
            client = await get_client(num)
            left = 0
            try:
                async for i in client.get_dialogs():
                    if i.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                        if i.chat.id not in [config.LOGGER_ID, -1001686672798, -1001549206010]:
                            if left == 20:
                                continue
                            if not await is_active_chat(i.chat.id):
                                try:
                                    await client.leave_chat(i.chat.id)
                                    left += 1
                                except:
                                    continue
            except:
                continue

asyncio.create_task(auto_leave())


async def auto_end():
    while not await asyncio.sleep(5):
        # always active auto-end
        for chat_id in autoend:
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    autoend[chat_id] = {}
                    continue
                autoend[chat_id] = {}
                try:
                    await Anony.stop_stream(chat_id)
                except:
                    continue
                try:
                    await app.send_message(
                        chat_id,
                        "<b>تم انهاء التشغيل لعدم وجود مستمعين ♥️🌿</b>",
                    )
                except:
                    continue


asyncio.create_task(auto_end())