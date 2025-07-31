"""
Database Module - إدارة قاعدة البيانات
يحتوي على جميع دوال إدارة قاعدة البيانات والتخزين المؤقت
"""

from .manager import (
    DatabaseManager,
    db_manager,
    get_sync_db,
    get_async_db,
    close_connections
)

from .models import (
    # Broadcast functions
    set_broadcast_status,
    get_broadcast_status,
    delete_broadcast_status,
    
    # Bot functions
    get_bot_info,
    save_bot_info,
    update_bot_status,
    delete_bot_info,
    get_all_bots,
    get_running_bots,
    
    # Factory functions
    get_factory_state,
    set_factory_state,
    
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
    
    # Broadcast Functions
    'set_broadcast_status',
    'get_broadcast_status',
    'delete_broadcast_status',
    
    # Bot Functions
    'get_bot_info',
    'save_bot_info',
    'update_bot_status',
    'delete_bot_info',
    'get_all_bots',
    'get_running_bots',
    
    # Factory Functions
    'get_factory_state',
    'set_factory_state',
    
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