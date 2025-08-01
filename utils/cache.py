"""
Cache Manager - مدير التخزين المؤقت
يحتوي على مدير التخزين المؤقت للاستعلامات المتكررة
"""

import time
from collections import OrderedDict
from typing import Optional, Any
from .logger import logger

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
        تعيين قيمة في التخزين المؤقت
        
        Args:
            key: المفتاح
            value: القيمة المراد تخزينها
            
        Returns:
            True إذا تم التخزين بنجاح، False في حالة الخطأ
        """
        try:
            # إزالة العنصر إذا كان موجوداً
            if key in self.cache:
                self.cache.pop(key)
            
            # التحقق من حجم التخزين المؤقت
            if len(self.cache) >= self.max_size:
                # إزالة أقدم عنصر
                oldest_key = next(iter(self.cache))
                self.cache.pop(oldest_key)
                if oldest_key in self.timestamps:
                    del self.timestamps[oldest_key]
            
            # إضافة العنصر الجديد
            self.cache[key] = value
            self.timestamps[key] = time.time()
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        حذف عنصر من التخزين المؤقت
        
        Args:
            key: المفتاح المراد حذفه
            
        Returns:
            True إذا تم الحذف بنجاح، False إذا لم يكن العنصر موجوداً
        """
        try:
            if key in self.cache:
                self.cache.pop(key)
                if key in self.timestamps:
                    del self.timestamps[key]
                return True
            return False
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        مسح التخزين المؤقت بالكامل
        
        Returns:
            True إذا تم المسح بنجاح
        """
        try:
            self.cache.clear()
            self.timestamps.clear()
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {str(e)}")
            return False
    
    def size(self) -> int:
        """
        الحصول على حجم التخزين المؤقت
        
        Returns:
            عدد العناصر في التخزين المؤقت
        """
        return len(self.cache)
    
    def get_stats(self) -> dict:
        """
        الحصول على إحصائيات التخزين المؤقت
        
        Returns:
            قاموس يحتوي على إحصائيات التخزين المؤقت
        """
        return {
            'size': self.size(),
            'max_size': self.max_size,
            'ttl': self.ttl,
            'usage_percentage': (self.size() / self.max_size) * 100 if self.max_size > 0 else 0
        }

# إنشاء مدير التخزين المؤقت العام
cache_manager = CacheManager(max_size=200, ttl=600)  # 200 عنصر، صلاحية 10 دقائق

# وظائف خاصة بصنع البوت
def set_bot_creation_data(user_id: int, data: dict) -> bool:
    """
    حفظ بيانات صنع البوت للمستخدم
    
    Args:
        user_id: معرف المستخدم
        data: البيانات المراد حفظها
        
    Returns:
        True إذا تم الحفظ بنجاح
    """
    key = f"bot_creation_{user_id}"
    return cache_manager.set(key, data)

def get_bot_creation_data(user_id: int) -> Optional[dict]:
    """
    الحصول على بيانات صنع البوت للمستخدم
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        البيانات المحفوظة أو None
    """
    key = f"bot_creation_{user_id}"
    return cache_manager.get(key)

def delete_bot_creation_data(user_id: int) -> bool:
    """
    حذف بيانات صنع البوت للمستخدم
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        True إذا تم الحذف بنجاح
    """
    key = f"bot_creation_{user_id}"
    return cache_manager.delete(key)