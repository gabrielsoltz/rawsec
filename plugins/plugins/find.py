# Plugin Config
ACTION = 'find'

class Actioner(object):
    ACTION = ACTION

    def __init__(self, resources, values):
        self.action = ACTION
        self.resources = resources
        self.values = values
        self.parsed_resources = self.parse(self.resources)
        
    def parse(self, resources):
        return resources

    def execute(self):
        
        EXECUTE_OUTPUT = {}
        
        for identifier, resource in self.parsed_resources.items():
            FINDINGS = []
            # First Level Search
            # for key, value in resource.items():
            #     if key != 'data':
            #         if search in str(value):
            #             print ('Found:', search, 'in resource:', resource['identifier'], 'in key:', key, resource[key])
            # Second Level Search (Data)
            for search in self.values:
                if str(search).lower() in str(resource['data']).lower():
                    for data_key, data_value in resource['data'].items():
                        if not isinstance(data_value, str):
                            if search.lower() in str(data_value).lower():
                                FINDINGS.append({data_key, str(data_value)})
                        else:
                            if search.lower() in data_value.lower():
                                FINDINGS.append({data_key, data_value})
                    resource[self.action] = {'output': FINDINGS}
                    EXECUTE_OUTPUT[identifier] = resource
                    
        return EXECUTE_OUTPUT