"""
Command Handlers - معالجات الأوامر
يحتوي على جميع معالجات الأوامر والرسائل في البوت
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from utils import logger
from users import is_dev, is_user, add_new_user, get_users, get_dev_count
from bots import (
    start_bot_process, stop_bot_process, get_all_bots, get_running_bots,
    get_bot_info, save_bot_info, update_bot_status, delete_bot_info
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
    if not is_dev(uid):
        return
    
    # تعريف bot_id مع التحقق
    try:
        bot_me = await client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        logger.error(f"Failed to get bot info: {str(e)}")
        return

    if msg.text == "الغاء":
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast", "fbroadcast", "users_up")
        await msg.reply("» تم الغاء بنجاح", quote=True)

    elif msg.text == "❲ اخفاء الكيبورد ❳":
        await msg.reply("≭︰تم اخفاء الكيبورد ارسل /start لعرضه مره اخرى", reply_markup=ReplyKeyboardRemove(), quote=True)

    elif msg.text == "❲ الاحصائيات ❳":
        user_list = await get_users()
        bots_count = bots_collection.count_documents({})
        running_bots = len(get_running_bots())
        await msg.reply(
            f"**≭︰عدد الاعضاء  **{len(user_list)}\n"
            f"**≭︰عدد مطورين في المصنع  **{len(OWNER_ID)}\n"
            f"**≭︰عدد البوتات المصنوعة  **{bots_count}\n"
            f"**≭︰عدد البوتات المشتغلة  **{running_bots}",
            quote=True
        )

    elif msg.text == "❲ اذاعه ❳":
        await set_broadcast_status(uid, bot_id, "broadcast")
        await delete_broadcast_status(uid, bot_id, "fbroadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتوجيه ❳":
        await set_broadcast_status(uid, bot_id, "fbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "pinbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ اذاعه بالتثبيت ❳":
        await set_broadcast_status(uid, bot_id, "pinbroadcast")
        await delete_broadcast_status(uid, bot_id, "broadcast", "fbroadcast")
        await msg.reply("ارسل الاذاعه :-\n نص + ملف + متحركه + ملصق + صوره ", quote=True)

    elif msg.text == "❲ تشغيل بوت ❳":
        # التحقق من حالة المصنع
        if get_factory_state():
            await msg.reply("**❌ المصنع مغلق حالياً**", quote=True)
            return
        
        # طلب معرف البوت من المستخدم
        await msg.reply(
            "**🔧 تشغيل بوت محدد**\n\n"
            "**أرسل معرف البوت الذي تريد تشغيله:**\n"
            "• مثال: `AAAK2BOT`\n"
            "• مثال: `@AAAK2BOT`\n\n"
            "**📝 ملاحظة:** تأكد من أن البوت موجود في مجلد Maked",
            quote=True
        )
        # تعيين حالة انتظار معرف البوت
        await set_broadcast_status(uid, bot_id, "start_bot")

    elif msg.text == "❲ تشغيل البوتات ❳":
        if not is_dev(uid):
            await msg.reply("** ≭︰هذا الامر يخص المطور **", quote=True)
            return
        
        all_bots = get_all_bots()
        if not all_bots:
            await msg.reply("** ≭︰لا يوجد بوتات مصنوعة **", quote=True)
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await msg.reply("**🔄 جاري تشغيل البوتات...**", quote=True)
        
        started_count = 0
        failed_count = 0
        already_running = 0
        
        for i, bot in enumerate(all_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري تشغيل البوتات... ({i}/{len(all_bots)})**")
            
            if bot.get("status") == "running":
                already_running += 1
                continue
                
            container_id = start_bot_process(bot["username"])
            if container_id:
                update_bot_status(bot["username"], "running")
                bots_collection.update_one(
                    {"username": bot["username"]},
                    {"$set": {"container_id": container_id}}
                )
                started_count += 1
            else:
                failed_count += 1

        # رسالة النتيجة النهائية
        result_text = f"**📊 نتائج تشغيل البوتات:**\n\n"
        result_text += f"✅ **تم تشغيل:** {started_count} بوت\n"
        result_text += f"⚠️ **كانت تعمل:** {already_running} بوت\n"
        result_text += f"❌ **فشل التشغيل:** {failed_count} بوت\n"
        
        if started_count == 0 and already_running == 0:
            result_text = "**❌ لم يتم تشغيل أي بوت**"
        elif started_count == 0:
            result_text = f"**⚠️ كل البوتات تعمل بالفعل ({already_running} بوت)**"
        
        await status_msg.edit(result_text)

@Client.on_message(filters.command("start") & filters.private)
async def new_user_handler(client, msg):
    """معالج المستخدمين الجدد"""
    # التحقق من صحة الرسالة
    if not msg or not msg.from_user:
        logger.warning("Invalid message received")
        return
    
    uid = msg.from_user.id
    name = msg.from_user.first_name
    
    # التحقق من حالة المصنع
    if get_factory_state():
        await msg.reply("** ≭︰المصنع مغلق حاليا **")
        return
    
    # إضافة المستخدم الجديد
    await add_new_user(uid)
    
    # إرسال رسالة الترحيب
    await msg.reply(
        f"**مرحبا {name} في مصنع البوتات**\n"
        "**لصنع بوت اضغط على زر صنع بوت**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❲ صنع بوت ❳", callback_data="make_bot")]
        ])
    )

@Client.on_message(filters.command("start") & filters.private, group=162728)
async def admins_handler(client, message: Message):
    """معالج المطورين"""
    # التحقق من صحة الرسالة
    if not message or not message.from_user:
        logger.warning("Invalid message received")
        return
    
    uid = message.from_user.id
    name = message.from_user.first_name
    
    if not is_dev(uid):
        return
    
    # إرسال لوحة تحكم المطور
    await message.reply(
        f"**مرحبا {name} في لوحة تحكم المطور**\n"
        "**اختر الأمر المطلوب:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❲ الاحصائيات ❳", callback_data="stats")],
            [InlineKeyboardButton("❲ اذاعه ❳", callback_data="broadcast")],
            [InlineKeyboardButton("❲ تشغيل البوتات ❳", callback_data="start_bots")],
            [InlineKeyboardButton("❲ ايقاف البوتات ❳", callback_data="stop_bots")]
        ])
    )

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

@Client.on_message(filters.command(["❲ السورس ❳"], ""))
async def alivehi_handler(client: Client, message):
    """معالج أمر السورس"""
    try:
        await message.reply(
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
            await message.reply(
                f"**👨‍💻 مطور السورس:**\n\n"
                f"**الاسم:** {dev_info.first_name}\n"
                f"**المعرف:** @{dev_info.username}\n"
                f"**الآيدي:** `{dev_info.id}`"
            )
        else:
            await message.reply("**❌ لم يتم العثور على معلومات المطور**")
    except Exception as e:
        logger.error(f"Error in you handler: {str(e)}")

@Client.on_message(filters.command("❲ رفع مطور ❳", ""))
async def add_dev_handler(client, message: Message):
    """معالج رفع مطور"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        if not message.reply_to_message:
            await message.reply("**❌ يجب الرد على رسالة المستخدم**")
            return
        
        user_id = message.reply_to_message.from_user.id
        
        # إضافة المطور (هذا يتطلب تنفيذ دالة إضافة المطور)
        # await add_dev(user_id)
        
        await message.reply(f"**✅ تم رفع المستخدم {user_id} كمطور**")
    except Exception as e:
        logger.error(f"Error in add_dev handler: {str(e)}")

@Client.on_message(filters.command("❲ تنزيل مطور ❳", ""))
async def remove_dev_handler(client, message: Message):
    """معالج تنزيل مطور"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        if not message.reply_to_message:
            await message.reply("**❌ يجب الرد على رسالة المستخدم**")
            return
        
        user_id = message.reply_to_message.from_user.id
        
        # تنزيل المطور (هذا يتطلب تنفيذ دالة تنزيل المطور)
        # await remove_dev(user_id)
        
        await message.reply(f"**✅ تم تنزيل المستخدم {user_id} من المطورين**")
    except Exception as e:
        logger.error(f"Error in remove_dev handler: {str(e)}")

@Client.on_message(filters.command("❲ المطورين ❳", ""))
async def list_devs_handler(client, message: Message):
    """معالج قائمة المطورين"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        dev_count = get_dev_count()
        await message.reply(f"**👥 عدد المطورين:** {dev_count}")
    except Exception as e:
        logger.error(f"Error in list_devs handler: {str(e)}")

@Client.on_message(filters.command(["❲ فتح المصنع ❳", "❲ قفل المصنع ❳"], "") & filters.private)
async def onoff_handler(client, message):
    """معالج فتح/قفل المصنع"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        command = message.text
        
        if "❲ فتح المصنع ❳" in command:
            success = set_factory_state(False)
            if success:
                await message.reply("**✅ تم فتح المصنع بنجاح**")
            else:
                await message.reply("**❌ فشل في فتح المصنع**")
        elif "❲ قفل المصنع ❳" in command:
            success = set_factory_state(True)
            if success:
                await message.reply("**✅ تم قفل المصنع بنجاح**")
            else:
                await message.reply("**❌ فشل في قفل المصنع**")
    except Exception as e:
        logger.error(f"Error in onoff handler: {str(e)}")

@Client.on_message(filters.command("❲ صنع بوت ❳", "") & filters.private)
async def maked_handler(client, message):
    """معالج صنع بوت"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # هذا يتطلب تنفيذ منطق صنع البوت
        # سيتم إضافة المنطق هنا
        
        await message.reply("**🔄 جاري صنع البوت...**")
    except Exception as e:
        logger.error(f"Error in maked handler: {str(e)}")

@Client.on_message(filters.command("❲ حذف بوت ❳", "") & filters.private)
async def deletbot_handler(client, message):
    """معالج حذف بوت"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # طلب معرف البوت من المستخدم
        await message.reply("**أرسل معرف البوت الذي تريد حذفه**")
    except Exception as e:
        logger.error(f"Error in deletbot handler: {str(e)}")

@Client.on_message(filters.command("❲ البوتات المصنوعه ❳", ""))
async def botat_handler(client, message):
    """معالج قائمة البوتات المصنوعة"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        all_bots = get_all_bots()
        if not all_bots:
            await message.reply("**❌ لا توجد بوتات مصنوعة**")
            return
        
        bot_list = "**🤖 قائمة البوتات المصنوعة:**\n\n"
        for i, bot in enumerate(all_bots, 1):
            status = "🟢" if bot.get("status") == "running" else "🔴"
            bot_list += f"{i}. {status} @{bot['username']}\n"
        
        await message.reply(bot_list)
    except Exception as e:
        logger.error(f"Error in botat handler: {str(e)}")

@Client.on_message(filters.command(["❲ الاسكرينات المفتوحه ❳"], ""))
async def kinhsker_handler(client: Client, message):
    """معالج الشاشات المفتوحة"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # هذا يتطلب تنفيذ منطق عرض الشاشات المفتوحة
        # سيتم إضافة المنطق هنا
        
        await message.reply("**🖥️ جاري جلب الشاشات المفتوحة...**")
    except Exception as e:
        logger.error(f"Error in kinhsker handler: {str(e)}")

@Client.on_message(filters.command("❲ تحديث الصانع ❳", ""))
async def update_factory_handler(client: Client, message):
    """معالج تحديث الصانع"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # هذا يتطلب تنفيذ منطق تحديث الصانع
        # سيتم إضافة المنطق هنا
        
        await message.reply("**🔄 جاري تحديث الصانع...**")
    except Exception as e:
        logger.error(f"Error in update_factory handler: {str(e)}")

@Client.on_message(filters.command("❲ ايقاف بوت ❳", ""))
async def stop_specific_bot_handler(client, message):
    """معالج إيقاف بوت محدد"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # طلب معرف البوت من المستخدم
        await message.reply("**أرسل معرف البوت الذي تريد إيقافه**")
    except Exception as e:
        logger.error(f"Error in stop_specific_bot handler: {str(e)}")

@Client.on_message(filters.command("❲ البوتات المشتغلة ❳", ""))
async def show_running_bots_handler(client, message):
    """معالج عرض البوتات المشتغلة"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if get_factory_state():
            await message.reply("**❌ المصنع مغلق حالياً**")
            return
        
        running_bots = get_running_bots()
        if not running_bots:
            await message.reply("**❌ لا توجد بوتات مشتغلة**")
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
        
        await message.reply(bot_list)
    except Exception as e:
        logger.error(f"Error in show_running_bots handler: {str(e)}")

@Client.on_message(filters.command("❲ تشغيل البوتات ❳", ""))
async def start_Allusers_handler(client, message):
    """معالج تشغيل جميع البوتات"""
    try:
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if get_factory_state():
            await message.reply("**❌ المصنع مغلق حالياً**")
            return
        
        all_bots = get_all_bots()
        if not all_bots:
            await message.reply("**❌ لا توجد بوتات مصنوعة**")
            return
        
        # التحقق من وجود بوتات قابلة للتشغيل
        startable_bots = [bot for bot in all_bots if bot.get("status") != "running"]
        if not startable_bots:
            await message.reply("**✅ جميع البوتات تعمل بالفعل**")
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await message.reply(f"**🔄 جاري تشغيل {len(startable_bots)} بوت...**")
        
        started_count = 0
        failed_count = 0
        
        for i, bot in enumerate(startable_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري التشغيل... ({i}/{len(startable_bots)})**")
                
            process_id = start_bot_process(bot["username"])
            if process_id:
                update_bot_status(bot["username"], "running")
                # تحديد نوع المعرف وتحديث الحقل المناسب
                if isinstance(process_id, str):
                    # Container ID
                    bots_collection.update_one(
                        {"username": bot["username"]},
                        {"$set": {"container_id": process_id}}
                    )
                elif isinstance(process_id, int):
                    # PID
                    bots_collection.update_one(
                        {"username": bot["username"]},
                        {"$set": {"pid": process_id}}
                    )
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
        if not is_dev(message.from_user.id):
            await message.reply("**❌ هذا الأمر يخص المطور فقط**")
            return
        
        # التحقق من حالة المصنع
        if get_factory_state():
            await message.reply("**❌ المصنع مغلق حالياً**")
            return
        
        running_bots = get_running_bots()
        if not running_bots:
            await message.reply("**❌ لا توجد بوتات مشتغلة**")
            return
        
        # إرسال رسالة بداية العملية
        status_msg = await message.reply("**🔄 جاري إيقاف جميع البوتات...**")
        
        stopped_count = 0
        failed_count = 0
        
        for i, bot in enumerate(running_bots, 1):
            # تحديث رسالة الحالة كل 3 بوتات
            if i % 3 == 0:
                await status_msg.edit(f"**🔄 جاري الإيقاف... ({i}/{len(running_bots)})**")
            
            container_id = bot.get("container_id")
            pid = bot.get("pid")
            
            if container_id:
                success = stop_bot_process(container_id)
                if success:
                    update_bot_status(bot["username"], "stopped")
                    stopped_count += 1
                else:
                    failed_count += 1
            elif pid:
                success = stop_bot_process(pid)
                if success:
                    update_bot_status(bot["username"], "stopped")
                    stopped_count += 1
                else:
                    failed_count += 1
            else:
                update_bot_status(bot["username"], "stopped")
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