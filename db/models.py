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

# دوال البث تم نقلها إلى broadcast/status.py

# دوال البوتات تم نقلها إلى bots/models.py

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