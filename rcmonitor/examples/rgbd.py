# -*- coding: utf-8 -*-

#    Copyright (C) 2010 by RoboLab - University of Extremadura
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

import Ice, sys, math, traceback

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *
from ui_kinectDlg import Ui_KinectDlg


class C(QWidget):
	def __init__(self, endpoint, modules):
		print modules.keys()
		QWidget.__init__(self)
		print "init"
		self.ui = Ui_KinectDlg()
		self.ui.setupUi(self)
		#hide kinect interface options
		self.ui.sbTilt.hide()
		self.ui.pbSetLed.hide()
		self.ui.label_4.hide()
		self.ui.cbLedOpt.hide()
		
		self.t = 0.
		arg = sys.argv
		arg.append("--Ice.MessageSizeMax=2000000")
		self.ic = Ice.initialize(arg)
		self.mods = modules
		self.prx = self.ic.stringToProxy(endpoint)
		print "endpoint", endpoint
		print "prx", self.prx
		print self.mods.keys()
		print "ya"
		self.proxy = self.mods['RoboCompRGBD'].RGBDPrx.checkedCast(self.prx)
		print "yaya"
		self.show()
		
		self.lalala = 0
		self.maxDepth = 9.0
		self.job()

	def job(self):
		print "hola"
		try:
			self.color, self.depth, self.headState, self.baseState = self.proxy.getData()
			#print len(self.color)
			if (len(self.color) == 0) or (len(self.depth) == 0):
				print 'Error retrieving images!'
		except Ice.Exception:
			traceback.print_exc()

	def paintEvent(self, event=None):
		if (len(self.color) == 3*640*480) and (len(self.depth) == 640*480):
			width = 640
			height = 480
		elif (len(self.color) == 3*320*240) and (len(self.depth) == 320*240):
			width = 320
			height = 240
			#print "color", len(self.color), "depth", len(self.depth)
		else:
			print 'we shall not paint!'
			return
		
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing, True)
		
		v = ''
		for i in range(len(self.depth)):
			ascii = 0
			try:
				ascii = int(255.-255.*(self.depth[i] / self.maxDepth / 1000. ) )
				if ascii > 255: ascii = 255
				if ascii < 0: ascii = 0
			except:
				pass
			if ascii > 255: ascii = 255
			v += chr(ascii)
		image = QImage(self.color, width, height, QImage.Format_RGB888)
		self.lalala+=1
		image.save("images/image"+str(self.lalala)+'.png')
		print "lalala: ", str(self.lalala)
		imageGrey = QImage(v, width, height, QImage.Format_Indexed8)
		for i in range(256):
			imageGrey.setColor(i, QColor(i,i,i).rgb())
		painter.drawImage(QPointF(self.ui.frameRGB.x(), self.ui.frameRGB.y()), image)
		painter.drawImage(QPointF(self.ui.frame.x(), self.ui.frame.y()), imageGrey)
		painter.end()
		#painter = None

