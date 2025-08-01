"""
Broadcast Status Management - إدارة حالة البث
يحتوي على دوال إدارة حالة البث للمستخدمين
"""

import asyncio
from typing import Optional, Tuple
from utils import logger, cache_manager, rate_limit_manager
from utils.errors import ValidationError

# المتغيرات العامة
broadcasts_collection = None

def set_collections(broadcasts_coll):
    """
    تعيين المجموعات المطلوبة من الملف الرئيسي
    
    Args:
        broadcasts_coll: مجموعة البث
    """
    global broadcasts_collection
    broadcasts_collection = broadcasts_coll

async def validate_user_id(user_id) -> Tuple[bool, Optional[int]]:
    """
    التحقق من صحة معرف المستخدم
    
    Args:
        user_id: معرف المستخدم المراد التحقق منه
        
    Returns:
        Tuple[bool, Optional[int]]: (صحة المعرف، المعرف المحقق)
    """
    try:
        if user_id is None:
            return False, None
        
        # تحويل إلى int إذا كان string
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return False, None
        
        # التحقق من أن المعرف موجب
        if not isinstance(user_id, int) or user_id <= 0:
            return False, None
        
        return True, user_id
    except Exception as e:
        logger.error(f"Error validating user_id {user_id}: {str(e)}")
        return False, None

async def set_broadcast_status(user_id, bot_id, key, max_retries=3):
    """
    تعيين حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم
        bot_id: معرف البوت
        key: المفتاح المراد تعيينه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم التعيين بنجاح، False خلاف ذلك
    """
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = await validate_user_id(user_id)
        is_valid_bot, validated_bot_id = await validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not key or not isinstance(key, str):
            logger.error(f"Invalid key: {key}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                # استخدام upsert للتأكد من إنشاء المستند إذا لم يكن موجوداً
                broadcasts_collection.update_one(
                    {"user_id": validated_user_id, "bot_id": validated_bot_id},
                    {"$set": {key: True}},
                    upsert=True
                )
                logger.info(f"Successfully set broadcast status for user {validated_user_id}, bot {validated_bot_id}, key {key}")
                
                # تحديث التخزين المؤقت
                cache_key = f"broadcast_status_{validated_user_id}_{validated_bot_id}_{key}"
                cache_manager.set(cache_key, True)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to set broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to set broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in set_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in set_broadcast_status function: {str(e)}")
        return False

async def get_broadcast_status(user_id, bot_id, key, max_retries=3):
    """
    الحصول على حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم
        bot_id: معرف البوت
        key: المفتاح المراد الحصول عليه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: حالة البث أو False إذا لم تكن موجودة
    """
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = await validate_user_id(user_id)
        is_valid_bot, validated_bot_id = await validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not key or not isinstance(key, str):
            logger.error(f"Invalid key: {key}")
            return False
        
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"broadcast_status_{validated_user_id}_{validated_bot_id}_{key}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                doc = broadcasts_collection.find_one({"user_id": validated_user_id, "bot_id": validated_bot_id})
                result = doc and doc.get(key)
                cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in get_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in get_broadcast_status function: {str(e)}")
        return False

async def delete_broadcast_status(user_id, bot_id, *keys, max_retries=3):
    """
    حذف حالة البث مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم
        bot_id: معرف البوت
        keys: المفاتيح المراد حذفها
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحذف بنجاح، False خلاف ذلك
    """
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = await validate_user_id(user_id)
        is_valid_bot, validated_bot_id = await validate_user_id(bot_id)
        
        if not is_valid_user or not is_valid_bot:
            logger.error(f"Invalid user_id or bot_id: {user_id}, {bot_id}")
            return False
        
        if not keys:
            logger.error("No keys provided for deletion")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                unset_dict = {key: "" for key in keys if key and isinstance(key, str)}
                if not unset_dict:
                    logger.error("No valid keys provided for deletion")
                    return False
                
                broadcasts_collection.update_one(
                    {"user_id": validated_user_id, "bot_id": validated_bot_id},
                    {"$unset": unset_dict}
                )
                logger.info(f"Successfully deleted broadcast status for user {validated_user_id}, bot {validated_bot_id}, keys {keys}")
                
                # حذف من التخزين المؤقت
                for key in keys:
                    if key and isinstance(key, str):
                        cache_key = f"broadcast_status_{validated_user_id}_{validated_bot_id}_{key}"
                        cache_manager.delete(cache_key)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to delete broadcast status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to delete broadcast status after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in delete_broadcast_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in delete_broadcast_status function: {str(e)}")
        return False