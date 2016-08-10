"""
A module to declare, initialize and expose variables to all modules in the system.
"""
import json
import os

from safestore.providers.dispatcher import Dispatcher

__DISPATCHER = None

def get_dispatcher_instance():
    """
    Returns a singleton instance of Dispatcher.
    Returns:
        (Dispatcher) A singleton instance of Dispatcher
    """
    global __DISPATCHER
    if __DISPATCHER is None:
        # Dispatcher configuration
        configuration_file_path = os.path.join(os.path.dirname(__file__), "dispatcher.json")
        with open(os.path.join(configuration_file_path)) as dispatcher_configuration_file:
            dispatcher_configuration = json.load(dispatcher_configuration_file)
            __DISPATCHER = Dispatcher(dispatcher_configuration)
    return __DISPATCHER
