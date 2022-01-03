import logging
import boto3


class Describer(object):
    SERVICE = 'rds'

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
                candidates = self.client.describe_db_instances(Marker=marker)
            else:
                candidates = self.client.describe_db_instances()

            # Check if we need to continue paging.
            if "Marker" in candidates:
                self.logger.debug(
                    "'Marker' found, additional page of results to fetch"
                )
                marker = candidates["Marker"]
            else:
                marker = None

            for rds in candidates["DBInstances"]:
                # Skip instances still being created as they may not yet have
                # endpoints created / generated.
                if rds["DBInstanceStatus"] == "creating":
                    self.logger.debug(
                        "Skipping instance as it's still being provisioned"
                    )
                    continue

                identifier = rds["DBInstanceArn"]
                resource = {
                    "service": self.SERVICE,
                    'account': self.account,
                    'region': self.region,
                    "identifier": identifier,
                    "data": rds
                }
                resources[identifier] = resource

        self.logger.info("Got %s resources", len(resources))
        return resources
