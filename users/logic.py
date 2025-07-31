"""
User Logic Functions - دوال إدارة المستخدمين
يحتوي على جميع دوال إدارة المستخدمين في المشروع
"""

import time
import asyncio
from typing import List, Optional
from utils import ValidationError, logger, cache_manager, rate_limit_manager
from .validation import validate_user_id

# استيراد المتغيرات المطلوبة من الملف الرئيسي
# سيتم استيرادها عند تشغيل التطبيق
OWNER_ID = None
devs_collection = None
users = None

def set_dependencies(owner_id, devs_coll, users_coll):
    """
    تعيين التبعيات المطلوبة من الملف الرئيسي
    
    Args:
        owner_id: قائمة معرفات المالكين
        devs_coll: مجموعة المطورين في قاعدة البيانات
        users_coll: مجموعة المستخدمين في قاعدة البيانات
    """
    global OWNER_ID, devs_collection, users
    OWNER_ID = owner_id
    devs_collection = devs_coll
    users = users_coll

def is_dev(user_id, max_retries=3):
    """
    التحقق من صلاحيات المطور مع التخزين المؤقت وآلية إعادة المحاولة
    
    Args:
        user_id: معرف المستخدم المراد التحقق منه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا كان المستخدم مطور، False خلاف ذلك
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"dev_status_{user_id}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # التحقق من المالكين مباشرة
        if user_id in OWNER_ID:
            cache_manager.set(cache_key, True)
            return True
        
        # البحث في قاعدة البيانات
        for attempt in range(max_retries):
            try:
                result = devs_collection.find_one({"user_id": user_id})
                is_developer = result is not None
                cache_manager.set(cache_key, is_developer)
                return is_developer
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to check dev status: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to check dev status after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in is_dev function: {str(e)}")
        return False

async def is_user(user_id, max_retries=3):
    """
    التحقق من وجود المستخدم مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم المراد التحقق منه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا كان المستخدم موجود، False خلاف ذلك
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"user_exists_{user_id}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        is_valid, validated_id = validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                result = await users.find_one({"user_id": validated_id})
                exists = result is not None
                cache_manager.set(cache_key, exists)
                return exists
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to check user: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to check user after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in is_user: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in is_user function: {str(e)}")
        return False

async def add_new_user(user_id, max_retries=3):
    """
    إضافة مستخدم جديد مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم المراد إضافته
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تمت الإضافة بنجاح، False خلاف ذلك
    """
    try:
        is_valid, validated_id = validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                # التحقق من عدم وجود المستخدم مسبقاً
                existing_user = await users.find_one({"user_id": validated_id})
                if existing_user:
                    logger.info(f"User {validated_id} already exists")
                    # تحديث التخزين المؤقت
                    cache_manager.set(f"user_exists_{validated_id}", True)
                    return True
                
                await users.insert_one({"user_id": validated_id})
                logger.info(f"Successfully added user {validated_id}")
                
                # تحديث التخزين المؤقت
                cache_manager.set(f"user_exists_{validated_id}", True)
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to add user: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to add user after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in add_new_user: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in add_new_user function: {str(e)}")
        return False

async def del_user(user_id, max_retries=3):
    """
    حذف مستخدم مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم المراد حذفه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الحذف بنجاح، False خلاف ذلك
    """
    try:
        is_valid, validated_id = validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                result = await users.delete_one({"user_id": validated_id})
                if result.deleted_count > 0:
                    logger.info(f"Successfully deleted user {validated_id}")
                    # حذف من التخزين المؤقت
                    cache_manager.delete(f"user_exists_{validated_id}")
                    return True
                else:
                    logger.warning(f"User {validated_id} not found for deletion")
                    return False
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to delete user: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to delete user after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in del_user: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in del_user function: {str(e)}")
        return False

async def get_users(max_retries=3):
    """
    الحصول على قائمة المستخدمين مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        List[int]: قائمة معرفات المستخدمين
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "all_users_list"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.debug("Retrieved users from cache")
            return cached_result
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                user_list = [user["user_id"] async for user in users.find()]
                logger.info(f"Successfully retrieved {len(user_list)} users")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, user_list)
                return user_list
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get users: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get users after {max_retries} attempts")
                    return []
                await asyncio.sleep(1)
        return []
    except Exception as e:
        logger.error(f"Error in get_users function: {str(e)}")
        return []

async def get_user_count(max_retries=3):
    """
    الحصول على عدد المستخدمين مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        int: عدد المستخدمين
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cache_key = "user_count"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                count = await users.count_documents({})
                logger.info(f"Successfully retrieved user count: {count}")
                
                # حفظ في التخزين المؤقت
                cache_manager.set(cache_key, count)
                return count
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get user count: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get user count after {max_retries} attempts")
                    return 0
                await asyncio.sleep(1)
        return 0
    except Exception as e:
        logger.error(f"Error in get_user_count function: {str(e)}")
        return 0

def clear_user_cache(user_id: Optional[int] = None):
    """
    مسح التخزين المؤقت للمستخدمين
    
    Args:
        user_id: معرف المستخدم المحدد (اختياري). إذا لم يتم تحديده، سيتم مسح جميع التخزين المؤقت
    """
    try:
        if user_id is not None:
            # مسح التخزين المؤقت لمستخدم محدد
            cache_manager.delete(f"user_exists_{user_id}")
            cache_manager.delete(f"dev_status_{user_id}")
            logger.debug(f"Cleared cache for user {user_id}")
        else:
            # مسح جميع التخزين المؤقت المتعلق بالمستخدمين
            cache_manager.delete("all_users_list")
            cache_manager.delete("user_count")
            logger.debug("Cleared all user-related cache")
    except Exception as e:
        logger.error(f"Error clearing user cache: {str(e)}")

def get_dev_count():
    """
    الحصول على عدد المطورين
    
    Returns:
        int: عدد المطورين
    """
    try:
        # عدد المالكين + عدد المطورين في قاعدة البيانات
        owner_count = len(OWNER_ID)
        dev_count = devs_collection.count_documents({"user_id": {"$nin": OWNER_ID}})
        return owner_count + dev_count
    except Exception as e:
        logger.error(f"Error getting dev count: {str(e)}")
        return len(OWNER_ID)  # إرجاع عدد المالكين فقط في حالة الخطأ