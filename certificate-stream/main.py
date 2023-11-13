import certstream

certstream_url = 'wss://certstream.calidog.io'


def print_callback(message, context):
    # print(f"Message -> {message}")
    # print(f"Context -> {context}")

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

    print_message = False

    for domain in all_domains:
        # print(f"New domain -> {domain}")
        if domain.endswith(".cz"):
            print_message = True
    
    if print_message:
        print(f"New certificate -> {', '.join(all_domains)}")

def main():
    certstream.listen_for_events(print_callback, url=certstream_url)

if __name__ == '__main__':
    main()
