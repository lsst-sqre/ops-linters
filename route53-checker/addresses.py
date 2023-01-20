import logging
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

logging.basicConfig(level=logging.INFO)

credentials = GoogleCredentials.get_application_default()

service = discovery.build('compute', 'v1', credentials=credentials)

projects = [
    'science-platform-int-dc5d',
    'science-platform-stable-6994',
    'science-platform-dev-7696',
    'plasma-geode-127520',
]


def lookup_addresses(project):
    addresses = []
    request = service.addresses().aggregatedList(project=project)
    while request is not None:
        response = request.execute()

        for name, addresses_scoped_list in response['items'].items():
            if 'addresses' in addresses_scoped_list:
                for address in addresses_scoped_list['addresses']:
                    addresses.append(address['address'])

        request = service.addresses().aggregatedList_next(
                previous_request=request,
                previous_response=response
            )

    return addresses


def lookup_all_addresses():
    all_addresses = []

    for p in projects:
        addresses = lookup_addresses(p)

        for a in addresses:
            all_addresses.append(a)

    return all_addresses


if __name__ == "__main__":
    all_addresses = lookup_all_addresses()
    logging.info(all_addresses)
