import os
import pdb
import pytest

from martepy.marte2.reader import readApplication, UnrecognisedParameterException
from martepy.marte2.reader import TreeNode, getParameters, setParameters, handleChildObjects, createBasicStateMachine, createHttpBrowser
from martepy.marte2.factory import Factory as mpyFactory
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.marte2.objects.message import MARTe2Message

mfactory = mpyFactory() 
main_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
mfactory.loadRemote(os.path.join(main_dir,'martepy','marte2',"objects","objects.json")) 

def test_reader():
    cfg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RTApp-2-10.cfg'))
    app = readApplication(cfg_file)[0]
    node = TreeNode('hello')
    createBasicStateMachine(node, app,app.states[0].configuration_name.lstrip('+'))

def test_gui_configs():
    test_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frameworks', 'simulation_framework'))
    files = ['external_input_one_thread.cfg', 'multi_states_threads.cfg', 'multiple_states.cfg', 'multiple_states.cfg', 'multistates_linux_timer.cfg',
             'multistatethread_complextype_timer_filereading.cfg', 'multistatethread_complextype_timer.cfg', 'multistatethread_complextype.cfg',
             'simple_one_thread_constant.cfg']
    for test_file in files:
        app = readApplication(os.path.join(test_dir, test_file))[0]

def test_http():
    http_node = TreeNode('HttpObjectBrowser')
    http_node.parameters['Root'] = ''
    http_node.parameters['Class'] = 'HttpObjectBrowser'
    child_http = TreeNode('HttpObjectBrowser')
    child_http.parameters['Root'] = ''
    child_http.parameters['Class'] = 'HttpObjectBrowser'
    http_node.children = [child_http]
    msg_interface = TreeNode('HttpMessageInterface')
    msg_interface.parameters['Class'] = 'HttpMessageInterface'
    child = TreeNode('+Parameters')
    child.parameters = {'Class': 'ConfigurationDatabase', 'param1':'State1'}
    parent = TreeNode('+ChangeToState1Msg')
    parent.children = [child]
    parent.parameters = {'Class': 'Message', 'Destination':'TestApp','Mode':'ExpectsReply','Function':'PrepareNextState', 'MaxWait':'0'}
    msg_interface.children = [parent]
    http_node.children += [msg_interface]
    dir_node = TreeNode('HttpDirectoryResource')
    dir_node.parameters['Class'] = 'HttpDirectoryResource'
    dir_node.parameters['BaseDir'] = './'
    http_node.children += [dir_node]
    createHttpBrowser(http_node, [])

def test_tree_node():
    node = TreeNode('reader')
    node.parameters = {'key': 'value'}
    child = TreeNode('child')
    node.children = [child]
    assert 'reader\n\tkey = value\n\tchild\n' == str(node)
    assert getParameters(node) == {'key': 'value'}
    with pytest.raises(UnrecognisedParameterException):
        setParameters(node, child, 'test_class')
    test_node = TreeNode('reader')
    test_node.key = ''
    setParameters(node, test_node, 'test_class')
    test_node.parameters['Class'] = 'classy'
    node.parameters['Class'] = 'not_so_classy'
    node.children += [test_node]

def test_handle_obj():
    child = TreeNode('+Parameters')
    child.parameters = {'Class': 'ConfigurationDatabase', 'param1':'State1'}
    parent = TreeNode('+ChangeToState1Msg')
    parent.children = [child]
    parent.parameters = {'Class': 'Message', 'Destination':'TestApp','Mode':'ExpectsReply','Function':'PrepareNextState', 'MaxWait':'0'}
    msg = MARTe2Message(parent.name, parent.parameters['Destination'].strip('"'), parent.parameters['Function'].strip('"'),
                  MARTe2ConfigurationDatabase(objects={}), parent.parameters['Mode'], 0)
    handleChildObjects(msg, parent, mfactory)
