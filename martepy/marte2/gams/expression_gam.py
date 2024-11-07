''' Pythonic representation of the Expression GAM'''

from functools import partial

from PyQt5.QtWidgets import (
    QTextEdit,
    QLabel
)

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import addInputSignalsSection, addOutputSignalsSection, paraChange
class ExpressionGAM(MARTe2GAM):
    ''' Pythonic representation of the Expression GAM'''
    def __init__(self,
                    configuration_name: str = 'ExpressionGAM',
                    input_signals: list = [],
                    output_signals: list = [],
                    expression: str = '',
                ):
        self.expression = expression
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'MathExpressionGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, config_writer):
        ''' Write the GAM configuration - i.e. the expression '''
        expression = self.expression.split('\n')
        firstline = expression[0]
        tabs = config_writer.tab_text * config_writer.tab
        tabs += ' ' * len('Expression = ')
        expression = [tabs + a for a in expression]
        expression[0] = firstline
        expression = '\n'.join(expression)
        config_writer.writeNode('Expression', f'"{expression}"')

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['expression'] = self.expression
        res['parameters']['Class name'] = 'ExpressionGAM'
        res['label'] = "ExpressionGAM"
        res['block_type'] = 'ExpressionGAM'
        res['class_name'] = 'ExpressionGAM'
        res['title'] = f"{self.configuration_name} (ExpressionGAM)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to our class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.expression = data['parameters']["expression"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)


        # Define Expression text
        lbl_wgt = QLabel("Expression: ")
        expression_wgt = QTextEdit(mainpanel_instance)
        expression_wgt.setPlainText(node.parameters['expression'])
        expression_wgt.textChanged.connect(partial(paraChange, expression_wgt, node, 'expression'))
        mainpanel_instance.configbarBox.addWidget(lbl_wgt, 2, 0)
        mainpanel_instance.configbarBox.addWidget(expression_wgt, 2, 1)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("ExpressionGAM", ExpressionGAM, plugin_datastore)
    factory.registerBlock("MathExpressionGAM", ExpressionGAM, plugin_datastore)
