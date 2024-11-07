"""A Generic factory implementation that can generate and work with any MARTe1ConfigObject
 or inheriting object.

Place thing function in each python file of something that can be loaded into the Factory:

def initialize(factory, plugin_datastore) -> None:
    factory.registerBlock("{class name to be used}", {class in file to use}, plugin_datastore)

"""

import importlib
import json

class Factory:
    ''' The general factory method, should work with any object that in it's python file
    contains an initialize method which calls and uses the register block. '''
    def __init__(self):
        self.classes = {}

    def importModule(self, name: str):
        ''' Imports a python file '''
        return importlib.import_module(name) # type: ignore

    def unloadAll(self):
        ''' Reset our loaded class instances '''
        self.classes = {}

    def loadRemote(self, path):
        ''' Load from a given JSON definition file '''
        with open(path, 'r', encoding='UTF-8') as json_file:
            plugins = json.load(json_file).values()
        self.loadPlugins(plugins, self.classes)

    def loadPlugins(self, plugins, plugin_datastore) -> None:
        """Load the plugins defined in the plugins list."""
        for plugin_name in plugins:
            plugin = self.importModule(plugin_name)
            plugin.initialize(self, plugin_datastore)

    def registerBlock(self, class_name: str, block_class: object, plugin_datastore):
        ''' Register a class instance into our plugin datastore - typically self.classes '''
        plugin_datastore[class_name] = block_class

    def unregisterBlock(self, class_name: str):
        ''' Unregister a given class instance from our list '''
        try:
            self.classes.pop(class_name)
        except KeyError:
            raise ValueError(f"Unknown block type {class_name}") # pylint: disable=W0707

    def create(self, block_type = "and"):
        """Create a block of a specific type, given an initblock."""
        try:
            return self.classes[block_type]
        except KeyError:
            raise ValueError(f"Unknown block type {block_type}") # pylint: disable=W0707

    def getAll(self):
        ''' Get an instance of all registered block classes. '''
        return list(self.classes.values())
