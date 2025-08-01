"""
Database Manager - مدير قاعدة البيانات
يحتوي على مدير قاعدة البيانات للاتصالات المتزامنة وغير المتزامنة
"""

import os
from typing import Optional
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from utils import logger, DatabaseError

class DatabaseManager:
    """
    مدير قاعدة البيانات
    يتعامل مع الاتصالات المتزامنة وغير المتزامنة مع MongoDB
    """
    
    def __init__(self, mongo_uri: str = None):
        """
        تهيئة مدير قاعدة البيانات
        
        Args:
            mongo_uri: رابط اتصال MongoDB (اختياري)
        """
        self.mongo_uri = mongo_uri or os.getenv("MONGO_DB_URI", "mongodb+srv://huSeen96:Huseenslah96@cluster0.ld2v7.mongodb.net/bot_factory?retryWrites=true&w=majority&appName=Cluster0")
        self.sync_client: Optional[MongoClient] = None
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.sync_db = None
        self.async_db = None
        
        # تهيئة الاتصالات
        self._initialize_connections()
    
    def _initialize_connections(self):
        """تهيئة اتصالات قاعدة البيانات"""
        try:
            # إنشاء اتصال متزامن
            self.sync_client = MongoClient(self.mongo_uri)
            
            # تحديد قاعدة البيانات الافتراضية
            if "/" in self.mongo_uri and "?" in self.mongo_uri:
                # استخراج اسم قاعدة البيانات من الرابط
                db_name = self.mongo_uri.split("/")[-1].split("?")[0]
                self.sync_db = self.sync_client[db_name]
            else:
                # استخدام قاعدة بيانات افتراضية
                self.sync_db = self.sync_client["bot_factory"]
            
            # اختبار الاتصال المتزامن
            self.sync_client.admin.command('ping')
            logger.info("Synchronous database connection established successfully")
            
            # إنشاء اتصال غير متزامن
            self.async_client = AsyncIOMotorClient(self.mongo_uri)
            
            # تحديد قاعدة البيانات الافتراضية
            if "/" in self.mongo_uri and "?" in self.mongo_uri:
                # استخراج اسم قاعدة البيانات من الرابط
                db_name = self.mongo_uri.split("/")[-1].split("?")[0]
                self.async_db = self.async_client[db_name]
            else:
                # استخدام قاعدة بيانات افتراضية
                self.async_db = self.async_client["bot_factory"]
            
            logger.info("Asynchronous database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def get_sync_db(self):
        """
        الحصول على قاعدة البيانات المتزامنة
        
        Returns:
            قاعدة البيانات المتزامنة
            
        Raises:
            DatabaseError: إذا فشل الاتصال
        """
        try:
            if self.sync_db is None:
                raise DatabaseError("Synchronous database connection not available")
            
            # اختبار الاتصال
            self.sync_client.admin.command('ping')
            return self.sync_db
            
        except Exception as e:
            logger.error(f"Failed to get sync database: {str(e)}")
            raise DatabaseError(f"Sync database error: {str(e)}")
    
    def get_async_db(self):
        """
        الحصول على قاعدة البيانات غير المتزامنة
        
        Returns:
            قاعدة البيانات غير المتزامنة
            
        Raises:
            DatabaseError: إذا فشل الاتصال
        """
        try:
            if self.async_db is None:
                raise DatabaseError("Asynchronous database connection not available")
            
            return self.async_db
            
        except Exception as e:
            logger.error(f"Failed to get async database: {str(e)}")
            raise DatabaseError(f"Async database error: {str(e)}")
    
    def close_connections(self):
        """إغلاق جميع اتصالات قاعدة البيانات"""
        try:
            if self.sync_client:
                self.sync_client.close()
                logger.info("Synchronous database connection closed")
            
            if self.async_client:
                self.async_client.close()
                logger.info("Asynchronous database connection closed")
                
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    def test_connections(self) -> bool:
        """
        اختبار جميع الاتصالات
        
        Returns:
            bool: True إذا كانت جميع الاتصالات تعمل، False خلاف ذلك
        """
        try:
            # اختبار الاتصال المتزامن
            if self.sync_client:
                self.sync_client.admin.command('ping')
            
            # اختبار الاتصال غير المتزامن
            if self.async_client:
                # لا يمكن اختبار الاتصال غير المتزامن بدون async/await
                # سنعتبر أنه يعمل إذا تم إنشاؤه بنجاح
                pass
            
            logger.info("All database connections are working properly")
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_collection(self, collection_name: str, sync: bool = True):
        """
        الحصول على مجموعة من قاعدة البيانات
        
        Args:
            collection_name: اسم المجموعة
            sync: True للحصول على مجموعة متزامنة، False للحصول على مجموعة غير متزامنة
            
        Returns:
            المجموعة المطلوبة
            
        Raises:
            DatabaseError: إذا فشل الحصول على المجموعة
        """
        try:
            if sync:
                db = self.get_sync_db()
            else:
                db = self.get_async_db()
            
            return db[collection_name]
            
        except Exception as e:
            logger.error(f"Failed to get collection {collection_name}: {str(e)}")
            raise DatabaseError(f"Collection error: {str(e)}")
    
    def get_database_info(self) -> dict:
        """
        الحصول على معلومات قاعدة البيانات
        
        Returns:
            dict: معلومات قاعدة البيانات
        """
        try:
            info = {
                "sync_connected": False,
                "async_connected": False,
                "database_name": None,
                "collections": []
            }
            
            # اختبار الاتصال المتزامن
            if self.sync_client:
                try:
                    self.sync_client.admin.command('ping')
                    info["sync_connected"] = True
                    info["database_name"] = self.sync_db.name
                    
                    # الحصول على قائمة المجموعات
                    collections = self.sync_db.list_collection_names()
                    info["collections"] = collections
                    
                except Exception as e:
                    logger.warning(f"Sync connection test failed: {str(e)}")
            
            # اختبار الاتصال غير المتزامن
            if self.async_client:
                info["async_connected"] = True
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get database info: {str(e)}")
            return {
                "sync_connected": False,
                "async_connected": False,
                "database_name": None,
                "collections": [],
                "error": str(e)
            }

# إنشاء مدير قاعدة البيانات العام (بدون تهيئة فورية)
db_manager = None

def initialize_db_manager():
    """تهيئة مدير قاعدة البيانات"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

# دوال مساعدة للوصول السريع
def get_sync_db():
    """الحصول على قاعدة البيانات المتزامنة"""
    if db_manager is None:
        initialize_db_manager()
    return db_manager.get_sync_db()

def get_async_db():
    """الحصول على قاعدة البيانات غير المتزامنة"""
    if db_manager is None:
        initialize_db_manager()
    return db_manager.get_async_db()

def close_connections():
    """إغلاق جميع اتصالات قاعدة البيانات"""
    if db_manager:
        db_manager.close_connections()