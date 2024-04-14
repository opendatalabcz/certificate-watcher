from imagehash import ImageHash, hex_to_hash, phash
from PIL import Image

from ..logging.app_logger import AppLogger


class AbstractHashHandler:
    def __init__(self):
        self.logger = AppLogger.get_logger(self.__class__.__name__)


class ImageHashHandler(AbstractHashHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def hash_image(image: Image) -> ImageHash:
        return phash(image)

    @staticmethod
    def compare_hashes(hash1: ImageHash, hash2: ImageHash) -> int:
        # returns hamming distance of hashes
        return hash1 - hash2

    @staticmethod
    def compare_string_hashes(hash1: str, hash2: str) -> int:
        return hex_to_hash(hash1) - hex_to_hash(hash2)

    @staticmethod
    def string_from_hash(hash_input: ImageHash) -> str:
        return str(hash_input)

    @staticmethod
    def string_to_hash(hash_string: str) -> ImageHash:
        return hex_to_hash(hash_string)
