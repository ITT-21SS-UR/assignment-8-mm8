#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from pyqtgraph.flowchart import Flowchart
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from DIPPID_pyqtnode import DIPPIDNode, BufferNode
from FFT_node import FFTNode
from Classifier_node import ClassifierNode
from DisplayText_node import DisplayTextNode


# noinspection PyAttributeOutsideInit
class FlowChart:
    def __init__(self, layout, port=5700):
        self.layout = layout
        self.port = port

        # Create an empty flowchart with a single input and output
        self.fc = Flowchart(terminals={})
        w = self.fc.widget()

        # Params are: widget, fromRow, fromColumn, rowSpan, columnSpan
        # -1 for the last two makes them completely extend to bottom / right
        self.layout.addWidget(w, 0, 0, 2, 1)

        self.create_plot_widgets()
        self.set_plot_widgets()
        self.create_nodes()
        self.connect_node_terminals()

    def create_plot_widgets(self):
        # create one plot widget for each axis below each other in the left column
        self.pw1 = pg.PlotWidget()
        self.layout.addWidget(self.pw1, 0, 3, 1, 1)
        self.pw1.setYRange(0, 1)
        self.pw1.setTitle("X-FFT")

        self.pw2 = pg.PlotWidget()
        self.layout.addWidget(self.pw2, 1, 3, 1, 1)
        self.pw2.setYRange(0, 1)
        self.pw2.setTitle("Y-FFt")

        self.pw3 = pg.PlotWidget()
        self.layout.addWidget(self.pw3, 2, 3, 1, 1)
        self.pw3.setYRange(0, 1)
        self.pw3.setTitle("Z-FFT")

    def set_plot_widgets(self):
        self.pw1Node = self.fc.createNode('PlotWidget', pos=(300, -450))
        self.pw1Node.setPlot(self.pw1)
        self.pw2Node = self.fc.createNode('PlotWidget', pos=(300, -350))
        self.pw2Node.setPlot(self.pw2)
        self.pw3Node = self.fc.createNode('PlotWidget', pos=(300, -250))
        self.pw3Node.setPlot(self.pw3)

    def create_nodes(self):
        # create the dippid node and set the provided port automatically
        self.dippidNode = self.fc.createNode("DIPPID", pos=(-20, 0))
        self.dippidNode.set_connection_port(self.port)

        # create buffer nodes for each axis
        self.bufferNodeX = self.fc.createNode('Buffer', pos=(100, -150))
        self.bufferNodeY = self.fc.createNode('Buffer', pos=(100, 0))
        self.bufferNodeZ = self.fc.createNode('Buffer', pos=(100, 150))

        # create fft nodes for each axis
        self.fftNodeX = self.fc.createNode('FFTNode', pos=(250, -150))
        self.fftNodeY = self.fc.createNode('FFTNode', pos=(250, 0))
        self.fftNodeZ = self.fc.createNode('FFTNode', pos=(250, 150))

        self.classifierNode = self.fc.createNode('ClassifierNode', pos=(350, 50))
        self.layout.addWidget(self.classifierNode.ctrlWidget(), 0, 1, 2, 2)
        self.displayTextNode = self.fc.createNode('DisplayTextNode', pos=(470, 50))
        self.layout.addWidget(self.displayTextNode.ctrlWidget(), 2, 1, 2, 2)

    def connect_node_terminals(self):
        # connect the acceleration values with the buffer nodes and the buffers with the corresponding plot widgets
        self.fc.connectTerminals(self.dippidNode['accelX'], self.bufferNodeX['dataIn'])
        self.fc.connectTerminals(self.dippidNode['accelY'], self.bufferNodeY['dataIn'])
        self.fc.connectTerminals(self.dippidNode['accelZ'], self.bufferNodeZ['dataIn'])
        self.fc.connectTerminals(self.bufferNodeX['dataOut'], self.fftNodeX['accelIn'])
        self.fc.connectTerminals(self.bufferNodeY['dataOut'], self.fftNodeY['accelIn'])
        self.fc.connectTerminals(self.bufferNodeZ['dataOut'], self.fftNodeZ['accelIn'])

        # for testing only: plot the output of the fft nodes
        self.fc.connectTerminals(self.fftNodeX['spectrumOut'], self.pw1Node['In'])
        self.fc.connectTerminals(self.fftNodeY['spectrumOut'], self.pw2Node['In'])
        self.fc.connectTerminals(self.fftNodeZ['spectrumOut'], self.pw3Node['In'])

        self.fc.connectTerminals(self.fftNodeX['spectrumOut'], self.classifierNode['valX'])
        self.fc.connectTerminals(self.fftNodeY['spectrumOut'], self.classifierNode['valY'])
        self.fc.connectTerminals(self.fftNodeZ['spectrumOut'], self.classifierNode['valZ'])

        # connect the result of the classifier node with the display node
        self.fc.connectTerminals(self.classifierNode['prediction'], self.displayTextNode['prediction'])


def register_custom_nodes():
    fclib.registerNodeType(FFTNode, [('Fft',)])
    fclib.registerNodeType(ClassifierNode, [('Classifier',)])
    fclib.registerNodeType(DisplayTextNode, [('Display',)])


def main():
    # parse command line input and print out some helpful information
    parser = ArgumentParser(description="A machine learning based activity recognizer based on the DIPPID protocol.")
    parser.add_argument("-p", "--port", help="The port on which the mobile device sends its data via DIPPID", type=int,
                        default=5700, required=False)
    args = parser.parse_args()
    port = args.port

    register_custom_nodes()

    # create the gui
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Assignment 8 - Activity Recognizer')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # win.showMaximized()
    win.setGeometry(50, 50, 1500, 1200)

    # create the flowchart
    flowchart = FlowChart(layout, port)

    win.show()
    # if not running in interactive mode or using PySide instead of PyQt, start the app
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    main()
