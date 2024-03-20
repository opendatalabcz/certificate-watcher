from ..logging.app_logger import AppLogger


class AbstractStorage:
    def __init__(self):
        self.is_closed = False
        self.logger = AppLogger.get_logger(self.__class__.__name__)

    def _close_connections(self):
        raise NotImplementedError("_close_connections of AbstractStorage not overloaded")
