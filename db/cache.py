"""
Cache Functions - دوال التخزين المؤقت
يحتوي على دوال التخزين المؤقت للاستعلامات المتكررة
"""

import time
from collections import OrderedDict
from typing import Optional, Any, Dict
from utils import logger, CacheError, cache_manager

class CacheManager:
    """
    مدير التخزين المؤقت للاستعلامات المتكررة
    يستخدم خوارزمية LRU (Least Recently Used) مع TTL (Time To Live)
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        """
        تهيئة مدير التخزين المؤقت
        
        Args:
            max_size: الحد الأقصى لعدد العناصر في التخزين المؤقت
            ttl: مدة صلاحية البيانات بالثواني (Time To Live)
        """
        self.max_size = max_size
        self.ttl = ttl  # Time To Live بالثواني
        self.cache = OrderedDict()
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        الحصول على قيمة من التخزين المؤقت
        
        Args:
            key: المفتاح المطلوب
            
        Returns:
            القيمة المخزنة أو None إذا لم تكن موجودة أو منتهية الصلاحية
        """
        try:
            if key in self.cache:
                # التحقق من انتهاء صلاحية البيانات
                if time.time() - self.timestamps[key] > self.ttl:
                    self.delete(key)
                    return None
                
                # نقل العنصر إلى النهاية (LRU)
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        حفظ قيمة في التخزين المؤقت
        
        Args:
            key: المفتاح
            value: القيمة المراد حفظها
            
        Returns:
            bool: True إذا تم الحفظ بنجاح، False خلاف ذلك
        """
        try:
            # التحقق من حجم التخزين المؤقت
            if len(self.cache) >= self.max_size:
                # حذف العنصر الأقل استخداماً
                oldest_key = next(iter(self.cache))
                self.delete(oldest_key)
            
            # حفظ القيمة الجديدة
            self.cache[key] = value
            self.timestamps[key] = time.time()
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        حذف قيمة من التخزين المؤقت
        
        Args:
            key: المفتاح المراد حذفه
            
        Returns:
            bool: True إذا تم الحذف بنجاح، False خلاف ذلك
        """
        try:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def clear(self) -> int:
        """
        مسح جميع البيانات من التخزين المؤقت
        
        Returns:
            int: عدد العناصر التي تم حذفها
        """
        try:
            count = len(self.cache)
            self.cache.clear()
            self.timestamps.clear()
            logger.info(f"Cache cleared, removed {count} items")
            return count
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0
    
    def size(self) -> int:
        """
        الحصول على حجم التخزين المؤقت
        
        Returns:
            int: عدد العناصر في التخزين المؤقت
        """
        return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """
        تنظيف العناصر منتهية الصلاحية
        
        Returns:
            int: عدد العناصر التي تم حذفها
        """
        try:
            current_time = time.time()
            expired_keys = [
                key for key, timestamp in self.timestamps.items()
                if current_time - timestamp > self.ttl
            ]
            
            for key in expired_keys:
                self.delete(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
            
            return len(expired_keys)
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات التخزين المؤقت
        
        Returns:
            dict: إحصائيات التخزين المؤقت
        """
        try:
            current_time = time.time()
            expired_count = sum(
                1 for timestamp in self.timestamps.values()
                if current_time - timestamp > self.ttl
            )
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "expired_items": expired_count,
                "utilization": (len(self.cache) / self.max_size) * 100 if self.max_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"Cache stats error: {str(e)}")
            return {
                "size": 0,
                "max_size": self.max_size,
                "ttl": self.ttl,
                "expired_items": 0,
                "utilization": 0,
                "error": str(e)
            }

# إنشاء مدير التخزين المؤقت العام
cache_manager = CacheManager(max_size=200, ttl=600)

# دوال مساعدة للوصول السريع
def get_cache(key: str) -> Optional[Any]:
    """
    الحصول على قيمة من التخزين المؤقت
    
    Args:
        key: المفتاح المطلوب
        
    Returns:
        القيمة المخزنة أو None
    """
    return cache_manager.get(key)

def set_cache(key: str, value: Any, ttl: int = None) -> bool:
    """
    حفظ قيمة في التخزين المؤقت
    
    Args:
        key: المفتاح
        value: القيمة المراد حفظها
        ttl: مدة الصلاحية المخصصة (اختياري)
        
    Returns:
        bool: True إذا تم الحفظ بنجاح
    """
    if ttl:
        # إنشاء مدير مؤقت مخصص لهذا العنصر
        temp_manager = CacheManager(max_size=1, ttl=ttl)
        return temp_manager.set(key, value)
    else:
        return cache_manager.set(key, value)

def delete_cache(key: str) -> bool:
    """
    حذف قيمة من التخزين المؤقت
    
    Args:
        key: المفتاح المراد حذفه
        
    Returns:
        bool: True إذا تم الحذف بنجاح
    """
    return cache_manager.delete(key)

def clear_cache() -> int:
    """
    مسح جميع البيانات من التخزين المؤقت
    
    Returns:
        int: عدد العناصر التي تم حذفها
    """
    return cache_manager.clear()

def get_cache_size() -> int:
    """
    الحصول على حجم التخزين المؤقت
    
    Returns:
        int: عدد العناصر في التخزين المؤقت
    """
    return cache_manager.size()

def cleanup_expired_cache() -> int:
    """
    تنظيف العناصر منتهية الصلاحية
    
    Returns:
        int: عدد العناصر التي تم حذفها
    """
    return cache_manager.cleanup_expired()

def get_cache_stats() -> Dict[str, Any]:
    """
    الحصول على إحصائيات التخزين المؤقت
    
    Returns:
        dict: إحصائيات التخزين المؤقت
    """
    return cache_manager.get_stats()

# دوال خاصة بقاعدة البيانات
def cache_database_query(query_key: str, query_func, ttl: int = 300):
    """
    تخزين مؤقت لاستعلام قاعدة البيانات
    
    Args:
        query_key: مفتاح الاستعلام
        query_func: دالة الاستعلام
        ttl: مدة الصلاحية بالثواني
        
    Returns:
        نتيجة الاستعلام (من التخزين المؤقت أو قاعدة البيانات)
    """
    try:
        # التحقق من التخزين المؤقت أولاً
        cached_result = get_cache(query_key)
        if cached_result is not None:
            logger.debug(f"Retrieved {query_key} from cache")
            return cached_result
        
        # تنفيذ الاستعلام
        result = query_func()
        
        # حفظ النتيجة في التخزين المؤقت
        if result is not None:
            set_cache(query_key, result, ttl)
            logger.debug(f"Cached {query_key}")
        
        return result
        
    except Exception as e:
        logger.error(f"Cache database query error for {query_key}: {str(e)}")
        # في حالة الخطأ، تنفيذ الاستعلام مباشرة
        return query_func()

def invalidate_cache_pattern(pattern: str) -> int:
    """
    حذف جميع العناصر التي تطابق نمط معين
    
    Args:
        pattern: النمط المطلوب (يمكن استخدام * كبديل)
        
    Returns:
        int: عدد العناصر التي تم حذفها
    """
    try:
        import fnmatch
        deleted_count = 0
        
        # الحصول على جميع المفاتيح
        keys = list(cache_manager.cache.keys())
        
        for key in keys:
            if fnmatch.fnmatch(key, pattern):
                if cache_manager.delete(key):
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} cache items matching pattern: {pattern}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Cache invalidation error: {str(e)}")
        return 0