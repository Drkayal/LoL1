#!/usr/bin/env python3
"""
اختبار واجهة المستخدم المحسنة
"""

import sys
import os
sys.path.append('Maker')

def test_ui_manager():
    """اختبار مدير واجهة المستخدم"""
    print("🔍 اختبار واجهة المستخدم...")
    
    try:
        # محاولة استيراد الوحدات
        print("1. اختبار الاستيرادات...")
        
        # اختبار استيراد ui_manager (بدون pyrogram)
        import importlib.util
        spec = importlib.util.spec_from_file_location("ui_manager", "Maker/core/ui_manager.py")
        
        if spec is None:
            print("❌ فشل في العثور على ملف ui_manager.py")
            return False
            
        print("✅ تم العثور على ملف ui_manager.py")
        
        # اختبار الهيكل الأساسي
        print("2. اختبار الهيكل الأساسي...")
        
        with open("Maker/core/ui_manager.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        # فحص وجود الكلاسات والدوال المهمة
        required_items = [
            "class UIManager",
            "def create_main_keyboard",
            "def format_welcome_message",
            "def format_stats_message",
            "def format_error_message",
            "ui_manager = UIManager()"
        ]
        
        for item in required_items:
            if item in content:
                print(f"✅ {item}")
            else:
                print(f"❌ مفقود: {item}")
                return False
        
        # فحص الرموز
        print("3. اختبار الرموز...")
        if "'success': '✅'" in content:
            print("✅ الرموز موجودة")
        else:
            print("❌ الرموز مفقودة")
            return False
        
        # فحص القوالب
        print("4. اختبار القوالب...")
        if "'header': \"━━━━━━━━━━━━━━━━━━━━━━\"" in content:
            print("✅ القوالب موجودة")
        else:
            print("❌ القوالب مفقودة")
            return False
        
        # فحص الأوامر
        print("5. اختبار الأوامر...")
        if "❲ صنع بوت ❳" in content:
            print("✅ الأوامر بالتنسيق الصحيح")
        else:
            print("❌ الأوامر بتنسيق خاطئ")
            return False
        
        print("✅ جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_integration():
    """اختبار التكامل مع الملف الرئيسي"""
    print("\n🔗 اختبار التكامل...")
    
    try:
        with open("Maker/Makr.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # فحص الاستيرادات
        if "from core.ui_manager import ui_manager" in content:
            print("✅ استيراد ui_manager موجود")
        else:
            print("❌ استيراد ui_manager مفقود")
            return False
        
        # فحص الاستخدام
        if "ui_manager.format_welcome_message" in content:
            print("✅ استخدام ui_manager موجود")
        else:
            print("❌ استخدام ui_manager مفقود")
            return False
        
        # فحص أمر التنبيهات
        if "❲ التنبيهات ❳" in content:
            print("✅ أمر التنبيهات موجود")
        else:
            print("❌ أمر التنبيهات مفقود")
            return False
        
        print("✅ التكامل سليم!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار التكامل: {e}")
        return False

if __name__ == "__main__":
    print("🧪 بدء اختبار واجهة المستخدم المحسنة\n")
    
    ui_test = test_ui_manager()
    integration_test = test_integration()
    
    print(f"\n📊 النتائج:")
    print(f"   واجهة المستخدم: {'✅ نجح' if ui_test else '❌ فشل'}")
    print(f"   التكامل: {'✅ نجح' if integration_test else '❌ فشل'}")
    
    if ui_test and integration_test:
        print("\n🎉 جميع الاختبارات نجحت! واجهة المستخدم جاهزة للاستخدام.")
        sys.exit(0)
    else:
        print("\n⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
        sys.exit(1)
