import logging

import addresses
import dns

logging.basicConfig(level=logging.INFO)

known_subnets = [
    '140.252.', # NOAO Tucson IP Subnet
    '139.229.' # NOAO Tucson IP Subnet
]

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

logging.info("The following hostnames may be dangling:")

for h, a in dangling.items():
    logging.error(f"{h}: {a}")

logging.info("The following hostnames look good:")

for h, a in not_dangling.items():
    logging.info(f"{h}: {a}")
