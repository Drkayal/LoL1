"""
Handlers Module - معالجات الأوامر
يحتوي على جميع معالجات الأوامر والرسائل في البوت
"""

from .commands import (
    cmd_handler,
    start_handler,
    user_count_callback_handler,
    alivehi_handler,
    you_handler,
    add_dev_handler,
    remove_dev_handler,
    list_devs_handler,
    onoff_handler,
    botat_handler,
    kinhsker_handler,
    update_factory_handler,
    show_running_bots_handler,
    start_Allusers_handler,
    stooop_Allusers_handler
)

from .broadcast import (
    forbroacasts_handler
)

# from .admin import (
#     # سيتم إضافة معالجات الإدارة هنا
# )

__all__ = [
    # Command Handlers
    'cmd_handler',
    'start_handler',
    'user_count_callback_handler',
    'alivehi_handler',
    'you_handler',
    'add_dev_handler',
    'remove_dev_handler',
    'list_devs_handler',
    'onoff_handler',
    'botat_handler',
    'kinhsker_handler',
    'update_factory_handler',
    'show_running_bots_handler',
    'start_Allusers_handler',
    'stooop_Allusers_handler',
    
    # Broadcast Handlers
    'forbroacasts_handler',
    
    # Admin Handlers
    # سيتم إضافة معالجات الإدارة هنا
]