"""
Factory Settings Functions - دوال إعدادات المصنع
يحتوي على دوال إدارة إعدادات المصنع في قاعدة البيانات
"""

import time
from utils import (
    logger, 
    ValidationError, 
    DatabaseError,
    cache_manager
)

# استيراد المتغيرات المطلوبة من الملف الرئيسي
# سيتم استيرادها عند تشغيل التطبيق
factory_settings = None

def set_collections(factory_coll):
    """
    تعيين المجموعات المطلوبة من الملف الرئيسي
    
    Args:
        factory_coll: مجموعة إعدادات المصنع
    """
    global factory_settings
    factory_settings = factory_coll

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