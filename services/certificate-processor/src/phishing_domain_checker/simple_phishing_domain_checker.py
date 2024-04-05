from ..commons.db_storage.models import SearchSetting
from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker


class SimplePhishingDomainChecker(AbstractPhishingDomainChecker):
    # SimplePhishingDomainChecker is a class that checks if a domain is a phishing domain
    # by looking for preset legitimate domain strings in a provided domain

    def __init__(self, settings: list[SearchSetting]):
        super().__init__(settings=settings)
        self.legitimate_strings: list = []
        self.result_company_table: dict = {}
        self.__setup_checker()

    def __setup_checker(self):
        self.logger.info(f"Setting up {self.__class__.__name__}")
        self.result_company_table = {setting.domain_base: setting for setting in self.settings}
        self.legitimate_strings = list(self.result_company_table.keys())

    def check_domain(self, domain: str) -> SearchSetting | None:
        if not domain:
            self.logger.warning("No domain provided")
            return None
        result = [self.result_company_table[wanted_string] for wanted_string in self.legitimate_strings if wanted_string in domain]
        return result[0] if result else None

    @staticmethod
    def get_algorithm_name() -> str:
        return "simple"
