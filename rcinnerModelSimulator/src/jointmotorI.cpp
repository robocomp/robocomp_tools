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
#include "jointmotorI.h"
#include "specificworker.h"

#include <math.h>


/**
* \brief Default constructor
*/
JointMotorI::JointMotorI(std::shared_ptr<SpecificWorker> _worker, QObject *parent) : QObject(parent)
{
	worker = _worker;	
	busparams.numMotors = 0;
	busparams.baudRate = 10000;
	busparams.basicPeriod = 10;
	busparams.handler = "RoboComp Simulator";
	busparams.device = "sim";
}


/**
* \brief Default destructor
*/
JointMotorI::~JointMotorI()
{
	// Free component resources here
}


void JointMotorI::add(QString id)
{
	jointIDs << id;

	MotorParams param;
	param.invertedSign = false;
	param.busId = jointIDs.size();
	
	InnerModelNode *node = worker->innerModel->getNode(id);
	if (dynamic_cast<InnerModelJoint*>(node) != NULL)
	{
		param.minPos = dynamic_cast<InnerModelJoint*>(node)->min;
		param.maxPos = dynamic_cast<InnerModelJoint*>(node)->max;
	}
	else if (dynamic_cast<InnerModelPrismaticJoint*>(node) != NULL)
	{
		param.minPos = dynamic_cast<InnerModelPrismaticJoint *>(node)->min;
		param.maxPos = dynamic_cast<InnerModelPrismaticJoint *>(node)->max;
	}

	param.maxVelocity = 10000.;
	param.zeroPos = 0.;
	param.stepsRange = 0;
	param.maxDegrees = 0;
	param.name = id.toStdString();
	params.push_back(param);

	MotorState state;
	state.p = 0;
	state.v = 0;
	state.temperature = 0;
	state.isMoving = false;
	state.pos = 0.;
	state.vel = 0.;
	state.power = 0.;
// 	state.timeStamp;
	states[id.toStdString()] = state;

	busparams.numMotors++;
}

void JointMotorI::remove(QString id)
{
	jointIDs.removeAll(id);
	states.erase(id.toStdString());

	for (MotorParamsList::iterator iter=params.begin(); iter!=params.end();)
	{
		if (iter->name == id.toStdString())
			params.erase(iter);
		else
			iter++;
	}

	busparams.numMotors--;
}

void JointMotorI::setPosition(const MotorGoalPosition &goal, const Ice::Current&)
{
	const QString name = QString::fromStdString(goal.name);
	if (jointIDs.contains(name))
	{
		//worker->jm_setPosition(name, goal);
		if (goal.maxSpeed == 0.0f)
		{
			printf("Instantaneous movement!\n");
			SpecificWorker::JointMovement m;
			m.endPos = goal.position;
			m.endSpeed = goal.maxSpeed;
			m.maxAcc = INFINITY;
			m.mode = SpecificWorker::JointMovement::FixedPosition;
			worker->jointMovements[name] = m;
		}
		else
		{
			printf("Target position\n");
			SpecificWorker::JointMovement m;
			m.endPos = goal.position;
			m.endSpeed = goal.maxSpeed;
			m.maxAcc = INFINITY;
			m.mode = SpecificWorker::JointMovement::TargetPosition;
			worker->jointMovements[name] = m;
		}
	}
}


void JointMotorI::setVelocity(const MotorGoalVelocity &goal, const Ice::Current&)
{
	const QString name = QString::fromStdString(goal.name);
	if (jointIDs.contains(name))
	{
		//worker->jm_setVelocity(name, goal);
		printf("Target speed\n");
		SpecificWorker::JointMovement m;
		m.endPos = INFINITY;
		m.endSpeed = goal.velocity;
		m.maxAcc = goal.maxAcc;
		m.mode = SpecificWorker::JointMovement::TargetSpeed;
		worker->jointMovements[name] = m;
	}
}


void JointMotorI::setSyncPosition(const MotorGoalPositionList &listGoals, const Ice::Current &ice)
{
	for (uint i=0; i<listGoals.size(); i++)
		setPosition(listGoals[i], ice);
}


void JointMotorI::setSyncVelocity(const MotorGoalVelocityList &listGoals, const Ice::Current &ice)
{
	for (uint i=0; i<listGoals.size(); i++)
		setVelocity(listGoals[i], ice);
}


MotorParams JointMotorI::getMotorParams(const std::string &motor, const Ice::Current&)
{
	for (uint i=0; i<params.size(); ++i)
		if (params[i].name == motor)
			return params[i];
	throw runtime_error(std::string("RCRobotSimulator: JointMotorI::getMotorParams(): No motor named: ") + motor);
}


MotorState JointMotorI::getMotorState(const std::string &motor, const Ice::Current&)
{
	for (QStringList::const_iterator name = jointIDs.constBegin() ; name != jointIDs.constEnd() ; ++name)
	{
		InnerModelNode *node = worker->innerModel->getNode(*name);
		if (dynamic_cast<InnerModelJoint*>(node) != nullptr)
			states[name->toStdString()].pos = dynamic_cast<InnerModelJoint*>(node)->getAngle();
		else if (dynamic_cast<InnerModelPrismaticJoint*>(node) != nullptr)
			states[name->toStdString()].pos = dynamic_cast<InnerModelPrismaticJoint*>(node)->getPosition();
	}
	return states[motor];
}

MotorStateMap JointMotorI::getMotorStateMap(const MotorList &mList, const Ice::Current&)
{
	for (QStringList::const_iterator name = jointIDs.constBegin() ; name != jointIDs.constEnd() ; ++name)
	{
		InnerModelNode *node = worker->innerModel->getNode(*name);
		if (dynamic_cast<InnerModelJoint*>(node) != NULL)
			states[name->toStdString()].pos = dynamic_cast<InnerModelJoint*>(node)->getAngle();
		else if (dynamic_cast<InnerModelPrismaticJoint*>(node) != NULL)
			states[name->toStdString()].pos = dynamic_cast<InnerModelPrismaticJoint*>(node)->getPosition();
	}
	return states;
}

void JointMotorI::getAllMotorState(MotorStateMap &mstateMap, const Ice::Current&)
{
	for (QStringList::const_iterator name = jointIDs.constBegin() ; name != jointIDs.constEnd() ; ++name)
	{
		InnerModelNode *node = worker->innerModel->getNode(*name);
		if (dynamic_cast<InnerModelJoint*>(node) !=  nullptr)
			states[name->toStdString()].pos = dynamic_cast<InnerModelJoint*>(node)->getAngle();
		else if (dynamic_cast<InnerModelPrismaticJoint*>(node) != nullptr)
			states[name->toStdString()].pos = dynamic_cast<InnerModelPrismaticJoint*>(node)->getPosition();
	}
	mstateMap = states;
}

MotorParamsList JointMotorI::getAllMotorParams(const Ice::Current&)
{
	return params;
}

RoboCompJointMotor::BusParams JointMotorI::getBusParams(const Ice::Current&)
{
	return busparams;
}
