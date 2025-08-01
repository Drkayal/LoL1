"""
Bots Module - إدارة البوتات
يحتوي على دوال إدارة البوتات والعمليات المتعلقة بها
"""

from .logic import (
    start_bot_process,
    stop_bot_process,
    initialize_factory
)

from .models import (
    get_bot_info,
    save_bot_info,
    update_bot_status,
    delete_bot_info,
    get_all_bots,
    get_running_bots,
    get_bots_count,
    update_bot_container_id,
    update_bot_process_id,
    set_collections
)

__all__ = [
    # Logic Functions
    'start_bot_process',
    'stop_bot_process',
    'initialize_factory',
    
    # Model Functions
    'get_bot_info',
    'save_bot_info',
    'update_bot_status',
    'delete_bot_info',
    'get_all_bots',
    'get_running_bots',
    'get_bots_count',
    'update_bot_container_id',
    'update_bot_process_id',
    'set_collections'
]