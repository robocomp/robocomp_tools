#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) ${year} by YOUR NAME HERE
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
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide2.QtCore import qApp, QTimer
from genericworker import *


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, testing=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        if testing:
            self.testing()
        else:
            ${timeout_compute_connect}
            self.timer.start(self.Period)
            ${statemachine_start_and_destroy}

    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        #try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        #except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    ${compute_creation}

    def testing(self):
        self.compute()
        QTimer.singleShot(2000, qApp.quit)

    ${statemachine_slots}

    ${subscription_methods}

    ${implements_methods}

