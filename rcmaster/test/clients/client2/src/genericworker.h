/*
 *    Copyright (C) 2016 by YOUR NAME HERE
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

// ICE includes
#include <Ice/Ice.h>
#include <Ice/Application.h>


#include <CommonBehavior.h>

#include <RCMaster.h>
#include <TestComp.h>

#define CHECK_PERIOD 5000
#define BASIC_PERIOD 100

struct ifaceData
{
	string alias;
	string name;
	string comp;
	ifaceData()
	{}
	ifaceData(string  ialias, string iname, string icomp)
	{
		alias = ialias;
		name = iname;
		comp = icomp;
	}
};

typedef map <string,::IceProxy::Ice::Object*> MapPrx;
typedef map <string, ifaceData> Mapiface;

using namespace std;

using namespace RoboCompTest;
using namespace RoboCompRCMaster;




class GenericWorker : 
public QObject
{
Q_OBJECT
public:
	GenericWorker(MapPrx& mprx, Mapiface& miface);
	virtual ~GenericWorker();
	virtual void killYourSelf();
	virtual void setPeriod(int p);
	
	virtual bool setParams(RoboCompCommonBehavior::ParameterList params) = 0;
	QMutex *mutex;
	Mapiface& ifaces;

	

	testPrx test_proxy;
	rcmasterPrx rcmaster_proxy;

	virtual void printmsg(const string &message) = 0;

protected:
	QTimer timer;
	int Period;

private:


public slots:
	virtual void compute() = 0;
signals:
	void kill();
};

#endif