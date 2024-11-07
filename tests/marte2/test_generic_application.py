import os, pdb, pytest, copy

from martepy.marte2.generic_application import MARTe2Application
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.datasources import GAMDataSource, LoggerDataSource, TimingDataSource, LinuxTimer, FileWriter, AsyncBridge
from martepy.marte2.objects import MARTe2GAMScheduler, MARTe2RealTimeState, MARTe2RealTimeThread, MARTe2ReferenceContainer
from martepy.functions.extra_functions import getname, calculateStackSize
from martepy.functions.gam_functions import getAlias
from ..utilities import top_lvl

@pytest.fixture
def setup_simple_app():
    app = MARTe2Application()

    app.add(additional_datasources=[GAMDataSource('DDB1')])
    app.add(additional_datasources=[LoggerDataSource()])
    app.add(additional_datasources=[TimingDataSource()])
    app.add(additional_datasources=[LinuxTimer(frequency=50)])

    writer = FileWriter(configuration_name='FileLogger', number_of_buffers = 10,
                cpu_mask = 255,
                stack_size = 10000000,
                file_name = "test.bin",
                overwrite = "yes",
                file_format = "binary",
                csv_separator = ",",
                store_on_trigger = 0,
                refreshcontent = 0,
                numpretriggers = 0,
                numposttriggers =0, input_signals=[('Counter',{'MARTeConfig':{'DataSource':'FileLogger','Type':'uint32'}}),
                                                        ('Time',{'MARTeConfig':{'DataSource':'FileLogger','Type':'uint32'}})])

    app.add(additional_datasources=[writer])

    assert getname(writer) == "FileLogger"
    
    app.default_data_source = 'DDB1'
    app.add(internals=[MARTe2GAMScheduler(timing_datasource_name='Timings')])

    thread = MARTe2RealTimeThread(configuration_name='Thread1', cpu_mask=0x1)

    state = MARTe2RealTimeState(configuration_name='State1', threads=MARTe2ReferenceContainer(configuration_name='Threads', objects=[thread]))

    timer = IOGAM(configuration_name='GAMTimer', input_signals=[('Counter',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32'}}),
                                                        ('Time',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32', 'Frequency': 50}})],
                                        output_signals=[('Counter',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}}),
                                                        ('Time',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    display = IOGAM(configuration_name='GAMDisplay', input_signals=[('Time',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})],
                                        output_signals=[('Time',{'MARTeConfig':{'DataSource':'LoggerDataSource','Type':'uint32'}})])
    logger = IOGAM(configuration_name='GAMLogger', input_signals=[('Counter',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}}),
                                                        ('Time',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})],
                                        output_signals=[('Counter',{'MARTeConfig':{'DataSource':'FileLogger','Type':'uint32'}}),
                                                        ('Time',{'MARTeConfig':{'DataSource':'FileLogger','Type':'uint32'}})])

    thread.functions = [timer, display, logger]

    app.add(states=[state])

    app.config['timefrequency'] = 50

    return app

def test_application(setup_simple_app):
    app = setup_simple_app
    text = app.writeToConfig()

    with open(os.path.join(top_lvl, 'tests','functions','simple_logger.cfg'), 'r') as comparison_file:
        comp_text = comparison_file.read()

    assert comp_text == text

def test_app_functions(setup_simple_app):
    app = setup_simple_app
    app.sanitize()
    assert app.getSignals() == {'Timer': {'Counter': ('Counter', {'MARTeConfig': {'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                          'Time': ('Time', {'MARTeConfig': {'Type': 'uint32', 'Frequency': 50, 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                          'AbsoluteTime': ('AbsoluteTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                          'DeltaTime': ('DeltaTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                          'TrigRephase': ('TrigRephase', {'MARTeConfig': {'Type': 'uint8', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}})},
                                'DDB1': {'Counter': ('Counter', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32'}}),
                                         'Time': ('Time', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32'}})},
                                'LoggerDataSource': {'Time': ('Time', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Type': 'uint32'}})},
                                'FileLogger': {'Counter': ('Counter', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}}),
                                               'Time': ('Time', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}})}}
    
    assert app.getInputDatasources() == [('Counter', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32'}}),
                                         ('Time', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Frequency': 50}})]

    assert app.getOutputDatasources() == [('Time', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Type': 'uint32'}}),
                                          ('Counter', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}}),
                                          ('Time', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}})]
    
    assert app.getinputSignals() == {'Counter': ('Counter', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}}),
                                     'Time': ('Time', {'MARTeConfig': {'DataSource': 'FileLogger', 'Type': 'uint32'}}),
                                     'AbsoluteTime': ('AbsoluteTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                     'DeltaTime': ('DeltaTime', {'MARTeConfig': {'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}),
                                     'TrigRephase': ('TrigRephase', {'MARTeConfig': {'Type': 'uint8', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}})}
    
    assert calculateStackSize(app.getInputDatasources()) == 8
    assert calculateStackSize(app.getOutputDatasources()) == 12

    assert app.newUniqueName('Counter') == 'Counter1'

    assert getAlias(('Counter',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32', 'Alias':'MockAlias'}})) == 'MockAlias'
    backup_app = copy.deepcopy(app)
    assert app.onlyErrors() == []

    gam = app.buildLog()

    assert app.logging_iogam.configuration_name == '+LoggingGAM'
    assert app.logging_iogam.__class__ == IOGAM
    assert app.logging_iogam.input_signals == [('Counter', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1', 'Alias': 'Counter'}}), ('Time', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1', 'Alias': 'Time'}})]
    assert app.logging_iogam.output_signals == [('Counter', {'MARTeConfig': {'DataSource': 'LogGAMSource', 'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}), ('Time', {'MARTeConfig': {'DataSource': 'LogGAMSource', 'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}})]

    filewriter = app.additional_datasources[-1]
    assert filewriter.configuration_name == '+LoggingFileWriter'
    assert filewriter.input_signals == [('Counter', {'MARTeConfig': {'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}}), ('Time', {'MARTeConfig': {'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements': '1'}})]

    removed_gam = GAMDataSource('DDB')
    removed_io = IOGAM()
    removed_async = AsyncBridge()
    app.add(additional_datasources=[removed_gam, removed_async])
    app.states[0].threads.objects[0].functions += [removed_io]

    app.removeUnused()
    assert removed_gam not in app.additional_datasources
    assert removed_io not in app.states[0].threads.objects[0].functions
    assert removed_io not in app.functions
    assert removed_async not in app.additional_datasources
    
