"""
Logger Configuration - إعدادات التسجيل
يحتوي على إعدادات الـ logger المستخدم في المشروع
"""

import logging
import os
from typing import Optional

def setup_logger(
    name: str = __name__,
    log_file: str = "factory_bot.log",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    إعداد الـ logger مع التخصيص
    
    Args:
        name: اسم الـ logger
        log_file: اسم ملف السجل
        level: مستوى التسجيل
        format_string: تنسيق الرسائل
    
    Returns:
        logger: كائن الـ logger المُعد
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # إنشاء الـ logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # تجنب إضافة handlers مكررة
    if logger.handlers:
        return logger
    
    # إنشاء formatter
    formatter = logging.Formatter(format_string)
    
    # Handler للملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler للكونسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# إنشاء الـ logger الافتراضي
logger = setup_logger("factory_bot")