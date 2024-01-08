import configparser
import optparse
import os
import sys

from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler

parser = optparse.OptionParser(description="Certificate watcher service to process certificates")
parser.add_option("-c", "--config-file", metavar="FILENAME", type=str, help="Config file location")
parser.add_option("-e", "--environment", metavar="NAME", type=str, help="Name of the environment (for loading config)")
(args, _) = parser.parse_args()

if not args.config_file:
    print("Config file must be provided")
    sys.exit(1)

# database_connection_info = PostgreSQLConnectionInfo(
#     hostname=os.environ.get("POSTGRES_HOST"),
#     port=os.environ.get("POSTGRES_PORT"),
#     database=os.environ.get("POSTGRES_DB"),
#     username=os.environ.get("POSTGRES_USER"),
#     password=os.environ.get("POSTGRES_PASSWORD"),
# )
# rabbitmq_connection_info = RabbitMQConnectionInfo(
#     hostname=os.environ.get("RABBITMQ_HOST"),
#     port=os.environ.get("RABBITMQ_PORT"),
#     username=os.environ.get("RABBITMQ_USER"),
#     password=os.environ.get("RABBITMQ_PASSWORD"),
#     virtualhost=os.environ.get("RABBITMQ_VHOST"),
# )
rabbitmq_connection_info = {"hostname": "rabbitmq", "port": 5672, "username": "guest", "password": "guest", "virtualhost": "/"}

try:
    print("Starting certificate-processor")

    config = configparser.ConfigParser()
    config.read(args.config_file)

    # CERTSTREAM_URL = config.get("certificate-stream", "certstream_url")

except Exception as e:
    print(f"Fatal error during initialization: {e}")
    sys.exit(1)

# postgres_storage = PostgresStorage(database_connection_info=database_connection_info)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=rabbitmq_connection_info, queue_name="certstream-test")


def callback(ch, method, properties, body):  # noqa: ARG001
    print(" [x] Received %r" % body)


def main():
    # data = rabbitmq_handler.receive_single_frame()
    # print(data)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    rabbitmq_handler.receive_multiple_frames(callback)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
