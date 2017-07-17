
import sys, signal, argparse

from PyQt4.QtGui import QApplication
from xmlreader import xml_reader
from viewer import Viewer
from model import Model
from controller import Controller
from logger import RCManagerLogger
from PyQt4 import QtCore, QtGui
from rcmanagerSignals import rcmanagerSignals
import argparse
#import pdb

class Main():
    """This is the Main class which spawns the objects for the Model,
    Viewer and the Controller, for our MVC model."""

    def __init__(self):
        xmldata = xml_reader(sys.argv[1])
        
        self.signalObject = rcmanagerSignals()
        
        # create model as a NetworkX graph using dict
        self.model = Model(self.signalObject)
        
        # create Qt Ui in a separate class
        self.viewer = Viewer(self.signalObject)
       	self.viewer.show()
        
        # create a controller to connect the viewer and the model
        self.controller = Controller(self.model, self.viewer, self.signalObject)
        self.setup_signal_connection()
        
        # load the xml file
        self.model.load_from_xml(sys.argv[1])
        
        self.signalObject.controllerIsReady.emit()
        
    def setup_signal_connection(self):
    	self.signalObject.modelIsReady.connect(self.controller.model_init_action)
    	self.signalObject.viewerIsReady.connect(self.controller.viewer_init_action)
        self.signalObject.controllerIsReady.connect(self.controller.controller_init_action)

if __name__ == '__main__':
    # process params with a argparse
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main = Main()
    ret = app.exec_()
    sys.exit(ret)
    
# window = MainClass()
# window.show()
