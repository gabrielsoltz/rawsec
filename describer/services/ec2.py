import logging
import boto3

from describer.helper import aws_ec2_arn

class Describer(object):
    SERVICE = 'ec2'

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
        filters = [
            {
                "Name": "instance-state-name",
                "Values": [
                    "pending",
                    "running",
                ],
            }
        ]

        next_token = ''
        while next_token is not None:
            if next_token:
                candidates = self.client.describe_instances(
                    Filters=filters,
                    NextToken=next_token
                )
            else:
                candidates = self.client.describe_instances(
                    Filters=filters
                )

            # Check if we need to continue paging.
            if "NextToken" in candidates:
                self.logger.debug(
                    "'NextToken' found, additional page of results to fetch"
                )
                next_token = candidates["NextToken"]
            else:
                next_token = None

            # A reservation can contain one or more instances
            for reservation in candidates["Reservations"]:
                self.logger.info(
                    "Inspecting reservation %s",
                    reservation["ReservationId"]
                )
                for instance in reservation["Instances"]:
                    self.logger.info(
                        "Inspecting instance %s", instance["InstanceId"]
                    )

                    identifier = aws_ec2_arn(self.region,instance["InstanceId"], self.account)
                    resource = {
                        "service": self.SERVICE,
                        'account': self.account,
                        'region': self.region,
                        "identifier": identifier,
                        "data": instance
                    }
                    resources[identifier] = resource

        self.logger.info("Got %s resources", len(resources))
        return resources
