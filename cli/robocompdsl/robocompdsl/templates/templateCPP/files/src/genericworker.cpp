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
GenericWorker::GenericWorker(${constructor_proxies}) : ${inherited_constructor}
{

	${statemachine_initialization}
	
	${require_and_publish_proxies_creation}

	${state_statemachine}

	${transition_statemachine}

	${add_state_statemachine}

	${configure_statemachine}

	${gui_setup}
}

/**
* \brief Default destructor
*/
GenericWorker::~GenericWorker()
{
	for (auto state : states) {
        delete state;
    }

}
void GenericWorker::killYourSelf()
{
	rDebug("Killing myself");
	emit kill();
}

void GenericWorker::initializeWorker()
{
	statemachine.start();

	connect(&hibernationChecker, SIGNAL(timeout()), this, SLOT(hibernationCheck()));

	auto error = statemachine.errorString();
    if (error.length() > 0){
        qWarning() << error;
        throw error;
    }

}

/**
* \brief Change compute period
* @param nameState name state "Compute" or "Emergency"
* @param per Period in ms
*/
void GenericWorker::setPeriod(STATES state, int p)
{
	switch (state)
	{
	case STATES::Compute:
		this->period = p;
		states[STATES::Compute]->setPeriod(this->period);
		std::cout << "Period Compute changed " << p  << "ms" << std::endl<< std::flush;
		break;

	case STATES::Emergency:
		states[STATES::Emergency]->setPeriod(this->period);
		std::cout << "Period Emergency changed " << p << "ms" << std::endl<< std::flush;
		break;
	
	default:
		std::cerr<<"No change in the period, the state parameter must be 'Compute' or 'Emergency'."<< std::endl<< std::flush;
		break;
	}
}

int GenericWorker::getPeriod(STATES state)
{
	if (state < 0 || state >= STATES::NumberOfStates) {
        std::cerr << "Invalid state parameter." << std::endl << std::flush;
        return -1;
    }
	return states[state]->getPeriod();
}

void GenericWorker::hibernationCheck()
{
	//Time between activity to activate hibernation
    static const int HIBERNATION_TIMEOUT = 5000;

    static std::chrono::high_resolution_clock::time_point lastWakeTime = std::chrono::high_resolution_clock::now();
	static int originalPeriod = this->period;
    static bool isInHibernation = false;

	// Update lastWakeTime by calling a function
    if (hibernation)
    {
        hibernation = false;
        lastWakeTime = std::chrono::high_resolution_clock::now();

		// Restore period
        if (isInHibernation)
        {
            this->setPeriod(STATES::Compute, originalPeriod);
            isInHibernation = false;
        }
    }

    auto now = std::chrono::high_resolution_clock::now();
    auto elapsedTime = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastWakeTime);

	//HIBERNATION_TIMEOUT exceeded, change period
    if (elapsedTime.count() > HIBERNATION_TIMEOUT && !isInHibernation)
    {
        isInHibernation = true;
		originalPeriod = this->getPeriod(STATES::Compute);
        this->setPeriod(STATES::Compute, 500);
    }
}

${agm_methods}
