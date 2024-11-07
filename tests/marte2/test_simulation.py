import os

from martepy.marte2.reader import readApplication
from martepy.frameworks.simulation_frameworkv2 import SimulationGenerator


def test_simulation():
    cfg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RTApp-2-10.cfg'))
    app = readApplication(cfg_file)[0]
    type_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'type_db'))
    app.loadTypeLibrary(type_dir)
    sim_generator = SimulationGenerator(app)
    sim_generator.build()

    test_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frameworks', 'simulation_framework'))
    files = ['external_input_one_thread.cfg', 'multi_states_threads.cfg', 'multiple_states.cfg', 'multiple_states.cfg', 'multistates_linux_timer.cfg',
             'multistatethread_complextype_timer_filereading.cfg', 'multistatethread_complextype_timer.cfg', 'multistatethread_complextype.cfg',
             'simple_one_thread_constant.cfg']
    for test_file in files:
        app = readApplication(os.path.join(test_dir, test_file))[0]
        app.loadTypeLibrary(type_dir)
        sim_generator = SimulationGenerator(app)
        sim_generator.build()
