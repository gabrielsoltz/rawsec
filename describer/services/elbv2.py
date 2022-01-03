import logging
import boto3
from botocore.exceptions import ConnectTimeoutError

class Describer(object):
    SERVICE = 'elbv2'

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

        # Iterate over results until AWS no longer returns a 'NextMarker' in
        # order to ensure all results are retrieved.
        marker = ''
        while marker is not None:
            # Unfortunately, Marker=None or Marker='' is invalid for this API
            # call, so it looks like we can't just set this to a None value,
            # or use a ternary here.
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
            for elb in candidates["LoadBalancers"]:
                self.logger.debug(
                    "Inspecting ELBv2 instance %s", elb["LoadBalancerArn"],
                )

                identifier = elb["LoadBalancerArn"]
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
