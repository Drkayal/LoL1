
import os
import importlib.util

def load_plugins():
    """تحميل جميع البرمجيات المساعدة"""
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            file_path = os.path.join(plugins_dir, filename)
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ تم تحميل البرمجية: {module_name}")

# تحميل البرمجيات تلقائياً
load_plugins()
