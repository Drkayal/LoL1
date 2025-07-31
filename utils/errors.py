"""
Custom Exceptions - أنواع الأخطاء المخصصة
يحتوي على جميع أنواع الأخطاء المخصصة المستخدمة في المشروع
"""

class ValidationError(Exception):
    """خطأ في التحقق من صحة المدخلات"""
    def __init__(self, message: str = "خطأ في التحقق من المدخلات"):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """خطأ في قاعدة البيانات"""
    def __init__(self, message: str = "خطأ في قاعدة البيانات"):
        self.message = message
        super().__init__(self.message)

class ProcessError(Exception):
    """خطأ في إدارة العمليات"""
    def __init__(self, message: str = "خطأ في إدارة العمليات"):
        self.message = message
        super().__init__(self.message)

class BroadcastError(Exception):
    """خطأ في عمليات البث"""
    def __init__(self, message: str = "خطأ في عمليات البث"):
        self.message = message
        super().__init__(self.message)

class CacheError(Exception):
    """خطأ في التخزين المؤقت"""
    def __init__(self, message: str = "خطأ في التخزين المؤقت"):
        self.message = message
        super().__init__(self.message)