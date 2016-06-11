import os
import sys
from functools import wraps


class CommandError(Exception):
    pass


def run_command(func_or_callable):
    try:
        func_or_callable()
    except CommandError, ex:
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[91m"
        sys.stdout.write(COLOR_SEQ+unicode(ex)+RESET_SEQ+'\n')
        sys.stdout.flush()


def command(func):
    @wraps(func)
    def wrapper():
        return run_command(func)
    return wrapper



def load_config():
    import pkg_resources
    from .. import profiles

    configs = (
            os.path.join(os.path.expanduser('~'), '.config', 'avchdtoolkit', 'codecs.ini'),
            os.path.sep+os.path.join('etc', 'avchdtoolkit', 'codecs.ini'),
            os.environ.get('AVCHDTRANSCODE_CODECS', None),
            pkg_resources.resource_filename('avchdtoolkit', 'codecs.ini'),
        )

    profiles.load_profiles_config(paths=configs)

