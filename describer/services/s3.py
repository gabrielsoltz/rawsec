import logging
import boto3
from botocore.exceptions import ConnectTimeoutError, ClientError

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
           
            # Adding Bucket ACL
            get_bucket_acl = self.client.get_bucket_acl(
                Bucket=bucket['Name'],
            )
            bucket['get_bucket_acl'] = get_bucket_acl['Grants']
            
            # Adding Bucket Policy and Status
            try:
                get_bucket_policy = self.client.get_bucket_policy(
                    Bucket=bucket['Name'],
                )
                get_bucket_policy = get_bucket_policy['Policy']
                get_bucket_policy_status = self.client.get_bucket_policy_status(
                                    Bucket=bucket['Name'],
                                ) 
                get_bucket_policy_status = get_bucket_policy_status['PolicyStatus']
            except ClientError as e:
                get_bucket_policy = []
                get_bucket_policy_status = []
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    pass
                    #print('\t NoSuchBucketPolicy')
                else:
                    pass
                    #print("unexpected error: %s" % (e.response))
            bucket['get_bucket_policy'] = get_bucket_policy
            bucket['get_bucket_policy_status'] = get_bucket_policy_status

            # Adding Website configuration
            try:
                get_bucket_website = self.client.get_bucket_website(
                    Bucket=bucket['Name'],
                )
            except ClientError as e:
                get_bucket_website = []
                if e.response['Error']['Code'] == 'NoSuchWebsiteConfiguration':
                    pass
                    #print('\t NoSuchWebsiteConfiguration')
                else:
                    pass
                    #print("unexpected error: %s" % (e.response))
            bucket['get_bucket_website'] = get_bucket_website

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
