#!/usr/bin/env python3
"""
سكريبت إدارة البوتات في Docker
Script for managing bots in Docker containers
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_command(command, capture_output=True, check=True):
    """تشغيل أمر في النظام"""
    try:
        result = subprocess.run(command, capture_output=capture_output, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تنفيذ الأمر: {e}")
        return None

def check_docker():
    """التحقق من وجود Docker"""
    result = run_command(["docker", "--version"], check=False)
    if result and result.returncode == 0:
        print("✅ Docker متاح")
        return True
    else:
        print("❌ Docker غير متاح")
        return False

def get_bot_directories():
    """الحصول على قائمة مجلدات البوتات"""
    maked_dir = Path("Maked")
    if not maked_dir.exists():
        print("❌ مجلد Maked غير موجود")
        return []
    
    bot_dirs = [d for d in maked_dir.iterdir() if d.is_dir()]
    return bot_dirs

def build_bot_image(bot_dir):
    """بناء صورة Docker للبوت"""
    bot_name = bot_dir.name
    print(f"🔨 جاري بناء صورة البوت: {bot_name}")
    
    dockerfile = bot_dir / "Dockerfile"
    if not dockerfile.exists():
        print(f"❌ Dockerfile غير موجود في {bot_name}")
        return None
    
    result = run_command(["docker", "build", "-t", f"bot-{bot_name}", "."], cwd=bot_dir)
    if result:
        print(f"✅ تم بناء صورة البوت: {bot_name}")
        return f"bot-{bot_name}"
    else:
        print(f"❌ فشل في بناء صورة البوت: {bot_name}")
        return None

def start_bot_container(bot_name, image_name):
    """تشغيل حاوية البوت"""
    container_name = f"bot-{bot_name}-{int(time.time())}"
    
    print(f"🚀 جاري تشغيل حاوية البوت: {bot_name}")
    
    result = run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "--restart", "unless-stopped",
        "--network", "host",
        "-e", f"BOT_USERNAME={bot_name}",
        "-e", f"BOT_WORKING_DIR=/app",
        image_name
    ])
    
    if result:
        container_id = result.stdout.strip()
        print(f"✅ تم تشغيل حاوية البوت: {bot_name} (ID: {container_id[:12]}...)")
        return container_id
    else:
        print(f"❌ فشل في تشغيل حاوية البوت: {bot_name}")
        return None

def stop_bot_container(container_id):
    """إيقاف حاوية البوت"""
    print(f"🛑 جاري إيقاف الحاوية: {container_id[:12]}...")
    
    # إيقاف الحاوية
    stop_result = run_command(["docker", "stop", container_id], check=False)
    if stop_result and stop_result.returncode == 0:
        print(f"✅ تم إيقاف الحاوية: {container_id[:12]}...")
        
        # حذف الحاوية
        rm_result = run_command(["docker", "rm", container_id], check=False)
        if rm_result and rm_result.returncode == 0:
            print(f"✅ تم حذف الحاوية: {container_id[:12]}...")
            return True
        else:
            print(f"⚠️ تم إيقاف الحاوية لكن فشل في حذفها: {container_id[:12]}...")
            return True
    else:
        print(f"❌ فشل في إيقاف الحاوية: {container_id[:12]}...")
        return False

def list_running_containers():
    """عرض الحاويات المشتغلة"""
    result = run_command(["docker", "ps", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])
    if result:
        print("🐳 الحاويات المشتغلة:")
        print(result.stdout)
    else:
        print("❌ فشل في الحصول على قائمة الحاويات")

def list_all_containers():
    """عرض جميع الحاويات"""
    result = run_command(["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])
    if result:
        print("🐳 جميع الحاويات:")
        print(result.stdout)
    else:
        print("❌ فشل في الحصول على قائمة الحاويات")

def clean_stopped_containers():
    """تنظيف الحاويات المتوقفة"""
    print("🧹 جاري تنظيف الحاويات المتوقفة...")
    
    result = run_command(["docker", "container", "prune", "-f"])
    if result:
        print("✅ تم تنظيف الحاويات المتوقفة")
    else:
        print("❌ فشل في تنظيف الحاويات المتوقفة")

def clean_unused_images():
    """تنظيف الصور غير المستخدمة"""
    print("🧹 جاري تنظيف الصور غير المستخدمة...")
    
    result = run_command(["docker", "image", "prune", "-f"])
    if result:
        print("✅ تم تنظيف الصور غير المستخدمة")
    else:
        print("❌ فشل في تنظيف الصور غير المستخدمة")

def show_bot_logs(container_id, lines=50):
    """عرض سجلات البوت"""
    print(f"📋 سجلات البوت: {container_id[:12]}...")
    
    result = run_command(["docker", "logs", "--tail", str(lines), container_id])
    if result:
        print(result.stdout)
    else:
        print("❌ فشل في الحصول على السجلات")

def main():
    """الدالة الرئيسية"""
    if not check_docker():
        return
    
    if len(sys.argv) < 2:
        print("""
🔧 سكريبت إدارة البوتات في Docker

الاستخدام:
  python scripts/manage_bots.py <command> [options]

الأوامر المتاحة:
  build-all          - بناء صور جميع البوتات
  start-all          - تشغيل جميع البوتات
  stop-all           - إيقاف جميع البوتات
  list               - عرض الحاويات المشتغلة
  list-all           - عرض جميع الحاويات
  clean              - تنظيف الحاويات والصور غير المستخدمة
  logs <container>   - عرض سجلات حاوية معينة
  build <bot_name>   - بناء صورة بوت محدد
  start <bot_name>   - تشغيل بوت محدد
  stop <container>   - إيقاف حاوية محددة

أمثلة:
  python scripts/manage_bots.py build-all
  python scripts/manage_bots.py start-all
  python scripts/manage_bots.py logs abc123def456
        """)
        return
    
    command = sys.argv[1]
    
    if command == "build-all":
        bot_dirs = get_bot_directories()
        for bot_dir in bot_dirs:
            build_bot_image(bot_dir)
    
    elif command == "start-all":
        bot_dirs = get_bot_directories()
        for bot_dir in bot_dirs:
            image_name = f"bot-{bot_dir.name}"
            start_bot_container(bot_dir.name, image_name)
    
    elif command == "stop-all":
        result = run_command(["docker", "ps", "-q", "--filter", "name=bot-"])
        if result and result.stdout.strip():
            container_ids = result.stdout.strip().split('\n')
            for container_id in container_ids:
                stop_bot_container(container_id)
        else:
            print("ℹ️ لا توجد بوتات مشتغلة")
    
    elif command == "list":
        list_running_containers()
    
    elif command == "list-all":
        list_all_containers()
    
    elif command == "clean":
        clean_stopped_containers()
        clean_unused_images()
    
    elif command == "logs" and len(sys.argv) > 2:
        container_id = sys.argv[2]
        show_bot_logs(container_id)
    
    elif command == "build" and len(sys.argv) > 2:
        bot_name = sys.argv[2]
        bot_dir = Path("Maked") / bot_name
        if bot_dir.exists():
            build_bot_image(bot_dir)
        else:
            print(f"❌ البوت {bot_name} غير موجود")
    
    elif command == "start" and len(sys.argv) > 2:
        bot_name = sys.argv[2]
        image_name = f"bot-{bot_name}"
        start_bot_container(bot_name, image_name)
    
    elif command == "stop" and len(sys.argv) > 2:
        container_id = sys.argv[2]
        stop_bot_container(container_id)
    
    else:
        print("❌ أمر غير صحيح. استخدم --help للعرض المساعدة")

if __name__ == "__main__":
    main()