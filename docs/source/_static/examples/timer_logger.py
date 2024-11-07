
from martepy.marte2 import (
    MARTe2Application,
    MARTe2RealTimeThread,
    MARTe2RealTimeState,
    MARTe2GAMScheduler
)

from martepy.marte2.gams import (
    IOGAM
)

from martepy.marte2.datasources import (
    LinuxTimer,
    LoggerDataSource,
    TimingDataSource
)

CPU_OFFSET_FROM_ONE = 0  # 0 to start at cpu 1
def cpu_thread_gen(x):
    ''' Generate a cpu core to used based on thread number x and pre-defined offset from core 1. '''
    return str(hex(2 ** (x + CPU_OFFSET_FROM_ONE)))

app = MARTe2Application()

app.add(additional_datasources = [
    TimingDataSource(configuration_name = '+Timings'),
])

app.add(additional_datasources = [
    LinuxTimer(
        configuration_name = '+Timer',
        cpu_mask = int(cpu_thread_gen(1), 16),
        sleep_nature = 'Busy',
        execution_mode = 'RealTimeThread',
        output_signals = [
            ('Counter', {'MARTeConfig':{'Type':'uint32' }}),
            ('Time',    {'MARTeConfig':{'Type':'uint32' }}),
        ],
    )
])

app.add(additional_datasources = [
    LoggerDataSource(configuration_name = '+LoggerDataSource'),
])

functions = []

functions += [IOGAM(
    configuration_name = '+GAMDisplay',
    input_signals = [
        ('Time', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Frequency': str(500)}}),
    ],
    output_signals = [
        ('DTime', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Alias': 'DTime', 'Type': 'uint32'}}),
    ],
)]

app.add(functions = functions)

app.add(states = [
    MARTe2RealTimeState(
        configuration_name = '+Running',
        threads = [
            MARTe2RealTimeThread(
                configuration_name = '+Thread0',
                cpu_mask = int(cpu_thread_gen(1), 16),
                functions = functions,
            ),
        ],
    ),
])

app.add(internals = [
    MARTe2GAMScheduler(
        configuration_name = '+Scheduler',
        timing_datasource_name = 'Timings',
        class_name = 'GAMScheduler',
    ),
])

full_config_string = app.writeToConfig() + '\n'
with open("timer_logger_example.cfg", "w") as text_file:
    print(full_config_string, file=text_file)
