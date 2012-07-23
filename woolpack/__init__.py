import os.path
import sys


def import_settings(settings_type=None):
    if settings_type is None:
        raise Exception("You need to define a settings type")
    user_file = os.path.join(os.getenv('HOME'), 'woolpack_config.py')
    if os.path.isfile(os.path.join(user_file)):
        if os.getenv('HOME') not in sys.path:
            sys.path.append(os.getenv('HOME'))
        try:
            from woolpack_config import settings
            return settings[settings_type]
        except ImportError:
            raise Exception("Could not load your settings.")
