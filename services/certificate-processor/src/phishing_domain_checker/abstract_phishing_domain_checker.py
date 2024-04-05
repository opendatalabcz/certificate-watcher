from ..commons.db_storage.models import SearchSetting
from ..commons.logging.app_logger import AppLogger


class AbstractPhishingDomainChecker:
    def __init__(self, settings: list[SearchSetting]):
        self.logger = AppLogger.get_logger(self.__class__.__name__)
        if not settings:
            self.logger.error("No settings provided for PhishingDomainChecker")
            raise ValueError("No settings provided for PhishingDomainChecker")
        self.settings = settings

    def check_domain(self, domain):
        raise NotImplementedError("check_domain of AbstractPhishingDomainChecker not overloaded")

    @staticmethod
    def get_algorithm_name() -> str:
        raise NotImplementedError("get_algorithm_name of AbstractPhishingDomainChecker not overloaded")
