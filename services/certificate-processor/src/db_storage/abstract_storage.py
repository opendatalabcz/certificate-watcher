class AbstractStorage:
    def __init__(self):
        self.is_closed = False

    def _close_connections(self):
        raise NotImplementedError("_close_connections of AbstractStorage not overloaded")
