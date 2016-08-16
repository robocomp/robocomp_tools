#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2016 by YOUR NAME HERE
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

# \mainpage RoboComp::client1
#
# \section intro_sec Introduction
#
# Some information about the component...
#
# \section interface_sec Interface
#
# Descroption of the interface provided...
#
# \section install_sec Installation
#
# \subsection install1_ssec Software depencences
# Software dependences....
#
# \subsection install2_ssec Compile and install
# How to compile/install the component...
#
# \section guide_sec User guide
#
# \subsection config_ssec Configuration file
#
# <p>
# The configuration file...
# </p>
#
# \subsection execution_ssec Execution
#
# Just: "${PATH_TO_BINARY}/client1 --Ice.Config=${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import sys, traceback, Ice, IceStorm, subprocess, threading, time, Queue, os, copy

# Ctrl+c handling
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PySide import *

from specificworker import *

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except:
    print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
    ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
    print 'ROBOCOMP environment variable not set! Exiting.'
    sys.exit()


preStr = "-I"+ROBOCOMP+"/interfaces/ -I/opt/robocomp/interfaces/ --all "+ROBOCOMP+"/interfaces/"
Ice.loadSlice(preStr+"CommonBehavior.ice")
import RoboCompCommonBehavior
Ice.loadSlice(preStr+"RCMaster.ice")
import RoboCompRCMaster
Ice.loadSlice(preStr+"ASR.ice")
import RoboCompASR
Ice.loadSlice(preStr+"Test.ice")
import RoboCompTest


class CommonBehaviorI(RoboCompCommonBehavior.CommonBehavior):
    def __init__(self, _handler, _communicator):
        self.handler = _handler
        self.communicator = _communicator
    def getFreq(self, current = None):
        self.handler.getFreq()
    def setFreq(self, freq, current = None):
        self.handler.setFreq()
    def timeAwake(self, current = None):
        try:
            return self.handler.timeAwake()
        except:
            print 'Problem getting timeAwake'
    def killYourSelf(self, current = None):
        self.handler.killYourSelf()
    def getAttrList(self, current = None):
        try:
            return self.handler.getAttrList(self.communicator)
        except:
            print 'Problem getting getAttrList'
            traceback.print_exc()
            status = 1
            return



if __name__ == '__main__':
    app = QtCore.QCoreApplication(sys.argv)
    params = copy.deepcopy(sys.argv)
    if len(params) > 1:
        if not params[1].startswith('--Ice.Config='):
            params[1] = '--Ice.Config=' + params[1]
    elif len(params) == 1:
        params.append('--Ice.Config=config')
    ic = Ice.initialize(params)
    status = 0
    
    mprx = {}
    mprx["name"] = ic.getProperties().getProperty('Ice.ProgramName');

    print mprx["name"]
    proxyData = {}
    proxyData["rcmaster"] = {"comp":"rcmaster","caster":RoboCompRCMaster.rcmasterPrx.checkedCast,"name":"rcmaster"}
    proxyData["test1"] = {"comp":"client31","caster":RoboCompTest.testPrx.checkedCast,"name":"test"}
    proxyData["test2"] = {"comp":"client32","caster":RoboCompTest.testPrx.checkedCast,"name":"test"}

    try:

        # Remote object connection for rcmaster
        try:
            with open(os.path.join(os.path.expanduser('~'), ".config/RoboComp/rcmaster.config"), 'r') as f:
                rcmaster_uri = f.readline().strip().split(":")
            basePrx = ic.stringToProxy("rcmaster:tcp -h "+rcmaster_uri[0]+" -p "+rcmaster_uri[1])
            try:
                print "Connecting to rcmaster " ,rcmaster_uri
                rcmaster_proxy = RoboCompRCMaster.rcmasterPrx.checkedCast(basePrx)
            except Ice.SocketException:
                raise Exception("RCMaster is not running")
            proxyData["rcmaster"]["proxy"] = rcmaster_proxy
        except Ice.Exception:
            print 'Cannot connect to the remote object (rcmaster)'
            traceback.print_exc()
            status = 1


        # Remote object connection for test1
        try:
            while True:
                try:
                    port = rcmaster_proxy.getComPort(proxyData["test1"]["comp"],"localhost");
                    basePrx = ic.stringToProxy("test:tcp -h localhost -p "+str(port))
                    test_proxy = RoboCompTest.testPrx.checkedCast(basePrx)
                    proxyData["test1"]["proxy"] = test_proxy
                except RoboCompRCMaster.ComponentNotFound:
                    print 'waiting for test1 interface'
                    time.sleep(3)
                except Ice.Exception:
                    print 'Cannot connect to the remote object (test)'
                    traceback.print_exc()
                    status = 1
                else:
                    break

        except Ice.Exception, e:
            print e
            print 'Cannot get testProxy property.'
            status = 1

        # Remote object connection for test2
        try:
            while True:
                try:
                    port = rcmaster_proxy.getComPort(proxyData["test2"]["comp"],"localhost");
                    basePrx = ic.stringToProxy("test:tcp -h localhost -p "+str(port))
                    test_proxy = RoboCompTest.testPrx.checkedCast(basePrx)
                    proxyData["test2"]["proxy"] = test_proxy
                except RoboCompRCMaster.ComponentNotFound:
                    print 'waiting for test2 interface'
                    time.sleep(3)
                except Ice.Exception:
                    print 'Cannot connect to the remote object (test)'
                    traceback.print_exc()
                    status = 1
                else:
                    break

        except Ice.Exception, e:
            print e
            print 'Cannot get testProxy property.'
            status = 1

    except:
            traceback.print_exc()
            status = 1


    if status == 0:
        mprx["proxyData"] = proxyData
        worker = SpecificWorker(mprx)

        # get port for all interfaces
        compInfo = RoboCompRCMaster.compData(name=mprx["name"])
        compInfo.interfaces = [RoboCompRCMaster.interfaceData('ASR')]
        idata = rcmaster_proxy.registerComp(compInfo,False,True)
        
        # activate all interfaces
        for iface in idata:
            adapter = ic.createObjectAdapterWithEndpoints(iface.name, iface.protocol+' -h localhost -p '+str(iface.port))
            workerObj = globals()[str(iface.name)+'I'](worker)
            adapter.add(workerObj, ic.stringToIdentity(iface.name))
            adapter.activate()
            print "activated interface :", (iface)


#       adapter.add(CommonBehaviorI(<LOWER>I, ic), ic.stringToIdentity('commonbehavior'))

        app.exec_()

    if ic:
        try:
            ic.destroy()
        except:
            traceback.print_exc()
            status = 1
