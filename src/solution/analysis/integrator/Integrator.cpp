//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  This program derives from OpenSees <http://opensees.berkeley.edu>
//  developed by the  «Pacific earthquake engineering research center».
//
//  Except for the restrictions that may arise from the copyright
//  of the original program (see copyright_opensees.txt)
//  XC is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details. 
//
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
/* ****************************************************************** **
**    OpenSees - Open System for Earthquake Engineering Simulation    **
**          Pacific Earthquake Engineering Research Center            **
**                                                                    **
**                                                                    **
** (C) Copyright 1999, The Regents of the University of California    **
** All Rights Reserved.                                               **
**                                                                    **
** Commercial use of this program without express permission of the   **
** University of California, Berkeley, is strictly prohibited.  See   **
** file 'COPYRIGHT'  in main directory for information on usage and   **
** redistribution,  and for a DISCLAIMER OF ALL WARRANTIES.           **
**                                                                    **
** Developed by:                                                      **
**   Frank McKenna (fmckenna@ce.berkeley.edu)                         **
**   Gregory L. Fenves (fenves@ce.berkeley.edu)                       **
**   Filip C. Filippou (filippou@ce.berkeley.edu)                     **
**                                                                    **
** ****************************************************************** */
                                                                        
// $Revision: 1.1.1.1 $
// $Date: 2000/09/15 08:23:17 $
// $Source: /usr/local/cvs/OpenSees/SRC/analysis/integrator/Integrator.cpp,v $
                                                                        
                                                                        
// File: ~/analysis/integrator/Integrator.C
// 
// Written: fmk 
// Created: 11/96
// Revision: A
//
// Description: This file contains the implementation of XC::Integrator.
//
// What: "@(#) Integrator.C, revA"

#include <solution/analysis/integrator/Integrator.h>
#include "solution/AnalysisAggregation.h"
#include "solution/analysis/model/AnalysisModel.h"
#include "domain/mesh/element/utils/RayleighDampingFactors.h"

//! @brief Constructor.
XC::Integrator::Integrator(AnalysisAggregation *owr,int clasTag)
  :MovableObject(clasTag), EntCmd(owr) {}

void XC::Integrator::applyLoadModel(double newTime)
  { getAnalysisModelPtr()->applyLoadDomain(newTime); }

int XC::Integrator::updateModel(void)
  { return getAnalysisModelPtr()->updateDomain(); }

int XC::Integrator::updateModel(double newTime, double dT)
  { return getAnalysisModelPtr()->updateDomain(newTime,dT); }

double XC::Integrator::getCurrentModelTime(void)
  { return getAnalysisModelPtr()->getCurrentDomainTime(); }

void XC::Integrator::setCurrentModelTime(const double &t)
  { getAnalysisModelPtr()->setCurrentDomainTime(t); }

void XC::Integrator::setRayleighDampingFactors(const RayleighDampingFactors &rF)
  { getAnalysisModelPtr()->setRayleighDampingFactors(rF); }

int XC::Integrator::commitModel(void)
  { return getAnalysisModelPtr()->commitDomain(); }

//! @brief Returns a pointer to the solution method that owns this object.
XC::AnalysisAggregation *XC::Integrator::getAnalysisAggregation(void)
  { return dynamic_cast<AnalysisAggregation *>(Owner()); }

//! @brief Returns a const pointer to the solution method that owns this object.
const XC::AnalysisAggregation *XC::Integrator::getAnalysisAggregation(void) const
  { return dynamic_cast<const AnalysisAggregation *>(Owner()); }


//! @brief Returns a pointer to the analysis model.
const XC::AnalysisModel *XC::Integrator::getAnalysisModelPtr(void) const
  {
    const AnalysisAggregation *sm= getAnalysisAggregation();
    assert(sm);
    return sm->getAnalysisModelPtr();
  }

//! @brief Returns a pointer to the analysis model.
XC::AnalysisModel *XC::Integrator::getAnalysisModelPtr(void)
  {
    const AnalysisAggregation *sm= getAnalysisAggregation();
    assert(sm);
    return sm->getAnalysisModelPtr();
  }

//! @brief Hace los cambios oportunos cuando se ha producido un cambio en el domain.
int XC::Integrator::domainChanged(void)
  { return 0; }

void XC::Integrator::Print(std::ostream &s, int flag)
  {
    if(getAnalysisModelPtr())
      s << "\t XC::LoadPath - currentLambda: " << getCurrentModelTime() << std::endl;
    else 
      s << "\t XC::LoadPath - no associated AnalysisModel\n"; 
  }

//! @brief Send object members through the channel being passed as parameter.
int XC::Integrator::sendData(CommParameters &cp)
  {
    return 0;
  }

//! @brief Receives object members through the channel being passed as parameter.
int XC::Integrator::recvData(const CommParameters &cp)
  {
    return 0;
  }
