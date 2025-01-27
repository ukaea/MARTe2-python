''' Mainly imports just the MARTe2Application instance and a basic GAM.'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.datasources import *
from martepy.marte2.gams import *
from martepy.marte2.objects import *
from martepy.marte2.generic_application import MARTe2Application

__all__ = [
    "MARTe2GAM",
    ]
