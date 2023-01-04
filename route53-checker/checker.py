import boto3
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)

client = boto3.client('route53')


def list_all_resource_record_sets(zone_id) -> Dict:
    """Returns all the resource record sets, including if they are
    truncated and we have to make another request."""
    all_recordsets = []
    rs = client.list_resource_record_sets(HostedZoneId=zone_id)

    for r in rs['ResourceRecordSets']:
        all_recordsets.append(r)

    truncated = rs['IsTruncated']

    while truncated:
        next_record_name = rs['NextRecordName']
        logging.info('Getting records starting with %s' % next_record_name)
        rs = client.list_resource_record_sets(
                HostedZoneId=zone_id,
                StartRecordName=next_record_name
        )

        truncated = rs['IsTruncated']

        for r in rs['ResourceRecordSets']:
            all_recordsets.append(r)


    logging.info("Printing all recordsets")
    logging.info(all_recordsets)
    return all_recordsets


def query_dns_records() -> Dict:
    """Query all the DNS records for the zones lsst.cloud and lsst.codes.
    This returns a dict that is keyed on hostname and the value is a list
    of IP addresses associated with that hostname."""

    logging.info("Getting hosted zones...")
    response = client.list_hosted_zones()
    lookup = {}

    for zone in response['HostedZones']:
        zone_name = zone['Name']

        if zone_name not in ['lsst.cloud.', 'lsst.codes.']:
            continue

        logging.info(zone_name)
        logging.info(zone)
        all_recordsets = list_all_resource_record_sets(zone['Id'])
        logging.info(all_recordsets)

        for recordset in all_recordsets:
            if 'ResourceRecords' in recordset:
                records = recordset['ResourceRecords']

                if recordset['Type'] == 'A':
                    logging.debug(recordset)
                    logging.debug(records)
                    
                    name = recordset['Name']
                    addresses = []

                    for record in records:
                        addresses.append(record['Value'])

                    logging.info("[%s : %s]" % (name, addresses))
                    lookup[name] = addresses

    return lookup


hosts = query_dns_records()
logging.info(hosts)
