# Plugin Config
ACTION = 'inventory'

class Actioner(object):
    ACTION = ACTION

    def __init__(self, resources, values):
        self.action = ACTION
        self.resources = resources
        self.values = values
        self.parsed_resources = self.parse(self.resources)
        
    def parse(self, resources):
        
        for identifier, resource in resources.items():
            resource['inventory'] = resource['data']

        return resources

    def execute(self):
        return self.parsed_resources