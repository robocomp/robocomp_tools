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
#ifndef GENERICWORKER_H
#define GENERICWORKER_H

#include <stdint.h>
${gui_includes}
${statemachine_includes}
#include <grafcetStep/GRAFCETStep.h>
#include <ConfigLoader/ConfigLoader.h>
#include <QStateMachine>
#include <QEvent>
#include <QString>
#include <functional>
#include <atomic>
#include <QtCore>
#include <variant>



${interfaces_includes}
${agm_includes}

${need_gui}

#define PROGRAM_NAME    "${component_name}"
#define SERVER_FULL_NAME   "RoboComp ${component_name}:: ${component_name}"

#define BASIC_PERIOD 100

${ice_proxies_map}

${agm_behaviour_parameter_struct}

class GenericWorker : ${inherited_object}
{
Q_OBJECT
public:
	GenericWorker(const ConfigLoader& configLoader, ${constructor_proxies});
	virtual ~GenericWorker();
	virtual void killYourSelf();

	enum STATES { Initialize, Compute, Emergency, Restore, NumberOfStates };
	void setPeriod(STATES state, int period);
	int getPeriod(STATES state);

	QStateMachine statemachine;
	QTimer hibernationChecker;
	std::atomic_bool hibernation = false;

	${agm_methods}

	${create_proxies}

	${implements}
	${subscribes}

protected:
	std::vector<GRAFCETStep*> states;
	ConfigLoader configLoader;
	
	${statemachine_creation}

	${agm_attributes_creation}


private:

public slots:
	${statemachine_slots}
	${virtual_statemachine}

	void initializeWorker();
	void hibernationCheck();

	
signals:
	void kill();
	${statemachine_signals}
	${signal_statemachine}
};

#endif
