#!/usr/bin/env python3
"""
Bot Entry Point - نقطة دخول البوت
ملف بديل لـ main.py لتشغيل البوت
"""

import asyncio
import sys
from pathlib import Path

# إضافة المجلد الحالي إلى مسار Python
sys.path.append(str(Path(__file__).parent))

# استيراد الدالة الرئيسية من main.py
from main import main

if __name__ == "__main__":
    try:
        # تشغيل البوت
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
    