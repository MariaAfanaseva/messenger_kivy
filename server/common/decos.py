import logging
import sys

if sys.argv[0].find('server') == -1:
    log = logging.getLogger('client')
else:
    log = logging.getLogger('server')


class Logging:
    """The decorator writes information about the launched function to the log."""
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            log.debug(f'Запущена функция {func.__name__}, из модуля {func.__module__}, с параметрами {args}, {kwargs}')
            result = func(*args, **kwargs)
            return result
        return wrapper
