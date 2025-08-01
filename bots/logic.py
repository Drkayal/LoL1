"""
Bot Logic Functions - دوال عمليات البوتات
يحتوي على دوال تشغيل وإيقاف البوتات وتهيئة المصنع
"""

import os
import time
import subprocess
import asyncio
from os import path
from utils import (
    logger, 
    ValidationError, 
    temp_file_manager,
    rate_limit_manager
)
from users import validate_bot_username
from .models import get_factory_state, get_running_bots, update_bot_status

def start_bot_process(bot_username, max_retries=3):
    """
    تشغيل عملية البوت مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        int: معرف العملية (PID) أو None إذا فشل التشغيل
    """
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return None
        
        bot_path = path.join("Maked", validated_username)
        main_file = path.join(bot_path, "__main__.py")
        
        if not path.exists(main_file):
            logger.error(f"Main file not found for bot: {validated_username}")
            return None
        
        # التحقق من وجود البيئة الافتراضية
        venv_python = path.join("/workspace/venv/bin/python")
        if not path.exists(venv_python):
            logger.error(f"Virtual environment not found at: {venv_python}")
            return None
        
        # إنشاء ملف مؤقت لتسجيل الأخطاء
        log_file = temp_file_manager.create_temp_file(suffix=".log", prefix=f"bot_{validated_username}_")
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                process = subprocess.Popen(
                    [venv_python, main_file],
                    cwd=bot_path,
                    stdout=open(log_file, 'w'),
                    stderr=subprocess.STDOUT,
                    text=True,
                    env={
                        **os.environ,
                        "PYTHONPATH": f"{bot_path}:{os.environ.get('PYTHONPATH', '')}"
                    }
                )
                
                # انتظار قليل للتأكد من بدء العملية
                time.sleep(2)
                
                # التحقق من أن العملية لا تزال تعمل
                if process.poll() is None:
                    logger.info(f"Started bot {validated_username} with PID: {process.pid}")
                    return process.pid
                else:
                    # قراءة الأخطاء إذا فشل التشغيل
                    try:
                        with open(log_file, 'r') as f:
                            error_log = f.read()
                        logger.error(f"Bot {validated_username} failed to start. Log: {error_log}")
                    except:
                        logger.error(f"Bot {validated_username} failed to start")
                    
                    if attempt == max_retries - 1:
                        # تنظيف الملف المؤقت
                        temp_file_manager.cleanup_temp_file(log_file)
                        return None
                    time.sleep(2)  # انتظار قبل إعادة المحاولة
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to start bot {validated_username}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to start bot {validated_username} after {max_retries} attempts")
                    # تنظيف الملف المؤقت
                    temp_file_manager.cleanup_temp_file(log_file)
                    return None
                time.sleep(2)
        
        # تنظيف الملف المؤقت
        temp_file_manager.cleanup_temp_file(log_file)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in start_bot_process: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in start_bot_process function: {str(e)}")
        return None

def stop_bot_process(pid, max_retries=3):
    """
    إيقاف عملية البوت مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة
    
    Args:
        pid: معرف العملية
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الإيقاف بنجاح، False خلاف ذلك
    """
    try:
        if not pid or not isinstance(pid, int) or pid <= 0:
            logger.error(f"Invalid PID: {pid}")
            return False
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                # استخدام psutil لإيقاف العملية
                import psutil
                process = psutil.Process(pid)
                process.terminate()
                
                # انتظار قليل للتأكد من إيقاف العملية
                time.sleep(1)
                
                if process.poll() is None:
                    # إذا لم تتوقف العملية، قم بإجبارها على التوقف
                    process.kill()
                    time.sleep(1)
                
                logger.info(f"Stopped process with PID: {pid}")
                return True
                
            except psutil.NoSuchProcess:
                logger.warning(f"Process with PID {pid} not found")
                return True  # العملية غير موجودة تعني أنها متوقفة بالفعل
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to stop process {pid}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to stop process {pid} after {max_retries} attempts")
                    return False
                time.sleep(1)
        return False
    except Exception as e:
        logger.error(f"Error in stop_bot_process function: {str(e)}")
        return False

async def initialize_factory(max_retries=3):
    """
    تهيئة المصنع مع التحقق من المدخلات والتخزين المؤقت وإعادة المحاولة
    
    Args:
        max_retries: عدد المحاولات الأقصى
    """
    try:
        # انتظار لتجنب الحظر
        await rate_limit_manager.async_wait_if_needed('database')
        
        # تهيئة حالة المصنع
        for attempt in range(max_retries):
            try:
                factory_state = get_factory_state()
                logger.info(f"Factory state initialized: {factory_state}")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get factory state: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Failed to initialize factory state, using default")
                await asyncio.sleep(1)
        
        # استعادة البوتات المشتغلة
        for attempt in range(max_retries):
            try:
                running_bots = get_running_bots()
                logger.info(f"Found {len(running_bots)} bots to restore")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to get running bots: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Failed to get running bots, skipping restoration")
                    return
                await asyncio.sleep(1)
        
        # محاولة إعادة تشغيل البوتات المشتغلة
        restored_count = 0
        failed_count = 0
        
        for bot in running_bots:
            if bot.get("status") == "running":
                bot_username = bot.get("username")
                if not bot_username:
                    logger.warning("Bot without username found, skipping")
                    continue
                
                logger.info(f"Attempting to restore bot: {bot_username}")
                
                # محاولة تشغيل البوت
                pid = start_bot_process(bot_username)
                if pid:
                    # تحديث PID في قاعدة البيانات
                    try:
                        from .models import bots_collection
                        bots_collection.update_one(
                            {"username": bot_username},
                            {"$set": {"pid": pid}}
                        )
                        restored_count += 1
                        logger.info(f"Successfully restored bot: {bot_username}")
                    except Exception as e:
                        logger.error(f"Failed to update PID for bot {bot_username}: {str(e)}")
                        failed_count += 1
                else:
                    # تحديث حالة البوت إلى متوقف
                    update_bot_status(bot_username, "stopped")
                    failed_count += 1
                    logger.warning(f"Failed to restore bot: {bot_username}")
                
                # تأخير بين البوتات لتجنب الحظر
                await asyncio.sleep(1)
        
        logger.info(f"Factory initialization completed. Restored: {restored_count}, Failed: {failed_count}")
        
    except Exception as e:
        logger.error(f"Error in initialize_factory function: {str(e)}")