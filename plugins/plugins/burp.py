import burpsuite
import contextlib
from tqdm.autonotebook import tqdm
import time
from plugins.plugins.public import Actioner as ActionerPublic

# Plugin Config
ACTION = 'burp'
ALLOWED_SERVICES = [
    'ec2',
    'elb',
    'elbv2',
    'route53',
    'es',
    'cloudfront'
]
SERVER_URL= 'http://127.0.0.1:1337/'
API_KEY = ''
options = {
    "crawler":{
        "crawl_optimization":{
            "crawl_strategy":"fastest"
        },
        "crawl_limits":{
            "maximum_crawl_time":10,
            "maximum_request_count":0,
            "maximum_unique_locations":1500
        }
    },
    "scanner":{
        "issues_reported":{
            "scan_type_intrusive_active": True,
            "scan_type_javascript_analysis": True,
            "scan_type_light_active": True,
            "scan_type_medium_active": True,
            "scan_type_passive": True,
            "select_individual_issues": True,
            "store_issues_within_queue_items": True
        }
    },
    "urls": [],
}

class Actioner(object):
    ACTION = ACTION

    def __init__(self, resources, values):
        self.action = ACTION
        self.resources = resources
        self.values = values
        self.parsed_resources = self.parse(self.resources)
        self.burp_api_client = burpsuite.BurpSuiteApi(server_url=SERVER_URL, api_key=API_KEY)

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
            for target in resource[self.action]['targets']:
                options['urls'] = [target]
                try:
                    burp_id = self.burp_api_client.initiate_scan(options=options)
                except burpsuite.exceptions.AuthorizationError:
                    return False
                progress = ''
                while not (progress == 'paused' or progress == 'succeeded' or progress == 'failed'):
                    time.sleep(5)
                    with contextlib.redirect_stdout(None):
                        scan = self.burp_api_client.get_scan(task_id=burp_id)
                    progress = scan['scan_status']
                resource[self.action] = {'target': target, 'output': scan}
                EXECUTE_OUTPUT[identifier] = resource        
        
        return EXECUTE_OUTPUT




