"""
Temp File Manager - مدير الملفات المؤقتة
يحتوي على مدير الملفات المؤقتة لإنشاء وحذف الملفات المؤقتة
"""

import tempfile
import os
import time
from typing import Optional, Set
from .logger import logger

class TempFileManager:
    """
    مدير الملفات المؤقتة
    يتعامل مع إنشاء وحذف الملفات المؤقتة بشكل آمن
    """
    
    def __init__(self):
        """تهيئة مدير الملفات المؤقتة"""
        self.temp_files: Set[str] = set()
        self.temp_dir = tempfile.gettempdir()
    
    def create_temp_file(self, suffix: str = "", prefix: str = "factory_bot_") -> Optional[str]:
        """
        إنشاء ملف مؤقت جديد
        
        Args:
            suffix: اللاحقة المطلوبة للملف
            prefix: البادئة المطلوبة للملف
            
        Returns:
            مسار الملف المؤقت أو None في حالة الخطأ
        """
        try:
            # إنشاء ملف مؤقت
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix=suffix,
                prefix=prefix,
                delete=False,
                dir=self.temp_dir
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # إضافة الملف إلى القائمة
            self.temp_files.add(temp_path)
            logger.info(f"تم إنشاء ملف مؤقت: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف مؤقت: {str(e)}")
            return None
    
    def create_temp_file_with_content(self, content: str, suffix: str = "", prefix: str = "factory_bot_") -> Optional[str]:
        """
        إنشاء ملف مؤقت مع محتوى محدد
        
        Args:
            content: المحتوى المراد كتابته في الملف
            suffix: اللاحقة المطلوبة للملف
            prefix: البادئة المطلوبة للملف
            
        Returns:
            مسار الملف المؤقت أو None في حالة الخطأ
        """
        try:
            temp_path = self.create_temp_file(suffix, prefix)
            if temp_path:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"تم إنشاء ملف مؤقت مع محتوى: {temp_path}")
                return temp_path
            return None
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف مؤقت مع محتوى: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        حذف ملف مؤقت محدد
        
        Args:
            file_path: مسار الملف المراد حذفه
            
        Returns:
            True إذا تم الحذف بنجاح، False في حالة الخطأ
        """
        try:
            if file_path in self.temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"تم حذف ملف مؤقت: {file_path}")
                self.temp_files.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في حذف ملف مؤقت {file_path}: {str(e)}")
            return False
    
    def cleanup_all_temp_files(self) -> int:
        """
        حذف جميع الملفات المؤقتة
        
        Returns:
            عدد الملفات التي تم حذفها بنجاح
        """
        deleted_count = 0
        files_to_remove = list(self.temp_files)
        
        for file_path in files_to_remove:
            if self.cleanup_temp_file(file_path):
                deleted_count += 1
        
        logger.info(f"تم حذف {deleted_count} ملف مؤقت من أصل {len(files_to_remove)}")
        return deleted_count
    
    def get_temp_files_count(self) -> int:
        """
        الحصول على عدد الملفات المؤقتة الحالية
        
        Returns:
            عدد الملفات المؤقتة
        """
        return len(self.temp_files)
    
    def get_temp_files_list(self) -> list:
        """
        الحصول على قائمة بجميع الملفات المؤقتة
        
        Returns:
            قائمة بمسارات الملفات المؤقتة
        """
        return list(self.temp_files)
    
    def cleanup_old_temp_files(self, max_age_hours: int = 24) -> int:
        """
        حذف الملفات المؤقتة القديمة
        
        Args:
            max_age_hours: العمر الأقصى للملفات بالساعات
            
        Returns:
            عدد الملفات التي تم حذفها
        """
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        files_to_remove = []
        
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        files_to_remove.append(file_path)
            except Exception as e:
                logger.warning(f"خطأ في فحص عمر الملف {file_path}: {str(e)}")
        
        for file_path in files_to_remove:
            if self.cleanup_temp_file(file_path):
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"تم حذف {deleted_count} ملف مؤقت قديم")
        
        return deleted_count

# إنشاء مدير الملفات المؤقتة العام
temp_file_manager = TempFileManager()