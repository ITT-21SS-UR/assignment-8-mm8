from pyqtgraph.flowchart import Node
import numpy as np
from scipy import fft


class FFTNode(Node):
    """
    Calculates the Fast Fourier Transformation (FFT) for the provided time-series data and the returns the
    frequency spectrum for the given signal.
    """
    nodeName = "FFTNode"

    def __init__(self, name):
        terminals = {
            'accelIn': dict(io='in'),
            'spectrumOut': dict(io='out'),
        }
        Node.__init__(self, name, terminals=terminals)

    def _plot_spectrum(self, y, Fs):
        """ Plots a Single-Sided Amplitude Spectrum of y(t);
        see http://glowingpython.blogspot.de/2011/08/how-to-plot-frequency-spectrum-with.html
        Frequency Spectrum: composition of a Signal's individual frequencies
        Amplitude Spectrum: the absolute value of the Frequency Spectrum

        Function taken from the provided dft_tour.ipynb notebook.
        """
        n = len(y)  # length of the signal
        k = np.arange(n)
        T = n / Fs
        frq = k / T  # two sides frequency range
        frq = frq[0:int(n/2)]  # one side frequency range
        Y = fft.fft(y) / n  # fft computing and normalization
        Y = Y[0:int(n/2)]  # use only first half as the function is mirrored

        # plot(frq, abs(Y),'r') # plotting the spectrum
        # xlabel('Frequency (Hz)')
        # ylabel('Intensity')

    def _calculate_fft(self, input_values):
        """
        Calculates the fft for the given accelerometer values.
        We use only half of the input values length to ignore the imaginary part.

        Formula taken from the provided Wiimote-FFT-SVM.ipynb notebook.
        """
        n = len(input_values)
        return np.abs(fft.fft(input_values) / n)[1:n // 2]

    def process(self, **kwds):
        input_values = kwds["accelIn"]
        frequency = self._calculate_fft(input_values)
        return {'spectrumOut': frequency}
