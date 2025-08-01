"""
Broadcast Handlers - معالجات البث
يحتوي على معالج البث والرسائل الجماعية
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from utils import logger
from users import is_dev, validate_user_id, del_user
from bots import start_bot_process, get_bot_info, update_bot_status
from broadcast import get_broadcast_status, delete_broadcast_status
from users import validate_bot_username
from factory.settings import get_factory_state

# المتغيرات المطلوبة من الملف الرئيسي
bots_collection = None

def set_dependencies(bots_coll):
    """
    تعيين المتغيرات المطلوبة من الملف الرئيسي
    
    Args:
        bots_coll: مجموعة البوتات
    """
    global bots_collection
    bots_collection = bots_coll

@Client.on_message(filters.private, group=368388)
async def forbroacasts_handler(client, msg):
    """معالج البث والرسائل الجماعية"""
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received in broadcast handler")
        return
    
    uid = msg.from_user.id
    if not is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info in broadcast handler: {str(e)}")
        return

    text = msg.text
    ignore = ["❲ اذاعه ❳", "❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳", "❲ الاحصائيات ❳", "❲ اخفاء الكيبورد ❳", "الغاء"]
    if text in ignore:
        return

    # معالجة تشغيل بوت محدد
    if await get_broadcast_status(uid, bot_id, "start_bot"):
        await delete_broadcast_status(uid, bot_id, "start_bot")
        
        # التحقق من حالة المصنع
        if get_factory_state():
            await msg.reply("**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # التحقق من صحة معرف البوت
        is_valid, validated_username = validate_bot_username(text)
        if not is_valid:
            await msg.reply(f"**❌ معرف البوت غير صحيح: {text}**", quote=True)
            return
        
        bot_info = get_bot_info(validated_username)
        if not bot_info:
            await msg.reply("**❌ هذا البوت غير موجود في قاعدة البيانات**", quote=True)
            return
        
        if bot_info.get("status") == "running":
            await msg.reply("**⚠️ هذا البوت يعمل بالفعل**", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await msg.reply(f"**🔄 جاري تشغيل البوت @{validated_username}...**", quote=True)
        
        # تأخير قصير قبل بدء العملية
        await asyncio.sleep(0.5)
        
        process_id = start_bot_process(validated_username)
        if process_id:
            if update_bot_status(validated_username, "running"):
                # تحديد نوع المعرف وتحديث الحقل المناسب
                if isinstance(process_id, str):
                    # Container ID
                    bots_collection.update_one(
                        {"username": validated_username},
                        {"$set": {"container_id": process_id}}
                    )
                    await status_msg.edit(f"**✅ تم تشغيل البوت @{validated_username} بنجاح**\n🐳 **في حاوية Docker:** `{process_id[:12]}...`")
                elif isinstance(process_id, int):
                    # PID
                    bots_collection.update_one(
                        {"username": validated_username},
                        {"$set": {"pid": process_id}}
                    )
                    await status_msg.edit(f"**✅ تم تشغيل البوت @{validated_username} بنجاح**\n🔧 **معرف العملية:** `PID {process_id}`")
            else:
                await status_msg.edit(f"**⚠️ تم تشغيل البوت @{validated_username} لكن فشل تحديث الحالة**")
        else:
            await status_msg.edit(f"**❌ فشل في تشغيل البوت @{validated_username}**\n\n**🔍 الأسباب المحتملة:**\n• البوت غير موجود في مجلد Maked\n• خطأ في ملفات البوت\n• مشكلة في التكوين")
        return

    # معالجة البث العادي
    if await get_broadcast_status(uid, bot_id, "broadcast"):
        await delete_broadcast_status(uid, bot_id, "broadcast")
        message = await msg.reply("• جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        from users import get_users
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in broadcast: {user}")
                    failed_count += 1
                    continue
                
                await msg.copy(validated_user_id)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")

    # معالجة البث بالتثبيت
    elif await get_broadcast_status(uid, bot_id, "pinbroadcast"):
        await delete_broadcast_status(uid, bot_id, "pinbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        from users import get_users
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in pin broadcast: {user}")
                    failed_count += 1
                    continue
                
                m = await msg.copy(validated_user_id)
                await m.pin(disable_notification=False, both_sides=True)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"» نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Pin broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")

    # معالجة البث بالتوجيه
    elif await get_broadcast_status(uid, bot_id, "fbroadcast"):
        await delete_broadcast_status(uid, bot_id, "fbroadcast")
        message = await msg.reply("» جاري الإذاعة ..", quote=True)
        
        # الحصول على قائمة المستخدمين مع التحقق
        from users import get_users
        users_list = await get_users()
        if not users_list:
            await message.edit("**❌ لا يوجد مستخدمين للإذاعة**")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users_list, start=1):
            try:
                # التحقق من صحة معرف المستخدم
                is_valid, validated_user_id = validate_user_id(user)
                if not is_valid:
                    logger.warning(f"Invalid user_id in forward broadcast: {user}")
                    failed_count += 1
                    continue
                
                await msg.forward(validated_user_id)
                success_count += 1
                
                progress = int((i / len(users_list)) * 100)
                if i % 5 == 0:
                    await message.edit(f"• نسبه الاذاعه {progress}%")
                    
                # تأخير لتجنب الحظر
                await asyncio.sleep(0.1)
                
            except PeerIdInvalid:
                await del_user(user)
                failed_count += 1
            except Exception as e:
                logger.error(f"Forward broadcast error for user {user}: {str(e)}")
                failed_count += 1
        
        await message.edit(f"» تمت الاذاعه بنجاح\n✅ نجح: {success_count}\n❌ فشل: {failed_count}")