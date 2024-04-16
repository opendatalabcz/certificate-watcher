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
        # with open(path, 'wb') as f:
        #     f.write(data)

    def get(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def delete(self, path: str):
        os.remove(f"{self.storage_path}/{path}")

    def clear_directory_keep(self, directory: str):
        # Iterate over all the entries in the directory
        dirpath = f"{self.storage_path}/{directory}"
        for entry in os.listdir(dirpath):
            path = os.path.join(dirpath, entry)
            # Check if it's a file or a directory
            if os.path.isdir(path):
                # It's a directory, remove it and all its contents
                shutil.rmtree(path)
            else:
                # It's a file, remove it
                os.remove(path)
        if directory == "":
            # Create empty .gitkeep file in root of the directory
            with open(f"{self.storage_path}/.gitkeep", "w") as f:  # noqa
                pass

    def __check_path(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
