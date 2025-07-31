"""
Users Module - إدارة المستخدمين
يحتوي على دوال التحقق من المدخلات ودوال إدارة المستخدمين
"""

from .validation import (
    validate_user_id,
    validate_bot_token,
    validate_session_string,
    validate_bot_username
)

from .logic import (
    is_dev,
    is_user,
    add_new_user,
    del_user,
    get_users,
    get_user_count,
    clear_user_cache,
    get_dev_count,
    set_dependencies
)

__all__ = [
    # Validation Functions
    'validate_user_id',
    'validate_bot_token',
    'validate_session_string',
    'validate_bot_username',
    
    # User Logic Functions
    'is_dev',
    'is_user',
    'add_new_user',
    'del_user',
    'get_users',
    'get_user_count',
    'clear_user_cache',
    'get_dev_count',
    'set_dependencies'
]