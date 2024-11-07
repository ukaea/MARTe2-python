.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Components
==========

.. toctree::
   :maxdepth: -1

Creating a new component can be fairly simple, we recommend to utilise the factory method so whenever you create a new component the file must include (generally at the end), the following:

.. code:: python
    
    def initialize(factory, plugin_datastore) -> None:
        factory.registerBlock(f"{class_name}", {class}, plugin_datastore)

Where class is a reference to the class and class_name is the class_name as you want it to be called/loaded.

Review the factory documentation and create a json file correspondingly for your class definition.

The class definition itself is the divided between whether you are creating a GAM or DataSource or other object.

Code styling rules
*******************

In all cases:

- A parameter of these items as they exist in MARTe2 should be an attribute of the class and be all lowercase with spaces replaced with underscores.
- You must have a serialize and deserialize function which places parameters under the parameters key or expects them here, i.e. res['parameters'].
- If you intend to use these in the XMARTe2 GUI, all GAMs and DataSource must have the loadParameters function.
- All objects must provide configuration_name as initialization and use the super().__init__() function to pass this argument along to the base classes.
- All objects must have a class_name defined, either overriding this in the initialization function of passing this along to the base classes as an argument as described above for configuration name.

Note: If you ever want to simplify the name/labels or your objects whilst maintaining their class name as defined in MARTe2 configurations, you can override this in the serialization functions:

.. code:: python

   # PID GAM as an example where we override it's label from it's class_name MathExpressionGAM
   def serialize(self):
        res = super().serialize()
        res['parameters']['expression'] = self.expression
        res['parameters']['Class name'] = 'ExpressionGAM'
        res['label'] = "ExpressionGAM"
        res['block_type'] = 'ExpressionGAM'
        res['class_name'] = 'ExpressionGAM'
        res['title'] = f"{self.configuration_name} (ExpressionGAM)"
        return res

If you want to enforce the inputs/outputs of a GAM/DataSource you can do so by defining input_signals or/and output_signals as properties of the class, we do this in the LinuxTimer like so:

.. code:: python

   @property
   def output_signals(self):
        return [('Counter',{'MARTeConfig':{'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                 ('Time',{'MARTeConfig':{'Type': 'uint32', 'Frequency': self.frequency, 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                  ('AbsoluteTime',{'MARTeConfig':{'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                   ('DeltaTime',{'MARTeConfig':{'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                    ('TrigRephase',{'MARTeConfig':{'Type': 'uint8', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}})]

Writing a GAM
**************

For this walkthrough we'll use the PID GAM example, as it is a good example simple enough to understand but complex enough that it has both inputs and outputs and also contains parameters.

To start with, initialize your class with your inputs, outputs and parameters and assign your parameters to the attribute names within your class, matching the format specified before.

.. code:: python

   from martepy.marte2.gam import MARTe2GAM

   class PIDGAM(MARTe2GAM):
      def __init__(self,
                     configuration_name: str = 'PID',
                     input_signals: list = [],
                     output_signals: list = [],
                     kp = 0.0,
                     ki = 0.0,
                     kd = 0.0,
                     samplefrequency = 1.0,
                     maxoutput = 1.0,
                     minoutput = 0.0
                  ):
         super().__init__(
                  configuration_name = configuration_name,
                  class_name = 'PIDGAM',
                  input_signals = input_signals,
                  output_signals = output_signals,
               )
         self.kp = kp
         self.ki = ki
         self.kd = kd
         self.samplefrequency = samplefrequency
         self.maxoutput = maxoutput
         self.minoutput = minoutput

*Note: it must inherit from the MARTe2GAM class definition*

*Note: How the attribute names match the MARTe2 Parameter name but all lowercase*

If a GAM does not have any parameters, writeGamConfig can simply be ommitted or pass. If it does have a parameter in it's MARTe2 configuration, you need to have this written in the function, take a look at the PID GAM as an example:

.. code:: python
    
   def writeGamConfig(self, config_writer):
        config_writer.writeNode("kp",self.kp)
        config_writer.writeNode("ki",self.ki)
        config_writer.writeNode("kd",self.kd)
        config_writer.writeNode("sampleFrequency",self.samplefrequency)
        config_writer.writeNode("maxOutput",self.maxoutput)
        config_writer.writeNode("minOutput",self.minoutput)

As mentioned, for all objects/GAMs/DataSource you need to also define a serialize and de-serialize function:

.. code:: python

    def serialize(self):
        res = super().serialize()
        res['parameters']['kp'] = self.kp
        res['parameters']['ki'] = self.ki
        res['parameters']['kd'] = self.kd
        res['parameters']['samplefrequency'] = self.samplefrequency
        res['parameters']['maxoutput'] = self.maxoutput
        res['parameters']['minoutput'] = self.minoutput
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        res = super().deserialize(data, hashmap, restore_id)
        # Now we build up 
        self.kp = data['parameters']["kp"]
        self.ki = data['parameters']["ki"]
        self.kd = data['parameters']["kd"]
        self.samplefrequency = data['parameters']["samplefrequency"]
        self.maxoutput = data['parameters']["maxoutput"]
        self.minoutput = data['parameters']["minoutput"]
        return self


Writing a DataSource
*********************

Writing a Datasource is very similar to writing a GAM except that you inherit from the MARTe2DataSource like below, we'll use the SDN Publisher example for similar reasons as to using PID for GAM:

.. code:: python

   from martepy.marte2.datasource import MARTe2DataSource

   class SDNPublisher(MARTe2DataSource):
      def __init__(self,
                    configuration_name: str = 'SDNPublisher',
                    input_signals = [],
                    topic: str = 'name',
                    interface: str = 'name',
                    address: str = '',
                    network_byte_order: int = 1,
                    source_port = '',
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'SDNPublisher',
                input_signals = input_signals,
                writing_gams = writing_gams,
            )
        self.topic = topic
        self.interface = interface
        self.port = source_port
        self.address = address
        self.byte_order = network_byte_order

And instead of writeGamConfig you use writeDatasourceConfig as the function prototype:

.. code:: python

   def writeDatasourceConfig(self, config_writer):
        config_writer.writeNode('Topic', '{:s}'.format(self.topic))
        config_writer.writeNode('Interface', '{:s}'.format(self.interface))
        config_writer.writeNode('NetworkByteOrder', '{:d}'.format(self.byte_order))
        if self.address != '':
            config_writer.writeNode('Address', '{:s}'.format(self.address))
        if self.port != '':
            config_writer.writeNode('SourcePort', '{:s}'.format(self.port))
        self.writeInputSignals(config_writer, section = 'Signals')

Writing an Object
******************

For any other object define in MARTe2 you can define these components also, these typically aren't loaded as Factory items but instead explicitly imported and used in code later.

These objects inherit from MARTe2ConfigObject which is the base class for all MARTe2 Pythonic classes. 

.. code:: python

    from martepy.marte2.config_object import MARTe2ConfigObject

   class MARTe2RealTimeState(MARTe2ConfigObject):
      ''' Object for configuring RealTimeStates for MARTe2 applications '''
      def __init__(self,
                     configuration_name: str = '+State',
                     threads: list = [],
                  ):
         super().__init__()
         self.configuration_name = configuration_name
         self.class_name = 'RealTimeState'
         self.threads = threads

Instead however the base class uses a similar but simpler name for writing which is write. In this case however you must define note just the parameters but the encapsulating sections.

A section is opened with startSection and does not require you to define a class, whereas startClass requires and defines the Class. In both cases, a name should be given however for the config_writer to know,
how to close the section/class when you call endSection/EndClass.

When you write startSection:

.. code:: python

   config_writer.startSection(self.configuration_name)
   config_writer.endSection(self.configuration_name)

This will generate:

   +MyConfigName{
   }

When you write startClass:

.. code:: python

   config_writer.startClass(self.configuration_name, self.class_name)
   config_writer.EndClass(self.configuration_name)

This will generate:

   +MyConfigName{
       Class = MyExampleClass
   }
   

So for example, when writing a RealTimeState Object we have:

.. code:: python:

      def write(self, config_writer):
         config_writer.startClass(self.configuration_name, self.class_name)
         config_writer.startClass('+Threads', 'ReferenceContainer')
         for i in self.threads:
               i.write(config_writer)
         config_writer.endSection('+Threads')
         config_writer.endSection(self.configuration_name)

Serialize and deserialize are very similar, if your object contains subobjects, you can store these into the dictionary but you must self manage their serialize and deserialization to maintain these object definitions. In this case, our RealTimeState contains a list of RealTimeThread objects:

.. code:: python

      def serialize(self):
         res = super().serialize()
         res['class_name'] = self.class_name
         if len(self.threads) > 0:
               res['threads'] = [a.serialize() for a in self.threads]
         else:
               res['threads'] = []
         return res

      def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, factory=None) -> bool:
         super().deserialize(data, hashmap, restore_id, factory=factory)
         self.class_name = data["class_name"]
         self.threads = [factory.create(a['class_name'])().deserialize(a, factory=factory) for a in data["threads"]]
         return self

*Note: All objects should have the factory as a parameter input, if they contain a list of objects as an attribute they should use the factory to create and deserialize these objects. This also means you need to define these objects into a json and pass this to your factories.*

Writing loadParameters functions
*********************************

For loading a GAM or Datasource into the GUI you must define a static method for the class called loadParameters with the function prototype loadParameters(mainpanel_instance, node).

*Note If you do not want the user to configure this node then pass the function.*

If your GAM provides output signals it's useful to identify the first GAMDataSource in the application with the lines:

.. code:: python

   app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
   datasource = app_def.configuration['misc']['gamsources'][0]

*Note: the following functions proceeding, require you import the qt_functions python file:*

.. code:: python

   from martepy.marte2.qt_functions import addLineEdit

To define a GAM with configurable inputs you can use the addInputSIgnalsSection function:

.. code:: python

   # Function Prototype: def addInputSignalsSection(mainpanel_instance, node, pack=True, samples=False, datasource=None, epics=False)
   addInputSignalsSection(mainpanel_instance, node, False)

*Note: Pack will add a spacer at the end of an Input/Output section to properly align this into the grid, set this to false if you have both inputs and outputs and True if only one is user configurable.*

*Note: By Setting samples to true, an additional column will appear in the signal configuration window for the user allowing them to set the Number of Samples, this is useful for GAMs like the MUX GAM.*

*Note: Setting the datasource to anything but False, 0, [] or None is useful for ot allowing the user to change this in the signal naming window.*

*Note: Setting epics provides the user with the column option PVName for each signal when set to True*

To add the ability to create and define output signals you can use:

.. code:: python

   # Function Prototype: def addOutputSignalsSection(mainpanel_instance, node, start = 0, pack=True, datasource=None, samples=False, default=False, epics=False)
   addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)

*Note: start denotes the starting row in the grid layout that is mainpanel_instance, it should generally always be 3.*

*Note: Default is primarily used for the ConstantGAM and provides the user with the column option Default to set for a signal. Default is a special flag in MARTe2, do not use it with signals which should not have a Default set or the configuration may fail.*

For parameters, you can define a line edit for text/number input with addLineEdit:

.. code:: python

   # Function Prototype: addLineEdit(mainpanel_instance, node, lbl_name, para_name, row, col_start)
   addLineEdit(mainpanel_instance, node, "Kp: ", 'kp', 3, 0)

*Note: para_name must match the classes attribute name for the said parameter.*

*Note: row and col_start denote the items position in the Grid Layout of mainpanel_instance.*

If your GAM/DataSource has a parameter with only a specific list of possible values you can use the addComboEdit function instead of addLineEdit:

.. code:: python

   # Function Prototype: def addComboEdit(mainpanel_instance, node, lbl_name, para_name, row, col_start, items)
   addComboEdit(mainpanel_instance, node,"Execution mode: ", 'execution_mode', 3, 0, ['IndependentThread', 'RealTimeThread'])

*Note: Items is the list of possible values for the ComboBox.*

Below is an example of the PID GAM GUI definition as it contains parameters, inputs and outputs:

.. code:: python

   @staticmethod
   def loadParameters(mainpanel_instance, node):
        '''
        This function is intended to be for the GUI where it can call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        '''

        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False)
        
        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)
        
        addLineEdit(mainpanel_instance, node, "Kp: ", 'kp', 3, 0)
        
        addLineEdit(mainpanel_instance, node, "Ki: ", 'ki', 3, 2)
        
        addLineEdit(mainpanel_instance, node, "Kd: ", 'kd', 4, 0)
        
        addLineEdit(mainpanel_instance, node, "Sample Frequency: ", 'samplefrequency', 4, 2)
        
        addLineEdit(mainpanel_instance, node, "Max Output: ", 'maxoutput', 5, 0)
        
        addLineEdit(mainpanel_instance, node, "Min Output: ", 'minoutput', 5, 2)

Loading these into the GUI
***************************

Once you have created a new set of GAMs/DataSources, you will need to create a json file as described in the factory documentation.
If you wish to then bring these into the GUI, you must then create a XMARTe2 Plugin which loads the factory into the application.