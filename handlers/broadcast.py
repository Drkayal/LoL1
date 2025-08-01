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
    
    # التحقق من وجود مجلد البوت
    import os
    bot_path = os.path.join("Maked", validated_username)
    if not os.path.exists(bot_path):
        await safe_reply_text(
            msg, 
            f"**❌ مجلد البوت @{validated_username} غير موجود**\n\n"
            "**📝 الحل:**\n"
            "• تأكد من أن البوت تم صنعه بشكل صحيح\n"
            "• جرب إعادة صنع البوت باستخدام زر '❲ صنع بوت ❳'", 
            quote=True
        )
        return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(msg, f"**🔄 جاري تشغيل البوت @{validated_username}...**", quote=True)
        
        # تأخير قصير قبل بدء العملية
        await asyncio.sleep(0.5)
        
        try:
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
                # فحص الأسباب المحتملة للفشل
                import os
                bot_path = os.path.join("Maked", validated_username)
                
                error_message = f"**❌ فشل في تشغيل البوت @{validated_username}**\n\n**🔍 الأسباب المحتملة:**\n"
                
                if not os.path.exists(bot_path):
                    error_message += "• ❌ البوت غير موجود في مجلد Maked\n"
                else:
                    error_message += "• ✅ البوت موجود في مجلد Maked\n"
                    
                    # فحص ملف config.py
                    config_file = os.path.join(bot_path, "config.py")
                    if not os.path.exists(config_file):
                        error_message += "• ❌ ملف config.py غير موجود\n"
                    else:
                        error_message += "• ✅ ملف config.py موجود\n"
                    
                    # فحص ملف OWNER.py
                    owner_file = os.path.join(bot_path, "OWNER.py")
                    if not os.path.exists(owner_file):
                        error_message += "• ❌ ملف OWNER.py غير موجود\n"
                    else:
                        error_message += "• ✅ ملف OWNER.py موجود\n"
                
                error_message += "\n**💡 الحلول:**\n"
                error_message += "• تأكد من صحة ملفات البوت\n"
                error_message += "• تحقق من صحة التوكن في config.py\n"
                error_message += "• تأكد من صحة معرف المطور في OWNER.py\n"
                error_message += "• جرب إعادة تشغيل البوت لاحقاً"
                
                await status_msg.edit(error_message)
        except Exception as e:
            logger.error(f"Error starting bot {validated_username}: {str(e)}")
            await status_msg.edit(f"**❌ فشل في تشغيل البوت @{validated_username}**\n\n**🔍 السبب:** {str(e)}")
        return

    # معالجة حذف بوت محدد - مرحلة التأكيد
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
        
        # حفظ معلومات البوت للتأكيد
        from utils.cache import set_bot_creation_data
        delete_data = {
            "bot_username": validated_username,
            "bot_info": bot_info,
            "stage": "delete_confirmation"
        }
        set_bot_creation_data(uid, delete_data)
        
        # طلب التأكيد
        status_text = f"**🗑️ تأكيد حذف البوت @{validated_username}**\n\n"
        status_text += f"**📋 معلومات البوت:**\n"
        status_text += f"• **الاسم:** {bot_info.get('bot_name', 'غير محدد')}\n"
        status_text += f"• **المطور:** {bot_info.get('owner_name', 'غير محدد')}\n"
        status_text += f"• **الحالة:** {bot_info.get('status', 'غير محدد')}\n"
        status_text += f"• **تاريخ الإنشاء:** {bot_info.get('created_at', 'غير محدد')}\n\n"
        status_text += f"**⚠️ تحذير:** سيتم حذف البوت نهائياً من:\n"
        status_text += f"• قاعدة البيانات\n"
        status_text += f"• مجلد Maked\n"
        status_text += f"• إيقاف العملية إذا كانت مشتغلة\n\n"
        status_text += f"**📝 أرسل 'نعم' لتأكيد الحذف أو 'لا' للإلغاء**"
        
        await safe_reply_text(msg, status_text, quote=True)
        await set_broadcast_status(uid, bot_id, "delete_bot_confirm")
        return

    # معالجة تأكيد حذف البوت
    if await get_broadcast_status(uid, bot_id, "delete_bot_confirm"):
        await delete_broadcast_status(uid, bot_id, "delete_bot_confirm")
        
        # التحقق من التأكيد
        if text.lower() not in ["نعم", "yes", "y", "1"]:
            await safe_reply_text(msg, "**❌ تم إلغاء عملية الحذف**", quote=True)
            # حذف البيانات المؤقتة
            from utils.cache import delete_bot_creation_data
            delete_bot_creation_data(uid)
            return
        
        # الحصول على بيانات البوت
        from utils.cache import get_bot_creation_data, delete_bot_creation_data
        delete_data = get_bot_creation_data(uid)
        if not delete_data or delete_data.get("stage") != "delete_confirmation":
            await safe_reply_text(msg, "**❌ انتهت صلاحية الجلسة**\n\n**📝 ابدأ العملية من جديد**", quote=True)
            return
        
        validated_username = delete_data["bot_username"]
        bot_info = delete_data["bot_info"]
        
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
        finally:
            # حذف البيانات المؤقتة
            delete_bot_creation_data(uid)
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
        import re
        
        # تحسين التحقق من صيغة التوكن
        if not re.match(r'^\d+:[A-Za-z0-9_-]{35,}$', text):
            await safe_reply_text(
                msg, 
                "**❌ صيغة توكن البوت غير صحيحة**\n\n"
                "**📝 الصيغة الصحيحة:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`\n"
                "**📝 احصل على التوكن من @BotFather**", 
                quote=True
            )
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
            
            # التحقق من عدم وجود البوت مسبقاً
            existing_bot = await get_bot_info(bot_username)
            if existing_bot:
                await safe_reply_text(
                    msg,
                    f"**⚠️ البوت @{bot_username} موجود بالفعل في المصنع**\n\n"
                    "**📝 يمكنك:**\n"
                    "• استخدام زر '❲ تشغيل بوت ❳' لتشغيله\n"
                    "• استخدام زر '❲ حذف بوت ❳' لحذفه أولاً", 
                    quote=True
                )
                return
            
            # التحقق من عدم وجود مجلد البوت
            import os
            bot_path = os.path.join("Maked", bot_username)
            if os.path.exists(bot_path):
                await safe_reply_text(
                    msg,
                    f"**⚠️ مجلد البوت @{bot_username} موجود بالفعل**\n\n"
                    "**📝 يمكنك:**\n"
                    "• استخدام زر '❲ حذف بوت ❳' لحذفه أولاً", 
                    quote=True
                )
                return
            
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
            await safe_reply_text(
                msg, 
                "**❌ كود الجلسة غير صحيح**\n\n"
                "**📝 الصيغة الصحيحة:** `1:...` (أكثر من 100 حرف)\n"
                "**📝 احصل على كود الجلسة من @StringSessionBot**", 
                quote=True
            )
            return
        
        # التحقق من صحة كود الجلسة عبر اختبار الاتصال
        try:
            from pyrogram import Client
            test_client = Client(
                "test_session",
                session_string=text,
                api_id=API_ID,
                api_hash=API_HASH
            )
            await test_client.start()
            me = await test_client.get_me()
            await test_client.stop()
            
            # التحقق من أن الحساب مساعد للبوت
            bot_data = get_bot_creation_data(uid)
            if bot_data and "bot_username" in bot_data:
                # محاولة الحصول على معلومات البوت
                try:
                    bot_info = await test_client.get_chat(f"@{bot_data['bot_username']}")
                    # إذا وصلنا هنا، فالحساب مساعد للبوت
                except Exception:
                    await safe_reply_text(
                        msg,
                        f"**❌ الحساب غير مساعد للبوت @{bot_data['bot_username']}**\n\n"
                        "**📝 تأكد من:**\n"
                        "• إضافة الحساب كمساعد للبوت\n"
                        "• صحة كود الجلسة\n"
                        "• أن الحساب نشط", 
                        quote=True
                    )
                    return
        except Exception as e:
            await safe_reply_text(
                msg,
                f"**❌ كود الجلسة غير صالح**\n\n"
                "**🔍 السبب:** {str(e)}\n\n"
                "**📝 تأكد من صحة كود الجلسة**", 
                quote=True
            )
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
            from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant
            
            assistant_client = Client(
                "assistant_session",
                session_string=bot_data["session_string"],
                api_id=API_ID,
                api_hash=API_HASH
            )
            
            try:
                await assistant_client.start()
                
                # إنشاء مجموعة التخزين
                try:
                    chat = await assistant_client.create_supergroup(
                        title=f"Logs - {bot_data['bot_name']}",
                        description="مجموعة تخزين سجلات البوت"
                    )
                    log_group_id = chat.id
                    
                    # رفع البوت في المجموعة
                    try:
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
                    except ChatAdminRequired:
                        await safe_edit_text(status_msg, "**⚠️ تم إنشاء المجموعة لكن فشل في رفع البوت كإشراف**")
                        log_group_id = chat.id
                    except Exception as e:
                        await safe_edit_text(status_msg, f"**⚠️ تم إنشاء المجموعة لكن فشل في رفع البوت: {str(e)}**")
                        log_group_id = chat.id
                        
                except FloodWait as e:
                    await safe_edit_text(status_msg, f"**❌ تم حظر الحساب مؤقتاً: {e.value} ثانية**")
                    await assistant_client.stop()
                    return
                except Exception as e:
                    await safe_edit_text(status_msg, f"**❌ فشل في إنشاء مجموعة التخزين: {str(e)}**")
                    await assistant_client.stop()
                    return
                    
            except Exception as e:
                await safe_edit_text(status_msg, f"**❌ فشل في الاتصال بالحساب المساعد: {str(e)}**")
                return
            finally:
                try:
                    await assistant_client.stop()
                except:
                    pass
            
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
            
            try:
                shutil.copytree(make_path, bot_path)
            except Exception as e:
                await safe_edit_text(status_msg, f"**❌ فشل في نسخ ملفات البوت: {str(e)}**")
                return
            
            # المرحلة السادسة: تحديث ملف config.py
            await safe_edit_text(status_msg, "**⚙️ المرحلة السادسة: تحديث ملف config.py...**")
            
            config_file = os.path.join(bot_path, "config.py")
            if os.path.exists(config_file):
                # إنشاء نسخة احتياطية
                backup_config = config_file + ".backup"
                shutil.copy2(config_file, backup_config)
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # تحديث التوكن
                old_token_pattern = r'BOT_TOKEN\s*=\s*getenv\("BOT_TOKEN",\s*"[^"]*"\)'
                new_token_line = f'BOT_TOKEN = getenv("BOT_TOKEN", "{bot_data["bot_token"]}")'
                if re.search(old_token_pattern, config_content):
                    config_content = re.sub(old_token_pattern, new_token_line, config_content)
                else:
                    # إضافة التوكن إذا لم يكن موجوداً
                    config_content += f'\n{new_token_line}'
                
                # تحديث API_HASH
                old_hash_pattern = r'API_HASH\s*=\s*getenv\("API_HASH",\s*"[^"]*"\)'
                new_hash_line = f'API_HASH = getenv("API_HASH", "{API_HASH}")'
                if re.search(old_hash_pattern, config_content):
                    config_content = re.sub(old_hash_pattern, new_hash_line, config_content)
                else:
                    # إضافة API_HASH إذا لم يكن موجوداً
                    config_content += f'\n{new_hash_line}'
                
                # إضافة معرف مجموعة السجل
                log_group_pattern = r'LOG_GROUP_ID\s*=\s*[-\d]+'
                new_log_group_line = f'LOG_GROUP_ID = {log_group_id}'
                if re.search(log_group_pattern, config_content):
                    config_content = re.sub(log_group_pattern, new_log_group_line, config_content)
                else:
                    # إضافة معرف مجموعة السجل إذا لم يكن موجوداً
                    config_content += f'\n{new_log_group_line}'
                
                try:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(config_content)
                except Exception as e:
                    await safe_edit_text(status_msg, f"**❌ فشل في تحديث ملف config.py: {str(e)}**")
                    return
            
            # تحديث ملف OWNER.py
            owner_file = os.path.join(bot_path, "OWNER.py")
            if os.path.exists(owner_file):
                # إنشاء نسخة احتياطية
                backup_owner = owner_file + ".backup"
                shutil.copy2(owner_file, backup_owner)
                
                with open(owner_file, 'r', encoding='utf-8') as f:
                    owner_content = f.read()
                
                # تحديث معرف المطور
                user_name = msg.from_user.first_name
                
                # تحديث OWNER__ID
                owner_id_pattern = r'OWNER__ID\s*=\s*\d+'
                new_owner_id_line = f'OWNER__ID = {owner_id}'
                if re.search(owner_id_pattern, owner_content):
                    owner_content = re.sub(owner_id_pattern, new_owner_id_line, owner_content)
                else:
                    owner_content += f'\n{new_owner_id_line}'
                
                # تحديث OWNER_DEVELOPER
                developer_pattern = r'OWNER_DEVELOPER\s*=\s*\d+'
                new_developer_line = f'OWNER_DEVELOPER = {owner_id}'
                if re.search(developer_pattern, owner_content):
                    owner_content = re.sub(developer_pattern, new_developer_line, owner_content)
                else:
                    owner_content += f'\n{new_developer_line}'
                
                # تحديث اسم المطور
                name_pattern = r'OWNER_NAME\s*=\s*"[^"]*"'
                new_name_line = f'OWNER_NAME = "{user_name}"'
                if re.search(name_pattern, owner_content):
                    owner_content = re.sub(name_pattern, new_name_line, owner_content)
                else:
                    owner_content += f'\n{new_name_line}'
                
                # تحديث معرف البوت
                bot_pattern = r'OWNER\s*=\s*\["[^"]*"\]'
                new_bot_line = f'OWNER = ["{bot_data["bot_username"]}"]'
                if re.search(bot_pattern, owner_content):
                    owner_content = re.sub(bot_pattern, new_bot_line, owner_content)
                else:
                    owner_content += f'\n{new_bot_line}'
                
                try:
                    with open(owner_file, 'w', encoding='utf-8') as f:
                        f.write(owner_content)
                except Exception as e:
                    await safe_edit_text(status_msg, f"**❌ فشل في تحديث ملف OWNER.py: {str(e)}**")
                    return
            
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
            try:
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
                logger.error(f"Error starting bot {bot_data['bot_username']}: {str(e)}")
                await safe_edit_text(
                    status_msg,
                    f"**⚠️ تم صنع البوت @{bot_data['bot_username']} لكن فشل في تشغيله**\n\n"
                    f"**🔍 السبب:** {str(e)}\n\n"
                    f"**📝 يمكنك تشغيله يدوياً باستخدام زر '❲ تشغيل بوت ❳'**"
                )
            
        except Exception as e:
            logger.error(f"Error in bot creation process: {str(e)}")
            
            # تنظيف البيانات المؤقتة
            delete_bot_creation_data(uid)
            
            # محاولة حذف المجلد إذا تم إنشاؤه جزئياً
            try:
                if 'bot_path' in locals() and os.path.exists(bot_path):
                    shutil.rmtree(bot_path)
            except:
                pass
            
            # إرسال رسالة الخطأ
            error_message = f"**❌ فشل في صنع البوت**\n\n**🔍 السبب:** {str(e)}"
            
            # إضافة اقتراحات حسب نوع الخطأ
            if "FloodWait" in str(e):
                error_message += "\n\n**💡 الحل:** انتظر قليلاً ثم حاول مرة أخرى"
            elif "ChatAdminRequired" in str(e):
                error_message += "\n\n**💡 الحل:** تأكد من أن الحساب مساعد للبوت"
            elif "FileNotFoundError" in str(e):
                error_message += "\n\n**💡 الحل:** تأكد من وجود مجلد Make"
            elif "PermissionError" in str(e):
                error_message += "\n\n**💡 الحل:** تأكد من صلاحيات الكتابة"
            
            await safe_edit_text(status_msg, error_message)
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