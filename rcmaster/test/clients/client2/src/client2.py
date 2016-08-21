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

# \mainpage RoboComp::client2
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
# Just: "${PATH_TO_BINARY}/client2 --Ice.Config=${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import sys, traceback, IceStorm, subprocess, threading, time, Queue, os, copy, socket

# Ctrl+c handling
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PySide import *

from specificworker import *


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

def get_open_port(self, portnum=0):
    '''
        get an open port for component
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg = ""
    port = -1
    if portnum != 0:
        if s.connect_ex(('127.0.0.1',portnum)) ==0 :
            msg = "Cant assign port, Alrady in use"
        else:
            port = portnum 
    else:
        try:
            s.bind(("", portnum))
        except socket.error, msg:
            msg = 'Cant assign port. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        else:
            port = s.getsockname()[1]

    s.close()
    return port, msg


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
	mprx["name"] = ic.getProperties().getProperty('Ice.ProgramName')
	proxyData = {}
	parameters = {}
	for i in ic.getProperties():
		parameters[str(i)] = str(ic.getProperties().getProperty(i))

	# Topic Manager
	proxy = ic.getProperties().getProperty("TopicManager.Proxy")
	obj = ic.stringToProxy(proxy)
	topicManager = IceStorm.TopicManagerPrx.checkedCast(obj)

	# Remote object connection for rcmaster
	proxyData["rcmaster"] = {"comp":"rcmaster","caster":rcmasterPrx.checkedCast,"name":"rcmaster"}
	try:
		with open(os.path.join(os.path.expanduser('~'), ".config/RoboComp/rcmaster.config"), 'r') as f:
			rcmaster_uri = f.readline().strip().split(":")
		basePrx = ic.stringToProxy("rcmaster:tcp -h "+rcmaster_uri[0]+" -p "+rcmaster_uri[1])
		try:
			print "Connecting to rcmaster " ,rcmaster_uri
			rcmaster_proxy = rcmasterPrx.checkedCast(basePrx)
		except Ice.SocketException:
			raise Exception("RCMaster is not running")
		proxyData["rcmaster"]["proxy"] = rcmaster_proxy
	except Ice.Exception:
		print 'Cannot connect to the remote object (rcmaster)'
		traceback.print_exc()
		status = 1

	if status == 0:
		mprx['proxyData'] = proxyData
		worker = SpecificWorker(mprx)
		worker.setParams(parameters)

		test_adapter = ic.createObjectAdapter("testTopic")
		testI_ = testI(worker)
		test_proxy = test_adapter.addWithUUID(testI_).ice_oneway()

		subscribeDone = False
		while not subscribeDone:
			try:
				test_topic = topicManager.retrieve("test")
				subscribeDone = True
			except Ice.Exception, e:
				print "Error. Topic does not exist (yet)"
				status = 0
				time.sleep(1)
		qos = {}
		test_topic.subscribeAndGetPublisher(qos, test_proxy)
		test_adapter.activate()


		app.exec_()

	if ic:
		try:
			ic.destroy()
		except:
			traceback.print_exc()
			status = 1
