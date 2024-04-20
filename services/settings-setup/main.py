import configparser
import json
import optparse
import os
import sys

from PIL import Image as PILImage
from src.commons.db_storage.models import Image, SearchSetting, User
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.hashing.hash_handler import ImageHashHandler
from src.commons.img_storage.local_image_storage import LocalImageStorage
from src.commons.logging.app_logger import AppLogger
from src.commons.utils.image import convert_image_to_rgb_with_white_bg

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

    ADD_DEMO_DATA = config.getboolean("settings-setup", "add_demo_settings")
    RESET_DB = config.getboolean("settings-setup", "reset_db")
    ADD_DEMO_USERS = config.getboolean("settings-setup", "add_demo_users")

    LOCAL_IMAGE_STORAGE_PATH = config.get("image-storage", "path") if config.getboolean("image-storage", "enabled") else None

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = SqlAlchemyStorage(database_connection_info=DATABASE_CONNECTION_INFO)
image_hasher: ImageHashHandler = ImageHashHandler()
local_image_storage: LocalImageStorage = LocalImageStorage(LOCAL_IMAGE_STORAGE_PATH) if LOCAL_IMAGE_STORAGE_PATH else None

if RESET_DB:
    logger.info("Resetting database")
    postgres_storage.reset_db_schema()
    if local_image_storage:
        local_image_storage.clear_directory_keep("")

if ADD_DEMO_USERS:
    # read data from assets/data.json into variable
    with open("assets/users.json") as f:
        data = json.load(f)
    session_id = postgres_storage.get_persistent_session_id("users-setup-session")
    # create users in db
    for user in data:
        pwd_hash = User.get_password_hash(user["password"])

        user_obj = User(username=user["username"], hashed_password=pwd_hash, is_admin=user["isAdmin"])
        # dont add user if already exists
        if not postgres_storage.get(User, username=user["username"]):
            postgres_storage.add([user_obj], persistent_session_id=session_id)
        logger.info(f"Created user: {user}")

if ADD_DEMO_DATA:
    # read data from assets/data.json into variable
    with open("assets/search_settings.json") as f:
        data = json.load(f)
    session_id = postgres_storage.get_persistent_session_id("settings-setup-session")
    # create settings in db
    for setting in data:
        user = setting.get("user")
        if user:
            owner: User = postgres_storage.get(User, persistent_session_id=session_id, username=user)[0]
            if not owner:
                continue

        else:
            continue
        setting.pop("user")

        logo = setting.get("logo")
        if logo:
            image_load = PILImage.open(f"assets/{logo}")
            image = convert_image_to_rgb_with_white_bg(image_load)
            name = logo.split("/")[-1].split(".")[-2]
            logo_img = Image(
                origin="logo",
                hash=image_hasher.string_from_hash(image_hasher.hash_image(image)),
                name=name,
                local_path=f"{owner.username}/{setting.get('domain_base')}/logo",
                format=image.format,
            )
            if local_image_storage:
                local_image_storage.save({name: {"img": image, "format": image.format}}, f"{owner.username}/{setting.get('domain_base')}/logo")
            if not postgres_storage.get(Image, origin="logo", name=name):
                postgres_storage.add([logo_img], persistent_session_id=session_id)

        setting.pop("logo")
        search_setting = SearchSetting(owner_id=owner.id, logo_id=logo_img.id if logo else None, **setting)
        # dont add setting if already exists
        if not postgres_storage.get(SearchSetting, persistent_session_id=session_id, owner_id=owner.id, domain_base=setting["domain_base"]):
            postgres_storage.add([search_setting], persistent_session_id=session_id)
        logger.info(f"Created setting for {owner.username}: {setting}")

    postgres_storage.close_persistent_session(session_id)
