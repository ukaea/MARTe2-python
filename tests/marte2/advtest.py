from martepy.marte2.generic_application import MARTe2Application
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.gams.conversion import ConversionGAM
from martepy.marte2.gams.simulink_gam import SimulinkGAM
from martepy.marte2.gams.constant_gam import ConstantGAM
from martepy.marte2.datasources.timing_datasource import TimingDataSource
from martepy.marte2.datasources.linux_timer import LinuxTimer
from martepy.marte2.datasources.files.writer import FileWriter
from martepy.marte2.datasources.udp.sender import UDPSender
from martepy.marte2.datasources.logger_datasource import LoggerDataSource
from martepy.marte2.datasources.rt_syncbridge import Synchronisation
from martepy.marte2.datasources.udp.receiver import UDPReceiver
from martepy.marte2.datasources.gam_datasource import GAMDataSource
from martepy.marte2.objects.real_time_state import MARTe2RealTimeState
from martepy.marte2.gams.message_gam import MARTe2ReferenceContainer
from martepy.marte2.objects.real_time_thread import MARTe2RealTimeThread
from martepy.marte2.objects.gam_scheduler import MARTe2GAMScheduler
from martepy.marte2.objects.statemachine.machine import MARTe2StateMachine
from martepy.marte2.objects.statemachine.event import MARTe2StateMachineEvent
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.marte2.objects.http.objectbrowser import MARTe2HTTPObjectBrowser
from martepy.marte2.objects.http.directoryresource import MARTe2HttpDirectoryResource
from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface
from martepy.marte2.objects.http.service import MARTe2HttpService


App = MARTe2Application("App")


# Generate Functions
# 
_IOTime = IOGAM('IOTime', [('Counter', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Alias': 'Counter', 'Frequency': '10000'}}), ('Time', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Alias': 'Time'}}), ('AbsoluteTime', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint64', 'Alias': 'AbsoluteTime'}})], [('Counter', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'Counter'}}), ('Time', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'Time'}}), ('AbsoluteTime', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint64', 'Alias': 'AbsoluteTime'}})])

App.functions += [_IOTime]

_IO_FromUDP = IOGAM('IO_FromUDP', [('seq_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'usempc_in'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'useobs_in'}}), ('time_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'uint32', 'Alias': 'time_in'}})], [('seq_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'use_mpc'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'use_obs'}}), ('time_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'time_us_32'}})])

App.functions += [_IO_FromUDP]

_convert_seq = ConversionGAM('convert_seq', [('seq_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'seq_in'}})], [('seq_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'seq_inf'}})])

App.functions += [_convert_seq]

# Generate Parameters for SimulinkWrapperGAM SimulinkWrapperGAM

SimulinkWrapperGAM_params = []
SimulinkWrapperGAM_params += [{'parameter_name': 'param1', 'type': 'float64', 'presets': '0.005'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'param2', 'type': 'float64', 'presets': '0.005'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'de', 'type': 'float64', 'presets': '0.005'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'wf', 'type': 'int32', 'presets': '7'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'wr', 'type': 'int32', 'presets': '1'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'rtf', 'type': 'float32', 'presets': '{ 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.20000000298023224, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.4000000059604645, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.550000011920929, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'rfm', 'type': 'float32', 'presets': '{  { 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },  { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 } }'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'rhf', 'type': 'float32', 'presets': '{ 0.0003030500083696097, 0.0008929200121201575, 0.0026309099048376083, 0.007751789875328541, 0.02284008078277111, 0.06729663163423538, 0.19828499853610992, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'rkf', 'type': 'float32', 'presets': '{ 0.3497979938983917, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }'}]
SimulinkWrapperGAM_params += [{'parameter_name': 'rtj', 'type': 'float32', 'presets': '{ 0.30000001192092896, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }'}]


_SimulinkWrapperGAM = SimulinkGAM('SimulinkWrapperGAM', [('adv1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv1_in', 'Bus': 'adverIn'}}), ('adv2', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv2_in', 'Bus': 'adverIn'}}), ('adv3', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv3_in', 'Bus': 'adverIn'}}), ('Sequence', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'seq_inf', 'Bus': 'adverIn'}})], [('req1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output1', 'Bus': 'adverOut'}}), ('req2', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output2', 'Bus': 'adverOut'}}), ('req3', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output3', 'Bus': 'adverOut'}})],
                                    '/sim.so', 'sim', 2, 0, 0,
                                    '', 'Structured')

_SimulinkWrapperGAM.parameters = SimulinkWrapperGAM_params
                                    
App.functions += [_SimulinkWrapperGAM]

_IO_UDP_Out = IOGAM('IO_UDP_Out', [('devType', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_devType'}}), ('diagId', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_diagId'}}), ('version', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_version'}}), ('payloadSize', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'payloadSize'}}), ('shotNumber', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'shotNumber'}}), ('time_us_32', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'time_us_32'}}), ('seq_send', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('computed_adv1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output1'}}), ('computed_adv2', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output2'}}), ('computed_adv3', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output3'}}), ('computed_adv4', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output4'}}), ('computed_adv5', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output5'}})], [('devType', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint8'}}), ('diagId', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint8'}}), ('version', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint8'}}), ('payloadSize', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint8'}}), ('shotNumber', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint32', 'Alias': 'shotNumber'}}), ('timestamp', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint32'}}), ('seq_out', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'uint32'}}), ('adver1', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'float32'}}), ('adver2', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'float32'}}), ('adver3', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'float32'}}), ('adver4', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'float32'}}), ('adver5', {'MARTeConfig': {'DataSource': 'UDPSender', 'Type': 'float32'}})])

App.functions += [_IO_UDP_Out]

_IOLog = IOGAM('IOLog', [('time_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'time_us_32'}}), ('MWI_Out', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('Density', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('in3', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('in4', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('output1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output1'}}), ('output2', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output2'}}), ('output3', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output3'}}), ('output4', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output4'}}), ('output5', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output5'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'use_mpc'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'use_obs'}}), ('AbsoluteTime', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint64', 'Alias': 'AbsoluteTime'}}), ('SeqIn', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'seq_in'}})], [('time_in', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'uint32', 'Alias': 'time_in'}}), ('MWI_Out', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'MWI_Out'}}), ('Density', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'Density'}}), ('in3', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'in3'}}), ('in4', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'in4'}}), ('output1', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'output1'}}), ('output2', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'output2'}}), ('output3', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'output3'}}), ('output4', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'output4'}}), ('output5', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'output5'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'usempc'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float32', 'Alias': 'useobs'}}), ('AbsoluteTime', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'uint64'}}), ('SeqIn', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'uint32'}})])

App.functions += [_IOLog]

_IODataLogger = IOGAM('IODataLogger', [('time_in', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'time_us_32'}}), ('output5', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'float32', 'Alias': 'output5'}})], [('DisplayTime', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Type': 'uint32', 'Alias': 'DisplayTime'}}), ('DisplayOut5', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Type': 'float32', 'Alias': 'DisplayOut5'}})])

App.functions += [_IODataLogger]

_IO_UDP_In = IOGAM('IO_UDP_In', [('devType', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint8', 'Alias': 'devType'}}), ('diagId', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint8', 'Alias': 'diagId'}}), ('version', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint8', 'Alias': 'version'}}), ('payloadSize', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint8', 'Alias': 'payloadSize'}}), ('shotNumber', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint32', 'Alias': 'shotNumber'}}), ('timestamp', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint32', 'Alias': 'time_in'}}), ('sequence', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adver1', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'adver1'}}), ('adver2', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'adver2'}}), ('adver3', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'adver3'}}), ('adver4', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'adver4'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'Use_MPC'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'UDPReceiver', 'Type': 'float32', 'Alias': 'Use_OBS'}})], [('devType', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'devType'}}), ('diagId', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'diagId'}}), ('version', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'version'}}), ('payloadSize', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'payloadSize_in'}}), ('shotNumber', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'shotNumber_int'}}), ('time_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'time_in'}}), ('seq_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'usempc_in'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'useobs_in'}})])

App.functions += [_IO_UDP_In]

_DeviceConstants = ConstantGAM('DeviceConstants', [], [('zero', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'zero', 'Default': '0'}}), ('pcs_devType', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_devType', 'Default': '1'}}), ('payloadSize', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'payloadSize', 'Default': '5'}}), ('shotNumber', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'shotNumber', 'Default': '900045'}}), ('pcs_diagId', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_diagId', 'Default': '1'}}), ('pcs_version', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint8', 'Alias': 'pcs_version', 'Default': '1'}})])
        
App.functions += [_DeviceConstants]

_IO_UDP_ToModel = IOGAM('IO_UDP_ToModel', [('seq_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'usempc_in'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'useobs_in'}}), ('time_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'time_in'}})], [('seq_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'usempc_in'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'float32', 'Alias': 'useobs_in'}}), ('time_in', {'MARTeConfig': {'DataSource': 'RealTimeSynch', 'Type': 'uint32', 'Alias': 'time_in'}})])

App.functions += [_IO_UDP_ToModel]

_IOUDPLogger = IOGAM('IOUDPLogger', [('seq_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('time_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'Alias': 'time_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'usempc_in'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'float32', 'Alias': 'useobs_in'}})], [('seq_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'uint32', 'Alias': 'seq_in'}}), ('time_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'uint32', 'Alias': 'time_in'}}), ('adv1_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'adv1_in'}}), ('adv2_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'adv2_in'}}), ('adv3_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'adv3_in'}}), ('adv4_in', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'adv4_in'}}), ('Use_MPC', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'usempc'}}), ('Use_OBS', {'MARTeConfig': {'DataSource': 'UDPFileWriter', 'Type': 'float32', 'Alias': 'useobs'}})])

App.functions += [_IOUDPLogger]


# Generate DataSources
# 
_TimingsDataSource = TimingDataSource('TimingsDataSource', [], [])

App.additional_datasources += [_TimingsDataSource]

_Timer = LinuxTimer('Timer', 'Default', 'IndependentThread',
                                4294967295, 0, 0, 1000, [], [('Counter', {'MARTeConfig': {'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}), ('Time', {'MARTeConfig': {'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1', 'Frequency': 1000}}), ('AbsoluteTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}), ('DeltaTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}), ('TrigRephase', {'MARTeConfig': {'Type': 'uint8', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}})])

App.additional_datasources += [_Timer]

_FileWriter = FileWriter('FileWriter', [('time_in', {'MARTeConfig': {'Type': 'uint32'}}), ('MWI_Out', {'MARTeConfig': {'Type': 'float32'}}), ('Density', {'MARTeConfig': {'Type': 'float32'}}), ('in3', {'MARTeConfig': {'Type': 'float32'}}), ('in4', {'MARTeConfig': {'Type': 'float32'}}), ('output1', {'MARTeConfig': {'Type': 'float32'}}), ('output2', {'MARTeConfig': {'Type': 'float32'}}), ('output3', {'MARTeConfig': {'Type': 'float32'}}), ('output4', {'MARTeConfig': {'Type': 'float32'}}), ('output5', {'MARTeConfig': {'Type': 'float32'}}), ('usempc', {'MARTeConfig': {'Type': 'float32'}}), ('useobs', {'MARTeConfig': {'Type': 'float32'}}), ('AbsoluteTime', {'MARTeConfig': {'Type': 'uint64'}}), ('SeqIn', {'MARTeConfig': {'Type': 'uint32'}})], [],
                                100000, 0x00000040, 100000000, 'log_0.csv', 'yes',
                                'csv', ',', 0, 0, 0, 0)

App.additional_datasources += [_FileWriter]

_UDPFileWriter = FileWriter('UDPFileWriter', [('seq_in', {'MARTeConfig': {'Type': 'uint32'}}), ('time_in', {'MARTeConfig': {'Type': 'uint32'}}), ('adv1_in', {'MARTeConfig': {'Type': 'float32'}}), ('adv2_in', {'MARTeConfig': {'Type': 'float32'}}), ('adv3_in', {'MARTeConfig': {'Type': 'float32'}}), ('adv4_in', {'MARTeConfig': {'Type': 'float32'}}), ('usempc', {'MARTeConfig': {'Type': 'float32'}}), ('useobs', {'MARTeConfig': {'Type': 'float32'}})], [],
                                100000, 0x00000040, 100000000, 'logudp_0.csv', 'yes',
                                'csv', ',', 0, 0, 0, 0)

App.additional_datasources += [_UDPFileWriter]

_UDPSender = UDPSender('UDPSender', [('devType', {'MARTeConfig': {'Type': 'uint8'}}), ('diagId', {'MARTeConfig': {'Type': 'uint8'}}), ('version', {'MARTeConfig': {'Type': 'uint8'}}), ('payloadSize', {'MARTeConfig': {'Type': 'uint8'}}), ('shotNumber', {'MARTeConfig': {'Type': 'uint32'}}), ('timestamp', {'MARTeConfig': {'Type': 'uint32'}}), ('seq_out', {'MARTeConfig': {'Type': 'uint32'}}), ('adver1', {'MARTeConfig': {'Type': 'float32'}}), ('adver2', {'MARTeConfig': {'Type': 'float32'}}), ('adver3', {'MARTeConfig': {'Type': 'float32'}}), ('adver4', {'MARTeConfig': {'Type': 'float32'}}), ('adver5', {'MARTeConfig': {'Type': 'float32'}})], 3341,
                                0x00000020, 'RealTimeThread', '10.347.729.8', 0, 0, 10000000)

App.additional_datasources += [_UDPSender]

_LoggerDataSource = LoggerDataSource('LoggerDataSource', [], [])

App.additional_datasources += [_LoggerDataSource]

_RealTimeSynch = Synchronisation('RealTimeSynch', 1, '1',
                                -1, [], [], False)

App.additional_datasources += [_RealTimeSynch]

_UDPReceiver = UDPReceiver('UDPReceiver', [('devType', {'MARTeConfig': {'Type': 'uint8'}}), ('diagId', {'MARTeConfig': {'Type': 'uint8'}}), ('version', {'MARTeConfig': {'Type': 'uint8'}}), ('payloadSize', {'MARTeConfig': {'Type': 'uint8'}}), ('shotNumber', {'MARTeConfig': {'Type': 'uint32'}}), ('timestamp', {'MARTeConfig': {'Type': 'uint32'}}), ('seq_in', {'MARTeConfig': {'Type': 'uint32'}}), ('adver1', {'MARTeConfig': {'Type': 'float32'}}), ('adver2', {'MARTeConfig': {'Type': 'float32'}}), ('adver3', {'MARTeConfig': {'Type': 'float32'}}), ('adver4', {'MARTeConfig': {'Type': 'float32'}}), ('Use_MPC', {'MARTeConfig': {'Type': 'float32'}}), ('Use_OBS', {'MARTeConfig': {'Type': 'float32'}})], '',
                                '', 10000000, 'RealTimeThread', 0, 3342, 4294967295)

App.additional_datasources += [_UDPReceiver]

_DDB0 = GAMDataSource('DDB0', [], [])

App.additional_datasources += [_DDB0]

_DDB1 = GAMDataSource('DDB1', [], [])

App.additional_datasources += [_DDB1]


# Generate States
# 
_State1 = MARTe2RealTimeState('State1')

_Threads = MARTe2ReferenceContainer('Threads')

_ModelThread = MARTe2RealTimeThread('ModelThread', 8)

_ModelThread.functions += [_IOTime]
_ModelThread.functions += [_IO_FromUDP]
_ModelThread.functions += [_convert_seq]
_ModelThread.functions += [_SimulinkWrapperGAM]
_ModelThread.functions += [_IO_UDP_Out]
_ModelThread.functions += [_IOLog]
_ModelThread.functions += [_IODataLogger]

_Threads.objects += [_ModelThread]

_UDPReceiverThread = MARTe2RealTimeThread('UDPReceiverThread', 16)

_UDPReceiverThread.functions += [_IO_UDP_In]
_UDPReceiverThread.functions += [_DeviceConstants]
_UDPReceiverThread.functions += [_IOUDPLogger]
_UDPReceiverThread.functions += [_IO_UDP_ToModel]

_Threads.objects += [_UDPReceiverThread]

_State1.threads = _Threads

App.states += [_State1]

_Error = MARTe2RealTimeState('Error')

_Threads = MARTe2ReferenceContainer('Threads')

_Error.threads = _Threads

App.states += [_Error]

_Error = MARTe2RealTimeState('Error')

_Threads = MARTe2ReferenceContainer('Threads')

_Thread1 = MARTe2RealTimeThread('Thread1', 4294967295)


_Threads.objects += [_Thread1]

_Error.threads = _Threads

App.states += [_Error]


# Generate Internals
# 
_Scheduler = MARTe2GAMScheduler('Scheduler', 'GAMScheduler', 'TimingsDataSource',
                            0)

App.internals += [_Scheduler]


# Generate Externals
# 
_StateMachine = MARTe2StateMachine('StateMachine')

_INITIAL = MARTe2ReferenceContainer('INITIAL')

_START = MARTe2StateMachineEvent('START', '"STATE1"', '"ERROR"', 0)



_StartHttpServer = MARTe2Message('StartHttpServer', 'WebServer', 'Start', 'ExpectsReply', -1)

# Generate Message Parameters objects for StartHttpServer
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StartHttpServer.parameters = [_Parameters]

_START.messages += [_StartHttpServer]



_PrepareChangeToState1Msg = MARTe2Message('PrepareChangeToState1Msg', 'App', 'PrepareNextState', '"ExpectsReply"', 0)

# Generate Message Parameters objects for PrepareChangeToState1Msg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_Parameters.objects['param1'] = "State1"
_PrepareChangeToState1Msg.parameters = [_Parameters]

_START.messages += [_PrepareChangeToState1Msg]



_StartNextStateExecutionMsg = MARTe2Message('StartNextStateExecutionMsg', 'App', 'StartNextStateExecution', '"ExpectsReply"', 0)

# Generate Message Parameters objects for StartNextStateExecutionMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StartNextStateExecutionMsg.parameters = [_Parameters]

_START.messages += [_StartNextStateExecutionMsg]

_INITIAL.objects += [_START]

_StateMachine.states = _INITIAL

_STATE1 = MARTe2ReferenceContainer('STATE1')

_ERROR = MARTe2StateMachineEvent('ERROR', '"ERROR"', '"ERROR"', 0)

_STATE1.objects += [_ERROR]

_StateMachine.states = _STATE1

_ERROR = MARTe2ReferenceContainer('ERROR')

_ENTER = MARTe2ReferenceContainer('ENTER')



_StopCurrentStateExecutionMsg = MARTe2Message('StopCurrentStateExecutionMsg', 'App', 'StopCurrentStateExecution', '"ExpectsReply"', 0)

# Generate Message Parameters objects for StopCurrentStateExecutionMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StopCurrentStateExecutionMsg.parameters = [_Parameters]

_ENTER.objects += [_StopCurrentStateExecutionMsg]



_PrepareChangeToErrorMsg = MARTe2Message('PrepareChangeToErrorMsg', 'App', 'PrepareNextState', '"ExpectsReply"', 0)

# Generate Message Parameters objects for PrepareChangeToErrorMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_Parameters.objects['param1'] = "Error"
_PrepareChangeToErrorMsg.parameters = [_Parameters]

_ENTER.objects += [_PrepareChangeToErrorMsg]



_StartNextStateExecutionMsg = MARTe2Message('StartNextStateExecutionMsg', 'App', 'StartNextStateExecution', '"ExpectsReply"', 0)

# Generate Message Parameters objects for StartNextStateExecutionMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StartNextStateExecutionMsg.parameters = [_Parameters]

_ENTER.objects += [_StartNextStateExecutionMsg]

_ERROR.objects += [_ENTER]

_RESET = MARTe2StateMachineEvent('RESET', '"STATE1"', '"STATE1"', 0)



_StopCurrentStateExecutionMsg = MARTe2Message('StopCurrentStateExecutionMsg', 'App', 'StopCurrentStateExecution', '"ExpectsReply"', 0)

# Generate Message Parameters objects for StopCurrentStateExecutionMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StopCurrentStateExecutionMsg.parameters = [_Parameters]

_RESET.messages += [_StopCurrentStateExecutionMsg]



_PrepareChangeToState1Msg = MARTe2Message('PrepareChangeToState1Msg', 'App', 'PrepareNextState', '"ExpectsReply"', 0)

# Generate Message Parameters objects for PrepareChangeToState1Msg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_Parameters.objects['param1'] = "State1"
_PrepareChangeToState1Msg.parameters = [_Parameters]

_RESET.messages += [_PrepareChangeToState1Msg]



_StartNextStateExecutionMsg = MARTe2Message('StartNextStateExecutionMsg', 'App', 'StartNextStateExecution', '"ExpectsReply"', 0)

# Generate Message Parameters objects for StartNextStateExecutionMsg
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_StartNextStateExecutionMsg.parameters = [_Parameters]

_RESET.messages += [_StartNextStateExecutionMsg]

_ERROR.objects += [_RESET]

_StateMachine.states = _ERROR

App.externals += [_StateMachine]

# Generate HTTP Object Browser objects for WebRoot


_WebRoot = MARTe2HTTPObjectBrowser('WebRoot', '"."')# Generate HTTP Object Browser objects for WebRoot
# Generate HTTP Object Browser objects for ObjectBrowse


_ObjectBrowse = MARTe2HTTPObjectBrowser('ObjectBrowse', '"/"')# Generate HTTP Object Browser objects for ObjectBrowse
_WebRoot.objects += [_ObjectBrowse]



_ResourcesHtml = MARTe2HttpDirectoryResource('ResourcesHtml', '"/MARTe2/Resources/HTTP/"')

_ResourcesHtml = MARTe2HttpMessageInterface('ResourcesHtml')# Generate HTTP Message Interface objects for ResourcesHtml


_GOTOIDLE = MARTe2Message('GOTOIDLE', 'StateMachine', 'GOTOIDLE', 'ExpectsReply', -1)

# Generate Message Parameters objects for GOTOIDLE
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_GOTOIDLE.parameters = [_Parameters]

_ResourcesHtml.objects += [_GOTOIDLE]



_GOTORUN = MARTe2Message('GOTORUN', 'StateMachine', 'GOTORUN', 'ExpectsReply', -1)

# Generate Message Parameters objects for GOTORUN
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_GOTORUN.parameters = [_Parameters]

_ResourcesHtml.objects += [_GOTORUN]



_GOTOERR = MARTe2Message('GOTOERR', 'StateMachineError', 'GOTOERR', 'ExpectsReply', -1)

# Generate Message Parameters objects for GOTOERR
_Parameters = MARTe2ConfigurationDatabase('Parameters')
_GOTOERR.parameters = [_Parameters]

_ResourcesHtml.objects += [_GOTOERR]

_WebRoot.objects += [_ResourcesHtml]

App.externals += [_WebRoot]

_WebServer = MARTe2HttpService('WebServer', "8084", '"WebRoot"',
                                    "0", "255", "1000", "8", "1")

                                    
App.externals += [_WebServer]


# Generate objects
# 


def getApplication():
    return App
