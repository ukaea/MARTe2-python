# TODO:
# Write test that class_name gets retained

import pdb

import os

from martepy.marte2.factory import Factory

from ..utilities import top_lvl

def test_retention_of_class_names():
    test_obj = Factory()
    json_file = os.path.join(top_lvl, 'martepy', 'marte2', 'gams', 'gams.json')

    test_obj.loadRemote(json_file)
    json_file = os.path.join(top_lvl, 'martepy', 'marte2', 'datasources', 'datasources.json')
    test_obj.loadRemote(json_file)

    for name, obj in test_obj.classes.items():
        t_obj = obj()
        class_name = t_obj.class_name
        serial = t_obj.serialize()
        serial['Class name'] = 'bippity'
        blk_cls = test_obj.create(name)()
        blk = blk_cls.deserialize(serial)
        assert blk.class_name == class_name
