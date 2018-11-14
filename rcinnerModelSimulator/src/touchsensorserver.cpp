/*
 * Copyright 2018 <copyright holder> <email>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#include "touchsensorserver.h"

TouchSensorServer::TouchSensorServer(Ice::CommunicatorPtr communicator, std::shared_ptr<SpecificWorker> worker_, uint32_t _port)
{
	port = _port;
	worker = worker_;
	std::stringstream out1;
	out1 << port;
	comm = communicator;
	std::string name = std::string("TouchSensor") + out1.str();
	std::string endp = std::string("tcp -p ")     + out1.str();

	adapter = communicator->createObjectAdapterWithEndpoints(name, endp);
	printf("Creating TouchSensor adapter <<%s>> with endpoint <<%s>>\n", name.c_str(), endp.c_str());
	interface = new TouchSensorI(worker);
	adapter->add(interface, Ice::stringToIdentity("touchsensor"));
	adapter->activate();
}

void TouchSensorServer::add(InnerModelTouchSensor *sensor)
{
	sensors.push_back(sensor);
	interface->add(sensor->id.toStdString());
}

void TouchSensorServer::remove(InnerModelTouchSensor *sensor)
{
	interface->remove(sensor->id.toStdString());
	sensors.erase(std::remove(sensors.begin(), sensors.end(), sensor), sensors.end());
}

bool TouchSensorServer::empty()
{
	if (sensors.size()==0)
		return true;
	return false;
}

void TouchSensorServer::shutdown()
{
	try
	{
		adapter->remove(Ice::stringToIdentity("touchsensor"));
	}
	catch(Ice::ObjectAdapterDeactivatedException e)
	{
	}
	adapter->destroy();
}

