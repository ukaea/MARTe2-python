''' Easy import of all available GAMs '''

from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.gams.constant_gam import ConstantGAM
from martepy.marte2.gams.ssm_gam import SSMGAM
from martepy.marte2.gams.simulink_gam import SimulinkGAM
from martepy.marte2.gams.conversion import ConversionGAM
from martepy.marte2.gams.expression_gam import ExpressionGAM
from martepy.marte2.gams.message_gam import MessageGAM
from martepy.marte2.gams.mux import MuxGAM
from martepy.marte2.gams.filter import FilterGAM
from martepy.marte2.gams.pid import PIDGAM
from martepy.marte2.gams.waveform_chirp import WaveformChirpGAM
from martepy.marte2.gams.waveform_points import WaveformPointsGAM
from martepy.marte2.gams.waveform_sin import WaveformSinGAM

__all__ = [
        'IOGAM',
        'ConstantGAM',
        'SSMGAM',
        'SimulinkGAM',
        'ConversionGAM',
        'ExpressionGAM',
        'MessageGAM',
        'MuxGAM',
        'FilterGAM',
        'PIDGAM',
        'WaveformChirpGAM',
        'WaveformPointsGAM',
        'WaveformSinGAM'
    ]
