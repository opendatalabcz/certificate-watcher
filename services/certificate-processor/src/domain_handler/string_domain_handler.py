from typing import Union

from ..phishing_domain_checker.abstract_phishing_domain_checker import AbstractPhishingDomainChecker
from .abstract_domain_handler import AbstractDomainHandler


class StringDomainHandler(AbstractDomainHandler):
    def __init__(self, config: dict = {}, checker: AbstractPhishingDomainChecker = None):  # noqa: B006
        super().__init__(config=config)
        if not checker:
            self.logger.error("No checker provided for StringDomainHandler")
            raise ValueError("No checker provided for StringDomainHandler")
        self.checker = checker

    # TODO: fix return stuff a bit and add also whois check
    def check(self, domain) -> Union[None, list]:
        return self.checker.check_domain(domain)

    def whois_check(self, domain):
        return domain
