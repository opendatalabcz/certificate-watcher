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
main_loop_session_id = postgres_storage.get_persistent_session_id("certificate-processor-main-loop")
search_settings_db = postgres_storage.get(SearchSetting, persistent_session_id=main_loop_session_id)

if not search_settings_db:
    logger.error("No search settings found in database, KILLING MYSELF!")
    sys.exit(1)


string_checker = phishing_domain_checker_factory(CHECKER_ALGORITHM, search_settings_db)
webscraper = BS4WebScraper(parser=WEB_SCRAPING.get("parser"), timeout=int(WEB_SCRAPING.get("timeout")))
local_image_storage = LocalImageStorage(LOCAL_IMAGE_STORAGE_PATH) if LOCAL_IMAGE_STORAGE_PATH else None
domain_handler_config = {}

string_domain_handler = StringDomainHandler(config=domain_handler_config, checker=string_checker)
image_domain_handler = ImageDomainHandler(
    config=domain_handler_config, postgres_storage=postgres_storage, image_storage=local_image_storage, webscraper=webscraper
)

# TODO: DELETE LATER
# test_domains = ["csob-bankapanka.cz", "ajvjaifmoneta.cz", "grafr-unicredit.cz", "komercnifrag-banka.cz", "slspawfe.sk", "www.site.monetae.io"]
# test_domains = ["monetamarkets-vietnam.com", "slspackaging.com", "monetaryaccounts.site", "monetary-policy-comm.finbitsindia.com", "www.site.monetae.io"]
test_domains = ["webmail.naturkunde-museum-coburg.de"]
TEST = False


def main():
    logger.info(" [*] Waiting for messages. To exit press CTRL+C")
    logger.info(" [*] Processing messages from queue")
    counter = 0

    while True:
        # TODO: DELETE LATER
        if TEST:  # noqa: SIM108
            domain = test_domains[counter % len(test_domains)]
            if counter == len(test_domains):
                break
            logger.info(f"Processing domain: {domain}")
        else:
            domain = rabbitmq_handler.receive_single_frame()
        if not domain:
            time.sleep(0.5)
            continue

        counter += 1
        str_check_result_setting: SearchSetting = string_domain_handler.check(domain)
        if str_check_result_setting:
            logger.info(f"Suspicious domain {domain} found for {str_check_result_setting.domain_base}, scraping started")
            record = FlaggedData(domain=domain, algorithm=CHECKER_ALGORITHM, search_setting_id=str_check_result_setting.id)
            postgres_storage.add([record], persistent_session_id=main_loop_session_id)
            try:
                image_domain_handler.check(domain, record, str_check_result_setting, main_loop_session_id)
                logger.info("Images successfully scraped")
            except (ConnectionError, SSLError, Timeout, RequestException) as err:
                logger.error(f"Connection error: {err}")
                record.note = "Connection error thrown on scraping"
                postgres_storage.commit_persistent_session(main_loop_session_id)
            except Exception as err:
                logger.error(f"Unexpected error: {err}")
                record.note = "Unexpected error thrown on scraping"
                postgres_storage.commit_persistent_session(main_loop_session_id)

            logger.info(f"Domain {domain} processed, result for: {str_check_result_setting.domain_base}")

        if counter % 50 == 0:
            logger.info(f"Processed {counter} domains")

    postgres_storage.close_persistent_session(main_loop_session_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
