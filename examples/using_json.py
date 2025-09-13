''' This example shows how to override the reader and build a config from JSON as well as write back to JSON format '''

import json

from martepy.marte2.reader import readApplication, TreeNode
from martepy.marte2.configwriting import JSONConfigWriter

def buildTreeFromJSON(self, content):
        """Read JSON string content and parse it into TreeNode classes for later interpretation"""
        root = TreeNode("root")

        def walk(value, parent, name=""):
            if isinstance(value, dict):
                # dictionaries become TreeNodes with children
                node = TreeNode(name, parent)
                parent.addChild(node)
                for k, v in value.items():
                    walk(v, node, k)
            elif isinstance(value, list):
                # lists get indexed children
                if parent.parameters['Class'] == 'RealTimeThread':
                    # Hacky fix for how functions are shown differently between cfg and json here
                    # where json is a list and cfg is a string list encapsulated with '{}'
                    # Shoulw be a parameter of parent
                    parent.parameters['Functions'] = "{ " + " ".join(value) + " }"
                else:
                    node = TreeNode(name, parent)
                    parent.addChild(node)
                    for idx, v in enumerate(value):
                        walk(v, node, f"[{idx}]")
            else:
                # primitives become parameters
                parent.addParameter(name, str(value))

        data = json.loads(content)
        walk(data, root, "json")
        return root.children[0]

# Read JSON
app, state_machine, http_browser, http_messages = readApplication("output.json", readFunc=buildTreeFromJSON)


# Write to JSON
str(app.writeToConfig(JSONConfigWriter()))