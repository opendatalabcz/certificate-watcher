import configparser
import optparse
import sys

import certstream
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler

parser = optparse.OptionParser(description="Certificate watcher service")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

AppLogger.setup_logging("certificate-stream")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)

# rabbitmq_connection_info = RabbitMQConnectionInfo(
#     hostname=os.environ.get("RABBITMQ_HOST"),
#     port=os.environ.get("RABBITMQ_PORT"),
#     username=os.environ.get("RABBITMQ_USER"),
#     password=os.environ.get("RABBITMQ_PASSWORD"),
#     virtualhost=os.environ.get("RABBITMQ_VHOST"),
# )
rabbitmq_connection_info = {"hostname": "rabbitmq", "port": 5672, "username": "guest", "password": "guest", "virtualhost": "/"}

try:
    logger.info("Starting certificate-watcher")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    CERTSTREAM_URL = config.get("certificate-stream", "certstream_url")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

# postgres_storage = PostgresStorage(database_connection_info=database_connection_info)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=rabbitmq_connection_info, queue_name="certstream-test")

database_query = """
        INSERT INTO "certstream-test".certificates (certificate_list) VALUES (%s);
    """


def print_callback(message, context):  # noqa: ARG001
    if message["message_type"] == "heartbeat":
        return

    if message["message_type"] == "certificate_update":
        all_domains = message["data"]["leaf_cert"]["all_domains"]

        for domain in all_domains:
            rabbitmq_handler.send(domain)

        logger.info(f"Sent to stream -> {', '.join(all_domains)}")


def main():
    certstream.listen_for_events(print_callback, url=CERTSTREAM_URL)


if __name__ == "__main__":
    main()
