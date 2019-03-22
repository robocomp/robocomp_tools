#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  -----------------------
#  -----  rcmanager  -----
#  -----------------------
#  An ICE component manager.
#
#    Copyright (C) 2009-2015 by RoboLab - University of Extremadura
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#

#
# CODE BEGINS
#

import sys
import signal
import argparse
import logging

from PyQt4.QtGui import QApplication
from viewer import Viewer
from model import Model
from controller import Controller
from PyQt4 import QtCore, QtGui
from rcmanagerSignals import CustomSignalCollection

class Main():
    """This is the Main class which spawns the objects for the Model,
    Viewer and the Controller, for our MVC model."""

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('filename', help='the xml file containing the component graph data')
        parser.add_argument('-v', '--verbose', help='show debug messages', dest='verbosity', action='store_true')
        args = parser.parse_args()

        # create model as a NetworkX graph using dict
        self.model = Model()

        # create Qt Ui in a separate class
        self.viewer = Viewer()
        self.viewer.show()
        
        # create a controller to connect the viewer and the model
        self.controller = Controller(self.model, self.viewer)
        self.setup_signal_connection()

        # set verbosity levels for the loggers of Model, Viewer and Controller
        self.set_verbosity(args.verbosity)

        CustomSignalCollection.controllerIsReady.emit(args.filename)

    def set_verbosity(self, verbosity):
        if verbosity:
            verbosity_level = logging.DEBUG
        else:
            verbosity_level = logging.CRITICAL

        self.model._logger.setLevel(verbosity_level)
        self.viewer._logger.setLevel(verbosity_level)
        self.controller._logger.setLevel(verbosity_level)
        
    def setup_signal_connection(self):
        #TODO: it's a way to use a global variable. It should be avoided. Try to look for a better solution?
        CustomSignalCollection.modelIsReady.connect(self.controller.model_init_action)
        CustomSignalCollection.viewerIsReady.connect(self.controller.view_init_action)
        CustomSignalCollection.controllerIsReady.connect(self.controller.controller_init_action)
        CustomSignalCollection.saveModel.connect(self.controller.save_manager_file)
        CustomSignalCollection.openModel.connect(self.controller.load_manager_file)
        CustomSignalCollection.closeModel.connect(self.controller.check_dirty_bit)
        CustomSignalCollection.startComponent.connect(self.controller.start_component)
        CustomSignalCollection.stopComponent.connect(self.controller.stop_component)
        CustomSignalCollection.removeComponent.connect(self.controller.remove_component)

        #TODO: Is there any non lambda connect solution?
        CustomSignalCollection.componentRunning.connect(
            lambda componentAlias: self.viewer.update_node_profile(componentAlias, 'Profile_1'))
        CustomSignalCollection.componentStopped.connect(
            lambda componentAlias: self.viewer.update_node_profile(componentAlias, 'Profile_2'))

if __name__ == '__main__':
    # process params with a argparse
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main = Main()
    ret = app.exec_()
    sys.exit(ret)
    
# window = MainClass()
# window.show()
