"""
Rate Limit Manager - مدير التأخير
يحتوي على مدير التأخير لتجنب الحظر وتحسين الأداء
"""

import time
import asyncio
from typing import Dict, Optional
from .logger import logger

class RateLimitManager:
    """
    مدير التأخير بين العمليات
    يضيف تأخيراً بين العمليات لتجنب الحظر وتحسين الأداء
    """
    
    def __init__(self):
        """تهيئة مدير التأخير"""
        self.last_operations: Dict[str, float] = {}
        self.min_delays = {
            'broadcast': 0.1,      # تأخير البث
            'database': 0.05,      # تأخير قاعدة البيانات
            'process': 0.5,        # تأخير العمليات
            'telegram': 0.2,       # تأخير عمليات تيليجرام
            'default': 0.1         # التأخير الافتراضي
        }
    
    def wait_if_needed(self, operation_type: str = 'default') -> None:
        """
        انتظار إذا كان مطلوباً لتجنب الحظر (للعمليات المتزامنة)
        
        Args:
            operation_type: نوع العملية
        """
        try:
            min_delay = self.min_delays.get(operation_type, self.min_delays['default'])
            last_time = self.last_operations.get(operation_type, 0)
            current_time = time.time()
            
            time_since_last = current_time - last_time
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last
                time.sleep(sleep_time)
                logger.debug(f"تم إضافة تأخير {sleep_time:.3f}s للعملية {operation_type}")
            
            self.last_operations[operation_type] = time.time()
        except Exception as e:
            logger.warning(f"خطأ في مدير التأخير للعملية {operation_type}: {str(e)}")
    
    async def async_wait_if_needed(self, operation_type: str = 'default') -> None:
        """
        انتظار إذا كان مطلوباً لتجنب الحظر (للعمليات غير المتزامنة)
        
        Args:
            operation_type: نوع العملية
        """
        try:
            min_delay = self.min_delays.get(operation_type, self.min_delays['default'])
            last_time = self.last_operations.get(operation_type, 0)
            current_time = time.time()
            
            time_since_last = current_time - last_time
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last
                await asyncio.sleep(sleep_time)
                logger.debug(f"تم إضافة تأخير {sleep_time:.3f}s للعملية {operation_type}")
            
            self.last_operations[operation_type] = time.time()
        except Exception as e:
            logger.warning(f"خطأ في مدير التأخير للعملية {operation_type}: {str(e)}")
    
    def get_last_operation_time(self, operation_type: str = 'default') -> float:
        """
        الحصول على وقت آخر عملية
        
        Args:
            operation_type: نوع العملية
            
        Returns:
            وقت آخر عملية
        """
        return self.last_operations.get(operation_type, 0)
    
    def set_min_delay(self, operation_type: str, delay: float) -> bool:
        """
        تعيين التأخير الأدنى لنوع عملية معين
        
        Args:
            operation_type: نوع العملية
            delay: التأخير المطلوب بالثواني
            
        Returns:
            True إذا تم التعيين بنجاح
        """
        try:
            if delay >= 0:
                self.min_delays[operation_type] = delay
                logger.info(f"تم تعيين التأخير الأدنى للعملية {operation_type} إلى {delay}s")
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في تعيين التأخير للعملية {operation_type}: {str(e)}")
            return False
    
    def get_min_delay(self, operation_type: str = 'default') -> float:
        """
        الحصول على التأخير الأدنى لنوع عملية معين
        
        Args:
            operation_type: نوع العملية
            
        Returns:
            التأخير الأدنى بالثواني
        """
        return self.min_delays.get(operation_type, self.min_delays['default'])
    
    def reset_operation_time(self, operation_type: str) -> None:
        """
        إعادة تعيين وقت آخر عملية
        
        Args:
            operation_type: نوع العملية
        """
        try:
            if operation_type in self.last_operations:
                del self.last_operations[operation_type]
                logger.debug(f"تم إعادة تعيين وقت العملية {operation_type}")
        except Exception as e:
            logger.warning(f"خطأ في إعادة تعيين وقت العملية {operation_type}: {str(e)}")
    
    def get_stats(self) -> Dict[str, any]:
        """
        الحصول على إحصائيات مدير التأخير
        
        Returns:
            قاموس يحتوي على إحصائيات مدير التأخير
        """
        current_time = time.time()
        stats = {
            'min_delays': self.min_delays.copy(),
            'last_operations': {},
            'total_operations': len(self.last_operations)
        }
        
        for op_type, last_time in self.last_operations.items():
            stats['last_operations'][op_type] = {
                'last_time': last_time,
                'time_since_last': current_time - last_time
            }
        
        return stats

# إنشاء مدير التأخير العام
rate_limit_manager = RateLimitManager()