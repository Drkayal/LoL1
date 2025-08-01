#!/bin/bash

# Bot Factory Maker - Startup Script
# سكريبت تشغيل مصنع البوتات

echo "🚀 بدء تشغيل مصنع البوتات..."

# التحقق من وجود الملفات المطلوبة
if [ ! -f "main.py" ]; then
    echo "❌ ملف main.py غير موجود!"
    exit 1
fi

if [ ! -f "config.py" ]; then
    echo "❌ ملف config.py غير موجود!"
    exit 1
fi

# إنشاء المجلدات المطلوبة
mkdir -p Maked logs temp cache

# تشغيل البوت
echo "✅ تشغيل البوت..."
python3 main.py