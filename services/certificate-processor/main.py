import configparser
import optparse
import os
import sys
import time

from requests.exceptions import ConnectionError, RequestException, SSLError, Timeout
from src.commons.db_storage.models import FlaggedData, SearchSetting
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.img_storage.local_image_storage import LocalImageStorage
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.commons.stream_handler.utils import RabbitMQConnectionInfo
from src.domain_handler.image_domain_handler import ImageDomainHandler
from src.domain_handler.string_domain_handler import StringDomainHandler
from src.phishing_domain_checker.phishing_domain_checker_factory import phishing_domain_checker_factory
from src.scraper.web_scraper import BS4WebScraper

parser = optparse.OptionParser(description="Certificate watcher service to process certificates")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

AppLogger.setup_logging("certificate-processor")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)


try:
    logger.info("Starting certificate-processor")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    RABBITMQ_CONNECTION_INFO = RabbitMQConnectionInfo(
        hostname=config.get("rabbitmq", "hostname"),
        port=config.getint("rabbitmq", "port"),
        virtualhost=config.get("rabbitmq", "virtualhost"),
        exchange=config.get("rabbitmq", "exchange"),
        connect_timeout=config.getint("rabbitmq", "connect_timeout"),
    )

    WEB_SCRAPING = dict(config.items("web-scraping"))

    LOCAL_IMAGE_STORAGE_PATH = config.get("image-storage", "path") if config.getboolean("image-storage", "enabled") else None

    logger.info(f"Loaded config from {args.config_file}")

    RABBITMQ_CONNECTION_INFO.username = os.environ.get("RABBITMQ_DEFAULT_USER")
    RABBITMQ_CONNECTION_INFO.password = os.environ.get("RABBITMQ_DEFAULT_PASS")
    RABBITMQ_CONNECTION_INFO.queue = os.environ.get("RABBITMQ_QUEUE", None)

    DATABASE_CONNECTION_INFO = PostgreSQLConnectionInfo(
        hostname=config.get("postgres", "hostname"),
        port=config.getint("postgres", "port"),
        database=config.get("postgres", "database"),
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )

    CHECKER_ALGORITHM = os.environ.get("ALGORITHM", "simple")

    logger.info("Loaded environment variables")
    logger.info("Config loaded successfully")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = SqlAlchemyStorage(database_connection_info=DATABASE_CONNECTION_INFO)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=RABBITMQ_CONNECTION_INFO)
rabbitmq_handler._setup_consumer()

# load phishing_catcher_settings from db
search_settings_db = postgres_storage.get(SearchSetting)

if not search_settings_db:
    logger.error("No search settings found in database, KILLING MYSELF!")
    sys.exit(1)


# maybe would be better as config file or program parameter
string_checker = phishing_domain_checker_factory(CHECKER_ALGORITHM, search_settings_db)
webscraper = BS4WebScraper(parser=WEB_SCRAPING.get("parser"), timeout=int(WEB_SCRAPING.get("timeout")))
local_image_storage = LocalImageStorage(LOCAL_IMAGE_STORAGE_PATH) if LOCAL_IMAGE_STORAGE_PATH else None

domain_handler_config = {}
string_domain_handler = StringDomainHandler(config=domain_handler_config, checker=string_checker)
image_domain_handler = ImageDomainHandler(webscraper=webscraper, config=domain_handler_config)

# TODO: DELETE LATER
test_domains = ["csob-bankapanka.cz", "ajvjaifmoneta.cz", "grafr-unicredit.cz", "komercnifrag-banka.cz", "slspawfe.sk"]
TEST = False


def main():
    logger.info(" [*] Waiting for messages. To exit press CTRL+C")
    logger.info(" [*] Processing messages from queue")
    counter = 0
    main_loop_session = postgres_storage.get_session()
    while True:
        # TODO: DELETE LATER
        if TEST:  # noqa: SIM108
            domain = test_domains[counter % len(test_domains)]
            print(f"Processing domain: {domain}")
        else:
            domain = rabbitmq_handler.receive_single_frame()
        if not domain:
            time.sleep(0.5)
            continue

        counter += 1
        str_check_result = string_domain_handler.check(domain)
        if str_check_result:
            logger.info(f"Suspicious domain {domain} found, scraping started:")
            main_loop_session.add(str_check_result)
            main_loop_session.refresh(str_check_result)
            record = FlaggedData(domain=domain, algorithm=CHECKER_ALGORITHM, search_setting_id=str_check_result.id, search_setting=str_check_result)
            try:
                img_result = image_domain_handler.check([domain])
                # record.scraped_images = img_result
                record.scraped = True
            except (ConnectionError, SSLError, Timeout, RequestException) as e:
                logger.error(f"Connection error: {e}")
                img_result = None
                record.scraped = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                img_result = None
                record.scraped = False

            logger.info(f"Domain {domain} processed, result: {str_check_result}")
            if not img_result:
                logger.debug("No images found")
            else:
                logger.info(f"Images found: {img_result}")

            # TODO: DELETE LATER
            if TEST:
                logger.info(f"Test domain {domain} processed, result: {record}")

            postgres_storage.add([record], prepared_session=main_loop_session)

        if counter % 50 == 0:
            logger.info(f"Processed {counter} domains")

    main_loop_session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
