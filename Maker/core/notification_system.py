"""
نظام الإشعارات والتنبيهات المتقدم
يوفر إشعارات فورية للمطورين والمستخدمين حول حالة النظام والبوتات
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعداد الـ logging
logger = logging.getLogger(__name__)

class NotificationLevel(Enum):
    """مستويات الإشعارات"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"

class NotificationType(Enum):
    """أنواع الإشعارات"""
    BOT_CREATED = "bot_created"
    BOT_DELETED = "bot_deleted"
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    BOT_ERROR = "bot_error"
    SYSTEM_ALERT = "system_alert"
    RESOURCE_WARNING = "resource_warning"
    MAINTENANCE = "maintenance"
    UPDATE_AVAILABLE = "update_available"

@dataclass
class Notification:
    """إشعار النظام"""
    id: str
    timestamp: float
    level: NotificationLevel
    type: NotificationType
    title: str
    message: str
    user_id: Optional[int] = None
    bot_username: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    sent: bool = False
    read: bool = False

class NotificationSystem:
    """نظام الإشعارات المتقدم"""
    
    def __init__(self):
        self.notifications = []
        self.subscribers = {
            NotificationLevel.INFO: set(),
            NotificationLevel.WARNING: set(),
            NotificationLevel.ERROR: set(),
            NotificationLevel.CRITICAL: set(),
            NotificationLevel.SUCCESS: set()
        }
        
        # إعدادات الإشعارات
        self.settings = {
            'max_notifications': 1000,
            'auto_cleanup_days': 7,
            'batch_send_delay': 2,  # ثواني
            'rate_limit_per_user': 10,  # إشعارات في الدقيقة
            'critical_immediate_send': True
        }
        
        # تتبع معدل الإرسال
        self.rate_limits = {}
        
        self.notification_counter = 0
        self.client = None
        
    def set_client(self, client: Client):
        """تعيين عميل Pyrogram"""
        self.client = client
    
    def subscribe(self, user_id: int, levels: List[NotificationLevel]):
        """اشتراك مستخدم في مستويات إشعارات معينة"""
        for level in levels:
            self.subscribers[level].add(user_id)
        
        logger.info(f"تم اشتراك المستخدم {user_id} في المستويات: {[l.value for l in levels]}")
    
    def unsubscribe(self, user_id: int, levels: List[NotificationLevel] = None):
        """إلغاء اشتراك مستخدم"""
        if levels is None:
            # إلغاء الاشتراك من جميع المستويات
            for level_subscribers in self.subscribers.values():
                level_subscribers.discard(user_id)
        else:
            for level in levels:
                self.subscribers[level].discard(user_id)
        
        logger.info(f"تم إلغاء اشتراك المستخدم {user_id}")
    
    def create_notification(
        self,
        level: NotificationLevel,
        type_: NotificationType,
        title: str,
        message: str,
        user_id: Optional[int] = None,
        bot_username: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """إنشاء إشعار جديد"""
        
        self.notification_counter += 1
        notification = Notification(
            id=f"notif_{self.notification_counter}_{int(time.time())}",
            timestamp=time.time(),
            level=level,
            type=type_,
            title=title,
            message=message,
            user_id=user_id,
            bot_username=bot_username,
            data=data or {}
        )
        
        self.notifications.append(notification)
        
        # تنظيف الإشعارات القديمة
        self._cleanup_old_notifications()
        
        logger.info(f"تم إنشاء إشعار جديد: {notification.id} - {title}")
        
        return notification
    
    async def send_notification(self, notification: Notification, target_users: Set[int] = None):
        """إرسال إشعار للمستخدمين المشتركين"""
        if not self.client:
            logger.error("لم يتم تعيين عميل Pyrogram")
            return
        
        # تحديد المستخدمين المستهدفين
        if target_users is None:
            target_users = self.subscribers[notification.level].copy()
        
        # إضافة المستخدم المحدد إذا كان موجوداً
        if notification.user_id:
            target_users.add(notification.user_id)
        
        if not target_users:
            logger.info(f"لا يوجد مشتركون للإشعار {notification.id}")
            return
        
        # تنسيق الرسالة
        formatted_message = self._format_notification_message(notification)
        keyboard = self._create_notification_keyboard(notification)
        
        sent_count = 0
        failed_count = 0
        
        for user_id in target_users:
            try:
                # فحص معدل الإرسال
                if not self._check_rate_limit(user_id):
                    logger.warning(f"تم تجاوز معدل الإرسال للمستخدم {user_id}")
                    continue
                
                await self.client.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
                
                sent_count += 1
                self._update_rate_limit(user_id)
                
                # تأخير قصير لتجنب الـ flood
                if sent_count % 5 == 0:
                    await asyncio.sleep(self.settings['batch_send_delay'])
                
            except Exception as e:
                logger.error(f"فشل إرسال الإشعار للمستخدم {user_id}: {e}")
                failed_count += 1
        
        notification.sent = True
        logger.info(f"تم إرسال الإشعار {notification.id} لـ {sent_count} مستخدم، فشل مع {failed_count}")
    
    async def send_immediate_notification(
        self,
        level: NotificationLevel,
        type_: NotificationType,
        title: str,
        message: str,
        target_users: Set[int] = None,
        **kwargs
    ):
        """إرسال إشعار فوري"""
        notification = self.create_notification(level, type_, title, message, **kwargs)
        await self.send_notification(notification, target_users)
        return notification
    
    async def broadcast_system_alert(self, title: str, message: str, level: NotificationLevel = NotificationLevel.WARNING):
        """بث تنبيه نظام لجميع المطورين"""
        # الحصول على جميع المطورين
        all_devs = set()
        for level_subscribers in self.subscribers.values():
            all_devs.update(level_subscribers)
        
        await self.send_immediate_notification(
            level=level,
            type_=NotificationType.SYSTEM_ALERT,
            title=f"🚨 {title}",
            message=message,
            target_users=all_devs
        )
    
    def _format_notification_message(self, notification: Notification) -> str:
        """تنسيق رسالة الإشعار"""
        level_icons = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️", 
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨",
            NotificationLevel.SUCCESS: "✅"
        }
        
        type_icons = {
            NotificationType.BOT_CREATED: "🤖",
            NotificationType.BOT_DELETED: "🗑️",
            NotificationType.BOT_STARTED: "🟢",
            NotificationType.BOT_STOPPED: "🔴",
            NotificationType.BOT_ERROR: "⚠️",
            NotificationType.SYSTEM_ALERT: "🚨",
            NotificationType.RESOURCE_WARNING: "📊",
            NotificationType.MAINTENANCE: "🔧",
            NotificationType.UPDATE_AVAILABLE: "🔄"
        }
        
        level_icon = level_icons.get(notification.level, "📢")
        type_icon = type_icons.get(notification.type, "📢")
        
        # تنسيق الوقت
        timestamp = time.strftime('%H:%M:%S', time.localtime(notification.timestamp))
        
        message = f"""
{level_icon} **إشعار النظام** {type_icon}

**العنوان:** {notification.title}
**الرسالة:** {notification.message}
**الوقت:** {timestamp}
"""
        
        # إضافة معلومات البوت إذا كانت متوفرة
        if notification.bot_username:
            message += f"**البوت:** @{notification.bot_username}\n"
        
        # إضافة بيانات إضافية
        if notification.data:
            for key, value in notification.data.items():
                if key not in ['internal_id', 'raw_data']:
                    message += f"**{key}:** {value}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━━"
        
        return message.strip()
    
    def _create_notification_keyboard(self, notification: Notification) -> Optional[InlineKeyboardMarkup]:
        """إنشاء لوحة مفاتيح للإشعار"""
        keyboard = []
        
        # أزرار حسب نوع الإشعار
        if notification.type == NotificationType.BOT_ERROR and notification.bot_username:
            keyboard.append([
                InlineKeyboardButton("🔄 إعادة تشغيل", 
                                   callback_data=f"restart_bot:{notification.bot_username}"),
                InlineKeyboardButton("📊 الإحصائيات", 
                                   callback_data=f"bot_stats:{notification.bot_username}")
            ])
        
        elif notification.type == NotificationType.SYSTEM_ALERT:
            keyboard.append([
                InlineKeyboardButton("📊 إحصائيات النظام", 
                                   callback_data="system_stats"),
                InlineKeyboardButton("🔧 الصيانة", 
                                   callback_data="maintenance_mode")
            ])
        
        elif notification.type == NotificationType.UPDATE_AVAILABLE:
            keyboard.append([
                InlineKeyboardButton("🔄 تحديث النظام", 
                                   callback_data="update_system"),
                InlineKeyboardButton("📄 تفاصيل التحديث", 
                                   callback_data="update_details")
            ])
        
        # أزرار عامة
        keyboard.append([
            InlineKeyboardButton("✅ تم القراءة", 
                               callback_data=f"mark_read:{notification.id}"),
            InlineKeyboardButton("🔕 إلغاء الاشتراك", 
                               callback_data=f"unsubscribe:{notification.level.value}")
        ])
        
        return InlineKeyboardMarkup(keyboard) if keyboard else None
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """فحص معدل الإرسال للمستخدم"""
        current_time = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # تنظيف الطوابع الزمنية القديمة (أكثر من دقيقة)
        self.rate_limits[user_id] = [
            timestamp for timestamp in self.rate_limits[user_id]
            if current_time - timestamp < 60
        ]
        
        # فحص الحد الأقصى
        return len(self.rate_limits[user_id]) < self.settings['rate_limit_per_user']
    
    def _update_rate_limit(self, user_id: int):
        """تحديث معدل الإرسال للمستخدم"""
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        self.rate_limits[user_id].append(time.time())
    
    def _cleanup_old_notifications(self):
        """تنظيف الإشعارات القديمة"""
        current_time = time.time()
        cleanup_threshold = self.settings['auto_cleanup_days'] * 24 * 3600
        
        # حذف الإشعارات القديمة
        self.notifications = [
            notif for notif in self.notifications
            if current_time - notif.timestamp < cleanup_threshold
        ]
        
        # الحد الأقصى للإشعارات
        if len(self.notifications) > self.settings['max_notifications']:
            self.notifications = self.notifications[-self.settings['max_notifications']:]
    
    def get_user_notifications(self, user_id: int, limit: int = 20, unread_only: bool = False) -> List[Notification]:
        """الحصول على إشعارات مستخدم معين"""
        user_notifications = [
            notif for notif in self.notifications
            if (notif.user_id == user_id or 
                user_id in self.subscribers.get(notif.level, set()))
        ]
        
        if unread_only:
            user_notifications = [notif for notif in user_notifications if not notif.read]
        
        # ترتيب حسب الوقت (الأحدث أولاً)
        user_notifications.sort(key=lambda x: x.timestamp, reverse=True)
        
        return user_notifications[:limit]
    
    def mark_notification_read(self, notification_id: str, user_id: int) -> bool:
        """تحديد إشعار كمقروء"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                logger.info(f"تم تحديد الإشعار {notification_id} كمقروء من قبل {user_id}")
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الإشعارات"""
        total_notifications = len(self.notifications)
        
        # إحصائيات حسب المستوى
        by_level = {}
        for level in NotificationLevel:
            by_level[level.value] = len([n for n in self.notifications if n.level == level])
        
        # إحصائيات حسب النوع
        by_type = {}
        for type_ in NotificationType:
            by_type[type_.value] = len([n for n in self.notifications if n.type == type_])
        
        # إحصائيات الإرسال
        sent_notifications = len([n for n in self.notifications if n.sent])
        read_notifications = len([n for n in self.notifications if n.read])
        
        # إحصائيات المشتركين
        total_subscribers = len(set().union(*self.subscribers.values()))
        
        return {
            'total_notifications': total_notifications,
            'sent_notifications': sent_notifications,
            'read_notifications': read_notifications,
            'unread_notifications': total_notifications - read_notifications,
            'by_level': by_level,
            'by_type': by_type,
            'total_subscribers': total_subscribers,
            'subscribers_by_level': {
                level.value: len(users) for level, users in self.subscribers.items()
            }
        }
    
    async def send_daily_summary(self):
        """إرسال ملخص يومي للمطورين"""
        stats = self.get_statistics()
        
        # إحصائيات اليوم
        today_start = time.time() - 24 * 3600
        today_notifications = [
            n for n in self.notifications 
            if n.timestamp >= today_start
        ]
        
        if not today_notifications:
            return
        
        summary = f"""
📊 **الملخص اليومي للإشعارات**

📈 **إحصائيات اليوم:**
▪️ إجمالي الإشعارات: {len(today_notifications)}
▪️ المرسلة: {len([n for n in today_notifications if n.sent])}
▪️ المقروءة: {len([n for n in today_notifications if n.read])}

⚠️ **التنبيهات الهامة:**
▪️ تحذيرات: {len([n for n in today_notifications if n.level == NotificationLevel.WARNING])}
▪️ أخطاء: {len([n for n in today_notifications if n.level == NotificationLevel.ERROR])}
▪️ حرجة: {len([n for n in today_notifications if n.level == NotificationLevel.CRITICAL])}

🎯 **النشاطات:**
▪️ بوتات تم إنشاؤها: {len([n for n in today_notifications if n.type == NotificationType.BOT_CREATED])}
▪️ بوتات تم حذفها: {len([n for n in today_notifications if n.type == NotificationType.BOT_DELETED])}

━━━━━━━━━━━━━━━━━━━━━━
📅 {time.strftime('%Y-%m-%d', time.localtime())}
        """
        
        # إرسال للمطورين المشتركين في الإشعارات
        dev_users = self.subscribers[NotificationLevel.INFO].union(
            self.subscribers[NotificationLevel.WARNING]
        )
        
        await self.send_immediate_notification(
            level=NotificationLevel.INFO,
            type_=NotificationType.SYSTEM_ALERT,
            title="الملخص اليومي",
            message=summary.strip(),
            target_users=dev_users
        )

# إنشاء مثيل نظام الإشعارات
notification_system = NotificationSystem()