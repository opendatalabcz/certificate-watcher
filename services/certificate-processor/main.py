import configparser
import optparse
import os
import sys
import time

from requests.exceptions import ConnectionError, RequestException, SSLError, Timeout
from src.commons.db_storage.models import FlaggedDomain
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.domain_handler.image_domain_handler import ImageDomainHandler
from src.domain_handler.string_domain_handler import StringDomainHandler
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

database_connection_info = PostgreSQLConnectionInfo(
    hostname=os.environ.get("POSTGRES_HOST"),
    port=int(os.environ.get("POSTGRES_PORT", "5432")),
    database=os.environ.get("POSTGRES_DB"),
    username=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
)
# rabbitmq_connection_info = RabbitMQConnectionInfo(
#     hostname=os.environ.get("RABBITMQ_HOST"),
#     port=os.environ.get("RABBITMQ_PORT"),
#     username=os.environ.get("RABBITMQ_USER"),
#     password=os.environ.get("RABBITMQ_PASSWORD"),
#     virtualhost=os.environ.get("RABBITMQ_VHOST"),
# )
rabbitmq_connection_info = {"hostname": "rabbitmq", "port": 5672, "username": "guest", "password": "guest", "virtualhost": "/"}

try:
    logger.info("Starting certificate-processor")

    config = configparser.ConfigParser()
    config.read(args.config_file)
except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = SqlAlchemyStorage(database_connection_info=database_connection_info)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=rabbitmq_connection_info, queue_name="certstream-test")
# parser should be loaded from config file
webscraper = BS4WebScraper(parser="lxml", timeout=5)

# config for domain handlers, should be loaded from config file
# simple substrings to look for in domain names
domain_handler_config = {"string_domains": ["csob", "moneta", "reiffeisen", "unicredit", "komercni-banka", "slsp", "kr-"]}
string_domain_handler = StringDomainHandler(config=domain_handler_config)
image_domain_handler = ImageDomainHandler(webscraper=webscraper, config=domain_handler_config)


def main():
    logger.info(" [*] Waiting for messages. To exit press CTRL+C")
    logger.info(" [*] Processing messages from queue")
    counter = 0
    while True:
        # rabbitmq_handler.receive_multiple_frames(callback)

        domain = rabbitmq_handler.receive_single_frame()
        if not domain:
            time.sleep(0.5)
            continue

        counter += 1
        str_result = string_domain_handler.check([domain])
        if str_result:
            logger.info(f"Suspicious domain {domain} found, scraping started:")
            record = FlaggedDomain(domain=domain, flagged_domain_base=str_result, algorithm_name="default")
            try:
                img_result = image_domain_handler.check([domain])
                record.scraped_images = img_result
                record.scraped = True
            except (ConnectionError, SSLError, Timeout, RequestException) as e:
                logger.error(f"Connection error: {e}")
                img_result = None
                record.scraped = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                img_result = None
                record.scraped = False

            logger.info(f"Domain {domain} processed, result: {str_result}")
            if not img_result:
                logger.info("No images found")
            else:
                logger.debug(f"Images found: {img_result}")
            postgres_storage.add([record])

        if counter % 50 == 0:
            logger.info(f"Processed {counter} domains")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
