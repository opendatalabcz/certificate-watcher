import configparser
import json
import optparse
import os
import sys

import certstream
from src.db_storage.postgres_storage import PostgresStorage
from src.db_storage.utils import PostgreSQLConnectionInfo

parser = optparse.OptionParser(description="Certificate watcher service")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

if not args.config_file:
    print("Config file must be provided")
    sys.exit(1)

database_connection_info = PostgreSQLConnectionInfo(
    hostname=os.environ.get("POSTGRES_HOST"),
    port=os.environ.get("POSTGRES_PORT"),
    database=os.environ.get("POSTGRES_DB"),
    username=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
)

try:
    print("Starting certificate-watcher")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    CERTSTREAM_URL = config.get("certificate-stream", "certstream_url")

except Exception as e:
    print(f"Fatal error during initialization: {e}")
    sys.exit(1)

postgres_storage = PostgresStorage(database_connection_info=database_connection_info)

database_query = """
        INSERT INTO "certstream-test".certificates (certificate_list) VALUES (%s);
    """


def print_callback(message, context):  # noqa: ARG001
    # print(f"Message -> {message}")
    # print(f"Context -> {context}")

    if message["message_type"] == "heartbeat":
        return

    if message["message_type"] == "certificate_update":
        all_domains = message["data"]["leaf_cert"]["all_domains"]
        postgres_storage.execute(query=database_query, params=(json.dumps(all_domains),))
        print(f"Sent to db -> {', '.join(all_domains)}")

    # for domain in all_domains:
    #     # print(f"New domain -> {domain}")
    #     if domain.endswith(".cz"):
    #         print_message = True

    # print(f"New certificate -> {', '.join(all_domains)}")


def main():
    certstream.listen_for_events(print_callback, url=CERTSTREAM_URL)


if __name__ == "__main__":
    main()
