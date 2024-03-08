# import AbstractWebScraper from directory next to current directory
from ..scraper.web_scraper import AbstractWebScraper
from .abstract_domain_handler import AbstractDomainHandler

# from scraper.web_scraper import AbstractWebScraper


class ImageDomainHandler(AbstractDomainHandler):
    def __init__(self, webscraper: AbstractWebScraper, config: dict = {}):  # noqa: B006
        super().__init__(config=config)
        self.webscraper = webscraper

    def check(self, domains: list):
        return {domain: self.webscraper.get_typed_images("https://" + domain) for domain in domains if "*" not in domain}
