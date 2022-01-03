import boto3
from botocore.exceptions import ClientError, InvalidRegionError, EndpointConnectionError
import logging

def get_logger():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s'
    )
    return logger

def aws_regions():
    logger = get_logger()
    ec2 = boto3.client('ec2', region_name='eu-west-1')
    try:
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    except ClientError as e:
        logger.error("Error gettion regions: {}".format(e))
        return False
    return regions

def aws_account_id():
    client = boto3.client('sts')
    return client.get_caller_identity()["Account"]

def aws_check_region(region):
    logger = get_logger()
    try:
        regional_sts = boto3.client('sts', region_name=region)
        try:
            regional_sts.get_caller_identity()
        except ClientError as e:
            logger.error("Error cheking region: {}".format(e))
            return False
        return True
    except ClientError as e:
        logger.error("Error cheking region: {}".format(e))
        return False
    except InvalidRegionError as e:
        logger.error("Error cheking region: {}".format(e))
        return False
    except EndpointConnectionError as e:
        logger.error("Error cheking region: {}".format(e))
        return False

def aws_assume_role(aws_account_number, role_name):
    """
    Assumes the provided role in each account and returns a client
    :param aws_account_number: AWS Account Number
    :param role_name: Role to assume in target account
    :param aws_region: AWS Region for the Client call, not required for IAM calls
    :return: client in the specified AWS Account and Region
    """
    logger = get_logger()
    # Beginning the assume role process for account
    sts_session = boto3.session.Session()
    sts_client = sts_session.client('sts')
    # Get the current partition
    partition = sts_client.get_caller_identity()['Arn'].split(":")[1]
    try:
        response = sts_client.assume_role(
            RoleArn='arn:{}:iam::{}:role/{}'.format(
                partition,
                aws_account_number,
                role_name,
            ),
            RoleSessionName='RAWSec',
            DurationSeconds=3600
        )
    except ClientError as e:
        logger.error("Error Assuming Role: {}".format(e))
        return False
    return {
        'aws_access_key_id': response['Credentials']['AccessKeyId'],
        'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
        'aws_session_token': response['Credentials']['SessionToken'],
    }
