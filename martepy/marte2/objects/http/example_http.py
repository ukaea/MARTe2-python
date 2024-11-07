''' This example shows how to create a basic setup of a HTTP Service in MARTe2 '''

from martepy.marte2.objects.http import *
from martepy.marte2.objects.message import MARTe2Message

def httpService(directory,app=None):
    """Fixed definition of HTTP Service however because the datagramtest
    repo has a dynamic definition this is possible to make dynamic here also"""
    # First thing to do is define the messages we might send to the
    # StateMachine (When working of course!)
    Messages = [MARTe2Message("+GOTOSTATE1","StateMachine","GOTOSTATE1"),
                MARTe2Message("+GOTOSTATE2","StateMachine","GOTOSTATE2")]

    # Object Browser Definition
    ObjectBrowser = MARTe2HTTPObjectBrowser('+ObjectBrowse','/')

    # ResourcesHtml Definition
    ResourcesHtml = MARTe2HttpDirectoryResource('+ResourcesHtml',
                                                f'{directory}/Resources/HTTP/')

    MessageInterface = MARTe2HttpMessageInterface('+HttpMessageInterface',Messages)

    Objectlist = [ObjectBrowser,ResourcesHtml,MessageInterface]

    HTTPBrowser = MARTe2HTTPObjectBrowser('+WebRoot','.',Objectlist)

    # Add WebServer
    service = MARTe2HttpService('+WebService')
    # Add this to application
    app.add(externals=[HTTPBrowser] + [service])
