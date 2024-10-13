from ..commons.db_storage.postgres_storage import SqlAlchemyStorage
from ..commons.logging.app_logger import AppLogger


class AbstractDomainHandler:
    def __init__(self, postgres_storage: SqlAlchemyStorage | None = None, config: dict | None = None):  # noqa: B006
        self.logger = AppLogger.get_logger(self.__class__.__name__)
        self.config = config if config else {}
        self.postgres_storage = postgres_storage
