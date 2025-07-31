import subprocess
import shlex
import os
import logging

logger = logging.getLogger(__name__)

class SecureProcessManager:
    @staticmethod
    def safe_execute(command, cwd=None, timeout=30):
        try:
            if isinstance(command, str):
                cmd_list = shlex.split(command)
            else:
                cmd_list = command
            
            result = subprocess.run(
                cmd_list,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=False
            )
            
            return result.returncode, result.stdout or "", result.stderr or ""
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر: {e}")
            return -1, "", str(e)

    @staticmethod
    def safe_copy_files(source, destination):
        try:
            if os.path.isdir(source):
                cmd = ["cp", "-r", source, destination]
            else:
                cmd = ["cp", source, destination]
            
            return_code, stdout, stderr = SecureProcessManager.safe_execute(cmd)
            return return_code == 0
                
        except Exception as e:
            logger.error(f"خطأ في نسخ الملفات: {e}")
            return False

    @staticmethod
    def safe_remove_directory(path):
        try:
            cmd = ["rm", "-rf", path]
            return_code, stdout, stderr = SecureProcessManager.safe_execute(cmd)
            return return_code == 0
                
        except Exception as e:
            logger.error(f"خطأ في حذف المجلد: {e}")
            return False

    @staticmethod
    def safe_kill_process(process_name):
        try:
            cmd = ["pkill", "-f", process_name]
            return_code, stdout, stderr = SecureProcessManager.safe_execute(cmd)
            return return_code == 0
                
        except Exception as e:
            logger.error(f"خطأ في إيقاف العملية: {e}")
            return False

safe_execute = SecureProcessManager.safe_execute
safe_copy = SecureProcessManager.safe_copy_files
safe_remove = SecureProcessManager.safe_remove_directory
safe_kill = SecureProcessManager.safe_kill_process
