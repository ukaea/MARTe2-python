.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Useful Functions
=====================

This document outlines some of the useful functions available in MARTe2-Python for a application.

MARTe2Application
*****************

The MARTe2Application instance is the first place to start, not only is it the central class of this repository and how
to construct a MARTe2 Application, it contains very useful functions which are described further below.

.. automodule:: martepy.marte2.generic_application.MARTe2Application
    :members:

CPU Configurator
****************

The CPU Configurator function is fairly useful, simply copy and paste the below code into your python to convert numeric CPU configuration to their hexadecimal equivalent.

.. code:: python

    CPU_OFFSET_FROM_ONE = 0  # 0 to start at cpu 1
    def cpu_thread_gen(x):
        ''' Generate a cpu core to used based on thread number x and pre-defined offset from core 1. '''
        return str(hex(2 ** (x + CPU_OFFSET_FROM_ONE)))
    
GAM Functions
*************

.. automodule:: martepy.functions.gam_functions
    :members:

Extra Functions
***************

.. automodule:: martepy.functions.extra_functions
    :members:

Bin2CSV
*******

The Bin2CSV tool can be used to parse a binary file generated in MARTe2 into a CSV file. It currently supports arrays and singles of int32, uint32, float32, uint64, float64, uint16, uint8.

*Note: User specific types cannot be incorporated into the FileReader and need to be split out*

Usage:

.. code:: python

    conv = Bin2CSV(source_binary, output_csv)
    conv.main()
    