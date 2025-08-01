from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from AnonXMusic import app

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    if not "https://t.me/A1DIIU":  # Not compulsory
        return
    try:
        try:
            await bot.get_chat_member("A1DIIU", msg.from_user.id)
        except UserNotParticipant:
            if "https://t.me/A1DIIU".isalpha():
                link = "https://t.me/A1DIIU"
            else:
                chat_info = await bot.get_chat("A1DIIU")
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"⌯︙عذࢪاَ عزيزي ↫ {msg.from_user.mention} \n⌯︙عـليك الاشـتࢪاك في قنـاة البـوت اولآ\n⌯︙قناة البوت: @A1DIIU .\nꔹ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ꔹ",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("اضغط للأشتراك .", url=link)]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"I'm not admin in the MUST_JOIN chat @A1DIIU !")


def must_join_ch(func):
    """Decorator to check if user must join channel"""
    async def wrapper(client: Client, message: Message):
        channel_username = "A1DIIU"  # Default channel
        
        try:
            await client.get_chat_member(channel_username, message.from_user.id)
            # User is member, continue with the original function
            return await func(client, message)
        except UserNotParticipant:
            try:
                chat_info = await client.get_chat(channel_username)
                link = chat_info.invite_link or f"https://t.me/{channel_username}"
                
                await message.reply(
                    f"⌯︙عذࢪاَ عزيزي ↫ {message.from_user.mention} \n⌯︙عـليك الاشـتࢪاك في قنـاة البـوت اولآ\n⌯︙قناة البوت: @{channel_username} .\nꔹ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ꔹ",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("اضغط للأشتراك .", url=link)]
                    ])
                )
                return  # Don't continue with the original function
            except Exception as e:
                print(f"Error in must_join_ch: {e}")
                return await func(client, message)  # Allow if error occurs
        except Exception as e:
            print(f"Error checking membership: {e}")
            return await func(client, message)  # Allow if error occurs
    
    return wrapper
