"""Nov 24 19:27 MSK 2015
warp-tracker - lib
"""

import logging
import threading

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class Singleton(type):
    """ Singleton metaclass """
    _instances = {}
    lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        logger.debug('Request %s singletone instance ', cls.__name__)
        with cls.lock:
            if cls not in cls._instances:
                logger.debug('Creating new instance')
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
