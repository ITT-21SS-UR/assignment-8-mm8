from pyqtgraph.flowchart import Node
from pyqtgraph.Qt import QtGui


class DisplayTextNode(Node):
    """
    Displays the activity that was predicted by the classifier.
    """
    nodeName = "DisplayTextNode"

    def __init__(self, name):
        terminals = {
            'prediction': dict(io='in')
        }

        self._show_ui()
        Node.__init__(self, name, terminals=terminals)

    def _show_ui(self):
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout()

        self.predicted_class = QtGui.QLabel()
        self.predicted_class.setStyleSheet("QLabel {font-weight: bold; font-size: 16px};")
        self.layout.addWidget(self.predicted_class)

        self.ui.setLayout(self.layout)

    def ctrlWidget(self):
        return self.ui

    def process(self, **kwds):
        predicted_activity = kwds["prediction"]
        self.predicted_class.setText(f"Predicted activity:  {predicted_activity}")
