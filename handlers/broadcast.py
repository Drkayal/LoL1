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

# استيراد المتغيرات من OWNER.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from OWNER import BOT_TOKEN, DATABASE

# استيراد API_ID و API_HASH من config.py
try:
    from config import API_ID, API_HASH
except ImportError:
    # قيم افتراضية إذا لم تكن موجودة
    API_ID = 123456
    API_HASH = "your_api_hash_here"

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
            
            # الحصول على معلومات البوت من Telegram API
            import requests
            bot_info_url = f"https://api.telegram.org/bot{text}/getMe"
            response = requests.get(bot_info_url)
            
            if response.status_code != 200:
                await safe_reply_text(msg, "**❌ توكن البوت غير صالح**\n\n**📝 تأكد من صحة التوكن من @BotFather**", quote=True)
                return
            
            bot_data = response.json()
            if not bot_data.get("ok"):
                await safe_reply_text(msg, "**❌ توكن البوت غير صالح**\n\n**📝 تأكد من صحة التوكن من @BotFather**", quote=True)
                return
            
            bot_username = bot_data["result"]["username"]
            bot_name = bot_data["result"]["first_name"]
            
            # حفظ البيانات في التخزين المؤقت
            from utils.cache import set_bot_creation_data
            bot_creation_data = {
                "bot_token": text,
                "bot_id": bot_id_from_token,
                "bot_username": bot_username,
                "bot_name": bot_name,
                "stage": "token_received"
            }
            set_bot_creation_data(uid, bot_creation_data)
            
            # المرحلة الثانية: طلب كود جلسة Pyrogram
            await set_broadcast_status(uid, bot_id, "make_bot_session")
            await safe_reply_text(
                msg,
                f"**🤖 صنع بوت جديد - المرحلة الثانية**\n\n"
                f"**✅ تم استلام توكن البوت:** @{bot_username}\n\n"
                f"**📱 أرسل كود جلسة Pyrogram للحساب المساعد:**\n"
                f"• استخدم @StringSessionBot\n"
                f"• أو استخدم أمر '❲ استخراج جلسه ❳'\n\n"
                f"**📝 ملاحظة:** يجب أن يكون الحساب مساعد للبوت @{bot_username}",
                quote=True
            )
            
        except Exception as e:
            logger.error(f"Error processing bot token: {str(e)}")
            await safe_reply_text(msg, "**❌ خطأ في معالجة توكن البوت**\n\n**📝 تأكد من صحة التوكن**", quote=True)
            return

    # معالجة صنع بوت جديد - المرحلة الثانية: كود جلسة Pyrogram
    elif await get_broadcast_status(uid, bot_id, "make_bot_session"):
        await delete_broadcast_status(uid, bot_id, "make_bot_session")
        
        # التحقق من صحة كود الجلسة
        if not text.startswith("1:") or len(text) < 100:
            await safe_reply_text(msg, "**❌ كود الجلسة غير صحيح**\n\n**📝 أرسل كود جلسة صحيح من @StringSessionBot**", quote=True)
            return
        
        # الحصول على البيانات المحفوظة
        from utils.cache import get_bot_creation_data, set_bot_creation_data
        bot_data = get_bot_creation_data(uid)
        if not bot_data:
            await safe_reply_text(msg, "**❌ انتهت صلاحية الجلسة**\n\n**📝 ابدأ العملية من جديد**", quote=True)
            return
        
        # تحديث البيانات بإضافة كود الجلسة
        bot_data["session_string"] = text
        bot_data["stage"] = "session_received"
        set_bot_creation_data(uid, bot_data)
        
        # المرحلة الثالثة: طلب معرف المطور
        await set_broadcast_status(uid, bot_id, "make_bot_owner")
        await safe_reply_text(
            msg,
            f"**🤖 صنع بوت جديد - المرحلة الثالثة**\n\n"
            f"**✅ تم استلام كود الجلسة للحساب المساعد**\n\n"
            f"**👤 أرسل معرف المطور (User ID):**\n"
            f"• مثال: `123456789`\n"
            f"• أو أرسل 'أنا' إذا كنت المطور\n\n"
            f"**📝 ملاحظة:** يمكنك الحصول على معرفك من @userinfobot",
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
        
        # الحصول على البيانات المحفوظة
        from utils.cache import get_bot_creation_data, delete_bot_creation_data
        bot_data = get_bot_creation_data(uid)
        if not bot_data:
            await safe_reply_text(msg, "**❌ انتهت صلاحية الجلسة**\n\n**📝 ابدأ العملية من جديد**", quote=True)
            return
        
        # بدء عملية صنع البوت
        status_msg = await safe_reply_text(msg, "**🔄 جاري صنع البوت...**", quote=True)
        
        try:
            # المرحلة الرابعة: إنشاء مجموعة التخزين
            await safe_edit_text(status_msg, "**📱 المرحلة الرابعة: إنشاء مجموعة التخزين...**")
            
            # استخدام الحساب المساعد لإنشاء مجموعة
            from pyrogram import Client
            assistant_client = Client(
                "assistant_session",
                session_string=bot_data["session_string"],
                api_id=API_ID,
                api_hash=API_HASH
            )
            
            await assistant_client.start()
            
            # إنشاء مجموعة التخزين
            chat = await assistant_client.create_supergroup(
                title=f"Logs - {bot_data['bot_name']}",
                description="مجموعة تخزين سجلات البوت"
            )
            
            # رفع البوت في المجموعة
            await assistant_client.promote_chat_member(
                chat_id=chat.id,
                user_id=int(bot_data["bot_id"]),
                privileges={
                    "can_post_messages": True,
                    "can_edit_messages": True,
                    "can_delete_messages": True,
                    "can_restrict_members": True,
                    "can_invite_users": True,
                    "can_pin_messages": True,
                    "can_manage_chat": True
                }
            )
            
            log_group_id = chat.id
            
            await assistant_client.stop()
            
            # المرحلة الخامسة: نسخ ملفات البوت
            await safe_edit_text(status_msg, "**📁 المرحلة الخامسة: نسخ ملفات البوت...**")
            
            import os
            import shutil
            bot_path = os.path.join("Maked", bot_data["bot_username"])
            
            if os.path.exists(bot_path):
                shutil.rmtree(bot_path)
            
            # نسخ مجلد Make إلى مجلد البوت
            make_path = "Make"
            if not os.path.exists(make_path):
                await safe_edit_text(status_msg, "**❌ مجلد Make غير موجود**")
                return
            
            shutil.copytree(make_path, bot_path)
            
            # المرحلة السادسة: تحديث ملف config.py
            await safe_edit_text(status_msg, "**⚙️ المرحلة السادسة: تحديث ملف config.py...**")
            
            config_file = os.path.join(bot_path, "config.py")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # تحديث التوكن
                config_content = config_content.replace(
                    'BOT_TOKEN = getenv("BOT_TOKEN", "7557280783:AAF44S35fdkcURM4j4Rp5-OOkASZ3_uCSR4")',
                    f'BOT_TOKEN = getenv("BOT_TOKEN", "{bot_data["bot_token"]}")'
                )
                
                # تحديث كود الجلسة
                config_content = config_content.replace(
                    'API_HASH = getenv("API_HASH", "ed923c3d59d699018e79254c6f8b6671")',
                    f'API_HASH = getenv("API_HASH", "{API_HASH}")'
                )
                
                # إضافة معرف مجموعة السجل
                if "LOG_GROUP_ID" not in config_content:
                    config_content += f'\nLOG_GROUP_ID = {log_group_id}'
                else:
                    config_content = config_content.replace(
                        'LOG_GROUP_ID = -1001234567890',
                        f'LOG_GROUP_ID = {log_group_id}'
                    )
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(config_content)
            
            # تحديث ملف OWNER.py
            owner_file = os.path.join(bot_path, "OWNER.py")
            if os.path.exists(owner_file):
                with open(owner_file, 'r', encoding='utf-8') as f:
                    owner_content = f.read()
                
                # تحديث معرف المطور
                owner_content = owner_content.replace(
                    'OWNER__ID = 985612253',
                    f'OWNER__ID = {owner_id}'
                )
                owner_content = owner_content.replace(
                    'OWNER_DEVELOPER = 985612253',
                    f'OWNER_DEVELOPER = {owner_id}'
                )
                
                # تحديث اسم المطور
                user_name = msg.from_user.first_name
                owner_content = owner_content.replace(
                    'OWNER_NAME = "𝐷𝑟. 𝐾ℎ𝑎𝑦𝑎𝑙 𓏺"',
                    f'OWNER_NAME = "{user_name}"'
                )
                
                # تحديث معرف البوت
                owner_content = owner_content.replace(
                    'OWNER = ["AAAKP"]',
                    f'OWNER = ["{bot_data["bot_username"]}"]'
                )
                
                with open(owner_file, 'w', encoding='utf-8') as f:
                    f.write(owner_content)
            
            # المرحلة السابعة: تشغيل البوت
            await safe_edit_text(status_msg, "**🚀 المرحلة السابعة: تشغيل البوت...**")
            
            # حفظ معلومات البوت في قاعدة البيانات
            config_data = {
                "bot_username": bot_data["bot_username"],
                "owner_id": owner_id,
                "owner_name": user_name,
                "bot_token": bot_data["bot_token"],
                "session_string": bot_data["session_string"],
                "log_group_id": log_group_id,
                "created_at": datetime.now().isoformat(),
                "status": "created"
            }
            
            save_success = await save_bot_info(bot_data["bot_username"], owner_id, None, config_data)
            if not save_success:
                await safe_edit_text(status_msg, "**❌ فشل في حفظ معلومات البوت في قاعدة البيانات**")
                return
            
            # تشغيل البوت
            process_id = await start_bot_process(bot_data["bot_username"])
            if process_id:
                await update_bot_status(bot_data["bot_username"], "running")
                await update_bot_process_id(bot_data["bot_username"], process_id)
                
                # حذف البيانات المؤقتة
                delete_bot_creation_data(uid)
                
                await safe_edit_text(
                    status_msg,
                    f"**✅ تم صنع البوت @{bot_data['bot_username']} بنجاح!**\n\n"
                    f"**📝 تم إكمال جميع المراحل:**\n"
                    f"✅ توكن البوت\n"
                    f"✅ كود جلسة Pyrogram\n"
                    f"✅ معرف المطور: {owner_id}\n"
                    f"✅ إنشاء مجموعة التخزين: {log_group_id}\n"
                    f"✅ نسخ ملفات البوت\n"
                    f"✅ تحديث ملف config.py\n"
                    f"✅ تشغيل البوت\n\n"
                    f"**🚀 البوت جاهز للاستخدام!**\n"
                    f"**📁 المجلد:** `{bot_path}`\n"
                    f"**👤 المطور:** `{user_name}`"
                )
            else:
                await safe_edit_text(
                    status_msg,
                    f"**⚠️ تم صنع البوت @{bot_data['bot_username']} لكن فشل في تشغيله**\n\n"
                    f"**📝 يمكنك تشغيله يدوياً باستخدام زر '❲ تشغيل بوت ❳'**"
                )
            
        except Exception as e:
            logger.error(f"Error in bot creation process: {str(e)}")
            await safe_edit_text(status_msg, f"**❌ فشل في صنع البوت**\n\n**🔍 السبب:** {str(e)}")
            # حذف البيانات المؤقتة في حالة الخطأ
            delete_bot_creation_data(uid)
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