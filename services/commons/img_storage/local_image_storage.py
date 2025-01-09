import os
import shutil

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
            if img_data["img"]:
                img_data["img"].save(f"{dirpath}/{filename}.{img_data['img'].format.lower()}")
                img_data["saved"] = True
            else:
                img_data["saved"] = False

    def get(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def delete(self, path: str, is_dir: bool = False):
        full_path = os.path.join(self.storage_path, path)
        if not os.path.exists(full_path):
            return
        if is_dir:
            os.rmdir(full_path)
        else:
            os.remove(full_path)

    def clear_directory_keep(self, directory: str):
        # Iterate over all the entries in the directory
        dirpath = f"{self.storage_path}/{directory}"
        if not os.path.exists(dirpath):
            return
        for entry in os.listdir(dirpath):
            path = os.path.join(dirpath, entry)
            # Check if it's a file or a directory
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        if directory == "":
            # Create empty .gitkeep file in root of the directory
            with open(f"{self.storage_path}/.gitkeep", "w") as f:  # noqa
                pass

    def __check_path(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
