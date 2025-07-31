"""
مدير واجهة المستخدم المحسن
يوفر أزرار تفاعلية ورسائل جميلة ومنظمة
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton,
    Message, CallbackQuery
)
from pyrogram import Client
from datetime import datetime

# إعداد الـ logging
logger = logging.getLogger(__name__)

class UIManager:
    """مدير واجهة المستخدم المحسن"""
    
    def __init__(self):
        self.callback_handlers = {}
        self.progress_messages = {}
        
        # الألوان والرموز
        self.icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'loading': '🔄',
            'bot': '🤖',
            'stats': '📊',
            'settings': '⚙️',
            'music': '🎵',
            'fire': '🔥',
            'rocket': '🚀',
            'chart': '📈',
            'memory': '💾',
            'cpu': '⚡',
            'time': '⏱️',
            'user': '👑',
            'group': '👥',
            'channel': '📺',
            'link': '🔗',
            'folder': '📁',
            'file': '📄',
            'trash': '🗑️',
            'refresh': '🔃',
            'power': '🔋',
            'shield': '🛡️',
            'bell': '🔔',
            'star': '⭐',
            'diamond': '💎',
            'crown': '👑'
        }
        
        # قوالب الرسائل
        self.templates = {
            'header': "━━━━━━━━━━━━━━━━━━━━━━",
            'separator': "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            'bullet': "▪️",
            'arrow': "➤",
            'check': "✓",
            'cross': "✗"
        }
    
    def create_main_keyboard(self, is_dev: bool = False) -> ReplyKeyboardMarkup:
        """إنشاء لوحة المفاتيح الرئيسية المحسنة"""
        if is_dev:
            keyboard = [
                [f"{self.icons['bot']} صنع بوت", f"{self.icons['trash']} حذف بوت"],
                [f"{self.icons['stats']} البوتات المشتغلة", f"{self.icons['settings']} إدارة البوتات"],
                [f"{self.icons['power']} تشغيل الكل", f"{self.icons['power']} إيقاف الكل"],
                [f"{self.icons['chart']} الإحصائيات", f"{self.icons['bell']} التنبيهات"],
                [f"{self.icons['shield']} استخراج جلسة", f"{self.icons['refresh']} تحديث النظام"],
                [f"{self.icons['user']} إدارة المطورين", f"{self.icons['channel']} السورس"],
                [f"{self.icons['file']} التقارير", f"{self.icons['settings']} الإعدادات"]
            ]
        else:
            keyboard = [
                [f"{self.icons['bot']} صنع بوت", f"{self.icons['trash']} حذف بوت"],
                [f"{self.icons['shield']} استخراج جلسة"],
                [f"{self.icons['channel']} السورس", f"{self.icons['user']} المطور"]
            ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    def create_bot_management_keyboard(self, bot_username: str) -> InlineKeyboardMarkup:
        """إنشاء لوحة مفاتيح إدارة البوت"""
        keyboard = [
            [
                InlineKeyboardButton(f"{self.icons['power']} تشغيل", 
                                   callback_data=f"start_bot:{bot_username}"),
                InlineKeyboardButton(f"{self.icons['power']} إيقاف", 
                                   callback_data=f"stop_bot:{bot_username}")
            ],
            [
                InlineKeyboardButton(f"{self.icons['refresh']} إعادة تشغيل", 
                                   callback_data=f"restart_bot:{bot_username}"),
                InlineKeyboardButton(f"{self.icons['stats']} الإحصائيات", 
                                   callback_data=f"bot_stats:{bot_username}")
            ],
            [
                InlineKeyboardButton(f"{self.icons['file']} السجلات", 
                                   callback_data=f"bot_logs:{bot_username}"),
                InlineKeyboardButton(f"{self.icons['settings']} الإعدادات", 
                                   callback_data=f"bot_settings:{bot_username}")
            ],
            [
                InlineKeyboardButton(f"{self.icons['trash']} حذف البوت", 
                                   callback_data=f"delete_bot:{bot_username}")
            ],
            [
                InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_main")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_stats_keyboard(self) -> InlineKeyboardMarkup:
        """إنشاء لوحة مفاتيح الإحصائيات"""
        keyboard = [
            [
                InlineKeyboardButton(f"{self.icons['chart']} إحصائيات عامة", 
                                   callback_data="general_stats"),
                InlineKeyboardButton(f"{self.icons['bot']} إحصائيات البوتات", 
                                   callback_data="bots_stats")
            ],
            [
                InlineKeyboardButton(f"{self.icons['memory']} استهلاك الذاكرة", 
                                   callback_data="memory_stats"),
                InlineKeyboardButton(f"{self.icons['cpu']} استهلاك المعالج", 
                                   callback_data="cpu_stats")
            ],
            [
                InlineKeyboardButton(f"{self.icons['bell']} التنبيهات", 
                                   callback_data="alerts_stats"),
                InlineKeyboardButton(f"{self.icons['file']} تقرير مفصل", 
                                   callback_data="detailed_report")
            ],
            [
                InlineKeyboardButton(f"{self.icons['refresh']} تحديث", 
                                   callback_data="refresh_stats"),
                InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_main")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_welcome_message(self, user_name: str, is_dev: bool = False) -> str:
        """تنسيق رسالة الترحيب"""
        role = "المطور" if is_dev else "العضو"
        
        message = f"""
{self.templates['header']}
{self.icons['crown']} **مرحباً بك في بوت صانع الموسيقى المحسن**
{self.templates['header']}

{self.icons['user']} **أهلاً بك عزيزي {role}: {user_name}**

{self.icons['fire']} **الميزات المتاحة:**
{self.templates['bullet']} صناعة بوتات موسيقى متطورة
{self.templates['bullet']} مراقبة شاملة للبوتات
{self.templates['bullet']} إحصائيات في الوقت الفعلي
{self.templates['bullet']} واجهة سهلة ومتطورة

{self.icons['rocket']} **اختر ما تريد فعله من الأزرار أدناه**

{self.templates['separator']}
{self.icons['diamond']} *تم تطوير البوت بأحدث التقنيات*
        """
        
        return message.strip()
    
    def format_bot_creation_progress(self, step: str, progress: int = 0) -> str:
        """تنسيق رسالة تقدم إنشاء البوت"""
        progress_bar = self._create_progress_bar(progress)
        
        message = f"""
{self.icons['rocket']} **جاري إنشاء البوت...**

{self.icons['loading']} **الخطوة الحالية:** {step}

{progress_bar}

{self.icons['info']} **يرجى الانتظار، العملية قد تستغرق دقيقة...**
        """
        
        return message.strip()
    
    def format_bot_success_message(self, bot_info: Dict[str, Any]) -> str:
        """تنسيق رسالة نجاح إنشاء البوت"""
        message = f"""
{self.templates['header']}
{self.icons['success']} **تم إنشاء البوت بنجاح!**
{self.templates['header']}

{self.icons['bot']} **معرف البوت:** @{bot_info['username']}
{self.icons['user']} **المطور:** {bot_info.get('owner_id', 'غير محدد')}
{self.icons['group']} **مجموعة السجلات:** [انقر هنا]({bot_info.get('logger_group', {}).get('invite_link', '#')})
{self.icons['music']} **النوع:** بوت موسيقى متقدم
{self.icons['power']} **الحالة:** {self.icons['success']} يعمل الآن

{self.templates['separator']}

{self.icons['fire']} **البوت جاهز للاستخدام!**
{self.icons['star']} يمكنك الآن إضافته لمجموعاتك والاستمتاع بالموسيقى

{self.icons['info']} **للحصول على المساعدة، استخدم الأزرار أدناه**
        """
        
        return message.strip()
    
    def format_stats_message(self, stats_data: Dict[str, Any]) -> str:
        """تنسيق رسالة الإحصائيات"""
        system_metrics = stats_data.get('system_metrics', {})
        summary = stats_data.get('summary', {})
        performance = stats_data.get('performance', {})
        
        # تنسيق وقت التشغيل
        uptime = summary.get('system_uptime', 0)
        uptime_str = self._format_uptime(uptime)
        
        message = f"""
{self.templates['header']}
{self.icons['chart']} **إحصائيات النظام المتقدمة**
{self.templates['header']}

{self.icons['bot']} **إحصائيات البوتات:**
{self.templates['bullet']} المجموع: **{summary.get('total_bots', 0)}** بوت
{self.templates['bullet']} المشغل: **{summary.get('running_bots', 0)}** {self.icons['success']}
{self.templates['bullet']} المتوقف: **{summary.get('total_bots', 0) - summary.get('running_bots', 0)}** {self.icons['error']}

{self.icons['memory']} **استهلاك الموارد:**
{self.templates['bullet']} الذاكرة: **{system_metrics.get('memory_usage', 0):.1f}%**
{self.templates['bullet']} المعالج: **{system_metrics.get('cpu_usage', 0):.1f}%**
{self.templates['bullet']} القرص: **{system_metrics.get('disk_usage', 0):.1f}%**

{self.icons['time']} **معلومات النظام:**
{self.templates['bullet']} وقت التشغيل: **{uptime_str}**
{self.templates['bullet']} العمليات النشطة: **{system_metrics.get('active_processes', 0)}**

{self.icons['bell']} **التنبيهات:**
{self.templates['bullet']} المجموع: **{summary.get('total_alerts', 0)}**
{self.templates['bullet']} غير المحلولة: **{summary.get('unresolved_alerts', 0)}**

{self.icons['star']} **الأداء:**
{self.templates['bullet']} معدل النجاح: **{performance.get('success_rate', 0):.1f}%**
{self.templates['bullet']} متوسط الاستجابة: **{performance.get('avg_response_time', 0):.2f}s**

{self.templates['separator']}
{self.icons['refresh']} *آخر تحديث: {datetime.now().strftime('%H:%M:%S')}*
        """
        
        return message.strip()
    
    def format_bot_list_message(self, bots: List[Dict[str, Any]], title: str = "قائمة البوتات") -> str:
        """تنسيق رسالة قائمة البوتات"""
        if not bots:
            return f"""
{self.icons['info']} **{title}**

{self.icons['error']} لا توجد بوتات حالياً

{self.templates['separator']}
{self.icons['bot']} يمكنك إنشاء بوت جديد باستخدام الأزرار أدناه
            """
        
        message = f"""
{self.templates['header']}
{self.icons['bot']} **{title}**
{self.templates['header']}

"""
        
        for i, bot in enumerate(bots, 1):
            status_icon = self.icons['success'] if bot.get('status') == 'running' else self.icons['error']
            uptime = self._format_uptime(bot.get('uptime', 0))
            
            message += f"""
{self.icons['diamond']} **{i}. @{bot.get('username', 'غير معروف')}**
{self.templates['bullet']} الحالة: {status_icon} {bot.get('status', 'غير معروف')}
{self.templates['bullet']} الذاكرة: **{bot.get('memory_usage', 0):.1f} MB**
{self.templates['bullet']} المعالج: **{bot.get('cpu_usage', 0):.1f}%**
{self.templates['bullet']} التشغيل: **{uptime}**
{self.templates['bullet']} المالك: **{bot.get('owner_id', 'غير معروف')}**

"""
        
        message += f"""
{self.templates['separator']}
{self.icons['stats']} **المجموع:** {len(bots)} بوت
{self.icons['refresh']} *آخر تحديث: {datetime.now().strftime('%H:%M:%S')}*
        """
        
        return message.strip()
    
    def format_error_message(self, error: str, details: str = None) -> str:
        """تنسيق رسالة خطأ"""
        message = f"""
{self.icons['error']} **حدث خطأ**

{self.icons['warning']} **الخطأ:** {error}
"""
        
        if details:
            message += f"""
{self.icons['info']} **التفاصيل:** {details}
"""
        
        message += f"""
{self.templates['separator']}
{self.icons['info']} يرجى المحاولة مرة أخرى أو التواصل مع المطور
        """
        
        return message.strip()
    
    def format_alert_message(self, alert: Dict[str, Any]) -> str:
        """تنسيق رسالة تنبيه"""
        level_icons = {
            'info': self.icons['info'],
            'warning': self.icons['warning'],
            'error': self.icons['error'],
            'critical': '🚨'
        }
        
        level_icon = level_icons.get(alert.get('level', 'info'), self.icons['info'])
        timestamp = datetime.fromtimestamp(alert.get('timestamp', time.time())).strftime('%H:%M:%S')
        
        message = f"""
{level_icon} **تنبيه النظام**

{self.icons['bell']} **العنوان:** {alert.get('title', 'تنبيه')}
{self.icons['info']} **الرسالة:** {alert.get('message', 'لا توجد تفاصيل')}
{self.icons['time']} **الوقت:** {timestamp}
"""
        
        if alert.get('bot_username'):
            message += f"{self.icons['bot']} **البوت:** @{alert['bot_username']}\n"
        
        return message.strip()
    
    def _create_progress_bar(self, progress: int, length: int = 10) -> str:
        """إنشاء شريط تقدم"""
        filled = int(progress / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {progress}%"
    
    def _format_uptime(self, seconds: float) -> str:
        """تنسيق وقت التشغيل"""
        if seconds < 60:
            return f"{int(seconds)}ث"
        elif seconds < 3600:
            return f"{int(seconds // 60)}د {int(seconds % 60)}ث"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}س {minutes}د"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}ي {hours}س"
    
    async def send_progress_message(self, client: Client, chat_id: int, initial_text: str) -> Message:
        """إرسال رسالة تقدم قابلة للتحديث"""
        message = await client.send_message(chat_id, initial_text)
        self.progress_messages[chat_id] = message
        return message
    
    async def update_progress_message(self, client: Client, chat_id: int, new_text: str):
        """تحديث رسالة التقدم"""
        if chat_id in self.progress_messages:
            try:
                await self.progress_messages[chat_id].edit_text(new_text)
            except Exception as e:
                logger.error(f"خطأ في تحديث رسالة التقدم: {e}")
    
    async def cleanup_progress_message(self, chat_id: int):
        """تنظيف رسالة التقدم"""
        if chat_id in self.progress_messages:
            del self.progress_messages[chat_id]
    
    def register_callback_handler(self, pattern: str, handler: Callable):
        """تسجيل معالج callback"""
        self.callback_handlers[pattern] = handler
    
    async def handle_callback(self, client: Client, callback_query: CallbackQuery):
        """معالجة callback queries"""
        data = callback_query.data
        
        for pattern, handler in self.callback_handlers.items():
            if data.startswith(pattern):
                try:
                    await handler(client, callback_query)
                    return
                except Exception as e:
                    logger.error(f"خطأ في معالجة callback {pattern}: {e}")
                    await callback_query.answer("حدث خطأ أثناء المعالجة", show_alert=True)
                    return
        
        # معالج افتراضي
        await callback_query.answer("هذا الزر غير مدعوم حالياً", show_alert=True)
    
    def create_confirmation_keyboard(self, action: str, target: str) -> InlineKeyboardMarkup:
        """إنشاء لوحة مفاتيح تأكيد"""
        keyboard = [
            [
                InlineKeyboardButton(f"{self.icons['success']} نعم", 
                                   callback_data=f"confirm:{action}:{target}"),
                InlineKeyboardButton(f"{self.icons['error']} لا", 
                                   callback_data=f"cancel:{action}:{target}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_confirmation_message(self, action: str, target: str) -> str:
        """تنسيق رسالة تأكيد"""
        actions_text = {
            'delete_bot': 'حذف البوت',
            'stop_bot': 'إيقاف البوت', 
            'restart_bot': 'إعادة تشغيل البوت',
            'stop_all': 'إيقاف جميع البوتات',
            'start_all': 'تشغيل جميع البوتات'
        }
        
        action_text = actions_text.get(action, action)
        
        message = f"""
{self.icons['warning']} **تأكيد العملية**

{self.icons['info']} هل أنت متأكد من {action_text}؟

{self.icons['bot']} **الهدف:** {target}

{self.templates['separator']}
{self.icons['warning']} **تحذير:** هذه العملية لا يمكن التراجع عنها
        """
        
        return message.strip()

# إنشاء مثيل مدير واجهة المستخدم
ui_manager = UIManager()