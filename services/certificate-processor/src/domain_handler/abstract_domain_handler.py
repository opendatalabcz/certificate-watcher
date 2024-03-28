from typing import Union

from ..commons.logging.app_logger import AppLogger


class AbstractDomainHandler:
    def __init__(self, config: dict = {}):  # noqa: B006
        self.logger = AppLogger.get_logger(self.__class__.__name__)
        self.config = config

    def check(self, domain: str) -> Union[None, list]:
        raise NotImplementedError
