import boto3
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)

client = boto3.client('route53')


def list_all_hosted_zones() -> List:
    logging.info("Getting hosted zones...")

    marker = None
    truncated = True
    all_zones = []

    response = client.list_hosted_zones()

    for zone in response['HostedZones']:
        all_zones.append(zone)

    truncated = response['IsTruncated']
    if truncated:
        marker = response['NextMarker']

    while truncated:
        response = client.list_hosted_zones(Marker=marker)

        for zone in response['HostedZones']:
            all_zones.append(zone)

        truncated = response['IsTruncated']

        if truncated:
            marker = response['NextMarker']

    for z in all_zones:
        logging.info(z['Name'])
    logging.info(f"Found {len(all_zones)} zones")

    return all_zones

def list_all_resource_record_sets(zone_id, zone_name) -> Dict:
    """Returns all the resource record sets, including if they are
    truncated and we have to make another request."""
    all_recordsets = []
    rs = client.list_resource_record_sets(HostedZoneId=zone_id)

    for r in rs['ResourceRecordSets']:
        all_recordsets.append(r)

    truncated = rs['IsTruncated']

    while truncated:
        next_record_name = rs['NextRecordName']
        logging.info(f'Getting records starting with {next_record_name}')
        rs = client.list_resource_record_sets(
                HostedZoneId=zone_id,
                StartRecordName=next_record_name
        )

        truncated = rs['IsTruncated']

        for r in rs['ResourceRecordSets']:
            all_recordsets.append(r)


    return all_recordsets


def query_dns_records(zones) -> Dict:
    """Query all the DNS records for the zones lsst.cloud and lsst.codes.
    This returns a dict that is keyed on hostname and the value is a list
    of IP addresses associated with that hostname."""

    lookup = {}

    for zone in zones:
        zone_name = zone['Name']

        # Limit zones that we're searching to lsst.cloud and lsst.codes,
        # to avoid IT managed zones.
        if zone_name not in ['lsst.cloud.', 'lsst.codes.']:
            continue

        logging.info(zone_name)
        all_recordsets = list_all_resource_record_sets(zone['Id'], zone['Name'])

        for recordset in all_recordsets:
            if 'ResourceRecords' in recordset:
                records = recordset['ResourceRecords']

                if recordset['Type'] == 'A':
                    name = recordset['Name']
                    addresses = []

                    for record in records:
                        addresses.append(record['Value'])

                    logging.info(f"[{name}: {addresses}")
                    lookup[name] = addresses

    return lookup

if __name__ == "__main__":
    zones = list_all_hosted_zones()
    hosts = query_dns_records(zones)

    for h in hosts:
        logging.info(f"{h}: {hosts[h]}")
