from ..logging.app_logger import AppLogger


class AbstractStreamHandler:
    def __init__(self):
        self.is_active = False
        self.logger = AppLogger.get_logger(self.__class__.__name__)

    def _close_connections(self):
        raise NotImplementedError("_close_connections of AbstractStreamHandler not overloaded")

    def send(self, data):
        raise NotImplementedError("send of AbstractStreamHandler not overloaded")

    def receive(self):
        raise NotImplementedError("receive of AbstractStreamHandler not overloaded")
