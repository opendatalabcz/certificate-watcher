import configparser
import json
import optparse
import os
import sys

from src.commons.db_storage.models import SearchSetting
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.logging.app_logger import AppLogger

parser = optparse.OptionParser(description="Certificate watcher service to setup demo environment")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

APP_NAME = "settings-setup"

AppLogger.setup_logging(f"{APP_NAME}")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)

try:
    logger.info(f"Starting {APP_NAME}")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    DATABASE_CONNECTION_INFO = PostgreSQLConnectionInfo(
        hostname=config.get("postgres", "hostname"),
        port=config.getint("postgres", "port"),
        database=config.get("postgres", "database"),
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )

    add_demo_data = config.getboolean("settings-setup", "add_demo_data")
    reset_db = config.getboolean("settings-setup", "reset_db")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = SqlAlchemyStorage(database_connection_info=DATABASE_CONNECTION_INFO)

if reset_db:
    logger.info("Resetting database")
    postgres_storage.reset_db_schema()

if add_demo_data:
    # read data from assets/data.json into variable
    with open("assets/data.json") as f:
        data = json.load(f)

    # create settings in db
    for owner, setting in data.items():
        search_setting = SearchSetting(owner=owner, **setting)
        # dont add setting if already exists
        if not postgres_storage.get(SearchSetting, owner=owner, domain_base=setting["domain_base"]):
            postgres_storage.add([search_setting])
        logger.info(f"Created setting for {owner}: {setting}")
