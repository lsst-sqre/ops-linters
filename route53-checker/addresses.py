import logging

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

logging.basicConfig(level=logging.INFO)

credentials = GoogleCredentials.get_application_default()

service = discovery.build('compute', 'v1', credentials=credentials)

projects = [
    'science-platform-stable-6994',
    'science-platform-int-dc5d',
    'science-platform-dev-7696',
    'plasma-geode-127520',
]

# Name of the region for this request.
region = 'us-central1'


def lookup_addresses(project, region):
    addresses = []
    request = service.addresses().list(project=project, region=region)
    while request is not None:
        response = request.execute()

        for address in response['items']:
            addresses.append(address['address'])

        request = service.addresses().list_next(previous_request=request, previous_response=response)

    return addresses

def lookup_all_addresses():
    all_addresses = []

    for p in projects:
        addresses = lookup_addresses(p, region)

        for a in addresses:
            all_addresses.append(a)

    return all_addresses


all_addresses = lookup_all_addresses()
logging.info(all_addresses)
