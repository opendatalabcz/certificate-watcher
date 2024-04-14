import os

from ..logging.app_logger import AppLogger


class AbstractImageStorage:
    def __init__(self, storage_path: str):
        self.logger = AppLogger.get_logger(self.__class__.__name__)
        self.storage_path = storage_path

    def save(self, data, path: str):
        raise NotImplementedError("Method save not implemented")

    def get(self, img):
        raise NotImplementedError("Method get not implemented")

    def delete(self, img):
        raise NotImplementedError("Method delete not implemented")

    def get_path(self):
        return self.path


class LocalImageStorage(AbstractImageStorage):
    def __init__(self, path: str):
        super().__init__(path)

    def save(self, data: dict, path: str):
        dirpath = f"{self.storage_path}/{path}"
        self.__check_path(dirpath)
        for filename, img_data in data.items():
            img_data["img"].save(f"{dirpath}/{filename}.{img_data['img'].format.lower()}")
        # with open(path, 'wb') as f:
        #     f.write(data)

    def get(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def delete(self, path: str):
        os.remove(path)

    def __check_path(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
