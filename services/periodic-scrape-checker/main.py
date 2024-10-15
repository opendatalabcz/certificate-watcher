import configparser
import optparse
import os
import sys
import time
from datetime import datetime, timedelta

from sqlalchemy import or_
from src.commons.db_storage.models import FlaggedData, ScanHistory
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


def main():
    logger.info(" [*] Starting periodic scrape checker service")

    while True:
        # Start a new session
        session_id = postgres_storage.get_persistent_session_id("flagged-data-processor-session")
        session = postgres_storage.get_session(session_id)
        # Get the current time
        now = datetime.now()

        # Fetch FlaggedData records that need to be processed
        flagged_data_list = (
            session.query(FlaggedData)
            .filter(or_(FlaggedData.next_scheduled_scan <= now, FlaggedData.next_scheduled_scan == None), FlaggedData.status == "active")  # noqa: E711
            .all()
        )

        if not flagged_data_list:
            logger.info("No flagged data to process, sleeping...")
            postgres_storage.close_persistent_session(session_id)
            time.sleep(60)  # Sleep for 1 minute before checking again
            continue

        for flagged_data in flagged_data_list:
            domain = flagged_data.domain

            # Determine the last scan time
            last_scan = session.query(ScanHistory).filter(ScanHistory.flagged_data_id == flagged_data.id).order_by(ScanHistory.scan_time.desc()).first()

            # Determine if we should scrape based on scan frequency
            should_scrape = False
            if flagged_data.scan_frequency:
                if last_scan:
                    time_since_last_scan = now - last_scan.scan_time
                    if flagged_data.scan_frequency == "daily":
                        should_scrape = time_since_last_scan >= timedelta(days=1)
                    elif flagged_data.scan_frequency == "weekly":
                        should_scrape = time_since_last_scan >= timedelta(weeks=1)
                    else:
                        # Default to scraping if frequency is unrecognized
                        should_scrape = True
                else:
                    # If never scanned before, we should scrape
                    should_scrape = True
            else:
                # If no scan frequency is set, decide default behavior
                should_scrape = True

            if should_scrape:
                # Send to the appropriate queue
                rabbitmq_producer.send(domain)
                logger.info(f"Queued domain {domain} for scraping")

                # Update next_scheduled_scan based on scan_frequency
                if flagged_data.scan_frequency:
                    if flagged_data.scan_frequency == "daily":
                        flagged_data.next_scheduled_scan = now + timedelta(days=1)
                    elif flagged_data.scan_frequency == "weekly":
                        flagged_data.next_scheduled_scan = now + timedelta(weeks=1)
                    else:
                        flagged_data.next_scheduled_scan = None
                else:
                    # Default to None to not schedule again
                    flagged_data.next_scheduled_scan = None

                # Update times_scanned
                flagged_data.times_scanned += 1

                # Update last_status_change
                flagged_data.last_status_change = now

                # Commit changes
                postgres_storage.commit_persistent_session(session_id)

        # Close the session
        postgres_storage.close_persistent_session(session_id)

        # Sleep for some time before next iteration
        time.sleep(60)  # Sleep for 1 minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
