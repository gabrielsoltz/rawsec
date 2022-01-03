import logging
import boto3
from botocore.exceptions import ConnectTimeoutError

class Describer(object):
    SERVICE = 'cloudfront'

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
                    list_distributions = self.client.list_distributions(
                        Marker=marker
                    )
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
            else:
                try:
                    list_distributions = self.client.list_distributions()
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
        
            # Check if we need to continue paging.
            if "NextMarker" in list_distributions:
                self.logger.debug(
                    "'NextMarker' found, additional page of results to fetch"
                )
                marker = list_distributions["NextMarker"]
            else:
                marker = None
        
        for distribution in list_distributions['DistributionList']['Items']:

            identifier = distribution['ARN']
            resource = {
                "service": self.SERVICE,
                'account': self.account,
                'region': self.region,
                "identifier": identifier,
                "data": distribution
            }
            resources[identifier] = resource

        self.logger.info("Got %s resources", len(resources))
        return resources
