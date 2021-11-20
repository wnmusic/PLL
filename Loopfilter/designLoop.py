#!/usr/local/bin/python3
import sys
import numpy as np
import scipy.signal as signal
from PyQt5 import QtCore, QtWidgets,QtGui
from optparse import OptionParser
from pygnuplot import gnuplot
import pandas as pd

PLOTTYPE_NORMAL = 0
PLOTTYPE_SPECTRUM = 1
PLOTTYPE_HEATMAP = 2

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, options):
        super().__init__()

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.order = int(options.order)

        dispLayout =  QtWidgets.QHBoxLayout()
        img = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap('3rd_order_network.png' if self.order==3 else '2nd_order_network.png')
        img.setPixmap(pixmap)
        dispLayout.addWidget(img)

        self.bw_label = QtWidgets.QLabel("Loop Bandwidth: \n")
        dispLayout.addWidget(self.bw_label)
        
        layout.addLayout(dispLayout);

        widLayout = QtWidgets.QHBoxLayout()
        r1_label = QtWidgets.QLabel("R1:(K)")
        self.r1_edit = QtWidgets.QLineEdit("10")
        self.r1_edit.setValidator(QtGui.QDoubleValidator())
        self.r1_edit.editingFinished.connect(self.analyze)
        widLayout.addWidget(r1_label)
        widLayout.addWidget(self.r1_edit)
        
        r2_label = QtWidgets.QLabel("R2:(K)")        
        self.r2_edit = QtWidgets.QLineEdit("1")
        self.r2_edit.editingFinished.connect(self.analyze)
        widLayout.addWidget(r2_label)        
        widLayout.addWidget(self.r2_edit)

        c1_label = QtWidgets.QLabel("C1:(n)")        
        self.c1_edit = QtWidgets.QLineEdit("1")
        self.c1_edit.editingFinished.connect(self.analyze)
        widLayout.addWidget(c1_label)        
        widLayout.addWidget(self.c1_edit)
        layout.addLayout(widLayout)

        if (self.order == 3):
            c2_label = QtWidgets.QLabel("C2:(n)")        
            self.c2_edit = QtWidgets.QLineEdit("0.1")
            self.c2_edit.editingFinished.connect(self.analyze)
            widLayout.addWidget(c2_label)        
            widLayout.addWidget(self.c2_edit)
            layout.addLayout(widLayout)

        k_label = QtWidgets.QLabel("K:(rad/s/V)")        
        self.k_edit = QtWidgets.QLineEdit("1000")
        self.k_edit.editingFinished.connect(self.analyze)
        widLayout.addWidget(k_label)        
        widLayout.addWidget(self.k_edit)
        layout.addLayout(widLayout)        
        
        ana_btn = QtWidgets.QPushButton("Plot");
        ana_btn.clicked.connect(self.analyze);
        layout.addWidget(ana_btn)


        self.open_gain_plot = gnuplot.Gnuplot()
        self.open_gain_plot.set(logscale='x')
        self.open_gain_plot.set('xtics')
        self.open_gain_plot.set('y2tics nomirror')
        self.open_gain_plot.set('ytics')
        self.open_gain_plot.set(grid='xtics')
        self.open_gain_plot.set(grid='ytics')
        self.open_gain_plot.set(title='"Open gain Bode"')

        self.gain_plot = gnuplot.Gnuplot()
        self.gain_plot.set(logscale='x')
        self.gain_plot.set(grid='xtics')
        self.gain_plot.set(grid='ytics')
        self.gain_plot.set(title = '"system gain"')
        
        self.step_plot = gnuplot.Gnuplot()
        self.step_plot.set(grid='xtics')
        self.step_plot.set(grid='ytics')
        self.step_plot.set('y2tics nomirror')
        self.step_plot.set(title = '"step/imp response"')
        
        
        self.setWindowTitle("PLL loopfilter design tool")        
        

    def analyze(self):
        r1 = float(self.r1_edit.text())*1e3
        r2 = float(self.r2_edit.text())*1e3
        c1 =  float(self.c1_edit.text())*1e-9
        Kd = float(self.k_edit.text())

        tc1 = (r1 + r2) * c1
        tc2 = r2 * c1
        if self.order == 2:
            G_num = [tc2*Kd, Kd]
            G_dem = [tc1, 1, 0]
            tf = signal.TransferFunction(G_num, G_dem)
            H_num = G_num
            H_dem = [tc1, 1+tc2*Kd, Kd]
            lti2 = signal.lti(H_num, H_dem)
            
        elif self.order==3:
            c2 = float(self.c2_edit.text())*1e-9
            G_num = [tc2*Kd, Kd]
            G_dem = [r1*r2*c1*c2, r1*(c1+c2)+tc2, 1, 0]
            tf = signal.TransferFunction(G_num, G_dem)
            H_num = G_num
            H_dem = [r1*r2*c1*c2, r1*(c1+c2)+tc2, 1+tc2*Kd, Kd]
            lti2 = signal.lti(H_num, H_dem)
        
        freq = np.logspace(0, 6, 200)
        _, mag, phase = signal.bode(tf, 2.0*np.pi*freq)
        fc_idx = np.argmin(abs(mag))
        fc = freq[fc_idx]

        
        df = pd.DataFrame(np.vstack((freq, mag, phase)).T, columns=['freq', 'mag', 'phase'])
        self.open_gain_plot.unset('arrow')
        self.open_gain_plot.unset('label')
        self.open_gain_plot.set('arrow from {},graph(0,0) to {},graph(1,1) nohead'.format(fc, fc))
        self.open_gain_plot.set('label 1 at {},{}'.format(fc*2, mag[fc_idx]+2))
        self.open_gain_plot.set('label 1 "{}"'.format("margin: {:.2f}".format(-180-phase[fc_idx])))
        self.open_gain_plot.plot_data(df, 'using 2:3 w l t "mag"'
                                          ,'using 2:4 w l axes x1y2 t "phase"')


        _, mag = lti2.freqresp(2.0*np.pi*freq)

        bw_idx = np.argmin(np.abs(np.abs(mag) - 0.707))
        self.bw_label.setText("Loop Bandwidth: {:.2f}Hz\n".format(freq[bw_idx]))
        
        df2 =  pd.DataFrame(np.vstack((freq, 20*np.log10(np.abs(mag)))).T, columns=['freq', 'mag'])

        t, hstep = lti2.step()
        _, himp = lti2.impulse()
        df3 =  pd.DataFrame(np.vstack((t, hstep, himp)).T, columns=['time', 'vol', 'imp'])
        self.gain_plot.plot_data(df2, 'u 2:3 w l t "mag"')
        self.step_plot.plot_data(df3, 'u 2:3 w l t "vol"')
        
        
        return 
    
if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-n", "--order", dest="order",
                      help="the order of the filter", default="3")
    parser.add_option("-i", "--current", dest="current",
                      help="charge pump current in mA", default=None)

    (options, args) = parser.parse_args()
    
    qapp = QtWidgets.QApplication(["PLL loopfilter"])
    app = ApplicationWindow(options)
    app.show()
    qapp.exec_()

