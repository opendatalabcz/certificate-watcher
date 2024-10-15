import configparser
import optparse
import os
import sys
import time
from datetime import datetime, timedelta

from sqlalchemy import or_
from src.commons.db_storage.models import FlaggedData
from src.commons.db_storage.postgres_storage import SqlAlchemyStorage
from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.commons.stream_handler.utils import RabbitMQConnectionInfo

parser = optparse.OptionParser(description="Periodic scrape checker service")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

AppLogger.setup_logging("periodic-scrape-checker")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)

try:
    logger.info("Starting flagged-data-processor")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    RABBITMQ_IMAGE_CHECKER_CONNECTION_INFO = RabbitMQConnectionInfo(
        hostname=config.get("rabbitmq", "hostname"),
        port=config.getint("rabbitmq", "port"),
        virtualhost=config.get("rabbitmq", "virtualhost"),
        exchange=config.get("rabbitmq", "exchange"),
        connect_timeout=config.getint("rabbitmq", "connect_timeout"),
        routing_key=config.get("rabbitmq", "DOMAIN_IMAGE_ROUTING_KEY"),
        queue=config.get("rabbitmq", "DOMAIN_IMAGE_PROMISC_QUEUE"),
    )

    logger.info(f"Loaded config from {args.config_file}")

    RABBITMQ_IMAGE_CHECKER_CONNECTION_INFO.username = os.environ.get("RABBITMQ_DEFAULT_USER")
    RABBITMQ_IMAGE_CHECKER_CONNECTION_INFO.password = os.environ.get("RABBITMQ_DEFAULT_PASS")

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
rabbitmq_producer = RabbitMQStreamHandler(connection_parameters=RABBITMQ_IMAGE_CHECKER_CONNECTION_INFO)
rabbitmq_producer.setup_producer()

SLEEP_PERIOD = 60 * 60 * 24  # Sleep for 1 day


def main():
    logger.info(" [*] Starting periodic scrape checker service")

    while True:
        # Start a new session
        session_id = postgres_storage.get_persistent_session_id("flagged-data-processor-session")
        session = postgres_storage.get_persistent_session(session_id)
        # Get the current time
        now = datetime.now()
        scraped_before = now - timedelta(days=5)

        flagged_data_list = (
            session.query(FlaggedData)
            .filter(FlaggedData.status == "active", or_(FlaggedData.last_scraped == None, FlaggedData.last_scraped <= scraped_before))  # noqa: E711
            .all()
        )
        if not flagged_data_list:
            logger.info("No flagged data to process, sleeping...")
            postgres_storage.close_persistent_session(session_id)
            time.sleep(SLEEP_PERIOD)
            continue

        logger.info(f"Processing {len(flagged_data_list)} flagged data entries")
        for flagged_data in flagged_data_list:
            domain = flagged_data.domain
            rabbitmq_producer.send(domain)

        # Close the session
        postgres_storage.close_persistent_session(session_id)

        # Sleep for some time before next iteration
        logger.info("Loop complete, sleeping...")
        time.sleep(SLEEP_PERIOD)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
