"""
وحدة إدارة العمليات المحسنة
تحتوي على وظائف مراقبة وإدارة البوتات المصنوعة
"""

import os
import psutil
import subprocess
import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# إعداد الـ logging
logger = logging.getLogger(__name__)

class BotStatus(Enum):
    """حالات البوت"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

@dataclass
class BotProcess:
    """معلومات عملية البوت"""
    username: str
    pid: Optional[int]
    status: BotStatus
    cpu_usage: float
    memory_usage: float
    start_time: Optional[float]
    log_file: str
    working_directory: str
    owner_id: int

class ProcessManager:
    """مدير العمليات المحسن"""
    
    def __init__(self):
        self.monitored_bots: Dict[str, BotProcess] = {}
        self.monitoring_active = False
        
    def scan_bot_processes(self) -> List[BotProcess]:
        """
        فحص جميع عمليات البوتات الموجودة
        """
        bot_processes = []
        
        try:
            # البحث في مجلد Maked
            if os.path.exists("Maked"):
                for bot_folder in os.listdir("Maded"):
                    if os.path.isdir(f"Maded/{bot_folder}"):
                        bot_process = self._get_bot_process_info(bot_folder)
                        if bot_process:
                            bot_processes.append(bot_process)
                            
        except Exception as e:
            logger.error(f"خطأ في فحص عمليات البوتات: {e}")
            
        return bot_processes
    
    def _get_bot_process_info(self, bot_username: str) -> Optional[BotProcess]:
        """
        الحصول على معلومات عملية بوت معين
        """
        try:
            bot_dir = f"Maded/{bot_username}"
            log_file = f"{bot_dir}/bot_{bot_username}.log"
            
            # البحث عن العملية
            pid = self._find_bot_pid(bot_username)
            
            if pid:
                try:
                    process = psutil.Process(pid)
                    
                    # التحقق من أن العملية ما زالت تعمل
                    if process.is_running():
                        cpu_usage = process.cpu_percent()
                        memory_info = process.memory_info()
                        memory_usage = memory_info.rss / 1024 / 1024  # MB
                        start_time = process.create_time()
                        
                        status = BotStatus.RUNNING
                    else:
                        cpu_usage = 0.0
                        memory_usage = 0.0
                        start_time = None
                        status = BotStatus.STOPPED
                        
                except psutil.NoSuchProcess:
                    pid = None
                    cpu_usage = 0.0
                    memory_usage = 0.0
                    start_time = None
                    status = BotStatus.STOPPED
                    
            else:
                cpu_usage = 0.0
                memory_usage = 0.0
                start_time = None
                status = BotStatus.STOPPED
            
            # محاولة قراءة معرف المالك من ملف التكوين
            owner_id = self._get_bot_owner_id(bot_username)
            
            return BotProcess(
                username=bot_username,
                pid=pid,
                status=status,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                start_time=start_time,
                log_file=log_file,
                working_directory=bot_dir,
                owner_id=owner_id or 0
            )
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات البوت {bot_username}: {e}")
            return None
    
    def _find_bot_pid(self, bot_username: str) -> Optional[int]:
        """
        البحث عن PID الخاص بالبوت
        """
        try:
            # البحث باستخدام pgrep
            result = subprocess.run(
                ["pgrep", "-f", f"Maded/{bot_username}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                # أخذ أول PID
                return int(pids[0])
                
            return None
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن PID للبوت {bot_username}: {e}")
            return None
    
    def _get_bot_owner_id(self, bot_username: str) -> Optional[int]:
        """
        الحصول على معرف مالك البوت من ملف التكوين
        """
        try:
            config_file = f"Maded/{bot_username}/config.py"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    
                # البحث عن OWNER_ID
                import re
                match = re.search(r'OWNER_ID\s*=\s*(\d+)', content)
                if match:
                    return int(match.group(1))
                    
            return None
            
        except Exception as e:
            logger.error(f"خطأ في قراءة معرف المالك للبوت {bot_username}: {e}")
            return None
    
    async def start_bot(self, bot_username: str) -> Tuple[bool, str]:
        """
        تشغيل بوت معين
        """
        try:
            bot_dir = f"Maded/{bot_username}"
            
            # التحقق من وجود المجلد
            if not os.path.exists(bot_dir):
                return False, f"مجلد البوت غير موجود: {bot_dir}"
            
            # التحقق من أن البوت غير مشغل بالفعل
            if self._find_bot_pid(bot_username):
                return False, f"البوت @{bot_username} يعمل بالفعل"
            
            # تشغيل البوت
            log_file = f"{bot_dir}/bot_{bot_username}.log"
            
            # إنشاء الأمر
            cmd = f"cd {bot_dir} && nohup python3 __main__.py > {log_file} 2>&1 &"
            
            # تنفيذ الأمر
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # انتظار قصير للتأكد من بدء العملية
            await asyncio.sleep(2)
            
            # التحقق من نجاح التشغيل
            pid = self._find_bot_pid(bot_username)
            if pid:
                logger.info(f"✅ تم تشغيل البوت @{bot_username} بنجاح (PID: {pid})")
                return True, f"تم تشغيل البوت @{bot_username} بنجاح"
            else:
                return False, f"فشل في تشغيل البوت @{bot_username}"
                
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت {bot_username}: {e}")
            return False, f"خطأ في تشغيل البوت: {e}"
    
    async def stop_bot(self, bot_username: str) -> Tuple[bool, str]:
        """
        إيقاف بوت معين
        """
        try:
            pid = self._find_bot_pid(bot_username)
            
            if not pid:
                return False, f"البوت @{bot_username} غير مشغل"
            
            # محاولة إيقاف العملية بلطف أولاً
            try:
                process = psutil.Process(pid)
                process.terminate()
                
                # انتظار حتى 10 ثوان للإيقاف اللطيف
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ تم إيقاف البوت @{bot_username} بلطف")
                    return True, f"تم إيقاف البوت @{bot_username} بنجاح"
                    
                except psutil.TimeoutExpired:
                    # إذا لم يتم الإيقاف، استخدم القوة
                    process.kill()
                    logger.info(f"✅ تم إيقاف البوت @{bot_username} بالقوة")
                    return True, f"تم إيقاف البوت @{bot_username} بالقوة"
                    
            except psutil.NoSuchProcess:
                return False, f"العملية غير موجودة للبوت @{bot_username}"
                
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت {bot_username}: {e}")
            return False, f"خطأ في إيقاف البوت: {e}"
    
    async def restart_bot(self, bot_username: str) -> Tuple[bool, str]:
        """
        إعادة تشغيل بوت معين
        """
        try:
            # إيقاف البوت أولاً
            stop_success, stop_message = await self.stop_bot(bot_username)
            
            if not stop_success and "غير مشغل" not in stop_message:
                return False, f"فشل في إيقاف البوت: {stop_message}"
            
            # انتظار قصير
            await asyncio.sleep(3)
            
            # تشغيل البوت
            start_success, start_message = await self.start_bot(bot_username)
            
            if start_success:
                return True, f"تم إعادة تشغيل البوت @{bot_username} بنجاح"
            else:
                return False, f"فشل في إعادة تشغيل البوت: {start_message}"
                
        except Exception as e:
            logger.error(f"خطأ في إعادة تشغيل البوت {bot_username}: {e}")
            return False, f"خطأ في إعادة تشغيل البوت: {e}"
    
    def get_bot_logs(self, bot_username: str, lines: int = 50) -> Optional[str]:
        """
        الحصول على سجلات البوت
        """
        try:
            log_file = f"Maded/{bot_username}/bot_{bot_username}.log"
            
            if not os.path.exists(log_file):
                return None
            
            # قراءة آخر عدد من الأسطر
            result = subprocess.run(
                ["tail", "-n", str(lines), log_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except Exception as e:
            logger.error(f"خطأ في قراءة سجلات البوت {bot_username}: {e}")
            return None
    
    def get_running_bots(self) -> List[BotProcess]:
        """
        الحصول على قائمة البوتات المشغلة
        """
        all_bots = self.scan_bot_processes()
        return [bot for bot in all_bots if bot.status == BotStatus.RUNNING]
    
    def get_stopped_bots(self) -> List[BotProcess]:
        """
        الحصول على قائمة البوتات المتوقفة
        """
        all_bots = self.scan_bot_processes()
        return [bot for bot in all_bots if bot.status == BotStatus.STOPPED]
    
    def get_bot_stats(self) -> Dict:
        """
        الحصول على إحصائيات البوتات
        """
        all_bots = self.scan_bot_processes()
        
        running_bots = [bot for bot in all_bots if bot.status == BotStatus.RUNNING]
        stopped_bots = [bot for bot in all_bots if bot.status == BotStatus.STOPPED]
        
        total_cpu = sum(bot.cpu_usage for bot in running_bots)
        total_memory = sum(bot.memory_usage for bot in running_bots)
        
        return {
            'total_bots': len(all_bots),
            'running_bots': len(running_bots),
            'stopped_bots': len(stopped_bots),
            'total_cpu_usage': total_cpu,
            'total_memory_usage': total_memory,
            'running_bot_list': [bot.username for bot in running_bots],
            'stopped_bot_list': [bot.username for bot in stopped_bots]
        }
    
    async def start_all_bots(self) -> Tuple[int, List[str]]:
        """
        تشغيل جميع البوتات المتوقفة
        """
        stopped_bots = self.get_stopped_bots()
        started_count = 0
        started_bots = []
        
        for bot in stopped_bots:
            success, message = await self.start_bot(bot.username)
            if success:
                started_count += 1
                started_bots.append(bot.username)
                # انتظار قصير بين تشغيل البوتات
                await asyncio.sleep(1)
        
        return started_count, started_bots
    
    async def stop_all_bots(self) -> Tuple[int, List[str]]:
        """
        إيقاف جميع البوتات المشغلة
        """
        running_bots = self.get_running_bots()
        stopped_count = 0
        stopped_bots = []
        
        for bot in running_bots:
            success, message = await self.stop_bot(bot.username)
            if success:
                stopped_count += 1
                stopped_bots.append(bot.username)
                # انتظار قصير بين إيقاف البوتات
                await asyncio.sleep(1)
        
        return stopped_count, stopped_bots
    
    def delete_bot(self, bot_username: str) -> Tuple[bool, str]:
        """
        حذف بوت نهائياً (إيقاف + حذف الملفات)
        """
        try:
            # إيقاف البوت أولاً
            pid = self._find_bot_pid(bot_username)
            if pid:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass
            
            # حذف مجلد البوت
            bot_dir = f"Maded/{bot_username}"
            if os.path.exists(bot_dir):
                import shutil
                shutil.rmtree(bot_dir)
                logger.info(f"✅ تم حذف البوت @{bot_username} ومجلده")
                return True, f"تم حذف البوت @{bot_username} بنجاح"
            else:
                return False, f"مجلد البوت @{bot_username} غير موجود"
                
        except Exception as e:
            logger.error(f"خطأ في حذف البوت {bot_username}: {e}")
            return False, f"خطأ في حذف البوت: {e}"
    
    async def monitor_bots(self, interval: int = 60):
        """
        مراقبة البوتات بشكل دوري
        """
        self.monitoring_active = True
        logger.info("🔍 بدء مراقبة البوتات...")
        
        while self.monitoring_active:
            try:
                # فحص جميع البوتات
                all_bots = self.scan_bot_processes()
                
                # تحديث قائمة البوتات المراقبة
                for bot in all_bots:
                    self.monitored_bots[bot.username] = bot
                
                # طباعة إحصائيات
                stats = self.get_bot_stats()
                logger.info(f"📊 إحصائيات البوتات: {stats['running_bots']} مشغل، {stats['stopped_bots']} متوقف")
                
                # انتظار الفترة المحددة
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"خطأ في مراقبة البوتات: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """
        إيقاف مراقبة البوتات
        """
        self.monitoring_active = False
        logger.info("🔴 تم إيقاف مراقبة البوتات")

# إنشاء مثيل مدير العمليات
process_manager = ProcessManager()