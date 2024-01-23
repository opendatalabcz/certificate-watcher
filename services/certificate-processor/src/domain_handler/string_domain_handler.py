from typing import Union

from .abstract_domain_handler import AbstractDomainHandler


class StringDomainHandler(AbstractDomainHandler):
    def __init__(self, config: dict = {}):  # noqa: B006
        super().__init__(config=config)

        self.wanted_domains = self.config.get("string_domains", [])

    def check(self, domains: list) -> Union[None, list]:
        return [domain for domain in domains if any(substring in domain for substring in self.wanted_domains)] or None
