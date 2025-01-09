import configparser
import optparse
import os
import sys

import certstream
from src.commons.logging.app_logger import AppLogger
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.commons.stream_handler.utils import RabbitMQConnectionInfo

parser = optparse.OptionParser(description="Certificate watcher service")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

AppLogger.setup_logging("certificate-stream")
logger = AppLogger.get_logger()

if not args.config_file:
    logger.error("Config file must be provided")
    sys.exit(1)

try:
    logger.info("Starting certificate-watcher")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    CERTSTREAM_URL = config.get("certificate-stream", "certstream_url")

    RABBITMQ_CONNECTION_INFO = RabbitMQConnectionInfo(
        hostname=config.get("rabbitmq", "hostname"),
        port=config.getint("rabbitmq", "port"),
        virtualhost=config.get("rabbitmq", "virtualhost"),
        exchange=config.get("rabbitmq", "exchange"),
        connect_timeout=config.getint("rabbitmq", "connect_timeout"),
        routing_key=config.get("rabbitmq", "DOMAIN_STRING_ROUTING_KEY"),
    )

    logger.info(f"Loaded config from {args.config_file}")

    RABBITMQ_CONNECTION_INFO.username = os.environ.get("RABBITMQ_DEFAULT_USER")
    RABBITMQ_CONNECTION_INFO.password = os.environ.get("RABBITMQ_DEFAULT_PASS")

    DATA_SOURCE = os.environ.get("DATA_SOURCE", "stream")

    logger.info("Loaded environment variables")
    logger.info("Config loaded successfully")

except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    sys.exit(1)

rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=RABBITMQ_CONNECTION_INFO)
rabbitmq_handler.setup_producer()


def callback(message, context):  # noqa: ARG001
    """
    Callback function for certstream events.
    :param message:
    :param context:
    :return:
    """
    if message["message_type"] == "heartbeat":
        return

    if message["message_type"] == "certificate_update":
        all_domains = message["data"]["leaf_cert"]["all_domains"]

        for domain in all_domains:
            rabbitmq_handler.send(domain)

        logger.info(f"Sent to stream -> {', '.join(all_domains)}")


def process_files(directory):
    """
    Iterate over files in the specified directory and process each domain.

    :param directory: Path to the directory containing the domain files.
    """
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort()

    for file_name in files:
        file_path = os.path.join(directory, file_name)
        print(f"Processing file: {file_name}")

        with open(file_path) as file:
            for line in file:
                domain = line.strip()
                if domain:  # Ensure no empty lines
                    try:
                        rabbitmq_handler.send(domain)
                        print(f"Sent domain: {domain}")
                    except Exception as e:
                        print(f"Error sending domain {domain}: {e}")


def main():
    if DATA_SOURCE == "stream":
        certstream.listen_for_events(callback, url=CERTSTREAM_URL)
    elif DATA_SOURCE == "testdata":
        dir_path = "testdata"
        process_files(dir_path)


if __name__ == "__main__":
    main()
