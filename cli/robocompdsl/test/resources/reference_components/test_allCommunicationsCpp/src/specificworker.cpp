/*
 *    Copyright (C) 2022 by YOUR NAME HERE
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
#include "specificworker.h"

/**
* \brief Default constructor
*/
SpecificWorker::SpecificWorker(MapPrx& mprx, bool startup_check) : GenericWorker(mprx)
{
	this->startup_check_flag = startup_check;
	// Uncomment if there's too many debug messages
	// but it removes the possibility to see the messages
	// shown in the console with qDebug()
//	QLoggingCategory::setFilterRules("*.debug=false\n");
}

/**
* \brief Default destructor
*/
SpecificWorker::~SpecificWorker()
{
	std::cout << "Destroying SpecificWorker" << std::endl;
	emit t_compute_to_finalize();
}

bool SpecificWorker::setParams(RoboCompCommonBehavior::ParameterList params)
{
//	THE FOLLOWING IS JUST AN EXAMPLE
//	To use innerModelPath parameter you should uncomment specificmonitor.cpp readConfig method content
//	try
//	{
//		RoboCompCommonBehavior::Parameter par = params.at("InnerModelPath");
//		std::string innermodel_path = par.value;
//		innerModel = std::make_shared(innermodel_path);
//	}
//	catch(const std::exception &e) { qFatal("Error reading config params"); }




	defaultMachine.start();


	return true;
}

void SpecificWorker::initialize(int period)
{
	std::cout << "Initialize worker" << std::endl;
	this->Period = period;
	if(this->startup_check_flag)
	{
		this->startup_check();
	}
	else
	{
		timer.start(Period);
		emit this->t_initialize_to_compute();
	}

}

void SpecificWorker::compute()
{
	//computeCODE
	//QMutexLocker locker(mutex);
	//try
	//{
	//  camera_proxy->getYImage(0,img, cState, bState);
	//  memcpy(image_gray.data, &img[0], m_width*m_height*sizeof(uchar));
	//  searchTags(image_gray);
	//}
	//catch(const Ice::Exception &e)
	//{
	//  std::cout << "Error reading from Camera" << e << std::endl;
	//}
	
	
}

int SpecificWorker::startup_check()
{
	std::cout << "Startup check" << std::endl;
	QTimer::singleShot(200, qApp, SLOT(quit()));
	return 0;
}



void SpecificWorker::sm_compute()
{
	std::cout<<"Entered state compute"<<std::endl;
	compute();
}


void SpecificWorker::sm_initialize()
{
	std::cout<<"Entered initial state initialize"<<std::endl;
}


void SpecificWorker::sm_finalize()
{
	std::cout<<"Entered final state finalize"<<std::endl;
}



int SpecificWorker::HandDetection_addNewHand(const int expectedHands, const RoboCompHandDetection::TRoi &roi)
{
//implementCODE

}

RoboCompHandDetection::Hands SpecificWorker::HandDetection_getHands()
{
//implementCODE

}

int SpecificWorker::HandDetection_getHandsCount()
{
//implementCODE

}

//SUBSCRIPTION to newAprilTag method from AprilTags interface
void SpecificWorker::AprilTags_newAprilTag(const RoboCompAprilTags::tagsList &tags)
{
//subscribesToCODE

}

//SUBSCRIPTION to newAprilTagAndPose method from AprilTags interface
void SpecificWorker::AprilTags_newAprilTagAndPose(const RoboCompAprilTags::tagsList &tags, const RoboCompGenericBase::TBaseState &bState, const RoboCompJointMotor::MotorStateMap &hState)
{
//subscribesToCODE

}



/**************************************/
// From the RoboCompCameraSimple you can call this methods:
// this->camerasimple_proxy->getImage(...)

/**************************************/
// From the RoboCompCameraSimple you can use this types:
// RoboCompCameraSimple::TImage

/**************************************/
// From the RoboCompRGBD you can call this methods:
// this->rgbd_proxy->getData(...)
// this->rgbd_proxy->getDepth(...)
// this->rgbd_proxy->getDepthInIR(...)
// this->rgbd_proxy->getImage(...)
// this->rgbd_proxy->getRGB(...)
// this->rgbd_proxy->getRGBDParams(...)
// this->rgbd_proxy->getRegistration(...)
// this->rgbd_proxy->getXYZ(...)
// this->rgbd_proxy->getXYZByteStream(...)
// this->rgbd_proxy->setRegistration(...)

/**************************************/
// From the RoboCompRGBD you can use this types:
// RoboCompRGBD::ColorRGB
// RoboCompRGBD::PointXYZ
// RoboCompRGBD::CameraParameters
// RoboCompRGBD::TRGBDParams

/**************************************/
// From the RoboCompAprilBasedLocalization you can publish calling this methods:
// this->aprilbasedlocalization_pubproxy->newAprilBasedPose(...)

/**************************************/
// From the RoboCompHandDetection you can use this types:
// RoboCompHandDetection::TImage
// RoboCompHandDetection::TRoi
// RoboCompHandDetection::Hand

/**************************************/
// From the RoboCompAprilTags you can use this types:
// RoboCompAprilTags::tag

