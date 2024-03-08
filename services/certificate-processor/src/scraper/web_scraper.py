import requests
from bs4 import BeautifulSoup


class AbstractWebScraper:
    def scrape(self, url: str):
        raise NotImplementedError("scrape of AbstractWebScraper not overloaded")

    def get_images(self, url: str):
        raise NotImplementedError("get_images of AbstractWebScraper not overloaded")

    def get_links(self, url: str):
        raise NotImplementedError("get_links of AbstractWebScraper not overloaded")

    def get_typed_images(self, url: str):
        raise NotImplementedError("get_typed_images of AbstractWebScraper not overloaded")


class BS4WebScraper(AbstractWebScraper):
    def __init__(self, parser: str = "lxml", timeout: int = 5):
        self.parser = parser
        self.timeout = timeout

    def scrape(self, url: str):
        r = requests.get(url, timeout=self.timeout)
        return BeautifulSoup(r.content, self.parser)

    def get_images(self, url: str):
        soup = self.scrape(url)
        return soup.find_all("img")

    def get_links(self, url: str):
        soup = self.scrape(url)
        return soup.find_all("a")

    # make a function that will return dict of images with their types as keys
    # (jpg, png, gif, svg, base64, etc.)
    def get_typed_images(self, url: str):
        images = self.get_images(url)
        typed_images = {}
        for image in images:
            if image.get("src"):
                # add image.get('src') to list at key image.get('src').split('.')[-1]
                imgtype = image.get("src").split(".")[-1]
                # can you do this in one line?
                if imgtype in typed_images:
                    typed_images[imgtype].append(image.get("src"))
                else:
                    typed_images[imgtype] = [image.get("src")]

                # typed_images[image.get('src')] = image.get('src').split('.')[-1]
        return typed_images
