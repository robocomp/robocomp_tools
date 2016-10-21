/*
 *    Copyright (C) 2006-2010 by RoboLab - University of Extremadura
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
#include "genericbaseI.h"
#include "specificworker.h"

GenericBaseI::GenericBaseI(SpecificWorker *_worker, QObject *parent): QThread(parent)
{
	// Pointer to the worker (needed to access the mutex)
	worker = _worker;
	// InnerModel
	innerModel = worker->getInnerModel();
}


void GenericBaseI::add(QString id)
{
	node                        = innerModel->getOmniRobot(id);
	parent                      = innerModel->getTransform(node->parent->id);
}


void GenericBaseI::run()
{
	while (true)
	{
		usleep(10000);
	}
}


void GenericBaseI::getBaseState(RoboCompGenericBase::TBaseState& state, const Ice::Current&)
{
	QMutexLocker locker(worker->mutex);

	{
		QVec retPOSR = innerModel->transform6D(parent->id, node->id+"_raw_odometry\"");
		state.x = retPOSR(0);
		state.z = retPOSR(2);
		state.alpha = retPOSR(4);
	}
	
	{
		QVec retPOSC = innerModel->transform6D(parent->id, node->id+"_corrected_odometry\"");
		state.correctedX = retPOSC(0);
		state.correctedZ = retPOSC(2);
		state.correctedAlpha = retPOSC(4);
	}

// 	state.isMoving = ( (fabs(advVelx)<0.0001 and fabs(advVelz)<0.0001 and fabs(rotVel)<0.0001));
	
// 	state.advVx = advVelx;
// 	state.advVz = advVelz;
// 	state.rotV  = rotVel;

}

