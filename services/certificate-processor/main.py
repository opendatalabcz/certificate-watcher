import configparser
import optparse
import os
import sys
import time

from requests.exceptions import ConnectionError, RequestException, SSLError, Timeout
from src.commons.db_storage.models import FlaggedData, Image, SearchSetting
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import NOTE_DB_MAPPING, PostgreSQLConnectionInfo
from src.commons.img_storage.local_image_storage import LocalImageStorage
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.commons.stream_handler.utils import RabbitMQConnectionInfo
from src.domain_handler.image_domain_handler import ImageDomainHandler
from src.domain_handler.string_domain_handler import StringDomainHandler
from src.phishing_domain_checker.abstract_phishing_domain_checker import AbstractPhishingDomainChecker
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

    CHECKER_ALGORITHM: str = os.environ.get("ALGORITHM", "simple")
    MODE: str = os.environ.get("MODE", "default")
    SCRAPING_ENABLED: bool = os.environ.get("SCRAPING_ENABLED", "true") == "true"

    logger.info("Loaded environment variables")
    logger.info("Config loaded successfully")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage: SqlAlchemyStorage = SqlAlchemyStorage(database_connection_info=DATABASE_CONNECTION_INFO)
rabbitmq_handler: RabbitMQStreamHandler = RabbitMQStreamHandler(connection_parameters=RABBITMQ_CONNECTION_INFO)
rabbitmq_handler._setup_consumer()

# load phishing_catcher_settings from db
main_loop_session_id: str = postgres_storage.get_persistent_session_id("certificate-processor-main-loop")
search_settings_db: list[SearchSetting] = postgres_storage.get(SearchSetting, persistent_session_id=main_loop_session_id)

if not search_settings_db:
    logger.error("No search settings found in database, KILLING MYSELF!")
    sys.exit(1)


string_checker: AbstractPhishingDomainChecker = phishing_domain_checker_factory(CHECKER_ALGORITHM, search_settings_db)
webscraper: BS4WebScraper = BS4WebScraper(parser=WEB_SCRAPING.get("parser"), timeout=int(WEB_SCRAPING.get("timeout")))
local_image_storage: LocalImageStorage = LocalImageStorage(LOCAL_IMAGE_STORAGE_PATH) if LOCAL_IMAGE_STORAGE_PATH else None
domain_handler_config: dict = {}

string_domain_handler: StringDomainHandler = StringDomainHandler(config=domain_handler_config, checker=string_checker)
image_domain_handler: ImageDomainHandler = ImageDomainHandler(
    config=domain_handler_config, postgres_storage=postgres_storage, image_storage=local_image_storage, webscraper=webscraper
)

# TODO: DELETE LATER
# test_domains = ["csob-bankapanka.cz", "ajvjaifmoneta.cz", "grafr-unicredit.cz", "komercnifrag-banka.cz", "slspawfe.sk", "www.site.monetae.io"]
# test_domains = ["monetamarkets-vietnam.com", "slspackaging.com", "monetaryaccounts.site", "monetary-policy-comm.finbitsindia.com", "www.site.monetae.io"]
test_domains = ["webmail.naturkunde-museum-coburg.de"]
TEST = False


def main():
    if MODE == "default":
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
                domain: str | None = rabbitmq_handler.receive_single_frame()
            if not domain:
                time.sleep(0.5)
                continue

            counter += 1
            str_check_result_setting: SearchSetting = string_domain_handler.check(domain)
            if str_check_result_setting:
                logger.info(f"Suspicious domain {domain} found for {str_check_result_setting.domain_base}, scraping started")
                record: FlaggedData = FlaggedData(domain=domain, algorithm=CHECKER_ALGORITHM, search_setting_id=str_check_result_setting.id)
                postgres_storage.add([record], persistent_session_id=main_loop_session_id)

                # TODO: REWORK TO SEND to rabbitmq
                if SCRAPING_ENABLED:
                    try:
                        success_image_handle = image_domain_handler.check(domain, record, str_check_result_setting, main_loop_session_id)
                        logger.info(f"Images {'successfully' if success_image_handle else 'unsuccessfully'} scraped for {record.domain}")
                    except (ConnectionError, SSLError, Timeout, RequestException) as err:
                        logger.error(f"Connection error: {err}")
                        postgres_storage.commit_persistent_session(main_loop_session_id)
                    except Exception as err:
                        logger.error(f"Unexpected error: {err}")
                        record.note = "Unexpected error thrown on scraping"
                        postgres_storage.commit_persistent_session(main_loop_session_id)

                logger.info(f"Domain {domain} processed, result for: {str_check_result_setting.domain_base}")

            if counter % 50 == 0:
                logger.info(f"Processed {counter} domains")

    elif MODE == "periodic":
        logger.info(" [*] Periodic mode")
        logger.info(" [*] Processing unfinished database records")
        while True:
            # TODO: REWORK INTO RECEIVING FROM RABBITMQ
            unscraped_flagged_data = postgres_storage.get(FlaggedData, persistent_session_id=main_loop_session_id, note=NOTE_DB_MAPPING["SCRAPE_ERROR"])
            filtered_flagged_data = [record for record in unscraped_flagged_data if "*" not in record.domain]

            logger.info(f"Found {len(filtered_flagged_data)} unscraped records")

            for record in filtered_flagged_data:
                try:
                    success_image_handle: bool = image_domain_handler.check_retry_domain(record, main_loop_session_id)

                    logger.info(f"Images {'successfully' if success_image_handle else 'unsuccessfully'} scraped for {record.domain}")
                except Exception as err:  # noqa: PERF203
                    logger.error(f"Unexpected error: {err}")
                    record.note = "Unexpected error thrown on scraping"
                    postgres_storage.commit_persistent_session(main_loop_session_id)

            unscraped_images = postgres_storage.get(Image, persistent_session_id=main_loop_session_id, note=NOTE_DB_MAPPING["IMG_DOWNLOAD_ERROR"])
            logger.info(f"Found {len(unscraped_images)} unscraped images")

            # divide images to lists with key base on flag_id as a dict key
            unscraped_images_dict = {}
            for image in unscraped_images:
                if image.flag_id not in unscraped_images_dict:
                    unscraped_images_dict[image.flag_id] = []
                unscraped_images_dict[image.flag_id].append(image)

            for flag_id, images in unscraped_images_dict.items():
                try:
                    flagged_data = postgres_storage.get(FlaggedData, persistent_session_id=main_loop_session_id, id=flag_id)[0]
                    success_retry_image_scrape = image_domain_handler.check_retry_download_images(flagged_data, images, main_loop_session_id)
                    logger.info(f"Images {'successfully' if success_retry_image_scrape else 'unsuccessfully'} scraped for {images[0].flagged_data.domain}")
                except Exception as err:  # noqa: PERF203
                    logger.error(f"Unexpected error: {err}")
                    postgres_storage.commit_persistent_session(main_loop_session_id)

            time.sleep(60 * 60 * 24)  # 24 hours

    else:
        logger.error("Invalid mode")

    postgres_storage.close_persistent_session(main_loop_session_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            sys.exit(0)
