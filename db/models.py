"""
Database Models - دوال قاعدة البيانات
يحتوي على جميع دوال التعامل مع قاعدة البيانات
"""

import time
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from utils import (
    logger, 
    ValidationError, 
    DatabaseError,
    rate_limit_manager
)
from users import (
    validate_user_id,
    validate_bot_token,
    validate_session_string,
    validate_bot_username
)
from .cache import cache_manager
from .manager import db_manager

# استيراد المتغيرات المطلوبة من الملف الرئيسي
# سيتم استيرادها عند تشغيل التطبيق
broadcasts_collection = None
bots_collection = None
factory_settings = None

def set_collections(broadcasts_coll, bots_coll, factory_coll):
    """
    تعيين المجموعات المطلوبة من الملف الرئيسي
    
    Args:
        broadcasts_coll: مجموعة البث
        bots_coll: مجموعة البوتات
        factory_coll: مجموعة إعدادات المصنع
    """
    global broadcasts_collection, bots_collection, factory_settings
    broadcasts_collection = broadcasts_coll
    bots_collection = bots_coll
    factory_settings = factory_coll

# ================================================
# ============== BROADCAST FUNCTIONS =============
# ================================================

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
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
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
                broadcasts_collection.update_one(
                    {"user_id": validated_user_id, "bot_id": validated_bot_id},
                    {"$set": {key: True}},
                    upsert=True
                )
                logger.info(f"Successfully set broadcast status for user {validated_user_id}, bot {validated_bot_id}, key {key}")
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
        key: المفتاح المطلوب
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: حالة البث أو False إذا لم تكن موجودة
    """
    try:
        # التحقق من المدخلات
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
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
        is_valid_user, validated_user_id = validate_user_id(user_id)
        is_valid_bot, validated_bot_id = validate_user_id(bot_id)
        
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

# ================================================
# ============== BOT FUNCTIONS ===================
# ================================================

def get_bot_info(bot_username, max_retries=3):
    """
    الحصول على معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        dict: معلومات البوت أو None إذا لم تكن موجودة
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"bot_info_{bot_username}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return None
        
        for attempt in range(max_retries):
            try:
                result = bots_collection.find_one({"username": validated_username})
                if result:
                    cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get bot info after {max_retries} attempts")
                    return None
                time.sleep(1)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in get_bot_info: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in get_bot_info function: {str(e)}")
        return None

def save_bot_info(bot_username, dev_id, pid, config_data, max_retries=3):
    """
    حفظ معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        dev_id: معرف المطور
        pid: معرف العملية
        config_data: بيانات التكوين
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحفظ بنجاح، False خلاف ذلك
    """
    try:
        is_valid_username, validated_username = validate_bot_username(bot_username)
        is_valid_dev, validated_dev_id = validate_user_id(dev_id)
        
        if not is_valid_username or not is_valid_dev:
            logger.error(f"Invalid bot_username or dev_id: {bot_username}, {dev_id}")
            return False
        
        if not isinstance(config_data, dict):
            logger.error("Config data must be a dictionary")
            return False
        
        for attempt in range(max_retries):
            try:
                bot_data = {
                    "username": validated_username,
                    "dev_id": validated_dev_id,
                    "pid": pid,
                    "config": config_data,
                    "created_at": datetime.now(),
                    "status": "running"
                }
                
                bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": bot_data},
                    upsert=True
                )
                logger.info(f"Successfully saved bot info for {validated_username}")
                
                # تحديث التخزين المؤقت
                cache_key = f"bot_info_{validated_username}"
                cache_manager.set(cache_key, bot_data)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to save bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to save bot info after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in save_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in save_bot_info function: {str(e)}")
        return False

def update_bot_status(bot_username, status, max_retries=3):
    """
    تحديث حالة البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        status: الحالة الجديدة
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم التحديث بنجاح، False خلاف ذلك
    """
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return False
        
        if not status or not isinstance(status, str):
            logger.error(f"Invalid status: {status}")
            return False
        
        valid_statuses = ["running", "stopped", "error"]
        if status not in valid_statuses:
            logger.error(f"Invalid status value: {status}. Must be one of {valid_statuses}")
            return False
        
        for attempt in range(max_retries):
            try:
                bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": {"status": status}}
                )
                logger.info(f"Successfully updated bot status for {validated_username} to {status}")
                
                # حذف من التخزين المؤقت لتحديث البيانات
                cache_key = f"bot_info_{validated_username}"
                cache_manager.delete(cache_key)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to update bot status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to update bot status after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in update_bot_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in update_bot_status function: {str(e)}")
        return False

def delete_bot_info(bot_username, max_retries=3):
    """
    حذف معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحذف بنجاح، False خلاف ذلك
    """
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return False
        
        for attempt in range(max_retries):
            try:
                result = bots_collection.delete_one({"username": validated_username})
                if result.deleted_count > 0:
                    logger.info(f"Successfully deleted bot info for {validated_username}")
                    
                    # حذف من التخزين المؤقت
                    cache_key = f"bot_info_{validated_username}"
                    cache_manager.delete(cache_key)
                    
                    return True
                else:
                    logger.warning(f"Bot {validated_username} not found for deletion")
                    return False
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to delete bot info: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to delete bot info after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in delete_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in delete_bot_info function: {str(e)}")
        return False

def get_all_bots(max_retries=3):
    """
    الحصول على جميع البوتات مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        List[dict]: قائمة جميع البوتات
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "all_bots_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved bots from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                bots = list(bots_collection.find())
                logger.info(f"Successfully retrieved {len(bots)} bots")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, bots)
                return bots
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get all bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get all bots after {max_retries} attempts")
                    return []
                time.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_all_bots function: {str(e)}")
        return []

def get_running_bots(max_retries=3):
    """
    الحصول على البوتات المشتغلة مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        List[dict]: قائمة البوتات المشتغلة
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "running_bots_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved running bots from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                bots = list(bots_collection.find({"status": "running"}))
                logger.info(f"Successfully retrieved {len(bots)} running bots")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, bots)
                return bots
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get running bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get running bots after {max_retries} attempts")
                    return []
                time.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_running_bots function: {str(e)}")
        return []

# ================================================
# ============== FACTORY FUNCTIONS ===============
# ================================================

def get_factory_state(max_retries=3):
    """
    الحصول على حالة المصنع مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: حالة المصنع (True = مغلق، False = مفتوح)
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "factory_state"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved factory state from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                settings = factory_settings.find_one({"name": "factory"})
                enabled = settings.get("enabled", True) if settings else True
                logger.info(f"Factory state retrieved: {enabled}")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, enabled)
                return enabled
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get factory state after {max_retries} attempts")
                    return True  # القيمة الافتراضية
                time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error in get_factory_state function: {str(e)}")
        return True

def set_factory_state(enabled, max_retries=3):
    """
    تعيين حالة المصنع مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        enabled: حالة المصنع (True = مغلق، False = مفتوح)
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم التعيين بنجاح، False خلاف ذلك
    """
    try:
        if not isinstance(enabled, bool):
            logger.error(f"Invalid enabled value: {enabled}. Must be boolean")
            return False
        
        for attempt in range(max_retries):
            try:
                factory_settings.update_one(
                    {"name": "factory"},
                    {"$set": {"enabled": enabled}},
                    upsert=True
                )
                logger.info(f"Successfully set factory state to: {enabled}")
                
                # تحديث التخزين المؤقت
                cache_key = "factory_state"
                cache_manager.set(cache_key, enabled)
                
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to set factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to set factory state after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in set_factory_state function: {str(e)}")
        return False

# ================================================
# ============== UTILITY FUNCTIONS ===============
# ================================================

def clear_bot_cache(bot_username: str = None):
    """
    مسح التخزين المؤقت للبوتات
    
    Args:
        bot_username: معرف البوت المحدد (اختياري). إذا لم يتم تحديده، سيتم مسح جميع التخزين المؤقت
    """
    try:
        if bot_username:
            # مسح التخزين المؤقت لبوت محدد
            cache_manager.delete(f"bot_info_{bot_username}")
            logger.debug(f"Cleared cache for bot {bot_username}")
        else:
            # مسح جميع التخزين المؤقت المتعلق بالبوتات
            cache_manager.delete("all_bots_list")
            cache_manager.delete("running_bots_list")
            logger.debug("Cleared all bot-related cache")
    except Exception as e:
        logger.error(f"Error clearing bot cache: {str(e)}")

def clear_factory_cache():
    """مسح التخزين المؤقت للمصنع"""
    try:
        cache_manager.delete("factory_state")
        logger.debug("Cleared factory cache")
    except Exception as e:
        logger.error(f"Error clearing factory cache: {str(e)}")

def get_database_stats() -> Dict[str, Any]:
    """
    الحصول على إحصائيات قاعدة البيانات
    
    Returns:
        dict: إحصائيات قاعدة البيانات
    """
    try:
        stats = {
            "bots_count": 0,
            "running_bots_count": 0,
            "broadcasts_count": 0,
            "factory_state": None
        }
        
        # عدد البوتات
        try:
            stats["bots_count"] = bots_collection.count_documents({})
        except:
            pass
        
        # عدد البوتات المشتغلة
        try:
            stats["running_bots_count"] = bots_collection.count_documents({"status": "running"})
        except:
            pass
        
        # عدد عمليات البث
        try:
            stats["broadcasts_count"] = broadcasts_collection.count_documents({})
        except:
            pass
        
        # حالة المصنع
        try:
            stats["factory_state"] = get_factory_state()
        except:
            pass
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {
            "bots_count": 0,
            "running_bots_count": 0,
            "broadcasts_count": 0,
            "factory_state": None,
            "error": str(e)
        }