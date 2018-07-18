#! /usr/bin/env python
"""
Gets the amount of free space in at the providers in use by the pyproxy
"""

import json
import os

from pyproxy.pyproxy.providers import ProviderFactory


CONFIGURATION_PATH = os.path.join(os.path.dirname(__file__), "./dispatcher.json")

def get_quota_from_providers():
    """
    Clear the data in the storage providers listed in dispatcher.json
    """
    with open(CONFIGURATION_PATH, "r") as configuration_file:
        configuration = json.load(configuration_file)
    if not configuration.has_key('providers'):
        raise Exception("the configuration should have a 'providers' key")
    if not configuration.has_key('providers'):
        raise Exception("the providers value should be an array")
    provider_configurations = configuration.get('providers')
    data = []
    factory = ProviderFactory()
    for provider_configuration in provider_configurations:
        provider = factory.get_provider(provider_configuration)
        provider_configuration["free_space"] = provider.quota()
        data.append(provider_configuration)
    return data

if __name__ == "__main__":
    print json.dumps(get_quota_from_providers(), sort_keys=True, indent=4)
