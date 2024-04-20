import re
from io import BytesIO
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import requests
from cairosvg import svg2png
from PIL import Image as PILImage

from ..commons.db_storage.models import FlaggedData, Image, SearchSetting
from ..commons.db_storage.postgres_storage import SqlAlchemyStorage
from ..commons.hashing.hash_handler import ImageHashHandler
from ..commons.img_storage.local_image_storage import LocalImageStorage
from ..commons.utils.image import convert_image_to_rgb_with_white_bg
from ..scraper.web_scraper import AbstractWebScraper
from .abstract_domain_handler import AbstractDomainHandler


class ImageDomainHandler(AbstractDomainHandler):
    def __init__(
        self,
        webscraper: AbstractWebScraper,
        postgres_storage: SqlAlchemyStorage | None,
        image_storage: LocalImageStorage | None,
        config: dict = {},  # noqa: B006
    ):
        super().__init__(config=config, postgres_storage=postgres_storage)
        self.webscraper = webscraper
        self.image_storage = image_storage
        self.hash_handler = ImageHashHandler()
        self.hash_threshold = config.get("hash_threshold", 5)
        self.SVG_R = r"(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b"
        self.SVG_RE = re.compile(self.SVG_R, re.DOTALL)

    def check(self, domain: str, flagged_data: FlaggedData, search_setting: SearchSetting, db_session_id: str | None = None) -> bool:
        url = f"https://{domain}"
        images_source = self.webscraper.get_images(url)

        images = self.download_images(url, images_source)

        local_path = None if not self.image_storage else f"{search_setting.owner.username}/{search_setting.domain_base}/{domain}"
        if self.image_storage:
            self.image_storage.save(images, local_path)

        db_images = [
            Image(
                origin="scraped",
                hash=self.hash_handler.string_from_hash(self.hash_handler.hash_image(image_data["img"])) if image_data.get("img") else None,
                name=name,
                image_url=image_data["src"],
                local_path=local_path if image_data["saved"] else None,
                format=image_data["img"].format if image_data["img"] else None,
                flag_id=flagged_data.id,
            )
            for name, image_data in images.items()
        ]

        self.postgres_storage.add(db_images, db_session_id)
        flagged_data.images_scraped = True

        if search_setting.logo:
            duplicate_image = self.check_for_duplicate_images(db_images, search_setting.logo)
            if duplicate_image:
                flagged_data.suspected_logo_found = duplicate_image.id
                self.logger.info(f"Duplicate image found: {duplicate_image.name}")

        if db_session_id:
            self.postgres_storage.commit_persistent_session(db_session_id)
        return bool(db_images)

    def check_for_duplicate_images(self, images: list[Image], logo: Image) -> Image | None:
        for image in images:
            hamming_distance = self.hash_handler.compare_string_hashes(logo.hash, image.hash)
            if hamming_distance < self.hash_threshold:
                return image

        return None

    def download_images(self, url: str, images_source) -> dict:
        result = {}
        for image in images_source:
            src = image.get("src")
            if src:
                full_url = self.normalize_image_url(src, url)
                if self.is_external_source(full_url, url):
                    self.logger.info(f"External image found: {full_url}")
                else:
                    self.logger.info(f"Internal image found: {full_url}")
                result[uuid4()] = {"img": self.__download_image(full_url), "src": full_url}

        return result

    def __download_image(self, image_url) -> type(PILImage) | None:
        try:
            response = requests.get(image_url, timeout=3)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred

            content = BytesIO(response.content)
            if self.SVG_RE.match(response.text):
                content = BytesIO(svg2png(response.text))

            image = PILImage.open(content)
            self.logger.info(f"Downloaded {image_url}")
            # Normalize image to RGB with white background
            return convert_image_to_rgb_with_white_bg(image)
        except requests.RequestException as e:
            self.logger.error(f"Failed to download {image_url}: {e}")
        except OSError as e:
            self.logger.error(f"Failed to open image {image_url}: {e}")

        return None

    def __get_image_urls(self, images):
        return [image.get("src") for image in images]

    def normalize_image_url(self, src, page_url):
        """
        Normalize the image URL by resolving relative and protocol-relative URLs
        against the page URL.
        """
        return urljoin(page_url, src)

    def is_external_source(self, url, base_url):
        """
        Determine if the URL is external by comparing its domain with the base URL's domain.
        """
        return urlparse(url).netloc != urlparse(base_url).netloc
