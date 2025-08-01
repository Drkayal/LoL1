"""
Bot Model Functions - دوال قاعدة البيانات للبوتات
يحتوي على دوال التعامل مع قاعدة البيانات للبوتات
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
    validate_bot_username
)

# استيراد المتغيرات المطلوبة من الملف الرئيسي
# سيتم استيرادها عند تشغيل التطبيق
bots_collection = None
factory_settings = None

def set_collections(bots_coll, factory_coll):
    """
    تعيين المجموعات المطلوبة من الملف الرئيسي
    
    Args:
        bots_coll: مجموعة البوتات
        factory_coll: مجموعة إعدادات المصنع
    """
    global bots_collection, factory_settings
    bots_collection = bots_coll
    factory_settings = factory_coll

async def get_bot_info(bot_username, max_retries=3):
    """
    الحصول على معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        dict: معلومات البوت أو None إذا لم تكن موجودة
    """
    try:
        from utils import cache_manager
        
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"bot_info_{bot_username}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        is_valid, validated_username = await validate_bot_username(bot_username)
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
                await asyncio.sleep(1)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in get_bot_info: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in get_bot_info function: {str(e)}")
        return None

async def save_bot_info(bot_username, dev_id, container_id, config_data, max_retries=3):
    """
    حفظ معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        dev_id: معرف المطور
        container_id: معرف الحاوية
        config_data: بيانات التكوين
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحفظ بنجاح، False خلاف ذلك
    """
    try:
        from utils import cache_manager
        
        is_valid_username, validated_username = await validate_bot_username(bot_username)
        is_valid_dev, validated_dev_id = await validate_user_id(dev_id)
        
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
                    "container_id": container_id,
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
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in save_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in save_bot_info function: {str(e)}")
        return False

async def update_bot_status(bot_username, status, max_retries=3):
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
        from utils import cache_manager
        
        is_valid, validated_username = await validate_bot_username(bot_username)
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
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in update_bot_status: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in update_bot_status function: {str(e)}")
        return False

async def delete_bot_info(bot_username, max_retries=3):
    """
    حذف معلومات البوت مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحذف بنجاح، False خلاف ذلك
    """
    try:
        from utils import cache_manager
        
        is_valid, validated_username = await validate_bot_username(bot_username)
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
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in delete_bot_info: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in delete_bot_info function: {str(e)}")
        return False

async def get_all_bots(max_retries=3):
    """
    الحصول على جميع البوتات مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        List[dict]: قائمة جميع البوتات
    """
    try:
        from utils import cache_manager
        
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
                await asyncio.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_all_bots function: {str(e)}")
        return []

async def get_running_bots(max_retries=3):
    """
    الحصول على البوتات المشتغلة مع التحقق من وجود الحاويات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        List[dict]: قائمة البوتات المشتغلة
    """
    try:
        from utils import cache_manager
        import subprocess
        
        # التحقق من التخزين المؤقت أولاً
        cache_key = "running_bots_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved running bots from cache")
            return cached_result
        
        for attempt in range(max_retries):
            try:
                bots = list(bots_collection.find({"status": "running"}))
                logger.info(f"Retrieved {len(bots)} bots with running status")
                
                # التحقق من وجود الحاويات أو العمليات فعلياً
                verified_running_bots = []
                bots_to_update = []
                
                for bot in bots:
                    container_id = bot.get("container_id")
                    pid = bot.get("pid")
                    
                    if container_id:
                        # التحقق من حاوية Docker
                        try:
                            result = subprocess.run(
                                ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                                capture_output=True,
                                text=True
                            )
                            if "Up" in result.stdout:
                                verified_running_bots.append(bot)
                            else:
                                # الحاوية غير موجودة أو متوقفة، تحديث الحالة
                                logger.warning(f"Container {container_id} for bot {bot.get('username')} is not running")
                                bots_to_update.append(bot.get("username"))
                        except Exception as e:
                            logger.warning(f"Failed to check container {container_id}: {str(e)}")
                            # في حالة فشل التحقق، نفترض أن البوت متوقف
                            bots_to_update.append(bot.get("username"))
                    elif pid:
                        # التحقق من العملية المباشرة
                        try:
                            import psutil
                            process = psutil.Process(pid)
                            if process.is_running():
                                verified_running_bots.append(bot)
                            else:
                                # العملية غير موجودة، تحديث الحالة
                                logger.warning(f"Process {pid} for bot {bot.get('username')} is not running")
                                bots_to_update.append(bot.get("username"))
                        except psutil.NoSuchProcess:
                            logger.warning(f"Process {pid} for bot {bot.get('username')} not found")
                            bots_to_update.append(bot.get("username"))
                        except Exception as e:
                            logger.warning(f"Failed to check process {pid}: {str(e)}")
                            bots_to_update.append(bot.get("username"))
                    else:
                        # لا يوجد معرف حاوية أو عملية، تحديث الحالة
                        logger.warning(f"Bot {bot.get('username')} has no container_id or pid")
                        bots_to_update.append(bot.get("username"))
                
                # تحديث حالة البوتات المتوقفة
                for bot_username in bots_to_update:
                    try:
                        update_bot_status(bot_username, "stopped")
                    except Exception as e:
                        logger.error(f"Failed to update status for bot {bot_username}: {str(e)}")
                
                logger.info(f"Successfully verified {len(verified_running_bots)} running bots")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, verified_running_bots)
                return verified_running_bots
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get running bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get running bots after {max_retries} attempts")
                    return []
                await asyncio.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_running_bots function: {str(e)}")
        return []

async def get_bots_count(max_retries=3):
    """
    الحصول على عدد البوتات مع إعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        int: عدد البوتات
    """
    try:
        for attempt in range(max_retries):
            try:
                count = bots_collection.count_documents({})
                logger.debug(f"Retrieved bots count: {count}")
                return count
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get bots count: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get bots count after {max_retries} attempts")
                    return 0
                await asyncio.sleep(1)
        return 0
    except Exception as e:
        logger.error(f"Error in get_bots_count function: {str(e)}")
        return 0

async def update_bot_container_id(bot_username, container_id, max_retries=3):
    """
    تحديث معرف الحاوية للبوت مع إعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        container_id: معرف الحاوية
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم التحديث بنجاح، False خلاف ذلك
    """
    try:
        is_valid, validated_username = await validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return False
        
        for attempt in range(max_retries):
            try:
                result = bots_collection.update_one(
                    {"username": validated_username},
                    {"$set": {"container_id": container_id}}
                )
                if result.modified_count > 0:
                    logger.info(f"Successfully updated container ID for bot {validated_username}")
                    return True
                else:
                    logger.warning(f"No document updated for bot {validated_username}")
                    return False
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to update container ID: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to update container ID after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in update_bot_container_id function: {str(e)}")
        return False

async def get_factory_state(max_retries=3):
    """
    الحصول على حالة المصنع مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: حالة المصنع (True = مغلق، False = مفتوح)
    """
    try:
        from utils import cache_manager
        
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
                await asyncio.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error in get_factory_state function: {str(e)}")
        return True