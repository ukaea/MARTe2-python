.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Type Database
=============

.. toctree::
   :maxdepth: -1

The MARTe2Application instance uses our Type Database class to store fundamental and complex types of MARTe2 which it uses
when generating the error state and a simulation version of a given config using the Simulation Framework.

The Type Database stores types internally as a class definition of Type and Field which can be recursive. As files it supports storing these in header format, this header uses a UKAEA pre-defined format inline
with ITER usage of storing type definitions of SDN Types (SDN is a form of network layer which MARTe2 also supports).

The Type Database can also support exporting your types into a MARTe2 C++ format for compiling and creating libraries for.

The fundamental MARTe2 types are already built in.

The Type Database is used to replace signals for simulation and error states, knowing complex types beforehand is necessary for the frameworks to:

- Replace these types when they are not available in a given state or function.
- Write/log these types

The Type Database includes a template setup and is capable of outputting to C++ library format.

Using the toLibrary function you can generate C++ headers and source files that can be compiled and included in a MARTe .cfg to define a type.

You may also modify the template as per your needs.

Main user functions:
********************

.. autoclass:: martepy.marte2.type_database.TypeDBv2
    :members:


