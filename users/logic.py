"""
User Management Logic - منطق إدارة المستخدمين
يحتوي على جميع الدوال المتعلقة بإدارة المستخدمين والمطورين
"""

import asyncio
from typing import List, Optional, Tuple
from utils import logger, cache_manager, rate_limit_manager
from utils.errors import ValidationError

# المتغيرات العامة
users = None
devs = None
OWNER_ID = None

def set_dependencies(owner_id, devs_coll, users_coll):
    """
    تعيين المتغيرات المطلوبة من الملف الرئيسي
    
    Args:
        owner_id: معرف المالك
        devs_coll: مجموعة المطورين
        users_coll: مجموعة المستخدمين
    """
    global users, devs, OWNER_ID
    
    # التحقق من صحة المدخلات
    if devs_coll is None:
        raise ValueError("devs_coll cannot be None")
    if users_coll is None:
        raise ValueError("users_coll cannot be None")
    if owner_id is None:
        raise ValueError("owner_id cannot be None")
    
    users = users_coll
    devs = devs_coll
    OWNER_ID = owner_id
    
    logger.info("Dependencies set successfully")
    logger.info(f"users collection: {users}")
    logger.info(f"devs collection: {devs}")
    logger.info(f"OWNER_ID: {OWNER_ID}")
    
    # فحص إضافي للتأكد من التهيئة
    if devs is None:
        logger.error("ERROR: devs is still None after set_dependencies")
    else:
        logger.info("SUCCESS: devs is properly initialized")
    
    if users is None:
        logger.error("ERROR: users is still None after set_dependencies")
    else:
        logger.info("SUCCESS: users is properly initialized")

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

async def is_dev(user_id, max_retries=3):
    """
    التحقق من كون المستخدم مطور مع التخزين المؤقت وإعادة المحاولة
    
    Args:
        user_id: معرف المستخدم المراد التحقق منه
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا كان المستخدم مطور، False خلاف ذلك
    """
    try:
        # فحص إضافي في بداية الدالة
        logger.info(f"is_dev called for user_id: {user_id}")
        logger.info(f"devs variable at start: {devs}")
        logger.info(f"users variable at start: {users}")
        logger.info(f"OWNER_ID variable at start: {OWNER_ID}")
        # التحقق من التخزين المؤقت أولاً
        cache_key = f"is_dev_{user_id}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        is_valid, validated_id = await validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        # التحقق من تهيئة المتغيرات
        if devs is None:
            logger.error("devs collection is not initialized")
            logger.error(f"devs variable: {devs}")
            logger.error(f"users variable: {users}")
            logger.error(f"OWNER_ID variable: {OWNER_ID}")
            logger.error("This should not happen - devs was initialized but became None")
            return False
            
        for attempt in range(max_retries):
            try:
                result = await devs.find_one({"user_id": validated_id})
                is_developer = result is not None
                cache_manager.set(cache_key, is_developer)
                return is_developer
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to check dev: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to check dev after {max_retries} attempts")
                    return False
                await asyncio.sleep(1)
        return False
    except ValidationError as e:
        logger.error(f"Validation error in is_dev: {str(e)}")
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
        
        is_valid, validated_id = await validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        # التحقق من تهيئة المتغيرات
        if users is None:
            logger.error("users collection is not initialized")
            return False
            
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
        is_valid, validated_id = await validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # التحقق من تهيئة المتغيرات
        if users is None:
            logger.error("users collection is not initialized")
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
        is_valid, validated_id = await validate_user_id(user_id)
        if not is_valid:
            logger.error(f"Invalid user_id: {user_id}")
            return False
        
        # التحقق من تهيئة المتغيرات
        if users is None:
            logger.error("users collection is not initialized")
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
        # التحقق من تهيئة المتغيرات
        if users is None:
            logger.error("users collection is not initialized")
            return []
            
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                cursor = users.find({}, {"user_id": 1})
                user_list = await cursor.to_list(length=None)
                user_ids = [user["user_id"] for user in user_list]
                logger.info(f"Successfully retrieved {len(user_ids)} users")
                return user_ids
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
    الحصول على عدد المستخدمين مع إعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        int: عدد المستخدمين
    """
    try:
        # التحقق من تهيئة المتغيرات
        if users is None:
            logger.error("users collection is not initialized")
            return 0
            
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        for attempt in range(max_retries):
            try:
                count = await users.count_documents({})
                logger.info(f"Successfully retrieved user count: {count}")
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
        user_id: معرف المستخدم المراد مسح تخزينه المؤقت (اختياري)
    """
    try:
        if user_id is not None:
            # مسح تخزين مؤقت لمستخدم محدد
            cache_manager.delete(f"user_exists_{user_id}")
            cache_manager.delete(f"is_dev_{user_id}")
            logger.info(f"Cleared cache for user {user_id}")
        else:
            # مسح جميع التخزين المؤقت للمستخدمين
            cache_manager.clear_pattern("user_exists_*")
            cache_manager.clear_pattern("is_dev_*")
            logger.info("Cleared all user cache")
    except Exception as e:
        logger.error(f"Error clearing user cache: {str(e)}")

async def get_dev_count():
    """
    الحصول على عدد المطورين
    
    Returns:
        int: عدد المطورين
    """
    try:
        if OWNER_ID:
            return len(OWNER_ID)
        return 0
    except Exception as e:
        logger.error(f"Error getting dev count: {str(e)}")
        return 0