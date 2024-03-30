from Levenshtein import ratio

from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker


class LevenshteinPhishingDomainChecker(AbstractPhishingDomainChecker):
    # LevenshteinPhishingDomainChecker is a class that checks
    # if a domain is a phishing domain by calculating the Levenshtein ratio
    # between the domain and a list of legitimate domains

    def __init__(self, settings: dict):
        super().__init__(settings=settings)
        self.legitimate_domains: list = []
        self.result_company_table: dict = {}
        self.ratio_threshold: float = 0.35
        self.__setup_checker()

    def __setup_checker(self):
        self.logger.info(f"Setting up {self.__class__.__name__}")
        self.result_company_table = {setting.get("domain"): setting_name for setting_name, setting in self.settings.items()}
        self.legitimate_domains = list(self.result_company_table.keys())
        if self.settings.get("ratio_threshold"):
            self.ratio_threshold = self.settings.get("ratio_threshold")

    def check_domain(self, domain: str) -> str | None:
        if not domain:
            self.logger.warning("No domain provided")
            return None
        result = [
            self.result_company_table[legitimate_domain]
            for legitimate_domain in self.legitimate_domains
            if self.__splitted_domain_check(domain, legitimate_domain)
        ]
        return result[0] if result else None

    @staticmethod
    def get_algorithm_name() -> str:
        return "levenshtein"

    def __splitted_domain_check(self, domain: str, legitimate_domain) -> bool:
        return any(ratio(domain_part, legitimate_domain) > self.ratio_threshold for domain_part in domain.split(".")[:-1])
