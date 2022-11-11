//----------------------------------------------------------------------------
//  xc utils library bilioteca de comandos para el intérprete del lenguaje
//  de entrada de datos.
//
//  Copyright (C)  Luis C. Pérez Tato
//
//  XC utils is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details. 
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//ActionsFamily.cxx

#include "ActionsFamily.h"
#include "ActionsAndFactors.h"
#include "utility/load_combinations/comb_analysis/Variations.h"
#include "utility/load_combinations/comb_analysis/LoadCombinationVector.h"
#include "utility/load_combinations/actions/Action.h"


//! @brief Default constructor.
cmb_acc::ActionsFamily::ActionsFamily(const std::string &nmb)
  : NamedEntity(nmb)
  {
    actions.set_owner(this);
  }

//! @brief Return the container that contains this object.
const  cmb_acc::ActionsAndFactors *cmb_acc::ActionsFamily::getActionsAndFactors(void) const
  {
    const CommandEntity *owr= Owner();
    const ActionsAndFactors *retval= dynamic_cast<const ActionsAndFactors *>(owr);
    if(!retval)
      std::cerr << getClassName() << "::" << __FUNCTION__
 	        << "; family: '" << getName()
		<< "' owner not found." << std::endl;
    return retval;
  }

//! @brief Return a pointer to the combination factors container.
const cmb_acc::CombinationFactorsMap *cmb_acc::ActionsFamily::getPtrCombinationFactors(void) const
  {
    const cmb_acc::CombinationFactorsMap *retval= nullptr;
    const ActionsAndFactors *tmp= getActionsAndFactors();
    if(tmp)
      retval= tmp->getFactors().getPtrCombinationFactors();
    return retval;
  }

//! @brief Return a pointer to the partial safety factors container.
const cmb_acc::PartialSafetyFactorsMap *cmb_acc::ActionsFamily::getPtrPartialSafetyFactors(void) const
  {
    const cmb_acc::PartialSafetyFactorsMap *retval= nullptr;
    const ActionsAndFactors *tmp= getActionsAndFactors();
    if(tmp)
      retval= tmp->getFactors().getPtrPartialSafetyFactors();
    return retval;
  }

//! @brief Insert the action argument and sets the its combination and
//! partial safety factors.
//! @param a: Action object to insert.
//! @param combination_factors_name: name of the combination factors that
//!                                  correspond to the action.
//! @param partial_safety_factors_name: name of the partial safety factors
//!                                     that correspond to the action.
cmb_acc::ActionWrapper &cmb_acc::ActionsFamily::insert(const Action &a,const std::string &combination_factors_name,const std::string &partial_safety_factors_name)
  { return actions.insert(a,combination_factors_name,partial_safety_factors_name); }

//! @brief Insert the group of actions being passed as parameter and sets
//! its combination and partial safety factors.
//! @param actions: Vector of action objects to insert.
//! @param combination_factors_names: vector of names of the combination factors //!                                  that correspond to the action.
//! @param partial_safety_factors_name: name (unique) of the partial safety
//!                                     factors that correspond to the actions
//!                                     of the group. The uniqueness of the
//!                                     applicable partial safety factors is
//!                                     the essence of a group of actions.
cmb_acc::ActionWrapper &cmb_acc::ActionsFamily::insertGroup(const std::vector<Action> &actions, const std::vector<std::string> &combination_factors_names, const std::string &partial_safety_factors_name)
  {
    return this->actions.insertGroup(actions, combination_factors_names, partial_safety_factors_name);
  }

//! @brief Insert the group of actions being passed as parameter and sets
//! its combination and partial safety factors.
//! @param actionTuples: list of (action, combination_factors_name) tuples.
//! @param partial_safety_factors_name: name (unique) of the partial safety
//!                                     factors that correspond to the actions
//!                                     of the group. The uniqueness of the
//!                                     applicable partial safety factors is
//!                                     the essence of a group of actions.
cmb_acc::ActionWrapper &cmb_acc::ActionsFamily::insertGroupPy(const boost::python::list &actionTuples, const std::string &partial_safety_factors_name)
  {
    return this->actions.insertGroupPy(actionTuples, partial_safety_factors_name);
  }