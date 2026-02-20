/*
 *    Copyright (C) ${year} by YOUR NAME HERE
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
#include "genericworker.h"
/**
* \brief Default constructor
*/
GenericWorker::GenericWorker(const ConfigLoader& configLoader, ${constructor_proxies}) : ${inherited_constructor}
{

	this->configLoader = configLoader;
    if (!this->configLoader.get<bool>("Component.Debug.Verbose")) {
        qInstallMessageHandler([](QtMsgType, const QMessageLogContext&, const QString&) {});
    }
	${require_and_publish_proxies_creation}

	${state_statemachine}

	${transition_statemachine}

	${add_state_statemachine}

	statemachine.setInitialState(states["Initialize"].get());

	connect(&hibernationChecker, SIGNAL(timeout()), this, SLOT(hibernationCheck()));

	${gui_setup}

    ${dsr_set_params}
}

/**
* \brief Default destructor
*/
GenericWorker::~GenericWorker()
{
    ${dsr_delete}
}
void GenericWorker::killYourSelf()
{
	qDebug("Killing myself");
	emit kill();
}

/**
* \brief Change compute period of state
* @param state name of state
* @param period Period in ms
*/
void GenericWorker::setPeriod(const std::string& state, int period)
{
    auto it = states.find(state); 
    if (it != states.end() && it->second != nullptr)
    {
		it->second->setPeriod(period);
		std::cout << "Period for state " << state << " changed to " << period << "ms" << std::endl << std::flush;
	}
    else
        std::cerr << "No change in the period, the state is not valid or not configured."<< std::endl;
}

int GenericWorker::getPeriod(const std::string& state)
{
    auto it = states.find(state);

    if (it == states.end() || it->second == nullptr)
    {
        std::cerr << "Invalid or unconfigured state: " << state << std::endl;
        return -1; 
	}
    return it->second->getPeriod();
}

void GenericWorker::hibernationCheck()
{
	//Time between activity to activate hibernation
    static const int HIBERNATION_TIMEOUT = 5000;

    static std::chrono::high_resolution_clock::time_point lastWakeTime = std::chrono::high_resolution_clock::now();
	static int originalPeriod;
    static bool isInHibernation = false;

	// Update lastWakeTime by calling a function
    if (hibernation)
    {
        hibernation = false;
        lastWakeTime = std::chrono::high_resolution_clock::now();

		// Restore period
        if (isInHibernation)
        {
            this->setPeriod("Compute", originalPeriod);
            isInHibernation = false;
        }
    }

    auto now = std::chrono::high_resolution_clock::now();
    auto elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastWakeTime);

	//HIBERNATION_TIMEOUT exceeded, change period
    if (elapsedTime.count() > HIBERNATION_TIMEOUT && !isInHibernation)
    {
        isInHibernation = true;
		originalPeriod = this->getPeriod("Compute");
        this->setPeriod("Compute", 500);
    }
}

void GenericWorker::hibernationTick(){
	hibernation = true;
}

${dsr_viewer}

void GenericWorker::initialize(){
    ${dsr_initialize}
};