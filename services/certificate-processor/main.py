import configparser
import optparse
import os
import sys
import time

from requests.exceptions import ConnectionError, RequestException, SSLError, Timeout
from src.commons.stream_handler.rabbitmq_stream_handler import RabbitMQStreamHandler
from src.commons.timer.func_timer import TimerExceptionError
from src.domain_handler.image_domain_handler import ImageDomainHandler
from src.domain_handler.string_domain_handler import StringDomainHandler
from src.scraper.web_scraper import BS4WebScraper

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
except Exception as e:
    print(f"Fatal error during initialization: {e}")
    sys.exit(1)

# postgres_storage = PostgresStorage(database_connection_info=database_connection_info)
rabbitmq_handler = RabbitMQStreamHandler(connection_parameters=rabbitmq_connection_info, queue_name="certstream-test")
# parser should be loaded from config file
webscraper = BS4WebScraper(parser="lxml", timeout=5)

# config for domain handlers, should be loaded from config file
# simple substrings to look for in domain names
domain_handler_config = {"string_domains": ["csob", "moneta", "reiffeisen", "unicredit", "komercni-banka", "slsp", "kr-"]}
string_domain_handler = StringDomainHandler(config=domain_handler_config)
image_domain_handler = ImageDomainHandler(webscraper=webscraper, config=domain_handler_config)

# def task_function(domain):
#     return image_domain_handler.check([domain])


def main():
    print(" [*] Waiting for messages. To exit press CTRL+C")
    print(" [*] Processing messages from queue")
    counter = 0
    while True:
        # rabbitmq_handler.receive_multiple_frames(callback)

        domain = rabbitmq_handler.receive_single_frame()
        if not domain:
            time.sleep(0.5)
            continue
        # print(domain)

        counter += 1
        # print("counter: ", counter)
        str_result = string_domain_handler.check([domain])
        if str_result:
            print(f"Suspicious domain {domain} found, scraping started:")
            try:
                img_result = image_domain_handler.check([domain])
                # img_result = run_with_timeout(task_function, 5, domain)
            except TimerExceptionError as e:
                print("TIMEOUT: ", e)
                img_result = None
            except (ConnectionError, SSLError, Timeout, RequestException) as e:
                print("BIG ERROR: ", e)
                img_result = None
            except Exception as e:
                print(f"Unexpected error: {e}")
                img_result = None

        if str_result:
            print(str_result)
            if img_result:
                print(img_result)
            else:
                print("No images found")

        if counter % 50 == 0:
            print(f"Processed {counter} domains")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
