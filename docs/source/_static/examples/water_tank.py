
from martepy.marte2 import (
    MARTe2Application,
    MARTe2RealTimeThread,
    MARTe2RealTimeState,
    MARTe2GAMScheduler
)

from martepy.marte2.gams import (
    IOGAM,
    ExpressionGAM,
    ConversionGAM
)

from martepy.marte2.datasources import (
    LinuxTimer,
    LoggerDataSource,
    TimingDataSource,
    FileReader,
    GAMDataSource
)

CPU_OFFSET_FROM_ONE = 0  # 0 to start at cpu 1
def cpu_thread_gen(x):
    ''' Generate a cpu core to used based on thread number x and pre-defined offset from core 1. '''
    return str(hex(2 ** (x + CPU_OFFSET_FROM_ONE)))

app = MARTe2Application()

# Define our DDB0 database
app.add(additional_datasources = [
    GAMDataSource(configuration_name = '+DDB0')])

# Add the file input
file_input = [("Level", {'MARTeConfig':{'Alias': 'Level', 'DataSource': 'FileReader', 'Type': 'float64'}})]
reader = FileReader(configuration_name = '+FileReader',filename='water_tank.csv', output_signals=file_input)
app.add(additional_datasources = [reader])

# Define our IOGAMs input and output signals.
file_to_db = [("CurrentLevel", {'MARTeConfig':{'Alias': 'CurrentLevel', 'DataSource': 'DDB0', 'Type': 'float64'}})]
# Create the IOGAM and add it to our application
app.add(functions=[IOGAM('+FileIn', file_input, file_to_db)])
# Convert our signal
input_signals = [("current_value", {'MARTeConfig':{'Alias': 'CurrentLevel', 'DataSource': 'DDB0', 'Type': 'float64'}})]
output_signals = [("converted_value", {'MARTeConfig':{'DataSource': 'DDB0', 'Type': 'uint8'}})]
app.add(functions=[ConversionGAM('+Convert',input_signals,output_signals)])
# Define our Expression
expression = '''
valve_on = current_value > (uint8)40;
pump_on = current_value < (uint8)40;
'''
input_signals = [("current_value", {'MARTeConfig':{'Alias': 'converted_value', 'DataSource': 'DDB0', 'Type': 'uint8'}})]
output_signals = [("valve_on", {'MARTeConfig':{'DataSource': 'DDB0', 'Type': 'uint8'}}),
    ("pump_on", {'MARTeConfig':{'DataSource': 'DDB0', 'Type': 'uint8'}})]
app.add(functions=[ExpressionGAM('+Eval',input_signals,output_signals,expression)])

# Add standard timing
app.add(internals = [
    MARTe2GAMScheduler(
        configuration_name = '+Scheduler',
        timing_datasource_name = 'Timings',
        class_name = "GAMScheduler"
    ),
])
app.add(additional_datasources = [
    TimingDataSource(configuration_name = '+Timings'),
])

# Add Logging to Screen
app.add(additional_datasources = [
    LoggerDataSource(configuration_name = '+LoggerDataSource'),
])

input_signals = [("valve_on", {'MARTeConfig':{'Alias': 'valve_on', 'DataSource': 'DDB0', 'Type': 'uint8'}}),
    ("pump_on", {'MARTeConfig':{'Alias': 'pump_on', 'DataSource': 'DDB0', 'Type': 'uint8'}})]
output_signals = [("valve_on", {'MARTeConfig':{'DataSource': 'LoggerDataSource', 'Type': 'uint8'}}),
    ("pump_on", {'MARTeConfig':{'DataSource': 'LoggerDataSource', 'Type': 'uint8'}})]

app.add(functions=[IOGAM('+ToLog', input_signals, output_signals)])

# Define run rate

input_signals = [("Counter", {'MARTeConfig':{'DataSource': 'Timer', 'Type': 'uint32'}}),
    ("Time", {'MARTeConfig':{'DataSource': 'Timer', 'Type': 'uint32', 'Frequency': '1'}})]
output_signals = [("Counter", {'MARTeConfig':{'DataSource': 'DDB0', 'Type': 'uint32'}}),
    ("Time", {'MARTeConfig':{'DataSource': 'DDB0', 'Type': 'uint32'}})]
timer = LinuxTimer(configuration_name='+Timer')
app.add(additional_datasources=[timer])
app.add(functions=[IOGAM('+Timer', input_signals, output_signals)])

app.add(states=[
    MARTe2RealTimeState(
        configuration_name='+Running',
        threads=[
            MARTe2RealTimeThread(
                configuration_name='+Thread0',
                cpu_mask=16,
                functions=app.functions,
            ),
        ],
    ),
])

file_contents = app.writeToConfig()

with open('water_tank.cfg','w') as outfile:
    outfile.write(file_contents)
