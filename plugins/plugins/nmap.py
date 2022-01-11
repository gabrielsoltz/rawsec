import nmap
from tqdm.autonotebook import tqdm
from multiprocessing.pool import ThreadPool
from plugins.plugins.public import Actioner as ActionerPublic


# Plugin Config
ACTION = 'nmap'
ALLOWED_SERVICES = [
    'ec2',
    'elb',
    'elbv2',
    'route53',
    'es',
    'cloudfront'
]
NMAP_NO_PING_PORTS = '-n -Pn -PE -p 21-23,80,3389'
NMAP_SYN_FAST = '-sS -F'
NMAP_ACK_FAST = '-sA -F'
NMAP_FIN_FAST = '-sF -F'
NMAP_UDP_FAST = '-sU -F'
NMAP_NOPING_FAST = '-Pn -F'

NMAP_ARGUMENTS = NMAP_NOPING_FAST

class Actioner(object):
    ACTION = ACTION

    def __init__(self, resources, values):
        self.action = ACTION
        self.resources = resources
        self.values = values
        self.parsed_resources = self.parse(self.resources)
        self.nm = nmap.PortScanner()
   
    def parse(self, resources):

        PARSE_OUTPUT = {}
                
        for identifier, resource in resources.items():
                        
            if resource['service'] in ALLOWED_SERVICES:
                
                public_targets = ActionerPublic(self.resources, self.values).parse_public_service(resource)
                if public_targets:
                    resource[self.action] = {'targets': public_targets}    
                    PARSE_OUTPUT[identifier] = resource

        return PARSE_OUTPUT
    
    def execute(self):
        
        EXECUTE_OUTPUT = {}
        for identifier, resource in tqdm(self.parsed_resources.items()):
            OUTPUT_LIST = []
            for target in resource[self.action]['targets']:
                scan = self.nm.scan(hosts=target, arguments=NMAP_ARGUMENTS)
                if scan['scan']:
                    OUTPUT_LIST.append({'target': target, 'output': scan['scan']})
                elif scan['nmap']['scaninfo']['error']:
                    OUTPUT_LIST.append({'target': target, 'output': scan['nmap']['scaninfo']['error'][0]})
                elif scan['nmap']['scaninfo']['warning']:
                    OUTPUT_LIST.append({'target': target, 'output': scan['nmap']['scaninfo']['warning'][0]})
            resource[self.action] = OUTPUT_LIST
            EXECUTE_OUTPUT[identifier] = resource
        
        return EXECUTE_OUTPUT
            
                