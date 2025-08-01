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
    تشغيل عملية البوت في حاوية Docker مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة
    
    Args:
        bot_username: معرف البوت
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        str: معرف الحاوية (Container ID) أو None إذا فشل التشغيل
    """
    try:
        is_valid, validated_username = validate_bot_username(bot_username)
        if not is_valid:
            logger.error(f"Invalid bot username: {bot_username}")
            return None
        
        bot_path = path.join("Maked", validated_username)
        dockerfile_path = path.join(bot_path, "Dockerfile")
        
        if not path.exists(dockerfile_path):
            logger.error(f"Dockerfile not found for bot: {validated_username}")
            return None
        
        # التحقق من وجود ملفات البوت الأساسية
        config_file = path.join(bot_path, "config.py")
        owner_file = path.join(bot_path, "OWNER.py")
        requirements_file = path.join(bot_path, "requirements.txt")
        
        if not path.exists(config_file):
            logger.error(f"Config file not found for bot: {validated_username}")
            return None
        
        if not path.exists(owner_file):
            logger.error(f"Owner file not found for bot: {validated_username}")
            return None
        
        if not path.exists(requirements_file):
            logger.error(f"Requirements file not found for bot: {validated_username}")
            return None
        
        # التحقق من وجود Docker
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error(f"Docker not found in system")
            return None
        
        # إنشاء اسم فريد للحاوية
        container_name = f"bot_{validated_username}_{int(time.time())}"
        image_name = f"bot_{validated_username}"
        
        # إنشاء ملف مؤقت لتسجيل الأخطاء
        log_file = temp_file_manager.create_temp_file(suffix=".log", prefix=f"docker_{validated_username}_")
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                logger.info(f"Building Docker image for bot: {validated_username}")
                
                # بناء صورة Docker للبوت
                build_process = subprocess.run(
                    ["docker", "build", "-t", image_name, "."],
                    cwd=bot_path,
                    stdout=open(log_file, 'w'),
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                if build_process.returncode != 0:
                    # قراءة الأخطاء إذا فشل البناء
                    try:
                        with open(log_file, 'r') as f:
                            error_log = f.read()
                        logger.error(f"Failed to build Docker image for bot {validated_username}. Log: {error_log}")
                    except:
                        logger.error(f"Failed to build Docker image for bot {validated_username}")
                    
                    if attempt == max_retries - 1:
                        temp_file_manager.cleanup_temp_file(log_file)
                        return None
                    time.sleep(2)
                    continue
                
                logger.info(f"Starting Docker container for bot: {validated_username}")
                
                # تشغيل حاوية Docker للبوت
                run_process = subprocess.run(
                    [
                        "docker", "run", 
                        "-d",  # تشغيل في الخلفية
                        "--name", container_name,
                        "--restart", "unless-stopped",  # إعادة التشغيل التلقائي
                        "--network", "host",  # استخدام شبكة المضيف للوصول للإنترنت
                        "-e", f"BOT_USERNAME={validated_username}",
                        "-e", f"BOT_WORKING_DIR={bot_path}",
                        image_name
                    ],
                    capture_output=True,
                    text=True
                )
                
                if run_process.returncode == 0:
                    container_id = run_process.stdout.strip()
                    logger.info(f"Started bot {validated_username} in Docker container: {container_id}")
                    
                    # التحقق من أن الحاوية تعمل
                    time.sleep(3)
                    check_process = subprocess.run(
                        ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Status}}"],
                        capture_output=True,
                        text=True
                    )
                    
                    if "Up" in check_process.stdout:
                        logger.info(f"Bot {validated_username} is running successfully in Docker")
                        temp_file_manager.cleanup_temp_file(log_file)
                        return container_id
                    else:
                        logger.warning(f"Container {container_id} is not running properly")
                        # حذف الحاوية الفاشلة
                        subprocess.run(["docker", "rm", "-f", container_id], 
                                     capture_output=True)
                        
                        if attempt == max_retries - 1:
                            temp_file_manager.cleanup_temp_file(log_file)
                            return None
                        time.sleep(2)
                else:
                    logger.error(f"Failed to start Docker container for bot {validated_username}: {run_process.stderr}")
                    
                    if attempt == max_retries - 1:
                        temp_file_manager.cleanup_temp_file(log_file)
                        return None
                    time.sleep(2)
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to start bot {validated_username} in Docker: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to start bot {validated_username} in Docker after {max_retries} attempts")
                    temp_file_manager.cleanup_temp_file(log_file)
                    return None
                time.sleep(2)
        
        temp_file_manager.cleanup_temp_file(log_file)
        return None
    except ValidationError as e:
        logger.error(f"Validation error in start_bot_process: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in start_bot_process function: {str(e)}")
        return None

def stop_bot_process(container_id, max_retries=3):
    """
    إيقاف حاوية Docker للبوت مع التحقق من المدخلات وإدارة الملفات المؤقتة وإعادة المحاولة
    
    Args:
        container_id: معرف الحاوية
        max_retries: عدد المحاولات الأقصى
        
    Returns:
        bool: True إذا تم الإيقاف بنجاح، False خلاف ذلك
    """
    try:
        if not container_id or not isinstance(container_id, str):
            logger.error(f"Invalid container ID: {container_id}")
            return False
        
        for attempt in range(max_retries):
            try:
                # انتظار لتجنب الحظر
                time.sleep(0.5)  # تأخير بين المحاولات
                
                # إيقاف الحاوية
                stop_process = subprocess.run(
                    ["docker", "stop", container_id],
                    capture_output=True,
                    text=True
                )
                
                if stop_process.returncode == 0:
                    logger.info(f"Stopped Docker container: {container_id}")
                    
                    # حذف الحاوية
                    rm_process = subprocess.run(
                        ["docker", "rm", container_id],
                        capture_output=True,
                        text=True
                    )
                    
                    if rm_process.returncode == 0:
                        logger.info(f"Removed Docker container: {container_id}")
                    else:
                        logger.warning(f"Failed to remove container {container_id}: {rm_process.stderr}")
                    
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1} failed to stop container {container_id}: {stop_process.stderr}")
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to stop container {container_id} after {max_retries} attempts")
                        return False
                    time.sleep(1)
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to stop container {container_id}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to stop container {container_id} after {max_retries} attempts")
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
                
                # محاولة تشغيل البوت في Docker
                container_id = start_bot_process(bot_username)
                if container_id:
                    # تحديث معرف الحاوية في قاعدة البيانات
                    try:
                        from .models import bots_collection
                        bots_collection.update_one(
                            {"username": bot_username},
                            {"$set": {"container_id": container_id}}
                        )
                        restored_count += 1
                        logger.info(f"Successfully restored bot: {bot_username}")
                    except Exception as e:
                        logger.error(f"Failed to update container ID for bot {bot_username}: {str(e)}")
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