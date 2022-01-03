import boto3

def aws_elb_arn(region, name, account):
    ''' Constructs an ARN for an ELB in the given region. '''
    return 'arn:aws:elasticloadbalancing:{0}:{1}:loadbalancer/{2}'.format(
        region,
        account,
        name,
    )

def aws_ec2_arn(region, identifier, account, resource='instance'):
    ''' Constructs an ARN for an EC2 resource in the given region. '''
    return 'arn:aws:ec2:{0}:{1}:{2}/{3}'.format(
        region,
        account,
        resource,
        identifier,
    )

def aws_route53_hz_arn(id):
    ''' Constructs an ARN for an Route53 HZ resource in the given region. '''
    return 'arn:aws:route53:::{0}'.format(
        id,
    )

def aws_account_id(sess=None):
    ''' Attempts to get the account id for the current AWS account. '''
    if not sess:
        client = boto3.client('sts')
    else:
        client = sess.client('sts')
    return client.get_caller_identity()["Account"]




