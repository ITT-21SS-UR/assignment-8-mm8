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

        label = QtGui.QLabel("Predicted activity:")
        self.layout.addWidget(label)

        self.predicted_class = QtGui.QLabel()
        self.predicted_class.setText("Unknown")
        self.layout.addWidget(self.predicted_class)

        self.ui.setLayout(self.layout)

    """
    def _show_ui(self):
        dialog = QtGui.QDialog()
        b1 = QtGui.QPushButton("Ok", dialog)
        b1.move(50, 50)
        dialog.setWindowTitle("Prediction Result")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()
    """

    def ctrlWidget(self):
        return self.ui

    def process(self, **kwds):
        predicted_activity = kwds["prediction"]
        self.predicted_class.setText(predicted_activity)

        # TODO self._show_ui() ??
