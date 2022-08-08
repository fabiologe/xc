//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis C. Pérez Tato
//
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
//python_interface.tcc

XC::DqUniaxialMaterial & (XC::ConnectedMaterial::*getConnectedMaterials)(void)= &XC::ConnectedMaterial::getMaterials;
class_<XC::ConnectedMaterial , bases<XC::UniaxialMaterial>, boost::noncopyable >("ConnectedMaterial", no_init)
  .add_property("numMaterials", &XC::ConnectedMaterial::getNumMaterials,"Return the number of connected materials.")
  .def("setMaterials",&XC::ConnectedMaterial::setMaterials, "Sets the connected materials.")
  .def("getMaterials",make_function(getConnectedMaterials,return_internal_reference<>()),"Return a reference to the material container.")
  ;

class_<XC::ParallelMaterial, bases<XC::ConnectedMaterial>, boost::noncopyable >("ParallelMaterial", no_init);

class_<XC::SeriesMaterial , bases<XC::ConnectedMaterial>, boost::noncopyable >("SeriesMaterial", no_init);


