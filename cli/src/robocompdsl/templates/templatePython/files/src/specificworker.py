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

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import os
console = Console(highlight=False)

try:
    import setproctitle
    setproctitle.setproctitle(os.path.basename(os.getcwd()))
except:
    pass

${dsr_import}

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, configData, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map, configData)
        self.Period = configData["Period"]["Compute"]
        ${dsr_init}
        if startup_check:
            self.startup_check()
        else:
            ${timeout_compute_connect}

    def __del__(self):
        """Destructor"""

    ${compute_creation}

    def startup_check(self):
        ${startup_check_ice}
        QTimer.singleShot(200, QApplication.instance().quit)



    ${subscription_methods}

    ${implements_methods}

    ${interface_specific_comment}

    ${dsr_slots}
