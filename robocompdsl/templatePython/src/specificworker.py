[[[cog

import sys
sys.path.append('/opt/robocomp/python')

import cog
def A():
	cog.out('<@@<')
def Z():
	cog.out('>@@>')
def TAB():
	cog.out('<TABHERE>')

from parseCDSL import *
component = CDSLParsing.fromFile(theCDSL)
if component == None:
	print('Can\'t locate', theCDSLs)
	sys.exit(1)

from parseIDSL import *
pool = IDSLPool(theIDSLs)

def replaceTypeCPP2Python(t):
	t = t.replace('::','.')
	t = t.replace('string', 'str')
	return t

]]]
[[[end]]]
#
# Copyright (C)
[[[cog
A()
import datetime
cog.out(' '+str(datetime.date.today().year))
Z()
]]]
[[[end]]]
 by YOUR NAME HERE
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

import sys, os, traceback, time

from PySide import *
from genericworker import *

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 2000
		self.timer.start(self.Period)

	def setParams(self, params):
		#try:
		#	par = params["InnerModelPath"]
		#	innermodel_path=par.value
		#	innermodel = InnerModel(innermodel_path)
		#except:
		#	traceback.print_exc()
		#	print "Error reading config params"
		return True

	@QtCore.Slot()
	def compute(self):
		print 'SpecificWorker.compute...'
		#try:
		#	self.differentialrobot_proxy.setSpeedBase(100, 0)
		#except Ice.Exception, e:
		#	traceback.print_exc()
		#	print e
		return True

[[[cog
lst = []
try:
	lst += component['subscribesTo']
except:
	pass
for imp in lst:
	if type(imp) == str:
		im = imp
	else:
		im = imp[0]
	module = pool.moduleProviding(im)
	for interface in module['interfaces']:
		if interface['name'] == im:
			for mname in interface['methods']:
				method = interface['methods'][mname]
				outValues = []
				if method['return'] != 'void':
					outValues.append([method['return'], 'ret'])
				paramStrA = ''
				for p in method['params']:
					if p['decorator'] == 'out':
						outValues.append([p['type'], p['name']])
					else:
						paramStrA += ', ' +  p['name']
				cog.outl('')
				cog.outl('<TABHERE>#')
				cog.outl('<TABHERE># ' + method['name'])
				cog.outl('<TABHERE>#')
				cog.outl('<TABHERE>def ' + method['name'] + '(self' + paramStrA + "):")
				if method['return'] != 'void': cog.outl("<TABHERE><TABHERE>ret = "+method['return']+'()')
				cog.outl("<TABHERE><TABHERE>#")
				cog.outl("<TABHERE><TABHERE># YOUR CODE HERE")
				cog.outl("<TABHERE><TABHERE>#")
				if len(outValues) == 0:
					cog.outl("<TABHERE><TABHERE>pass\n")
				elif len(outValues) == 1:
					if method['return'] != 'void':
						cog.outl("<TABHERE><TABHERE>return ret\n")
					else:
						cog.outl("<TABHERE><TABHERE>"+outValues[0][1]+" = "+replaceTypeCPP2Python(outValues[0][0])+"()")
						cog.outl("<TABHERE><TABHERE>return "+outValues[0][1]+"\n")
				else:
					for v in outValues:
						if v[1] != 'ret':
							cog.outl("<TABHERE><TABHERE>"+v[1]+" = "+replaceTypeCPP2Python(v[0])+"()")
					first = True
					cog.out("<TABHERE><TABHERE>return [")
					for v in outValues:
						if not first: cog.out(', ')
						cog.out(v[1])
						if first:
							first = False
					cog.out("]\n")
for imp in component['implements']:
	if type(imp) == str:
		im = imp
	else:
		im = imp[0]
	if not communicationIsIce(imp):
		module = pool.moduleProviding(im)
		for interface in module['interfaces']:
			if interface['name'] == im:
				for mname in interface['methods']:
					method = interface['methods'][mname]
					cog.outl('<TABHERE>def ' + method['name'] + "(self, req):")
					cog.outl("<TABHERE><TABHERE>#")
					cog.outl("<TABHERE><TABHERE># YOUR CODE HERE")
					cog.outl("<TABHERE><TABHERE>#Example ret = req.a + req.b")
					cog.outl("<TABHERE><TABHERE>#")
					cog.outl("<TABHERE><TABHERE>return "+method['name']+"Response(ret)")
	else:
		module = pool.moduleProviding(im)
		for interface in module['interfaces']:
			if interface['name'] == im:
				for mname in interface['methods']:
					method = interface['methods'][mname]
					outValues = []
					if method['return'] != 'void':
						outValues.append([method['return'], 'ret'])
					paramStrA = ''
					for p in method['params']:
						if p['decorator'] == 'out':
							outValues.append([p['type'], p['name']])
						else:
							paramStrA += ', ' +  p['name']
					cog.outl('')
					cog.outl('<TABHERE>#')
					cog.outl('<TABHERE># ' + method['name'])
					cog.outl('<TABHERE>#')
					cog.outl('<TABHERE>def ' + method['name'] + '(self' + paramStrA + "):")
					if method['return'] != 'void': cog.outl("<TABHERE><TABHERE>ret = "+method['return']+'()')
					cog.outl("<TABHERE><TABHERE>#")
					cog.outl("<TABHERE><TABHERE># YOUR CODE HERE")
					cog.outl("<TABHERE><TABHERE>#")
					if len(outValues) == 0:
						cog.outl("<TABHERE><TABHERE>pass\n")
					elif len(outValues) == 1:
						if method['return'] != 'void':
							cog.outl("<TABHERE><TABHERE>return ret\n")
						else:
							cog.outl("<TABHERE><TABHERE>"+outValues[0][1]+" = "+replaceTypeCPP2Python(outValues[0][0])+"()")
							cog.outl("<TABHERE><TABHERE>return "+outValues[0][1]+"\n")
					else:
						for v in outValues:
							if v[1] != 'ret':
								cog.outl("<TABHERE><TABHERE>"+v[1]+" = "+replaceTypeCPP2Python(v[0])+"()")
						first = True
						cog.out("<TABHERE><TABHERE>return [")
						for v in outValues:
							if not first: cog.out(', ')
							cog.out(v[1])
							if first:
								first = False
						cog.out("]\n")
]]]
[[[end]]]




