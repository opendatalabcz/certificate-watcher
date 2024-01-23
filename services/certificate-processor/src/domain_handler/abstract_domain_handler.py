from typing import Union


class AbstractDomainHandler:
    def __init__(self, config: dict = {}):  # noqa: B006
        # contains all the configuration for the domain handler
        # - can be used to set string domains
        # - can be used to set images to look for
        self.config = config

    def check(self, domain: list) -> Union[None, list]:
        raise NotImplementedError
