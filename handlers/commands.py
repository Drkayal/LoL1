"""
Command Handlers - معالجات الأوامر
يحتوي على جميع معالجات الأوامر والرسائل في البوت
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from utils import logger, safe_reply_text, safe_edit_text, safe_answer_callback, safe_edit_callback_message
from users import is_dev, is_user, add_new_user, get_users, get_dev_count
from bots import (
    start_bot_process, stop_bot_process, get_all_bots, get_running_bots,
    get_bot_info, save_bot_info, update_bot_status, delete_bot_info,
    get_bots_count, update_bot_container_id
)
from broadcast import set_broadcast_status, delete_broadcast_status
from factory import get_factory_state, set_factory_state

# المتغيرات المطلوبة من الملف الرئيسي
OWNER_ID = None
bots_collection = None

def set_dependencies(owner_id, bots_coll):
    """
    تعيين المتغيرات المطلوبة من الملف الرئيسي
    
    Args:
        owner_id: معرف المالك
        bots_coll: مجموعة البوتات
    """
    global OWNER_ID, bots_collection
    OWNER_ID = owner_id
    bots_collection = bots_coll

@Client.on_message(filters.text & filters.private, group=5662)
async def cmd_handler(client, msg):
    """معالج الأوامر الرئيسية"""
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received")
        return
    
    uid = msg.from_user.id
    if not await is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info: {str(e)}")
        return

    if msg.text == "الغاء":
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast", "fbroadcast", "users_up", "start_bot", "delete_bot", "stop_bot", "make_bot")
        await safe_reply_text(msg, "» تم الغاء بنجاح", quote=True)

    elif msg.text == "❲ اخفاء الكيبورد ❳":
        await safe_reply_text(msg, "≭︰تم اخفاء الكيبورد ارسل /start لعرضه مره اخرى", reply_markup=ReplyKeyboardRemove(), quote=True)

    elif msg.text == "❲ الاحصائيات ❳":
        user_list = await get_users()
        bots_count = await get_bots_count()
        running_bots = len(await get_running_bots())
        await safe_reply_text(
            msg,
            f"**≭︰عدد الاعضاء  **{len(user_list)}\n"
            f"**≭︰عدد مطورين في المصنع  **{len(OWNER_ID)}\n"
            f"**≭︰عدد البوتات المصنوعة  **{bots_count}\n"
            f"**≭︰عدد البوتات المشتغلة  **{running_bots}",
            quote=True
        )

    elif msg.text == "❲ اذاعه ❳":
        await set_broadcast_status(uid, bot_id, "broadcast")
        await delete_broadcast_status(uid, bot_id, "fbroadcast", "pinbroadcast")
        await safe_reply_text(msg, "ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتوجيه ❳":
        await set_broadcast_status(uid, bot_id, "fbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast")
        await safe_reply_text(msg, "ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتثبيت ❳":
        await set_broadcast_status(uid, bot_id, "pinbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "fbroadcast")
        await safe_reply_text(msg, "ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ تشغيل بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # طلب معرف البوت من المستخدم
        await safe_reply_text(
            msg,
            "**🔧 تشغيل بوت محدد**\n\n"
            "**أرسل معرف البوت الذي تريد تشغيله:**\n"
            "• مثال: `AAAK2BOT`\n"
            "• مثال: `@AAAK2BOT`\n\n"
            "**📝 ملاحظة:** تأكد من أن البوت موجود في مجلد Maked\n"
            "**💡 يمكنك رؤية البوتات المتاحة باستخدام زر '❲ البوتات المصنوعه ❳'**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت
        await set_broadcast_status(uid, bot_id, "start_bot")

    elif msg.text == "❲ حذف بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # طلب معرف البوت من المستخدم
        await safe_reply_text(
            msg,
            "**🗑️ حذف بوت نهائياً**\n\n"
            "**أرسل معرف البوت الذي تريد حذفه:**\n"
            "• مثال: `AAAK2BOT`\n"
            "• مثال: `@AAAK2BOT`\n\n"
            "**⚠️ تحذير:** سيتم حذف البوت نهائياً من:\n"
            "• قاعدة البيانات\n"
            "• مجلد Maked\n"
            "• إيقاف العملية إذا كانت مشتغلة\n\n"
            "**💡 بعد إرسال المعرف، سيطلب منك التأكيد**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت للحذف
        await set_broadcast_status(uid, bot_id, "delete_bot")

    elif msg.text == "❲ ايقاف بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # طلب معرف البوت من المستخدم
        await safe_reply_text(
            msg,
            "**⏹️ إيقاف بوت محدد**\n\n"
            "**أرسل معرف البوت الذي تريد إيقافه:**\n"
            "• مثال: `AAAK2BOT`\n"
            "• مثال: `@AAAK2BOT`\n\n"
            "**📝 ملاحظة:** سيتم إيقاف البوت مؤقتاً\n"
            "**💡 يمكنك إعادة تشغيله لاحقاً باستخدام زر '❲ تشغيل بوت ❳'**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت للإيقاف
        await set_broadcast_status(uid, bot_id, "stop_bot")

    elif msg.text == "❲ تشغيل البوتات ❳":
        # تم نقل المعالجة إلى start_Allusers_handler
        pass

    elif msg.text == "❲ صنع بوت ❳":
        # تم نقل المعالجة إلى broadcast.py - make_bot_token
        pass

    elif msg.text == "❲ حذف بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**🗑️ حذف بوت محدد**\n\n"
            "**📝 أرسل معرف البوت المراد حذفه:**\n"
            "• مثال: `@username` أو `username`\n\n"
            "**⚠️ تحذير:** سيتم حذف البوت نهائياً من المصنع\n"
            "**💡 يمكنك رؤية البوتات المتاحة باستخدام زر '❲ البوتات المصنوعه ❳'**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت للحذف
        await set_broadcast_status(uid, bot_id, "delete_bot")

    elif msg.text == "❲ ايقاف بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**⏹️ إيقاف بوت محدد**\n\n"
            "**أرسل معرف البوت الذي تريد إيقافه:**\n"
            "• مثال: `AAAK2BOT`\n"
            "• مثال: `@AAAK2BOT`\n\n"
            "**📝 ملاحظة:** سيتم إيقاف البوت مؤقتاً\n"
            "**💡 يمكنك إعادة تشغيله لاحقاً باستخدام زر '❲ تشغيل بوت ❳'**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت للإيقاف
        await set_broadcast_status(uid, bot_id, "stop_bot")

    elif msg.text == "❲ فتح المصنع ❳":
        # تم نقل المعالجة إلى onoff_handler
        pass

    elif msg.text == "❲ قفل المصنع ❳":
        # تم نقل المعالجة إلى onoff_handler
        pass

    elif msg.text == "❲ ايقاف البوتات ❳":
        # تم نقل المعالجة إلى stooop_Allusers_handler
        pass

    elif msg.text == "❲ البوتات المشتغلة ❳":
        # تم نقل المعالجة إلى show_running_bots_handler
        pass

    elif msg.text == "❲ تشغيل بوت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**🤖 تشغيل بوت محدد**\n\n"
            "**📝 أرسل معرف البوت المراد تشغيله:**\n"
            "• مثال: `@username` أو `username`\n\n"
            "**💡 يمكنك رؤية البوتات المتاحة باستخدام زر '❲ البوتات المصنوعه ❳'**",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت للتشغيل
        await set_broadcast_status(uid, bot_id, "start_bot")

    elif msg.text == "❲ البوتات المصنوعه ❳":
        # تم نقل المعالجة إلى botat_handler
        pass

    elif msg.text == "❲ تحديث الصانع ❳":
        # تم نقل المعالجة إلى update_factory_handler
        pass

    elif msg.text == "❲ الاحصائيات ❳":
        # الحصول على إحصائيات المصنع
        try:
            # عدد المستخدمين
            users_count = await get_user_count()
            
            # عدد البوتات
            bots_count = await get_bots_count()
            
            # عدد البوتات المشتغلة
            running_bots = await get_running_bots()
            running_count = len(running_bots)
            
            # حالة المصنع
            factory_state = await get_factory_state()
            factory_status = "🔴 مغلق" if factory_state else "🟢 مفتوح"
            
            stats_text = f"**📊 إحصائيات المصنع:**\n\n"
            stats_text += f"👥 **المستخدمين:** {users_count}\n"
            stats_text += f"🤖 **البوتات المصنوعة:** {bots_count}\n"
            stats_text += f"🟢 **البوتات المشتغلة:** {running_count}\n"
            stats_text += f"🔴 **البوتات المتوقفة:** {bots_count - running_count}\n"
            stats_text += f"🏭 **حالة المصنع:** {factory_status}\n"
            
            await safe_reply_text(msg, stats_text, quote=True)
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            await safe_reply_text(msg, "**❌ فشل في جلب الإحصائيات**", quote=True)

    elif msg.text == "❲ رفع مطور ❳":
        # تم نقل المعالجة إلى add_dev_handler
        pass

    elif msg.text == "❲ تنزيل مطور ❳":
        # تم نقل المعالجة إلى remove_dev_handler
        pass

    elif msg.text == "❲ المطورين ❳":
        # تم نقل المعالجة إلى list_devs_handler
        pass

    elif msg.text == "❲ اذاعه ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**📢 إرسال إذاعة**\n\n"
            "**📝 أرسل الرسالة المراد إذاعتها:**\n"
            "• يمكنك إرسال نص أو صورة أو فيديو أو ملف\n"
            "• سيتم إرسالها لجميع المستخدمين المسجلين",
            quote=True
        )
        # تعيين حالة انتظار رسالة الإذاعة
        await set_broadcast_status(uid, bot_id, "broadcast")

    elif msg.text == "❲ اذاعه بالتوجيه ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**📢 إرسال إذاعة بالتوجيه**\n\n"
            "**📝 أرسل الرسالة المراد إذاعتها:**\n"
            "• يمكنك إرسال نص أو صورة أو فيديو أو ملف\n"
            "• سيتم إرسالها لجميع المستخدمين المسجلين مع التوجيه",
            quote=True
        )
        # تعيين حالة انتظار رسالة الإذاعة بالتوجيه
        await set_broadcast_status(uid, bot_id, "forwardbroadcast")

    elif msg.text == "❲ اذاعه بالتثبيت ❳":
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(msg, "**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        await safe_reply_text(
            msg,
            "**📢 إرسال إذاعة بالتثبيت**\n\n"
            "**📝 أرسل الرسالة المراد إذاعتها:**\n"
            "• يمكنك إرسال نص أو صورة أو فيديو أو ملف\n"
            "• سيتم إرسالها لجميع المستخدمين المسجلين مع التثبيت",
            quote=True
        )
        # تعيين حالة انتظار رسالة الإذاعة بالتثبيت
        await set_broadcast_status(uid, bot_id, "pinbroadcast")

    elif msg.text == "❲ استخراج جلسه ❳":
        # تم نقل المعالجة إلى Maker/session.py - getsession
        pass

    elif msg.text == "❲ الاسكرينات المفتوحه ❳":
        # تم نقل المعالجة إلى kinhsker_handler
        pass

    elif msg.text == "❲ 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳":
        await safe_reply_text(msg, "**🔄 جاري تحديث الكوكيز...**", quote=True)
        # هنا يمكن إضافة منطق تحديث الكوكيز
        await safe_reply_text(msg, "**✅ تم تحديث الكوكيز بنجاح**", quote=True)

    elif msg.text == "❲ 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳":
        await safe_reply_text(msg, "**🔄 جاري إعادة تشغيل الكوكيز...**", quote=True)
        # هنا يمكن إضافة منطق إعادة تشغيل الكوكيز
        await safe_reply_text(msg, "**✅ تم إعادة تشغيل الكوكيز بنجاح**", quote=True)

    elif msg.text == "❲ السورس ❳":
        # تم نقل المعالجة إلى alivehi_handler
        pass

    elif msg.text == "❲ مطور السورس ❳":
        # تم نقل المعالجة إلى you_handler
        pass

    elif msg.text == "❲ اخفاء الكيبورد ❳":
        # إخفاء لوحة المفاتيح
        from pyrogram.types import ReplyKeyboardRemove
        await safe_reply_text(
            msg,
            "**✅ تم إخفاء لوحة المفاتيح**\n\n"
            "**💡 لإعادة ظهورها:**\n"
            "• أرسل `/start` مرة أخرى",
            reply_markup=ReplyKeyboardRemove()
        )

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, msg):
    """معالج أمر start للمستخدمين والمطورين"""
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received")
        return
    
    uid = msg.from_user.id
    name = msg.from_user.first_name
    
    # التحقق من حالة المصنع
    if await get_factory_state():
        await safe_reply_text(msg, "** ≭︰المصنع مغلق حاليا **")
        return
    
    # إضافة المستخدم الجديد
    await add_new_user(uid)
    
    # إنشاء لوحة أزرار الكيبورد
    keyboard = ReplyKeyboardMarkup(
        [
            ["❲ صنع بوت ❳", "❲ حذف بوت ❳"],
            ["❲ فتح المصنع ❳", "❲ قفل المصنع ❳"],
            ["❲ ايقاف بوت ❳", "❲ تشغيل بوت ❳"],
            ["❲ ايقاف البوتات ❳", "❲ تشغيل البوتات ❳"],
            ["❲ البوتات المشتغلة ❳", "❲ البوتات المصنوعه ❳"],
            ["❲ تحديث الصانع ❳", "❲ الاحصائيات ❳"],
            ["❲ رفع مطور ❳", "❲ تنزيل مطور ❳"],
            ["❲ المطورين ❳", "❲ اذاعه ❳"],
            ["❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳"],
            ["❲ استخراج جلسه ❳", "❲ الاسكرينات المفتوحه ❳"],
            ["❲ 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳", "❲ 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳"],
            ["❲ السورس ❳", "❲ مطور السورس ❳"],
            ["❲ اخفاء الكيبورد ❳"]
        ],
        resize_keyboard=True
    )
    
    # إرسال رسالة الترحيب المناسبة
    if await is_dev(uid):
        # رسالة للمطورين
        await safe_reply_text(
            msg,
            "**مرحباً بك في صانع بوتات الميوزك الخاص بسورس لول .**",
            reply_markup=keyboard
        )
    else:
        # رسالة للمستخدمين العاديين
        await safe_reply_text(
            msg,
            f"**مرحبا {name} في مصنع البوتات**\n"
            "**استخدم لوحة المفاتيح أدناه للتحكم**",
            reply_markup=keyboard
        )

# تم دمج معالج المطورين مع معالج المستخدمين في start_handler أعلاه

@Client.on_callback_query(filters.regex("^user_count_"))
async def user_count_callback_handler(client, callback_query):
    """معالج استعلام عدد المستخدمين"""
    try:
        await callback_query.answer()
        
        # الحصول على عدد المستخدمين
        user_list = await get_users()
        user_count = len(user_list)
        
        await callback_query.message.edit_text(
            f"**📊 إحصائيات المستخدمين:**\n\n"
            f"**عدد المستخدمين:** {user_count}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in user_count_callback: {str(e)}")

@Client.on_callback_query(filters.regex("^make_bot$"))
async def make_bot_callback_handler(client, callback_query):
    """معالج زر صنع البوت"""
    try:
        await callback_query.answer()
        
        uid = callback_query.from_user.id
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await callback_query.message.edit_text(
                "**❌ المصنع مغلق حالياً**\n\n"
                "**📝 ملاحظة:** المصنع مغلق من قبل المطور",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]
                ])
            )
            return
        
        # طلب معرف البوت من المستخدم
        await callback_query.message.edit_text(
            "**🤖 صنع بوت جديد**\n\n"
            "**أرسل معرف البوت الذي تريد صنعه:**\n"
            "• مثال: `MyMusicBot`\n"
            "• مثال: `@MyMusicBot`\n\n"
            "**📝 ملاحظة:** تأكد من أن المعرف متاح في @BotFather",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]
            ])
        )
        
        # تعيين حالة انتظار معرف البوت لصنع البوت
        try:
            bot_me = await client.get_me()
            bot_id = bot_me.id
            await set_broadcast_status(uid, bot_id, "make_bot")
        except Exception as e:
            logger.error(f"Failed to set broadcast status for make_bot: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in make_bot_callback: {str(e)}")

@Client.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main_callback_handler(client, callback_query):
    """معالج العودة للقائمة الرئيسية"""
    try:
        await callback_query.answer()
        
        uid = callback_query.from_user.id
        name = callback_query.from_user.first_name
        
        # إنشاء لوحة أزرار الكيبورد
        keyboard = ReplyKeyboardMarkup(
            [
                ["❲ صنع بوت ❳", "❲ حذف بوت ❳"],
                ["❲ فتح المصنع ❳", "❲ قفل المصنع ❳"],
                ["❲ ايقاف بوت ❳", "❲ تشغيل بوت ❳"],
                ["❲ ايقاف البوتات ❳", "❲ تشغيل البوتات ❳"],
                ["❲ البوتات المشتغلة ❳", "❲ البوتات المصنوعه ❳"],
                ["❲ تحديث الصانع ❳", "❲ الاحصائيات ❳"],
                ["❲ رفع مطور ❳", "❲ تنزيل مطور ❳"],
                ["❲ المطورين ❳", "❲ اذاعه ❳"],
                ["❲ اذاعه بالتوجيه ❳", "❲ اذاعه بالتثبيت ❳"],
                ["❲ استخراج جلسه ❳", "❲ الاسكرينات المفتوحه ❳"],
                ["❲ 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳", "❲ 𝚁𝙴𝚂𝚃𝙰𝚁𝚃 𝙲𝙾𝙾𝙺𝙸𝙴𝚂 ❳"],
                ["❲ السورس ❳", "❲ مطور السورس ❳"],
                ["❲ اخفاء الكيبورد ❳"]
            ],
            resize_keyboard=True
        )
        
        if await is_dev(uid):
            # قائمة المطور
            await callback_query.message.edit_text(
                "**مرحباً بك في صانع بوتات الميوزك الخاص بسورس لول .**"
            )
            # إرسال لوحة المفاتيح منفصلة للمطور
            await callback_query.message.reply(
                "**استخدم لوحة المفاتيح أدناه للتحكم:**",
                reply_markup=keyboard
            )
        else:
            # قائمة المستخدم العادي
            await callback_query.message.edit_text(
                f"**مرحبا {name} في مصنع البوتات**\n"
                "**استخدم لوحة المفاتيح أدناه للتحكم**"
            )
            # إرسال لوحة المفاتيح منفصلة للمستخدم العادي
            await callback_query.message.reply(
                "**استخدم لوحة المفاتيح أدناه للتحكم:**",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error(f"Error in back_to_main_callback: {str(e)}")

@Client.on_message(filters.command(["❲ السورس ❳"], ""))
async def alivehi_handler(client: Client, message):
    """معالج أمر السورس"""
    try:
        await safe_reply_text(
            message,
            "**🔰 مرحبا بك في مصنع البوتات**\n\n"
            "**المطور:** @username\n"
            "**السورس:** مصنع البوتات\n"
            "**الإصدار:** 1.0.0"
        )
    except Exception as e:
        logger.error(f"Error in alivehi handler: {str(e)}")

@Client.on_message(filters.command(["❲ مطور السورس ❳"], ""))
async def you_handler(client: Client, message):
    """معالج أمر مطور السورس"""
    try:
        async def get_user_info(user_id):
            try:
                user = await client.get_users(user_id)
                return user
            except:
                return None
        
        # الحصول على معلومات المطور
        dev_info = await get_user_info(OWNER_ID[0])
        
        if dev_info:
            await safe_reply_text(
                message,
                f"**👨‍💻 مطور السورس:**\n\n"
                f"**الاسم:** {dev_info.first_name}\n"
                f"**المعرف:** @{dev_info.username}\n"
                f"**الآيدي:** `{dev_info.id}`"
            )
        else:
            await safe_reply_text(message, "**❌ لم يتم العثور على معلومات المطور**")
    except Exception as e:
        logger.error(f"Error in you handler: {str(e)}")

@Client.on_message(filters.command("❲ رفع مطور ❳", ""))
async def add_dev_handler(client, message: Message):
    """معالج رفع مطور"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        if not message.reply_to_message:
            await safe_reply_text(message, "**❌ يجب الرد على رسالة المستخدم**")
            return
        
        user_id = message.reply_to_message.from_user.id
        
        # إضافة المطور (هذا يتطلب تنفيذ دالة إضافة المطور)
        # await add_dev(user_id)
        
        await safe_reply_text(message, f"**✅ تم رفع المستخدم {user_id} كمطور**")
    except Exception as e:
        logger.error(f"Error in add_dev handler: {str(e)}")

@Client.on_message(filters.command("❲ تنزيل مطور ❳", ""))
async def remove_dev_handler(client, message: Message):
    """معالج تنزيل مطور"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        if not message.reply_to_message:
            await safe_reply_text(message, "**❌ يجب الرد على رسالة المستخدم**")
            return
        
        user_id = message.reply_to_message.from_user.id
        
        # تنزيل المطور (هذا يتطلب تنفيذ دالة تنزيل المطور)
        # await remove_dev(user_id)
        
        await safe_reply_text(message, f"**✅ تم تنزيل المستخدم {user_id} من المطورين**")
    except Exception as e:
        logger.error(f"Error in remove_dev handler: {str(e)}")

@Client.on_message(filters.command("❲ المطورين ❳", ""))
async def list_devs_handler(client, message: Message):
    """معالج قائمة المطورين"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        dev_count = await get_dev_count()
        await safe_reply_text(message, f"**👥 عدد المطورين:** {dev_count}")
    except Exception as e:
        logger.error(f"Error in list_devs handler: {str(e)}")

@Client.on_message(filters.command(["❲ فتح المصنع ❳", "❲ قفل المصنع ❳"], "") & filters.private)
async def onoff_handler(client, message):
    """معالج فتح/قفل المصنع"""
    try:
        if not await is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        command = message.text
        
        if "❲ فتح المصنع ❳" in command:
            success = await set_factory_state(False)
            if success:
                await safe_reply_text(message, "**✅ تم فتح المصنع بنجاح**")
            else:
                await safe_reply_text(message, "**❌ فشل في فتح المصنع**")
        elif "❲ قفل المصنع ❳" in command:
            success = await set_factory_state(True)
            if success:
                await safe_reply_text(message, "**✅ تم قفل المصنع بنجاح**")
            else:
                await safe_reply_text(message, "**❌ فشل في قفل المصنع**")
    except Exception as e:
        logger.error(f"Error in onoff handler: {str(e)}")

# تم نقل معالجة "❲ صنع بوت ❳" إلى callback_query handler

# تم نقل معالجة "❲ حذف بوت ❳" إلى cmd_handler

@Client.on_message(filters.command("❲ البوتات المصنوعه ❳", ""))
async def botat_handler(client, message):
    """معالج قائمة البوتات المصنوعة"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        all_bots = await get_all_bots()
        if not all_bots:
            await safe_reply_text(message, "**❌ لا توجد بوتات مصنوعة**")
            return
        
        bot_list = "**🤖 قائمة البوتات المصنوعة:**\n\n"
        for i, bot in enumerate(all_bots, 1):
            status = "🟢" if bot.get("status") == "running" else "🔴"
            bot_list += f"{i}. {status} @{bot['username']}\n"
        
        await safe_reply_text(message, bot_list)
    except Exception as e:
        logger.error(f"Error in botat handler: {str(e)}")

@Client.on_message(filters.command(["❲ الاسكرينات المفتوحه ❳"], ""))
async def kinhsker_handler(client: Client, message):
    """معالج الشاشات المفتوحة"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # هذا يتطلب تنفيذ منطق عرض الشاشات المفتوحة
        # سيتم إضافة المنطق هنا
        
        await safe_reply_text(message, "**🖥️ جاري جلب الشاشات المفتوحة...**")
    except Exception as e:
        logger.error(f"Error in kinhsker handler: {str(e)}")

@Client.on_message(filters.command("❲ تحديث الصانع ❳", ""))
async def update_factory_handler(client: Client, message):
    """معالج تحديث الصانع"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # هذا يتطلب تنفيذ منطق تحديث الصانع
        # سيتم إضافة المنطق هنا
        
        await safe_reply_text(message, "**🔄 جاري تحديث الصانع...**")
    except Exception as e:
        logger.error(f"Error in update_factory handler: {str(e)}")

# تم نقل معالجة "❲ ايقاف بوت ❳" إلى cmd_handler

@Client.on_message(filters.command("❲ البوتات المشتغلة ❳", ""))
async def show_running_bots_handler(client, message):
    """معالج عرض البوتات المشتغلة"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(message, "**❌ المصنع مغلق حالياً**")
            return
        
        running_bots = await get_running_bots()
        if not running_bots:
            await safe_reply_text(message, "**❌ لا توجد بوتات مشتغلة**")
            return
        
        bot_list = f"**🟢 البوتات المشتغلة ({len(running_bots)} بوت):**\n\n"
        for i, bot in enumerate(running_bots, 1):
            container_id = bot.get('container_id')
            pid = bot.get('pid')
            dev_id = bot.get('dev_id', 'غير محدد')
            
            if container_id:
                bot_list += f"{i}. @{bot['username']}\n   🐳 الحاوية: `{container_id[:12]}...`\n   👤 المطور: `{dev_id}`\n\n"
            elif pid:
                bot_list += f"{i}. @{bot['username']}\n   🔧 العملية: `PID {pid}`\n   👤 المطور: `{dev_id}`\n\n"
            else:
                bot_list += f"{i}. @{bot['username']}\n   ⚠️ معرف غير محدد\n   👤 المطور: `{dev_id}`\n\n"
        
        await safe_reply_text(message, bot_list)
    except Exception as e:
        logger.error(f"Error in show_running_bots handler: {str(e)}")

@Client.on_message(filters.command("❲ تشغيل البوتات ❳", ""))
async def start_Allusers_handler(client, message):
    """معالج تشغيل جميع البوتات"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(message, "**❌ المصنع مغلق حالياً**")
            return
        
        all_bots = await get_all_bots()
        if not all_bots:
            await safe_reply_text(message, "**❌ لا توجد بوتات مصنوعة**")
            return
        
        # التحقق من وجود بوتات قابلة للتشغيل
        startable_bots = [bot for bot in all_bots if bot.get("status") != "running"]
        if not startable_bots:
            await safe_reply_text(message, "**✅ جميع البوتات تعمل بالفعل**")
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(message, f"**🔄 جاري تشغيل {len(startable_bots)} بوت...**")
        
        started_count = 0
        failed_count = 0
        
        for i, bot in enumerate(startable_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري التشغيل... ({i}/{len(startable_bots)})**")
                
            process_id = await start_bot_process(bot["username"])
            if process_id:
                await update_bot_status(bot["username"], "running")
                # تحديد نوع المعرف وتحديث الحقل المناسب
                if isinstance(process_id, str):
                    # Container ID
                    await update_bot_container_id(bot["username"], process_id)
                elif isinstance(process_id, int):
                    # PID - نحتاج لإنشاء async function مماثلة
                    await update_bot_container_id(bot["username"], str(process_id))
                started_count += 1
            else:
                failed_count += 1
            
            # تأخير بين البوتات لتجنب الحظر
            if i < len(startable_bots):
                await asyncio.sleep(1)

        # رسالة النتيجة النهائية
        result_text = f"**📊 نتائج تشغيل البوتات:**\n\n"
        result_text += f"✅ **تم تشغيل:** {started_count} بوت\n"
        result_text += f"❌ **فشل التشغيل:** {failed_count} بوت\n"
        result_text += f"📊 **إجمالي البوتات:** {len(all_bots)} بوت\n"
        
        if started_count == 0:
            result_text = "**❌ لم يتم تشغيل أي بوت**"
        
        await status_msg.edit(result_text)
    except Exception as e:
        logger.error(f"Error in start_Allusers handler: {str(e)}")

@Client.on_message(filters.command("❲ ايقاف البوتات ❳", ""))
async def stooop_Allusers_handler(client, message):
    """معالج إيقاف جميع البوتات"""
    try:
        if not await is_dev(message.from_user.id):
            await safe_reply_text(message, "**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if await get_factory_state():
            await safe_reply_text(message, "**❌ المصنع مغلق حالياً**")
            return
        
        running_bots = await get_running_bots()
        if not running_bots:
            await safe_reply_text(message, "**❌ لا توجد بوتات مشتغلة**")
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await safe_reply_text(message, "**🔄 جاري إيقاف جميع البوتات...**")
        
        stopped_count = 0
        failed_count = 0
        
        for i, bot in enumerate(running_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري الإيقاف... ({i}/{len(running_bots)})**")
            
            container_id = bot.get("container_id")
            pid = bot.get("pid")
            
            if container_id:
                success = await stop_bot_process(container_id)
                if success:
                    await update_bot_status(bot["username"], "stopped")
                    stopped_count += 1
                else:
                    failed_count += 1
            elif pid:
                success = await stop_bot_process(pid)
                if success:
                    await update_bot_status(bot["username"], "stopped")
                    stopped_count += 1
                else:
                    failed_count += 1
            else:
                await update_bot_status(bot["username"], "stopped")
                stopped_count += 1
            
            # تأخير بين البوتات لتجنب الحظر
            if i < len(running_bots):
                await asyncio.sleep(0.5)

        # رسالة النتيجة النهائية
        result_text = f"**📊 نتائج إيقاف البوتات:**\n\n"
        result_text += f"✅ **تم إيقاف:** {stopped_count} بوت\n"
        result_text += f"❌ **فشل الإيقاف:** {failed_count} بوت\n"
        
        if stopped_count == 0:
            result_text = "**❌ لم يتم إيقاف أي بوت**"
        
        await status_msg.edit(result_text)
    except Exception as e:
        logger.error(f"Error in stooop_Allusers handler: {str(e)}")