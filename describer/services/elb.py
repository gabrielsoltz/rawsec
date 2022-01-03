import logging
import boto3
from botocore.exceptions import ConnectTimeoutError
from describer.helper import aws_elb_arn

class Describer(object):
    SERVICE = 'elb'

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
                    candidates = self.client.describe_load_balancers(
                        Marker=marker
                    )
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
            else:
                try:
                    candidates = self.client.describe_load_balancers()
                except ConnectTimeoutError as e:
                    self.logger.error("Error: {} Account: {} Service: {} Region: {}".format(e, self.account, self.SERVICE, self.region))
                    break
                
            # Check if we need to continue paging.
            if "NextMarker" in candidates:
                self.logger.debug(
                    "'NextMarker' found, additional page of results to fetch"
                )
                marker = candidates["NextMarker"]
            else:
                marker = None

            # For some odd reason the AWS API doesn't appear to allow a
            # filter on describe operations for ELBs, so we'll have to filter
            # manually.
            for elb in candidates["LoadBalancerDescriptions"]:
                self.logger.debug(
                    "Inspecting ELB %s", elb["LoadBalancerName"],
                )
                
                identifier = aws_elb_arn(self.region,elb["LoadBalancerName"],self.account)
                resource = {
                    "service": self.SERVICE,
                    'account': self.account,
                    'region': self.region,
                    "identifier": identifier,
                    "data": elb
                }
                resources[identifier] = resource

        self.logger.info("Got %s resources", len(resources))
        return resources
