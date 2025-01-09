from ..commons.db_storage.models import SearchSetting
from ..phishing_domain_checker.abstract_phishing_domain_checker import AbstractPhishingDomainChecker
from .abstract_domain_handler import AbstractDomainHandler


class StringDomainHandler(AbstractDomainHandler):
    def __init__(self, config: dict = {}, checker: AbstractPhishingDomainChecker = None):  # noqa: B006
        super().__init__(config=config)
        if not checker:
            self.logger.error("No checker provided for StringDomainHandler")
            raise ValueError("No checker provided for StringDomainHandler")
        self.checker = checker

    def check(self, domain) -> None | SearchSetting:
        return self.checker.check_domain(domain)
