"""
Database Module - إدارة قاعدة البيانات
يحتوي على جميع دوال إدارة قاعدة البيانات والتخزين المؤقت
"""

from .manager import (
    DatabaseManager,
    db_manager,
    initialize_db_manager,
    get_sync_db,
    get_async_db,
    close_connections
)

from .models import (
    # Utility functions
    clear_bot_cache,
    clear_factory_cache,
    get_database_stats,
    set_collections
)

from .cache import (
    CacheManager,
    cache_manager,
    get_cache,
    set_cache,
    delete_cache,
    clear_cache,
    get_cache_size
)

__all__ = [
    # Database Manager
    'DatabaseManager',
    'db_manager',
    'get_sync_db',
    'get_async_db',
    'close_connections',
    
    # Utility Functions
    'clear_bot_cache',
    'clear_factory_cache',
    'get_database_stats',
    'set_collections',
    
    # Cache Functions
    'CacheManager',
    'cache_manager',
    'get_cache',
    'set_cache',
    'delete_cache',
    'clear_cache',
    'get_cache_size'
]