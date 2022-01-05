#!/usr/bin/env python3

import argparse
import sys
import logging

from describer import describer
from plugins import pluginer
from helpers import aws_regions, aws_check_region, aws_account_id, aws_assume_role

AVAILABLE_SERVICES = [
    'rds',
    'ec2',
    'elb',
    'elbv2',
    'es',
    'cloudfront',
    'route53',
    's3'
]

AVAILABLE_PLUGINS = [
    'nmap',
    'burp',
    'inventory',
    'find',
    'public'
]

def get_parser():
    parser = argparse.ArgumentParser(prog='rawsec')
    parser.add_argument('-r', '--regions', nargs='*', help='List of AWS Regions. Example: -r us-east-1 eu-west-1. Default All regions')
    parser.add_argument('-s', '--services', nargs='*', help='List of AWS Services. Example: -s EC2 S3. Default: All Services')
    parser.add_argument('-a', '--accounts', nargs='*', help='List of AWS Accounts to describe. Example: -a 0123456789')
    parser.add_argument('-ro', '--role', help='List of AWS Accounts to describe. Example: -ro SecurityAudit')
    parser.add_argument('-p', '--plugins', nargs='*', help='Enabled plugins. Example: -p inventory nmap. Deafult: inventory')
    parser.add_argument('-v', '--values', nargs='*', help='Plugins values. Example: -v plugin:value')
    return parser

def get_logger():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - %(filename)s:%(funcName)s - [%(levelname)s] %(message)s'
    )
    return logger

def main(args):
    logger = get_logger()
    parser = get_parser()
    args = parser.parse_args(args)

    if args.regions:
        for region in args.regions:
            if aws_check_region(region) is False:
                logger.error('Error checking AWS Region: {}'.format(region))
                sys.exit(1)
        regions = args.regions
    else:
        regions = aws_regions()
        if regions is False:
            logger.error('Error getting AWS Regions')
            sys.exit(1)

    if args.services:
        if not set(args.services).issubset(AVAILABLE_SERVICES):
            logger.error('Error checking service: {}'.format(' '.join(args.services)))
            sys.exit(1)
        else:
            services = args.services
    else:
        services = AVAILABLE_SERVICES

    if args.accounts:
        accounts = args.accounts
        if not args.role:
            logger.error('Error AWS Account provided but not role. Use -ro <ROLE>')
            sys.exit(1)
        role = args.role
        for account in accounts:
            if not aws_assume_role(account, role):
                sys.exit(1)
    else:
        role = None
        accounts = aws_account_id()

    if args.plugins:
        if not set(args.plugins).issubset(AVAILABLE_PLUGINS):
            logger.error('Error checking plugin: {}'.format(' '.join(args.plugins)))
            sys.exit(1)
        else:
            plugins = args.plugins
    else:
        plugins = ['inventory']
    
    if args.values:
        values = args.values
        for value in values:
            value_plugin = value.split(":")[0]
            if not value_plugin in AVAILABLE_PLUGINS:
                logger.error('Error value plugin: {}'.format(value_plugin))
                sys.exit(1)
    else:
        values = None

    if role:
        resources = {}
        for account in accounts:
            session = aws_assume_role(account, role)
            resources.update(describer.run_describer(services, regions, session))
    else:
        resources = describer.run_describer(services, regions)
    
    pluginer.run_pluginer(resources, plugins, values)      

if __name__ == '__main__':
    main(sys.argv[1:])