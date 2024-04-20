from dnstwist import Fuzzer
from Levenshtein import ratio

from ..commons.db_storage.models import SearchSetting
from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker


class LevenshFuzzPhishingDomainChecker(AbstractPhishingDomainChecker):
    KEYWORDS: list = [
        "bank",
        "login",
        "secure",
        "account",
        "update",
        "verify",
        "password",
        "support",
        "service",
        "online",
        "payment",
        "customer",
        "signin",
        "banking",
        "credit",
        "card",
        "information",
        "personal",
        "identity",
        "financial",
        "transaction",
        "money",
        "transfer",
    ]

    def __init__(self, settings: list[SearchSetting]):
        super().__init__(settings=settings)
        self.domain_lookup_table: dict = {}
        self.result_company_table: dict = {}
        self.ratio_threshold: float = 0.9
        self.__setup_checker()

    def __setup_checker(self):
        self.logger.info(f"Setting up {self.__class__.__name__}")
        for setting in self.settings:
            whole_domain = f"{setting.domain_base}.{setting.tld}"
            self.domain_lookup_table[setting.domain_base] = self.extract_fuzzed_domains(Fuzzer(whole_domain, self.KEYWORDS))
        self.result_company_table = {setting.domain_base: setting for setting in self.settings}

    def extract_fuzzed_domains(self, fuzzer: Fuzzer):
        # get only the last part of the domain
        if not fuzzer.domains:
            fuzzer.generate()
        return {".".join(item.get("domain").split(".")[:-1]) for item in fuzzer.domains}

    def check_domain(self, domain: str) -> SearchSetting | None:
        if not domain:
            self.logger.warning("No domain provided")
            return None

        for legitimate_domain, fuzzed_domains in self.domain_lookup_table.items():
            for fuzzed_domain in fuzzed_domains:
                if self.__splitted_domain_check(domain, fuzzed_domain):
                    self.logger.info(f"Found {fuzzed_domain} in {domain}")
                    return self.result_company_table[legitimate_domain]
        return None

    def __splitted_domain_check(self, suspect_domain: str, fuzzed_domain) -> bool:
        return any(ratio(suspect_domain_part, fuzzed_domain) > self.ratio_threshold for suspect_domain_part in suspect_domain.split(".")[:-1])

    @staticmethod
    def get_algorithm_name() -> str:
        return "levensh_fuzz"
