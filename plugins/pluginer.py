
import logging
import json
from tqdm.autonotebook import tqdm

import plugins.plugins

def get_logger():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - %(filename)s:%(funcName)s - [%(levelname)s] %(message)s'
    )
    return logger

def parse_values(plugin, values):
    for value in values:
        value_plugin = value.split(":")[0]
        if value_plugin == plugin:
            value_value = value.split(":")[1]
            return [value_value]
    return None

def run_pluginer(resources, actions, values=None):
    logger = get_logger()
    output = {}

    for plugin in tqdm(actions, "Running plugins: " + ", ".join(actions)):
        if values: values = parse_values(plugin, values)
        try:
            # Ensure a handler exists for this type of resource.
            hndl = getattr(plugins.plugins, plugin).Actioner(
                resources=resources, values=values
            )
        except AttributeError as err:
            logger.error(
                "Handler for %s plugin not found, skipping: %s",
                plugin,
                err
            )
            continue
        
        execute = hndl.execute()
        
        if execute is not False:
            output.update(execute)
        else:
            logger.error(
                "plugin %s error, skipping",
                plugin
            )
        
    output = remove_data(output)
    output = json.dumps(output, indent=2, sort_keys=True, default=str)
    print (output)
        
    return output

def remove_data(output):
    for identifier, resource in output.items():
        del resource['data']
    return output
        
    