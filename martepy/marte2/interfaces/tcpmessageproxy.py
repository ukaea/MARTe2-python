''' Pythonic representation of the TCP Message Proxy provided by padova '''

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton
)

from martepy.marte2.interface import MARTe2Interface


class TCPMessageProxy(MARTe2Interface):
    ''' Pythonic representation of the TCP Message Proxy provided by padova '''
    def __init__(self,
                    configuration_name: str = 'TCPMessageProxy',
                    input_signals = [],
                    output_signals = [],
                    port = 8400
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'TCPSocketMessageProxyExample',
            )
        self.port = port

    def writeInterfaceConfig(self, config_writer):
        ''' Write out our port configuration '''
        config_writer.writeNode('Port', '{}'.format(self.port))

    def serialize(self):
        ''' Serialize '''
        res = super().serialize()
        res['parameters']['port'] = self.port

        # Override name
        res['label'] = "TCPMessageProxy"
        res['block_type'] = 'TCPMessageProxy'
        res['class_name'] = 'TCPMessageProxy'
        res['title'] = f"{self.configuration_name} (TCPMessageProxy)"
        return res

    def deserialize(self, data: dict) -> bool:
        ''' Deserialize '''
        super().deserialize(data)
        self.port = int(data['parameters']["port"])
        return self

    def configure(self):
        dialog = PortDialog(current_port=self.port)
        if dialog.exec_() == dialog.Accepted:
            self.port = dialog.get_port()

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object with the factory '''
    factory.registerBlock("TCPSocketMessageProxyExample", TCPMessageProxy, plugin_datastore)
    factory.registerBlock("TCPMessageProxy", TCPMessageProxy, plugin_datastore)

class PortDialog(QDialog):
    def __init__(self, current_port=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Port")
        self.port = current_port if current_port is not None else 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Label + numeric input
        input_layout = QHBoxLayout()
        label = QLabel("Port:")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.port)

        input_layout.addWidget(label)
        input_layout.addWidget(self.port_input)
        layout.addLayout(input_layout)

        # OK / Cancel buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def get_port(self):
        """Return the port chosen by the user."""
        return self.port_input.value()