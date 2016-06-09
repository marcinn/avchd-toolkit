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


