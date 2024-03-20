import logging
import sys


class AppLogger:
    _configured = False
    _app_name = "App"

    @classmethod
    def setup_logging(cls, app_name=None):
        if cls._configured:
            return

        if app_name:
            cls._app_name = app_name

        format_str = f"%(asctime)s - [{cls._app_name}] - %(levelname)s - %(name)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Configure the root logger
        logging.basicConfig(
            level=logging.INFO,
            format=format_str,
            datefmt=date_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"{cls._app_name.lower()}.log"),
                logging.FileHandler(f"{cls._app_name.lower()}_error.log", mode="a"),
            ],
        )

        error_handler = logging.FileHandler(f"{cls._app_name.lower()}_error.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(format_str, date_format))

        # Adding a specific handler for error level to root logger
        logging.getLogger().addHandler(error_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name="root"):
        if not cls._configured:
            raise ValueError("Logger not configured. Call setup_logging first.")
        return logging.getLogger(name)
