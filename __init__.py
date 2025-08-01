"""
Bot Factory Maker - مصنع البوتات
حزمة Python الرئيسية لمصنع البوتات
"""

__version__ = "2.0.0"
__author__ = "Bot Factory Team"
__description__ = "مصنع البوتات - نظام متكامل لإنشاء وإدارة البوتات"

# استيراد الدالة الرئيسية
from .main import main, BotFactory

__all__ = [
    'main',
    'BotFactory',
    '__version__',
    '__author__',
    '__description__'
]