"""
Async Helpers - مساعدات غير متزامنة
يحتوي على wrappers للـ Pyrogram functions لتجنب مشاكل asyncio loop
"""

import asyncio
from pyrogram.types import Message
from utils import logger

async def safe_reply_text(message: Message, text: str, **kwargs):
    """
    إرسال رسالة رد بشكل آمن مع معالجة الأخطاء
    
    Args:
        message: الرسالة المراد الرد عليها
        text: النص المراد إرساله
        **kwargs: معاملات إضافية
        
    Returns:
        Message أو None في حالة الخطأ
    """
    try:
        return await message.reply_text(text, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_reply_text: {str(e)}")
        return None

async def safe_edit_text(message: Message, text: str, **kwargs):
    """
    تعديل رسالة بشكل آمن مع معالجة الأخطاء
    
    Args:
        message: الرسالة المراد تعديلها
        text: النص الجديد
        **kwargs: معاملات إضافية
        
    Returns:
        Message أو None في حالة الخطأ
    """
    try:
        return await message.edit_text(text, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_edit_text: {str(e)}")
        return None

async def safe_send_message(client, chat_id, text: str, **kwargs):
    """
    إرسال رسالة بشكل آمن مع معالجة الأخطاء
    
    Args:
        client: عميل Pyrogram
        chat_id: معرف المحادثة
        text: النص المراد إرساله
        **kwargs: معاملات إضافية
        
    Returns:
        Message أو None في حالة الخطأ
    """
    try:
        return await client.send_message(chat_id, text, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_send_message: {str(e)}")
        return None

async def safe_answer_callback(callback_query, text: str = None, **kwargs):
    """
    الرد على callback query بشكل آمن مع معالجة الأخطاء
    
    Args:
        callback_query: استعلام الرد
        text: النص المراد إرساله
        **kwargs: معاملات إضافية
        
    Returns:
        bool: True إذا نجح، False خلاف ذلك
    """
    try:
        await callback_query.answer(text, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Error in safe_answer_callback: {str(e)}")
        return False

async def safe_edit_callback_message(callback_query, text: str, **kwargs):
    """
    تعديل رسالة callback query بشكل آمن مع معالجة الأخطاء
    
    Args:
        callback_query: استعلام الرد
        text: النص الجديد
        **kwargs: معاملات إضافية
        
    Returns:
        Message أو None في حالة الخطأ
    """
    try:
        return await callback_query.message.edit_text(text, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_edit_callback_message: {str(e)}")
        return None