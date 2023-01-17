import asyncio
import logging
import os
import structlog

import addresses
import dns
from slack import SlackAlertClient

logging.basicConfig(level=logging.INFO)

known_subnets = [
    '140.252.', # NOAO Tucson IP Subnet
    '139.229.', # NOAO Tucson IP Subnet
]

async def run_checker():
    # Slack client for sending alerts
    logger = structlog.get_logger("dns-linter")
    webhook = os.getenv('SLACK_WEBHOOK')

    slack_client = SlackAlertClient(webhook, 'DNS linter', logger)

    # Get the DNS information
    zones = dns.list_all_hosted_zones()
    hosts = dns.query_dns_records(zones)

    # Get addresses information
    all_addresses = addresses.lookup_all_addresses()

    dangling = {}
    not_dangling = {}

    for h in hosts:
        for address in hosts[h]:
            found = False
            for subnet in known_subnets:
                if address.startswith(subnet):
                    not_dangling[h] = address
                    found = True

            if address in all_addresses:
                not_dangling[h] = address
                found = True

            if not found:
                dangling[h] = address

    logging.info("The following hostnames look good:")
    for h, a in not_dangling.items():
        logging.info(f"{h}: {a}")

    logging.info("The following hostnames may be dangling:")

    dangling_alert = "The following hostnames may be dangling:\n"

    for h, a in dangling.items():
        logging.error(f"{h}: {a}")
        next_dangler = f"{h}: {a}\n"

        # Slack will truncate messages of over 3000 characters,
        # so we have to send multiple messages
        if len(next_dangler) + len(dangling_alert) > 3000:
            await slack_client.message(dangling_alert)
            dangling_alert = "Continuing dangling names:\n" + next_dangler
        else:
            dangling_alert += next_dangler

    await slack_client.message(dangling_alert)

if __name__ == "__main__":
    asyncio.run(run_checker())
