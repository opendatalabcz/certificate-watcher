import configparser
import optparse
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.img_storage.local_image_storage import LocalImageStorage
from src.commons.logging.app_logger import AppLogger
from src.placeholder.get_db import get_db
from src.routers import auth, flagged_data, images, search_settings

parser = optparse.OptionParser(description="Certificate watcher service to manage the application")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

AppLogger.setup_logging("manager")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)


try:
    logger.info("Starting manager")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    LOCAL_IMAGE_STORAGE_PATH = config.get("image-storage", "path") if config.getboolean("image-storage", "enabled") else None

    DATABASE_CONNECTION_INFO = PostgreSQLConnectionInfo(
        hostname=config.get("postgres", "hostname"),
        port=config.getint("postgres", "port"),
        database=config.get("postgres", "database"),
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )

    logger.info("Loaded environment variables")
    logger.info("Config loaded successfully")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = SqlAlchemyStorage(database_connection_info=DATABASE_CONNECTION_INFO)
image_storage = LocalImageStorage(LOCAL_IMAGE_STORAGE_PATH)

app = FastAPI()
app.state.image_storage = image_storage

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.dependency_overrides[get_db] = postgres_storage.get_session

API_PREFIX = "/api"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(search_settings.router, prefix=API_PREFIX)
app.include_router(flagged_data.router, prefix=API_PREFIX)
app.include_router(images.router, prefix=API_PREFIX)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, reload_excludes=["*.log"], reload_dirs=["/app/src"])  # noqa: S104
