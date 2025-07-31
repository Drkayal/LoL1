#!/usr/bin/env python3
"""
ملف التشغيل المحسن لبوت صانع الموسيقى
يتضمن مراقبة العمليات وإدارة محسنة للبوتات
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# إضافة المسار الحالي
sys.path.insert(0, str(Path(__file__).parent))

# إعداد الـ logging المحسن
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('maker_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MakerBotManager:
    """مدير بوت الصانع المحسن"""
    
    def __init__(self):
        self.bot = None
        self.process_manager = None
        self.monitoring_task = None
        self.shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """تهيئة البوت والوحدات"""
        try:
            # استيراد البوت
            from bot import bot, start_bot
            self.bot = bot
            
            # استيراد مدير العمليات
            try:
                from core.process_manager import process_manager
                self.process_manager = process_manager
                logger.info("✅ تم تحميل مدير العمليات المحسن")
            except ImportError:
                logger.warning("⚠️ لم يتم العثور على مدير العمليات المحسن")
                
            # التحقق من الإعدادات
            from config import final_config_check
            final_config_check()
            
            logger.info("✅ تم تهيئة البوت بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة البوت: {e}")
            return False
    
    async def start_monitoring(self):
        """بدء مراقبة البوتات"""
        if self.process_manager:
            try:
                self.monitoring_task = asyncio.create_task(
                    self.process_manager.monitor_bots(interval=120)
                )
                logger.info("🔍 تم بدء مراقبة البوتات")
            except Exception as e:
                logger.error(f"❌ خطأ في بدء المراقبة: {e}")
    
    async def stop_monitoring(self):
        """إيقاف مراقبة البوتات"""
        if self.process_manager:
            self.process_manager.stop_monitoring()
            
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            
        logger.info("🔴 تم إيقاف مراقبة البوتات")
    
    async def shutdown(self):
        """إيقاف البوت بشكل آمن"""
        logger.info("🔄 بدء عملية الإيقاف الآمن...")
        
        # إيقاف المراقبة
        await self.stop_monitoring()
        
        # إيقاف البوت
        if self.bot:
            try:
                await self.bot.stop()
                logger.info("✅ تم إيقاف البوت بنجاح")
            except Exception as e:
                logger.error(f"❌ خطأ في إيقاف البوت: {e}")
        
        # تعيين حدث الإيقاف
        self.shutdown_event.set()
        
        logger.info("🔴 تم إيقاف جميع العمليات")
    
    def setup_signal_handlers(self):
        """إعداد معالجات الإشارات للإيقاف الآمن"""
        def signal_handler(signum, frame):
            logger.info(f"📡 تم استلام إشارة {signum}")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
    
    async def run(self):
        """تشغيل البوت مع المراقبة"""
        try:
            # تهيئة البوت
            if not await self.initialize():
                return False
            
            # إعداد معالجات الإشارات
            self.setup_signal_handlers()
            
            # بدء مراقبة البوتات
            await self.start_monitoring()
            
            # بدء البوت
            logger.info("🚀 بدء تشغيل بوت الصانع...")
            
            # تشغيل البوت في مهمة منفصلة
            bot_task = asyncio.create_task(start_bot())
            
            # انتظار إشارة الإيقاف أو انتهاء البوت
            done, pending = await asyncio.wait(
                [bot_task, asyncio.create_task(self.shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # إلغاء المهام المعلقة
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            return True
            
        except KeyboardInterrupt:
            logger.info("⌨️ تم إيقاف البوت بواسطة المستخدم")
            await self.shutdown()
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            await self.shutdown()
            return False

async def main():
    """الدالة الرئيسية"""
    manager = MakerBotManager()
    
    try:
        success = await manager.run()
        if success:
            logger.info("✅ تم إنهاء البوت بنجاح")
            return 0
        else:
            logger.error("❌ فشل في تشغيل البوت")
            return 1
            
    except Exception as e:
        logger.error(f"❌ خطأ حرج في البوت: {e}")
        return 1

if __name__ == "__main__":
    try:
        # تشغيل البوت
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("⌨️ تم إيقاف البوت")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)