/*
 *    Copyright (C)2017 by YOUR NAME HERE
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
#ifndef DISPLAY_H
#define DISPLAY_H

#include <QImage>

// Ice includes
#include <Ice/Ice.h>
#include <Display.h>
#include <innermodel/innermodel.h>
#include "specificworker.h"

// Simulator includes
#include <config.h>


using namespace RoboCompDisplay;

class DisplayI : public virtual RoboCompDisplay::Display
{
public:
DisplayI(GenericWorker *_worker);
	~DisplayI();

	void add(QString id);
	void remove(QString id);

	void setImage(const Image  &img, const Ice::Current&);

private:

	GenericWorker *worker;
	QString id;

};

#endif
