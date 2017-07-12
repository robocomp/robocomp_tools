
import sys, signal, argparse

from PyQt4.QtGui import QApplication
from xmlreader import xml_reader
from viewer import Viewer
from model import Model
from controller import Controller
from logger import RCManagerLogger
from PyQt4 import QtCore, QtGui
from rcmanagerSignals import rcmanager_signals

class Main():
    """This is the Main class which spawns the objects for the Model,
    Viewer and the Controller, for our MVC model."""

    def __init__(self):
        xmldata = xml_reader(sys.argv[1])
        
        self.signalObject = rcmanager_signals()
        
        # create model as a NetworkX graph using dict
        self.model = Model(xmldata, self.signalObject)
        
        # create Qt Ui in a separate class
        self.viewer = Viewer()
        self.viewer.show()
        
        # create controller
        controller = Controller(self.model, self.viewer, self.signalObject)
        
        # calling the function to emit a signal
        self.model.sample_emit()

if __name__ == '__main__':
    # process params with a argparse
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main = Main()
    ret = app.exec_()
    sys.exit(ret)


# window = MainClass()
# window.show()
