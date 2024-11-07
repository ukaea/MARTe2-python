.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Factory
=======

.. toctree::
   :maxdepth: -1

The factory is a factory class which allows us to load GAMs and Datasource definitions as classes into a factory method and then create object instances of them through their class_name in the factory.

In order for a GAM to support being imported into the factory, it must first have the function definition within the python file (not the class definition):

.. code:: python
    
    def initialize(factory, plugin_datastore) -> None:
        factory.registerBlock(f"{class_name}", {class}, plugin_datastore)

Where class is a reference to the class and class_name is the class_name as you want it to be called/loaded.

*Note: For best supportability, it must match the class_name as it appears in MARTe2 and we recommend to maintain consistency throughout with MARTe2 namings. Otherwise these may not be read in as easily.*

*Note: You can have multiple instances of factory.registerBlock in the initialize function to register your class under multiple class_names in the factory*

You must then create a json of the format similar to below which gives a name and a reference to the python module path which you then pass to the factory.

The factory will then iterate all items in the dictionary and load each python file. When it loads the file, it expects the initialize function and calls it, passing it a reference to itself.
This function then registers the classes defined in that python file with the factory for later recall.

.. code:: json
    
    {
        "constant": "martepy.marte2.gams.constant_gam",
        "conversion": "martepy.marte2.gams.conversion",
        "expression": "martepy.marte2.gams.expression_gam",
        "iogam": "martepy.marte2.gams.iogam",
        "message": "martepy.marte2.gams.message_gam",
        "mux": "martepy.marte2.gams.mux",
        "ssm": "martepy.marte2.gams.ssm_gam",
        "waveformsin": "martepy.marte2.gams.waveform_sin",
        "waveformchirp": "martepy.marte2.gams.waveform_chirp",
        "waveformpoints": "martepy.marte2.gams.waveform_points",
        "pid": "martepy.marte2.gams.pid",
        "filter": "martepy.marte2.gams.filter"
    }

