//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
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

typedef XC::ModelComponentContainer<XC::Pnt> cm_point_map;
class_<cm_point_map, bases<XC::ModelComponentContainerBase>, boost::noncopyable >("CMPointMap", no_init)
  .def(XC::mapptr_indexing_suite<cm_point_map>() )
  .add_property("size", &cm_point_map::size)
  .def("exists", &cm_point_map::exists)
  .def("get", make_function(&cm_point_map::get,return_internal_reference<>()))
  .def("getKeys", &cm_point_map::getKeys)
   ;

typedef XC::EntityMap<XC::Pnt> point_map;
XC::Pnt *(point_map::*getNearestPoint)(const Pos3d &)= &point_map::getNearest;
class_<point_map, bases<cm_point_map>, boost::noncopyable >("point_map", no_init)
  .def("getNearest", getNearestPoint, return_internal_reference<>(),"Return the nearest point.")
   ;

XC::Pnt *(XC::PntMap::*newPoint)(void)= &XC::PntMap::New;
XC::Pnt *(XC::PntMap::*newPointFromPos3d)(const Pos3d &)= &XC::PntMap::New;
XC::Pnt *(XC::PntMap::*newPointIDPos3d)(const size_t &,const Pos3d &)= &XC::PntMap::New;
class_<XC::PntMap, bases<point_map>, boost::noncopyable >("PntMap", no_init)
  .def("newPnt", newPoint, return_internal_reference<>(),"Creates a point.")
  .def("newPntFromPos3d", newPointFromPos3d, return_internal_reference<>(),"Creates a point in the position.")
  .def("newPntIDPos3d", newPointIDPos3d, return_internal_reference<>(),"Creates a point with the ID and the the position provided.")
   .def("get", &XC::PntMap::get, return_internal_reference<>(),"Return the i-th point.")
   ;

typedef XC::ModelComponentContainer<XC::Edge> map_cm_edges;
class_<map_cm_edges, bases<XC::ModelComponentContainerBase>, boost::noncopyable >("MapCMEdges", no_init)
  .def(XC::mapptr_indexing_suite<map_cm_edges>() )
  .add_property("size", &map_cm_edges::size)
  .def("exists", &map_cm_edges::exists)
  .def("get", make_function(&map_cm_edges::get,return_internal_reference<>()))
  .def("getKeys", &map_cm_edges::getKeys)
   ;

typedef XC::EntityMap<XC::Edge> map_edges;
class_<map_edges, bases<map_cm_edges>, boost::noncopyable >("map_edges", no_init)
   ;

class_<XC::LineMap, bases<map_edges>, boost::noncopyable >("LineMap", no_init)
   .def("newLine", &XC::LineMap::newLine, return_internal_reference<>(),"Creates a line.")
   .def("newDividedLine", &XC::LineMap::newDividedLine, return_internal_reference<>(),"Creates a line.")
   .def("newCircleArc", &XC::LineMap::newCircleArc, return_internal_reference<>(),"Creates a circle arc.")
   .def("newLineSequence", &XC::LineMap::newLineSequence, return_internal_reference<>(),"Creates a line sequence (polyline).")
   .def("get", &XC::LineMap::get, return_internal_reference<>(),"Return the i-th line.")
   ;

typedef XC::ModelComponentContainer<XC::Face> map_cm_faces;
class_<map_cm_faces, bases<XC::ModelComponentContainerBase>, boost::noncopyable >("MapCMFaces", no_init)
  .def(XC::mapptr_indexing_suite<map_cm_faces>() )
  .add_property("size", &map_cm_faces::size)
  .def("exists", &map_cm_faces::exists)
  .def("get", make_function(&map_cm_faces::get,return_internal_reference<>()))
  .def("getKeys", &map_cm_faces::getKeys)
   ;

typedef XC::EntityMap<XC::Face> map_faces;
class_<map_faces, bases<map_cm_faces>, boost::noncopyable >("map_faces", no_init)
   ;

class_<XC::SurfaceMap, bases<map_faces>, boost::noncopyable >("SurfaceMap", no_init)
   .def("newQuadSurfacePts", &XC::SurfaceMap::newQuadSurfacePts, return_internal_reference<>(),"Creates a quadrilateral surface.")
   .def("newQuadSurfaceLines", &XC::SurfaceMap::newQuadSurfaceLines, return_internal_reference<>(),"Creates a quadrilateral surface.")
   .def("newQuadSurfaceGridPts", &XC::SurfaceMap::newQuadSurfaceGridPoints, return_internal_reference<>(),"Create a quadrilateral surface.")
   .def("get", &XC::SurfaceMap::get, return_internal_reference<>(),"Return the i-th face.")
   .def("conciliaNDivs", &XC::SurfaceMap::conciliaNDivs)
   .def("checkNDivs",&XC::SurfaceMap::checkNDivs,"Check the number of divisions.")
   ;

typedef XC::ModelComponentContainer<XC::Body> map_cm_bodies;
class_<map_cm_bodies, bases<XC::ModelComponentContainerBase>, boost::noncopyable >("MapCMBodies", no_init)
  .def(XC::mapptr_indexing_suite<map_cm_bodies>() )
  .add_property("size", &map_cm_bodies::size)
  .def("exists", &map_cm_bodies::exists)
  .def("get", make_function(&map_cm_bodies::get,return_internal_reference<>()))
  .def("getKeys", &map_cm_bodies::getKeys)
   ;

typedef XC::EntityMap<XC::Body> map_bodies;
class_<map_bodies, bases<map_cm_bodies>, boost::noncopyable >("map_bodies", no_init)
   ;

class_<XC::BodyMap, bases<map_bodies>, boost::noncopyable >("MapBodies", no_init)
   .def("newBlockPts", &XC::BodyMap::newBlockPts, return_internal_reference<>(),"Creates a hexahedrical block.")
   .def("get", &XC::BodyMap::get, return_internal_reference<>(),"Return the i-th face.")
   .def("conciliaNDivs", &XC::BodyMap::conciliaNDivs)
   .def("checkNDivs",&XC::BodyMap::checkNDivs,"Check the number of divisions.")
   ;

typedef XC::ModelComponentContainer<XC::UniformGrid> map_cm_ugrids;
class_<map_cm_ugrids, bases<XC::ModelComponentContainerBase>, boost::noncopyable >("MapCMUgrids", no_init)
  .def(XC::mapptr_indexing_suite<map_cm_ugrids>() )
  .add_property("size", &map_cm_ugrids::size)
  .def("exists", &map_cm_ugrids::exists)
  .def("get", make_function(&map_cm_ugrids::get,return_internal_reference<>()))
  .def("getKeys", &map_cm_ugrids::getKeys)
   ;

typedef XC::EntityMap<XC::UniformGrid> map_ugrids;
class_<map_ugrids, bases<map_cm_ugrids>, boost::noncopyable >("map_ugrids", no_init)
   ;

XC::UniformGrid *(XC::UniformGridMap::*newUniformGrid)(void)= &XC::UniformGridMap::New;

class_<XC::UniformGridMap, bases<map_ugrids>, boost::noncopyable >("UniformGridMap", no_init)
   .def("newUniformGrid", newUniformGrid, return_internal_reference<>(),"Creates a uniform grid.")
   ;




