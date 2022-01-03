#!/usr/bin/env python3

import os
import logging
from boto3 import Session

from describer.helper import aws_account_id
import describer.services

def lambda_handler(event, context):
    regions = os.getenv("RAWSEC_REGIONS", "eu-west-1").split(",")
    services = os.getenv("RAWSEC_SERVICES", "ec2").split(",")
    resources = run_describer(services, regions)
    return resources

def get_logger():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - %(filename)s:%(funcName)s - [%(levelname)s] %(message)s'
    )
    return logger

def get_boto3_session(session):
    tmp_access_key = session['aws_access_key_id']
    tmp_secret_key = session['aws_secret_access_key']
    security_token = session['aws_session_token']

    boto3_session = Session(
        aws_access_key_id=tmp_access_key,
        aws_secret_access_key=tmp_secret_key, aws_session_token=security_token
    )
    return boto3_session

def run_describer(services, regions, session=None):
    logger = get_logger()
    output = {}
    
    # Accounts, Regions
    if session:
        session = get_boto3_session(session)
    account = aws_account_id(session)
    
    logger.info("Running in AWS account %s services %s regions %s", account, ", ".join(services), ", ".join(regions))

    for region in regions:
        logger.info("Attempting to enumerate resources in %s", region)

        for service in services:
            logger.info("Attempting to enumerate %s resources", service)
            
            try:
                # Ensure a handler exists for this type of resource.
                hndl = getattr(describer.services, service).Describer(
                    region=region, account=account, sess=session
                )
            except AttributeError as err:
                logger.error(
                    "Handler for %s resources not found, skipping: %s",
                    service,
                    err
                )
                continue

            output.update(hndl.get())
    
    return output

if __name__ == '__main__':
    lambda_handler(
        dict(),
        dict()
    )