import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL 
from typing import Union
import random
from youtube_search import YoutubeSearch
import yt_dlp
from AnonXMusic import app
import os
import glob
cookies_file = "/root/cookies/cookies.txt"
os.makedirs("downloads", exist_ok=True)

@app.on_message(filters.command(['نزل', 'حمل', 'تنزيل', 'يوت'], ""))
async def download_song(client: Client, msg: Message):
    try:
        if len(msg.text.split()) < 2:
            ask = await msg.reply("<b>≯︰شبدك تنزل؟</b>")
            try:
                response: Message = await client.listen(msg.chat.id, timeout=30)
                name = response.text.strip()
                await ask.delete()
                await response.delete()
            except asyncio.TimeoutError:
                return await ask.edit("<b>≯︰لم يتم تلقي أي رد، تم إلغاء العملية.</b>")
        else:
            name = msg.text.split(' ', 1)[1]

        x = await msg.reply("<b>جاري البحث انتظر قليلاً .🚦</b>")

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'keepvideo': True,
            'prefer_ffmpeg': False,
            'geo_bypass': True,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'cookiefile': cookies_file
        }

        try:
            results = YoutubeSearch(name, max_results=1).to_dict()
            if not results:
                return await msg.reply(f'<b>لم يتم العثور على نتائج لـ {name}</b>')

            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            thumbnail = results[0]["id"]
            thumb_name = f"downloads/thumb{thumbnail}.jpg"

            thumb = requests.get(f"https://img.youtube.com/vi/{thumbnail}/hqdefault.jpg", allow_redirects=True)
            with open(thumb_name, "wb") as f:
                f.write(thumb.content)

            duration = results[0]["duration"]
        except:
            return await msg.reply("<b>≯︰حدث خطأ أثناء البحث عن الفيديو.</b>")

        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        if dur > 3600:
            return await msg.reply("<b>غير مسموح بهذا الحد من الوقت .⚡</b>")

        try:
            await x.edit('<b>≯︰تم العثور وجاري التنزيل....</b>')
        except:
            pass

        try:
            with YoutubeDL(ydl_opts) as ytdl:
                ytdl_data = ytdl.extract_info(link, download=True)
                file_name = ytdl.prepare_filename(ytdl_data)
        except:
            return await msg.reply("<b>≯︰حدث خطأ أثناء تنزيل الصوت أو الفيديو.</b>")

        bot_username = client.me.username
        rep = f"<b>≯︰uploader : @{bot_username}</b>"

        try:
            await x.edit("<b>≯︰جاري الرفع انتظر  </b>")
        except:
            pass

        try:
            if msg.text.split()[0] in ['نزل', 'تنزيل', 'يوت']:
                await client.send_audio(
                    chat_id=msg.chat.id,
                    audio=file_name,
                    caption=rep,
                    thumb=thumb_name,
                    title=title,
                    duration=dur
                )
            else:
                await client.send_video(
                    chat_id=msg.chat.id,
                    video=file_name,
                    caption=rep,
                    thumb=thumb_name,
                    duration=dur
                )
            await x.delete()
        except:
            pass
        finally:
            try:
                if os.path.exists(file_name):
                    os.remove(file_name)
                if os.path.exists(thumb_name):
                    os.remove(thumb_name)
            except Exception as e:
                print(f"Error while deleting files: {e}")

    except Exception as e:
        print(traceback.format_exc())