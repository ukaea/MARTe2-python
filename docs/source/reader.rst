.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Reader
======

.. toctree::
   :maxdepth: -1

The MARTe2-Python repository whilst providing Python class representations of GAMs, DataSources and every object which makes up a MARTe2Application, also provides the functionality to read
a pre-existing .cfg file and input this into the pythonic MARTe2Application instance. To use it you can:

.. code:: python

    from martepy.marte2.reader import readApplication

    app, state_machine, http_browser, http_messages = readApplication(filename)

Where filename is the filename of your .cfg and app contains all aspects of the application. For simplifying coding, it also
returns any detected state machines, http browsers and http messages combined together as a tuple that you can seperate as in the above line.

*Note: if no state machine exists in the .cfg, one will be auto generated for the MARTe2Application instance*

*Note: The reader does not currently support importing types defined within a .cfg*
