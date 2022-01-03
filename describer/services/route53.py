import logging
import boto3
from botocore.exceptions import ConnectTimeoutError

from describer.helper import aws_route53_hz_arn

class Describer(object):
    SERVICE = 'route53'

    def __init__(self, region, account, sess=None):
        self.logger = logging.getLogger(__name__)
        self.account = account
        self.region = region
        if not sess:
            self.client = boto3.client(self.SERVICE, region_name=region)
        else:
            self.client = sess.client(self.SERVICE, region_name=region)

    def get(self):
        resources = {}
        
        marker = ''
        while marker is not None:
            if marker:
                try:
                    list_hosted_zones = self.client.list_hosted_zones(
                        Marker=marker
                    )
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
            else:
                try:
                    list_hosted_zones = self.client.list_hosted_zones()
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
        
            # Check if we need to continue paging.
            if "NextMarker" in list_hosted_zones:
                self.logger.debug(
                    "'NextMarker' found, additional page of results to fetch"
                )
                marker = list_hosted_zones["NextMarker"]
            else:
                marker = None
        
        for hz in list_hosted_zones['HostedZones']:
            # Zone
            identifier = aws_route53_hz_arn(hz['Id'])
            
            # Adding Records
            list_resource_records_sets = self.client.list_resource_record_sets(
                HostedZoneId=hz['Id'],
            )
            hz['records'] = list_resource_records_sets['ResourceRecordSets']
            
            resource = {
                "service": self.SERVICE,
                'account': self.account,
                'region': self.region,
                "identifier": identifier,
                "data": hz
            }
            resources[identifier] = resource
            
        self.logger.info("Got %s resources", len(resources))
        return resources
