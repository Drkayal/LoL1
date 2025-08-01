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

# دوال المصنع تم نقلها إلى factory/settings.py

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
            from factory import get_factory_state
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