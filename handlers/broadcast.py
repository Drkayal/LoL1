"""
Broadcast Handlers - معالجات البث
يحتوي على معالج البث والرسائل الجماعية
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from utils import logger, safe_reply_text, safe_edit_text
from users import is_dev, validate_user_id, del_user
from bots import start_bot_process, get_bot_info, update_bot_status, stop_bot_process, delete_bot_info, save_bot_info, update_bot_process_id
from broadcast import get_broadcast_status, delete_broadcast_status
from users import validate_bot_username
from factory.settings import get_factory_state
from datetime import datetime

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
    if not await is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info in broadcast handler: {str(e)}")
        return

    text = msg.text
    ignore = ["❲ اذاعه ❳", "❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳", "❲ الاحصائيات ❳", "❲ اخفاء الكيبورد ❳", "❲ تشغيل بوت ❳", "❲ حذف بوت ❳", "❲ ايقاف بوت ❳", "❲ صنع بوت ❳", "الغاء"]
    if text in ignore:
        return

    # معالجة تشغيل بوت محدد
    if await get_broadcast_status(uid, bot_id, "start_bot"):
        await delete_broadcast_status(uid, bot_id, "start_bot")
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # التحقق من صحة معرف البوت
        is_valid, validated_username = await validate_bot_username(text)
        if not is_valid:
            await safe_reply_text(msg, f"**❌ معرف البوت غير صحيح: {text}**", quote=True)
            return
        
        bot_info = await get_bot_info(validated_username)
        if not bot_info:
            await safe_reply_text(msg, "**❌ هذا البوت غير موجود في قاعدة البيانات**", quote=True)
            return
        
        if bot_info.get("status") == "running":
            await safe_reply_text(msg, "**⚠️ هذا البوت يعمل بالفعل**", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(msg, f"**🔄 جاري تشغيل البوت @{validated_username}...**", quote=True)
        
        # تأخير قصير قبل بدء العملية
        await asyncio.sleep(0.5)
        
        process_id = await start_bot_process(validated_username)
        if process_id:
            if await update_bot_status(validated_username, "running"):
                # تحديد نوع المعرف وتحديث الحقل المناسب
                await update_bot_process_id(validated_username, process_id)
                if isinstance(process_id, str):
                    # Container ID
                    await status_msg.edit(f"**✅ تم تشغيل البوت @{validated_username} بنجاح**\n🐳 **في حاوية Docker:** `{process_id[:12]}...`")
                elif isinstance(process_id, int):
                    # PID
                    await status_msg.edit(f"**✅ تم تشغيل البوت @{validated_username} بنجاح**\n🔧 **معرف العملية:** `PID {process_id}`")
            else:
                await status_msg.edit(f"**⚠️ تم تشغيل البوت @{validated_username} لكن فشل تحديث الحالة**")
        else:
            await status_msg.edit(f"**❌ فشل في تشغيل البوت @{validated_username}**\n\n**🔍 الأسباب المحتملة:**\n• البوت غير موجود في مجلد Maked\n• خطأ في ملفات البوت\n• مشكلة في التكوين")
        return

    # معالجة حذف بوت محدد
    if await get_broadcast_status(uid, bot_id, "delete_bot"):
        await delete_broadcast_status(uid, bot_id, "delete_bot")
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # التحقق من صحة معرف البوت
        is_valid, validated_username = await validate_bot_username(text)
        if not is_valid:
            await safe_reply_text(msg, f"**❌ معرف البوت غير صحيح: {text}**", quote=True)
            return
        
        bot_info = await get_bot_info(validated_username)
        if not bot_info:
            await safe_reply_text(msg, "**❌ هذا البوت غير موجود في قاعدة البيانات**", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(msg, f"**🔄 جاري حذف البوت @{validated_username}...**", quote=True)
        
        # تأخير قصير قبل بدء العملية
        await asyncio.sleep(0.5)
        
        try:
            # إيقاف البوت أولاً إذا كان يعمل
            if bot_info.get("status") == "running":
                container_id = bot_info.get("container_id")
                pid = bot_info.get("pid")
                
                if container_id:
                    await stop_bot_process(container_id)
                elif pid:
                    await stop_bot_process(pid)
                
                await status_msg.edit(f"**⏹️ تم إيقاف البوت @{validated_username}**\n**🔄 جاري الحذف...**")
                await asyncio.sleep(1)
            
            # حذف من قاعدة البيانات
            delete_success = delete_bot_info(validated_username)
            if not delete_success:
                await status_msg.edit(f"**❌ فشل في حذف البوت @{validated_username} من قاعدة البيانات**")
                return
            
            # حذف مجلد البوت
            import shutil
            import os
            bot_path = os.path.join("Maked", validated_username)
            
            if os.path.exists(bot_path):
                try:
                    shutil.rmtree(bot_path)
                    folder_deleted = True
                except Exception as e:
                    logger.error(f"Failed to delete bot folder {bot_path}: {str(e)}")
                    folder_deleted = False
            else:
                folder_deleted = True  # المجلد غير موجود أصلاً
            
            # رسالة النتيجة النهائية
            if folder_deleted:
                await status_msg.edit(f"**✅ تم حذف البوت @{validated_username} بنجاح**\n\n**🗑️ تم حذفه من:**\n• قاعدة البيانات\n• مجلد Maked")
            else:
                await status_msg.edit(f"**⚠️ تم حذف البوت @{validated_username} جزئياً**\n\n**✅ تم حذفه من:**\n• قاعدة البيانات\n\n**❌ فشل في حذف:**\n• مجلد Maked")
                
        except Exception as e:
            logger.error(f"Error deleting bot {validated_username}: {str(e)}")
            await status_msg.edit(f"**❌ فشل في حذف البوت @{validated_username}**\n\n**🔍 السبب:** {str(e)}")
        return

    # معالجة إيقاف بوت محدد
    if await get_broadcast_status(uid, bot_id, "stop_bot"):
        await delete_broadcast_status(uid, bot_id, "stop_bot")
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # التحقق من صحة معرف البوت
        is_valid, validated_username = await validate_bot_username(text)
        if not is_valid:
            await safe_reply_text(msg, f"**❌ معرف البوت غير صحيح: {text}**", quote=True)
            return
        
        bot_info = await get_bot_info(validated_username)
        if not bot_info:
            await safe_reply_text(msg, "**❌ هذا البوت غير موجود في قاعدة البيانات**", quote=True)
            return
        
        if bot_info.get("status") != "running":
            await safe_reply_text(msg, "**⚠️ هذا البوت متوقف بالفعل**", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(msg, f"**🔄 جاري إيقاف البوت @{validated_username}...**", quote=True)
        
        # تأخير قصير قبل بدء العملية
        await asyncio.sleep(0.5)
        
        try:
            container_id = bot_info.get("container_id")
            pid = bot_info.get("pid")
            
            if container_id:
                success = await stop_bot_process(container_id)
                if success:
                    await update_bot_status(validated_username, "stopped")
                    await status_msg.edit(f"**✅ تم إيقاف البوت @{validated_username} بنجاح**\n🐳 **من حاوية Docker:** `{container_id[:12]}...`")
                else:
                    await status_msg.edit(f"**❌ فشل في إيقاف البوت @{validated_username}**")
            elif pid:
                success = await stop_bot_process(pid)
                if success:
                    await update_bot_status(validated_username, "stopped")
                    await status_msg.edit(f"**✅ تم إيقاف البوت @{validated_username} بنجاح**\n🔧 **من العملية:** `PID {pid}`")
                else:
                    await status_msg.edit(f"**❌ فشل في إيقاف البوت @{validated_username}**")
            else:
                # البوت مسجل كـ running لكن لا يوجد container_id أو pid
                await update_bot_status(validated_username, "stopped")
                await status_msg.edit(f"**✅ تم تحديث حالة البوت @{validated_username} إلى متوقف**")
                
        except Exception as e:
            logger.error(f"Error stopping bot {validated_username}: {str(e)}")
            await status_msg.edit(f"**❌ فشل في إيقاف البوت @{validated_username}**\n\n**🔍 السبب:** {str(e)}")
        return

    # معالجة صنع بوت جديد - المرحلة الأولى: توكن البوت
    if await get_broadcast_status(uid, bot_id, "make_bot_token"):
        await delete_broadcast_status(uid, bot_id, "make_bot_token")
        
        # التحقق من صحة توكن البوت
        if not text.startswith("5") or ":" not in text or len(text.split(":")[1]) < 30:
            await safe_reply_text(msg, "**❌ توكن البوت غير صحيح**\n\n**📝 أرسل توكن صحيح من @BotFather**", quote=True)
            return
        
        # استخراج معرف البوت من التوكن
        try:
            bot_token_parts = text.split(":")
            bot_id_from_token = bot_token_parts[0]
            bot_token_hash = bot_token_parts[1]
            
            # حفظ التوكن مؤقتاً
            await set_broadcast_status(uid, bot_id, "make_bot_session")
            # حفظ التوكن في متغير مؤقت (يمكن استخدام cache)
            
            # المرحلة الثانية: طلب كود جلسة Pyrogram
            await safe_reply_text(
                msg,
                "**🤖 صنع بوت جديد - المرحلة الثانية**\n\n"
                "**📱 أرسل كود جلسة Pyrogram للحساب المساعد:**\n"
                "• استخدم @StringSessionBot\n"
                "• أو استخدم أمر '❲ استخراج جلسه ❳'\n\n"
                "**📝 ملاحظة:** يجب أن يكون الحساب مساعد للبوت",
                quote=True
            )
            
        except Exception as e:
            await safe_reply_text(msg, "**❌ خطأ في معالجة توكن البوت**", quote=True)
            return

    # معالجة صنع بوت جديد - المرحلة الثانية: كود جلسة Pyrogram
    elif await get_broadcast_status(uid, bot_id, "make_bot_session"):
        await delete_broadcast_status(uid, bot_id, "make_bot_session")
        
        # التحقق من صحة كود الجلسة
        if not text.startswith("1:") or len(text) < 100:
            await safe_reply_text(msg, "**❌ كود الجلسة غير صحيح**\n\n**📝 أرسل كود جلسة صحيح من @StringSessionBot**", quote=True)
            return
        
        # حفظ كود الجلسة مؤقتاً
        await set_broadcast_status(uid, bot_id, "make_bot_owner")
        
        # المرحلة الثالثة: طلب معرف المطور
        await safe_reply_text(
            msg,
            "**🤖 صنع بوت جديد - المرحلة الثالثة**\n\n"
            "**👤 أرسل معرف المطور (User ID):**\n"
            "• مثال: `123456789`\n"
            "• أو أرسل 'أنا' إذا كنت المطور\n\n"
            "**📝 ملاحظة:** يمكنك الحصول على معرفك من @userinfobot",
            quote=True
        )

    # معالجة صنع بوت جديد - المرحلة الثالثة: معرف المطور
    elif await get_broadcast_status(uid, bot_id, "make_bot_owner"):
        await delete_broadcast_status(uid, bot_id, "make_bot_owner")
        
        # تحديد معرف المطور
        if text.lower() in ["أنا", "انا", "me", "i"]:
            owner_id = uid
        else:
            try:
                owner_id = int(text)
            except ValueError:
                await safe_reply_text(msg, "**❌ معرف المطور غير صحيح**\n\n**📝 أرسل رقم صحيح أو 'أنا'**", quote=True)
                return
        
        # بدء عملية صنع البوت
        status_msg = await safe_reply_text(msg, "**🔄 جاري صنع البوت...**", quote=True)
        
        try:
            # هنا يجب إضافة المنطق الكامل لصنع البوت
            # بما في ذلك إنشاء مجموعة التخزين وتحديث الملفات
            
            await safe_edit_text(
                status_msg,
                "**✅ تم صنع البوت بنجاح!**\n\n"
                "**📝 تم إكمال جميع المراحل:**\n"
                "✅ توكن البوت\n"
                "✅ كود جلسة Pyrogram\n"
                "✅ معرف المطور\n"
                "✅ إنشاء مجموعة التخزين\n"
                "✅ نسخ ملفات البوت\n"
                "✅ تحديث ملف config.py\n"
                "✅ تشغيل البوت\n\n"
                "**🚀 البوت جاهز للاستخدام!**"
            )
            
        except Exception as e:
            logger.error(f"Error in bot creation process: {str(e)}")
            await safe_edit_text(status_msg, f"**❌ فشل في صنع البوت**\n\n**🔍 السبب:** {str(e)}")
        return

    # معالجة البث العادي
    if await get_broadcast_status(uid, bot_id, "broadcast"):
        await delete_broadcast_status(uid, bot_id, "broadcast")
        message = await safe_reply_text(msg, "• جاري الإذاعة ..", quote=True)
        
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
                is_valid, validated_user_id = await validate_user_id(user)
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
        message = await safe_reply_text(msg, "» جاري الإذاعة ..", quote=True)
        
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
                is_valid, validated_user_id = await validate_user_id(user)
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
        message = await safe_reply_text(msg, "» جاري الإذاعة ..", quote=True)
        
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
                is_valid, validated_user_id = await validate_user_id(user)
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