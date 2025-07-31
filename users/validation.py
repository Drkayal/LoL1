"""
Validation Functions - دوال التحقق من المدخلات
يحتوي على جميع دوال التحقق من صحة المدخلات المستخدمة في المشروع
"""

from utils import ValidationError, logger

def validate_user_id(user_id):
    """
    التحقق من صحة معرف المستخدم
    
    Args:
        user_id: معرف المستخدم المراد التحقق منه
        
    Returns:
        tuple: (is_valid, validated_user_id) حيث is_valid هو boolean
        
    Raises:
        ValidationError: إذا كان معرف المستخدم غير صحيح
    """
    try:
        if not user_id:
            raise ValidationError("معرف المستخدم فارغ")
        
        # تحويل إلى رقم صحيح
        user_id = int(user_id)
        
        if user_id <= 0:
            raise ValidationError("معرف المستخدم يجب أن يكون رقم موجب")
        
        return True, user_id
        
    except (ValueError, TypeError):
        raise ValidationError("معرف المستخدم يجب أن يكون رقم صحيح")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من معرف المستخدم: {str(e)}")

def validate_bot_token(token):
    """
    التحقق من صحة توكن البوت
    
    Args:
        token: توكن البوت المراد التحقق منه
        
    Returns:
        tuple: (is_valid, validated_token) حيث is_valid هو boolean
        
    Raises:
        ValidationError: إذا كان توكن البوت غير صحيح
    """
    try:
        if not token or not isinstance(token, str):
            raise ValidationError("توكن البوت فارغ أو غير صحيح")
        
        if len(token) < 40:
            raise ValidationError("توكن البوت قصير جداً")
        
        # التحقق من صيغة التوكن (يجب أن يحتوي على : واحد)
        if not token.count(':') == 1:
            raise ValidationError("صيغة توكن البوت غير صحيحة")
        
        # التحقق من أن التوكن يبدأ برقم
        parts = token.split(':')
        if not parts[0].isdigit():
            raise ValidationError("جزء معرف البوت في التوكن يجب أن يكون رقم")
        
        return True, token
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من توكن البوت: {str(e)}")

def validate_session_string(session):
    """
    التحقق من صحة كود الجلسة
    
    Args:
        session: كود الجلسة المراد التحقق منه
        
    Returns:
        tuple: (is_valid, validated_session) حيث is_valid هو boolean
        
    Raises:
        ValidationError: إذا كان كود الجلسة غير صحيح
    """
    try:
        if not session or not isinstance(session, str):
            raise ValidationError("كود الجلسة فارغ أو غير صحيح")
        
        if len(session) < 100:
            raise ValidationError("كود الجلسة قصير جداً")
        
        # التحقق من أن كود الجلسة يحتوي على أجزاء أساسية
        if not session.startswith('1:'):
            raise ValidationError("صيغة كود الجلسة غير صحيحة")
        
        return True, session
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من كود الجلسة: {str(e)}")

def validate_bot_username(username):
    """
    التحقق من صحة معرف البوت
    
    Args:
        username: معرف البوت المراد التحقق منه
        
    Returns:
        tuple: (is_valid, validated_username) حيث is_valid هو boolean
        
    Raises:
        ValidationError: إذا كان معرف البوت غير صحيح
    """
    try:
        if not username or not isinstance(username, str):
            raise ValidationError("معرف البوت فارغ أو غير صحيح")
        
        # إزالة @ من البداية إذا وجدت
        username = username.replace('@', '').strip()
        
        if len(username) < 3:
            raise ValidationError("معرف البوت قصير جداً")
        
        if len(username) > 32:
            raise ValidationError("معرف البوت طويل جداً")
        
        # التحقق من أن المعرف يحتوي على أحرف صحيحة فقط
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("معرف البوت يحتوي على أحرف غير مسموحة")
        
        # التحقق من أن المعرف لا يبدأ برقم
        if username[0].isdigit():
            raise ValidationError("معرف البوت لا يمكن أن يبدأ برقم")
        
        return True, username
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من معرف البوت: {str(e)}")

def validate_message(message):
    """
    التحقق من صحة رسالة Telegram
    
    Args:
        message: رسالة Telegram المراد التحقق منها
        
    Returns:
        bool: True إذا كانت الرسالة صحيحة
        
    Raises:
        ValidationError: إذا كانت الرسالة غير صحيحة
    """
    try:
        if not message:
            raise ValidationError("الرسالة فارغة")
        
        if not hasattr(message, 'from_user'):
            raise ValidationError("الرسالة لا تحتوي على معلومات المستخدم")
        
        if not message.from_user:
            raise ValidationError("معلومات المستخدم فارغة")
        
        return True
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من الرسالة: {str(e)}")

def validate_callback_query(callback_query):
    """
    التحقق من صحة استعلام Callback
    
    Args:
        callback_query: استعلام Callback المراد التحقق منه
        
    Returns:
        bool: True إذا كان الاستعلام صحيح
        
    Raises:
        ValidationError: إذا كان الاستعلام غير صحيح
    """
    try:
        if not callback_query:
            raise ValidationError("استعلام Callback فارغ")
        
        if not hasattr(callback_query, 'data'):
            raise ValidationError("استعلام Callback لا يحتوي على بيانات")
        
        if not callback_query.data:
            raise ValidationError("بيانات استعلام Callback فارغة")
        
        return True
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"خطأ غير متوقع في التحقق من استعلام Callback: {str(e)}")