/*
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


]]]
[[[end]]]
 *    Copyright (C) 
[[[cog
A()
import datetime
cog.out(str(datetime.date.today().year))
Z()
]]]
[[[end]]]
 by YOUR NAME HERE
 *
 *    This file is part of RoboComp
 *
 *    RoboComp is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    RoboComp is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
 */
#ifndef GENERICWORKER_H
#define GENERICWORKER_H

#include "config.h"
#include <QtGui>
#include <stdint.h>
#include <qlog/qlog.h>

[[[cog
if component['gui'] != 'none':
	cog.outl("#include <ui_mainUI.h>")
]]]
[[[end]]]

#include <CommonBehavior.h>
[[[cog

for m in pool.modulePool:
	cog.outl("#include <"+m+".h>")

]]]
[[[end]]]

[[[cog

try:
	if 'agmagent' in [ x.lower() for x in component['options'] ]:
		cog.outl("#include <agm.h>")


except:
	pass

if len(component['publishes'])>0 or len(component['subscribesTo'])>0:
	cog.outl("#include <IceStorm/IceStorm.h>")

]]]
[[[end]]]


#define CHECK_PERIOD 5000
#define BASIC_PERIOD 100

typedef map <string,::IceProxy::Ice::Object*> MapPrx;

using namespace std;

[[[cog

pool = IDSLPool(theIDSLs)
for m in pool.modulePool:
	cog.outl("using namespace "+pool.modulePool[m]['name']+";")

]]]
[[[end]]]

[[[cog

try:
	if 'agmagent' in [ x.lower() for x in component['options'] ]:
		cog.outl("""
		struct BehaviorParameters 
		{
			RoboCompPlanning::Action action;
			std::vector< std::vector <std::string> > plan;
		};""")
except:
	pass

]]]
[[[end]]]



class GenericWorker : 
[[[cog
if component['gui'] != 'none':
	cog.outl("""#ifdef USE_QTGUI
public QWidget, public Ui_guiDlg
#else
public QObject
#endif""")
else:
	cog.outl("public QObject")
]]]
[[[end]]]
{
Q_OBJECT
public:
	GenericWorker(MapPrx& mprx);
	virtual ~GenericWorker();
	virtual void killYourSelf();
	virtual void setPeriod(int p);
	
	virtual bool setParams(RoboCompCommonBehavior::ParameterList params) = 0;
	QMutex *mutex;
[[[cog

try:
	if 'agmagent' in [ x.lower() for x in component['options'] ]:
		cog.outl("<TABHERE>bool activate(const BehaviorParameters& parameters);")
		cog.outl("<TABHERE>bool deactivate();")
		cog.outl("<TABHERE>bool isActive() { return active; }")
except:
	pass

]]]
[[[end]]]
	

[[[cog
for namea, num in getNameNumber(component['requires']+component['publishes']):
	if type(namea) == str:
		name = namea
	else:
		name = namea[0]
	cog.outl('<TABHERE>'+name+'Prx '+name.lower()+num +'_proxy;')

if len(component['publishes'])>0 or len(component['subscribesTo'])>0:
	cog.outl("<TABHERE>IceStorm::TopicManagerPrx topicmanager_proxy;")
]]]
[[[end]]]

[[[cog
if 'implements' in component:
	for impa in component['implements']:
		if type(impa) == str:
			imp = impa
		else:
			imp = impa[0]
		module = pool.moduleProviding(imp)
		for interface in module['interfaces']:
			if interface['name'] == imp:
				for mname in interface['methods']:
					method = interface['methods'][mname]
					paramStrA = ''
					for p in method['params']:
						# delim
						if paramStrA == '': delim = ''
						else: delim = ', '
						# decorator
						ampersand = '&'
						if p['decorator'] == 'out':
							const = ''
						else:
							const = 'const '
							if p['type'].lower() in ['int', '::ice::int', 'float', '::ice::float']:
								ampersand = ''
						# STR
						paramStrA += delim + const + p['type'] + ' ' + ampersand + p['name']
					cog.outl("<TABHERE>virtual " + method['return'] + ' ' + method['name'] + '(' + paramStrA + ") = 0;")

if 'subscribesTo' in component:
	for imp in component['subscribesTo']:
		nname = imp
		while type(nname) != type(''):
			nname = nname[0]
		module = pool.moduleProviding(nname)
		if module == None:
			print ('\nCan\'t find module providing', nname, '\n')
			sys.exit(-1)
		if communicationIsIce(nname):
			for interface in module['interfaces']:
				if interface['name'] == nname:
					for mname in interface['methods']:
						method = interface['methods'][mname]
						paramStrA = ''
						for p in method['params']:
							# delim
							if paramStrA == '': delim = ''
							else: delim = ', '
							# decorator
							ampersand = '&'
							if p['decorator'] == 'out':
								const = ''
							else:
								const = 'const '
								if p['type'].lower() in ['int', '::ice::int', 'float', '::ice::float']:
									ampersand = ''
							# STR
							paramStrA += delim + const + p['type'] + ' ' + ampersand + p['name']
						cog.outl("<TABHERE>virtual " + method['return'] + ' ' + method['name'] + '(' + paramStrA + ") = 0;")
		else:
			cog.outl("<TABHERE>virtual ROS" + method['return'] + ' ' + method['name'] + "() = 0;")
	

				
]]]
[[[end]]]


protected:
	QTimer timer;
	int Period;
[[[cog
try:
	if 'agmagent' in [ x.lower() for x in component['options'] ]:
		cog.outl("<TABHERE>bool active;")
		cog.outl("<TABHERE>AGMModel::SPtr worldModel;")
		cog.outl("<TABHERE>BehaviorParameters p;")
		cog.outl("<TABHERE>ParameterMap params;")
		cog.outl("<TABHERE>int iter;")
		cog.outl("<TABHERE>bool setParametersAndPossibleActivation(const ParameterMap &prs, bool &reactivated);")
		cog.outl("<TABHERE>RoboCompPlanning::Action createAction(std::string s);")
except:
	pass

]]]
[[[end]]]

[[[cog
if len(component['publishes'])>0 or len(component['subscribesTo'])>0:
	cog.outl("<TABHERE>QTimer storm_timer;");
	cog.outl("<TABHERE>int storm_period;");
]]]
[[[end]]]

public slots:
	virtual void compute() = 0;
[[[cog
if len(component['publishes'])>0 or len(component['subscribesTo'])>0:
	cog.outl("<TABHERE>void check_storm();");
]]]
[[[end]]]

signals:
	void kill();
};

#endif
