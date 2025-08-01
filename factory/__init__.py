"""
Factory Module - إدارة المصنع
يحتوي على دوال إدارة المصنع والإعدادات المتعلقة بها
"""

# دوال منطق المصنع ستتم إضافتها في المستقبل

from .settings import (
    get_factory_state,
    set_factory_state,
    set_collections
)

__all__ = [
    # Settings Functions
    'get_factory_state',
    'set_factory_state',
    'set_collections'
]