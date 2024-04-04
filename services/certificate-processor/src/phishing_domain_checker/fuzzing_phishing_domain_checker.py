from dnstwist import Fuzzer

from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker


class FuzzingPhishingDomainChecker(AbstractPhishingDomainChecker):
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

    def __init__(self, settings: dict):
        super().__init__(settings=settings)
        self.domain_lookup_table: dict = {}
        self.result_company_table: dict = {}
        self.__setup_checker()

    def __setup_checker(self):
        self.logger.info(f"Setting up {self.__class__.__name__}")
        for setting in self.settings.values():
            whole_domain = f"{setting.get('domain')}.{setting.get('top_level_domain')}"
            self.domain_lookup_table[setting.get("domain")] = self.extract_fuzzed_domains(Fuzzer(whole_domain, self.KEYWORDS))
        self.result_company_table = {setting.get("domain"): setting_name for setting_name, setting in self.settings.items()}

    def extract_fuzzed_domains(self, fuzzer: Fuzzer):
        # get only the last part of the domain
        if not fuzzer.domains:
            fuzzer.generate()
        return {item.get("domain").split(".")[-2] for item in fuzzer.domains}

    def check_domain(self, domain: str) -> str | None:
        if not domain:
            self.logger.warning("No domain provided")
            return None
        for legitimate_domain, fuzzed_domains in self.domain_lookup_table.items():
            for fuzzed_domain in fuzzed_domains:
                if fuzzed_domain in domain:
                    return self.result_company_table[legitimate_domain]
        return None

    @staticmethod
    def get_algorithm_name() -> str:
        return "fuzzing"
