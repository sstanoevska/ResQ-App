import os
from kivy.utils import platform
from os.path import join

try:
    if platform == "android":
        from android.storage import app_storage_path
        base_path = app_storage_path()
    else:
        base_path = os.getcwd()
except ImportError:
    # In case you're testing on a non-Android system that cannot import android.*
    base_path = os.getcwd()

remember_file_path = join(base_path, "remember_me.txt")

