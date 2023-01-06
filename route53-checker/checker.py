import logging

import addresses
import dns

logging.basicConfig(level=logging.INFO)


# Get the DNS information
zones = dns.list_all_hosted_zones()
hosts = dns.query_dns_records(zones)

for h in hosts:
    logging.info(f"{h}: {hosts[h]}")

# Get addresses information
all_addresses = addresses.lookup_all_addresses()
logging.info(all_addresses)


logging.info("The following hostnames may be dangling:")

for h in hosts:
    for address in hosts[h]:
        if address not in all_addresses:
            logging.error(f"{h}: {address}")

logging.info("The following hostnames look good:")

for h in hosts:
    for address in hosts[h]:
        if address in all_addresses:
            logging.info(f"{h}: {address}")
