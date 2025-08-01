#!/usr/bin/env python3
"""
Main Entry Point - نقطة الدخول الرئيسية
مصنع البوتات - Bot Factory Maker
"""

import asyncio
import sys
import os
from pathlib import Path

# إضافة المجلد الحالي إلى مسار Python
sys.path.append(str(Path(__file__).parent))

# استيراد الإعدادات الأساسية
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, OWNER_NAME
from OWNER import DATABASE, CHANNEL, GROUP, PHOTO, VIDEO, LOGS

# استيراد Pyrogram
from pyrogram import Client, idle

# استيراد الأدوات المساعدة
from utils import logger

# استيراد مدير قاعدة البيانات
from db import db_manager, initialize_db_manager

# استيراد دوال المصنع
from bots import initialize_factory

# استيراد دوال المستخدمين
from users import set_dependencies as set_users_dependencies

# استيراد دوال قاعدة البيانات
from db import set_collections as set_db_collections

# استيراد دوال البوتات
from bots import set_collections as set_bots_collections

# استيراد دوال البث
from broadcast import set_collections as set_broadcast_collections

# استيراد دوال المصنع
from factory import set_collections as set_factory_collections

# استيراد معالجات الأوامر
from handlers.commands import set_dependencies as set_commands_dependencies
from handlers.broadcast import set_dependencies as set_broadcast_dependencies

# استيراد دالة التنظيف
from Maker.Makr import cleanup_database_connections

# تسجيل دالة التنظيف عند إنهاء البرنامج
import atexit
atexit.register(cleanup_database_connections)

class BotFactory:
    """فئة مصنع البوتات الرئيسية"""
    
    def __init__(self):
        """تهيئة مصنع البوتات"""
        self.bot = None
        self.bot_id = None
        self.is_running = False
        
        # تهيئة قاعدة البيانات
        self.db = None
        self.mongodb = None
        
        # تهيئة المجموعات
        self.users = None
        self.chats = None
        self.mkchats = None
        self.blocked = []
        self.blockeddb = None
        self.broadcasts_collection = None
        self.devs_collection = None
        self.bots_collection = None
        self.factory_settings = None
        
        # حالة المصنع
        self.off = True
        self.mk = []  # قائمة المحادثات
        
        logger.info("Bot Factory initialized successfully")
    
    async def setup_database(self):
        """إعداد قاعدة البيانات والمجموعات"""
        try:
            # تهيئة مدير قاعدة البيانات
            self.db_manager = initialize_db_manager()
            
            # الحصول على اتصالات قاعدة البيانات
            self.db = self.db_manager.get_sync_db()
            self.mongodb = self.db_manager.get_async_db()
            
            # تهيئة المجموعات
            self.users = self.mongodb.tgusersdb
            self.chats = self.mongodb.chats
            self.mkchats = self.db.chatss
            self.blockeddb = self.db.blocked
            self.broadcasts_collection = self.db["broadcasts"]
            self.devs_collection = self.db["devs"]
            self.bots_collection = self.db["bots"]
            self.factory_settings = self.db["factory_settings"]
            
            logger.info("Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def setup_dependencies(self):
        """إعداد التبعيات لجميع الوحدات"""
        try:
            # تعيين التبعيات لمجلد users
            set_users_dependencies(OWNER_ID, self.devs_collection, self.users)
            
            # تعيين المجموعات لمجلد db
            set_db_collections(self.broadcasts_collection, self.bots_collection, self.factory_settings)
            
            # تعيين المجموعات لمجلد bots
            set_bots_collections(self.bots_collection, self.factory_settings)
            
            # تعيين المجموعات لمجلد broadcast
            set_broadcast_collections(self.broadcasts_collection)
            
            # تعيين المجموعات لمجلد factory
            set_factory_collections(self.factory_settings)
            
            # تعيين التبعيات لمعالجات الأوامر
            set_commands_dependencies(OWNER_ID, self.bots_collection)
            set_broadcast_dependencies(self.bots_collection)
            
            logger.info("Dependencies setup completed successfully")
            
        except Exception as e:
            logger.error(f"Dependencies setup failed: {str(e)}")
            raise
    
    async def create_bot(self):
        """إنشاء وتكوين البوت"""
        try:
            # إنشاء البوت مع الإعدادات المطلوبة
            self.bot = Client(
                "bot_maker",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                plugins=dict(root="Maker"),
                in_memory=True
            )
            
            logger.info("Bot client created successfully")
            
        except Exception as e:
            logger.error(f"Bot creation failed: {str(e)}")
            raise
    
    async def start_bot(self):
        """تشغيل البوت"""
        try:
            await self.bot.start()
            me = await self.bot.get_me()
            self.bot_id = me.id
            self.is_running = True
            
            logger.info(f"✅ Bot started successfully: {me.first_name} (@{me.username})")
            logger.info(f"🆔 Bot ID: {me.id}")
            
            # طباعة معلومات البوت
            print("=" * 60)
            print(f"🎯 Bot Factory Started Successfully!")
            print(f"🤖 Bot Name: {me.first_name}")
            print(f"👤 Bot Username: @{me.username}")
            print(f"🆔 Bot ID: {me.id}")
            print(f"👨‍💻 Owner: {OWNER_NAME}")
            print(f"🔧 Factory Status: {'🟢 Running' if not self.off else '🔴 Stopped'}")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"Bot startup failed: {str(e)}")
            raise
    
    async def initialize_factory(self):
        """تهيئة المصنع واستعادة البوتات"""
        try:
            logger.info("Initializing factory...")
            await initialize_factory()
            logger.info("Factory initialization completed")
            
        except Exception as e:
            logger.error(f"Factory initialization failed: {str(e)}")
            # لا نريد إيقاف البرنامج إذا فشلت تهيئة المصنع
            pass
    
    async def run(self):
        """تشغيل مصنع البوتات"""
        try:
            logger.info("Starting Bot Factory...")
            
            # إعداد قاعدة البيانات
            await self.setup_database()
            
            # إعداد التبعيات
            self.setup_dependencies()
            
            # إنشاء البوت
            await self.create_bot()
            
            # تشغيل البوت
            await self.start_bot()
            
            # تهيئة المصنع
            await self.initialize_factory()
            
            logger.info("Bot Factory is ready and running!")
            
            # انتظار حتى إيقاف البوت
            await idle()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Bot Factory runtime error: {str(e)}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """تنظيف الموارد عند الإغلاق"""
        try:
            if self.bot and self.is_running:
                await self.bot.stop()
                self.is_running = False
                logger.info("Bot stopped successfully")
            
            logger.info("Bot Factory shutdown completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

async def main():
    """الدالة الرئيسية"""
    factory = BotFactory()
    await factory.run()

if __name__ == "__main__":
    try:
        # تشغيل البوت
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot Factory stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)




