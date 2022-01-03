import logging
import boto3

class Describer(object):
    SERVICE = 'es'

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

        candidates = self.client.list_domain_names()

        for es in candidates["DomainNames"]:
            # Query for data about this domain based on the enumerated name.
            domain = self.client.describe_elasticsearch_domain(
                DomainName=es["DomainName"]
            )
            
            self.logger.debug("Inspecting ES domain %s", es["DomainName"])
            
            if domain["DomainStatus"]["Created"] == False:
                self.logger.debug(
                    "Skipping ES domain as it's still being provisioned"
                )
                continue

            if domain["DomainStatus"]["Deleted"] == True:
                self.logger.debug(
                    "Skipping ES domain as it's currently being deleted"
                )
                continue

            identifier = domain["DomainStatus"]["ARN"]
            resource = {
                "service": self.SERVICE,
                'account': self.account,
                'region': self.region,
                "identifier": identifier,
                "data": domain
            }
            resources[identifier] = resource

            
        self.logger.info("Got %s resources", len(resources))
        return resources
