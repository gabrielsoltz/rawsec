# Plugin Config
ACTION = 'public'
ALLOWED_SERVICES = [
    'ec2',
    'elb',
    'elbv2',
    'route53'
]

class Actioner(object):
    ACTION = ACTION

    def __init__(self, resources, values):
        self.action = ACTION
        self.resources = resources
        self.values = values
        self.parsed_resources = self.parse(self.resources)

    def parse_public(self, resources):

        PARSE_PUBLIC_OUTPUT = {}
                
        for identifier, resource in resources.items():
                        
            if resource['service'] in ALLOWED_SERVICES:
                resource[self.action] = {'targets': self.parse_public_service(resource)}
                PARSE_PUBLIC_OUTPUT[identifier] = resource

        return PARSE_PUBLIC_OUTPUT
    
    def parse_public_service(self, resource):
        targets = []
        
        if resource['service'] == 'ec2':
            # An instance can have multiple NICs.
            for nic in resource['data']["NetworkInterfaces"]:
                # A NIC can have multiple IPs.
                for ip in nic["PrivateIpAddresses"]:
                    # An IP may not have an association if it is only
                    # an RFC1918 address.
                    if "Association" in ip and "PublicIp" in ip["Association"]:
                        targets.append(
                            ip["Association"]["PublicIp"]
                        )
                                
        if resource['service'] == 'elb' or resource['service'] == 'elbv2':
            if resource['data']["Scheme"] == "internet-facing":
                targets.append(resource['data']["DNSName"])
        
        if resource['service'] == 'route53':
            if resource['data']['Config']["PrivateZone"] == False:
                for record in resource['data']['records']:
                    if record['Type'] in ('A', 'CNAME'):
                        targets.append(record['Name'])
        
        return targets        

    def parse(self, resources):

        PARSE_OUTPUT = {}

        PARSE_OUTPUT = self.parse_public(resources)

        return PARSE_OUTPUT

    def execute(self):
        return self.parsed_resources
            
                