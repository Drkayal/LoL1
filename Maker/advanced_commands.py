"""
الأوامر المتقدمة للبوت مع الواجهة المحسنة
"""

import time
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

# استيراد الوحدات المتقدمة
try:
    from core.monitoring import monitoring_dashboard
    from core.ui_manager import ui_manager
    from core.notification_system import notification_system, NotificationLevel, NotificationType
    from core.process_manager import process_manager
    ADVANCED_FEATURES_AVAILABLE = True
    print("✅ تم تحميل الميزات المتقدمة")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"⚠️ الميزات المتقدمة غير متاحة: {e}")

print("📁 تم تحميل ملف الأوامر المتقدمة")
