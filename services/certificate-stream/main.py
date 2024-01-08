import configparser
import optparse
import os
import sys

from src.commons.db_storage.utils import PostgreSQLConnectionInfo
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler

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
# rabbitmq_connection_info = RabbitMQConnectionInfo(
#     hostname=os.environ.get("RABBITMQ_HOST"),
#     port=os.environ.get("RABBITMQ_PORT"),
#     username=os.environ.get("RABBITMQ_USER"),
#     password=os.environ.get("RABBITMQ_PASSWORD"),
#     virtualhost=os.environ.get("RABBITMQ_VHOST"),
# )
rabbitmq_connection_info = {"hostname": "rabbitmq", "port": 5672, "username": "guest", "password": "guest", "virtualhost": "/"}

try:
    print("Starting certificate-watcher")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    CERTSTREAM_URL = config.get("certificate-stream", "certstream_url")

except Exception as e:
    print(f"Fatal error during initialization: {e}")
    sys.exit(1)

# postgres_storage = PostgresStorage(database_connection_info=database_connection_info)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=rabbitmq_connection_info, queue_name="certstream-test")

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
        # postgres_storage.execute(query=database_query, params=(json.dumps(all_domains),))
        print(f"Sent to stream -> {', '.join(all_domains)}")

    # for domain in all_domains:
    #     # print(f"New domain -> {domain}")
    #     if domain.endswith(".cz"):
    #         print_message = True

    # print(f"New certificate -> {', '.join(all_domains)}")


# connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
# channel = connection.channel()
# channel.queue_declare(queue='hello')


def main():
    # certstream.listen_for_events(print_callback, url=CERTSTREAM_URL)
    rabbitmq_handler.send("test")
    # channel.basic_publish(exchange='',
    #                       routing_key='hello',
    #                       body='Hello World!')
    # print(" [x] Sent 'Hello World!'")

    # connection.close()


if __name__ == "__main__":
    main()
