#!/usr/bin/env python3
"""
Simple Start Script - سكريبت بدء بسيط
ملف بدء سريع وبسيط لتشغيل البوت
"""

import sys
import os

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """الدالة الرئيسية البسيطة"""
    try:
        print("🚀 بدء تشغيل مصنع البوتات...")
        print("📦 تحميل الوحدات...")
        
        # استيراد الدالة الرئيسية
        from main import main as run_bot
        
        print("✅ تم تحميل جميع الوحدات بنجاح")
        print("🤖 بدء تشغيل البوت...")
        
        # تشغيل البوت
        import asyncio
        asyncio.run(run_bot())
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت بواسطة المستخدم")
    except ImportError as e:
        print(f"❌ خطأ في استيراد الوحدات: {e}")
        print("🔧 تأكد من تثبيت جميع المتطلبات:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()