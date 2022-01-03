import logging
import boto3
from botocore.exceptions import ConnectTimeoutError

from describer.helper import aws_s3_bucket_arn

class Describer(object):
    SERVICE = 's3'

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
        list_buckets = self.client.list_buckets()
        
        for bucket in list_buckets['Buckets']:
           
            # Adding ACL
            # list_resource_records_sets = self.client.list_resource_record_sets(
            #     HostedZoneId=hz['Id'],
            # )
            # hz['records'] = list_resource_records_sets['ResourceRecordSets']
            
            # Adding WEB
            
            identifier = aws_s3_bucket_arn(bucket['Name'])
            
            resource = {
                "service": self.SERVICE,
                'account': self.account,
                'region': self.region,
                "identifier": identifier,
                "data": bucket
            }
            resources[identifier] = resource
            
        self.logger.info("Got %s resources", len(resources))
        return resources
