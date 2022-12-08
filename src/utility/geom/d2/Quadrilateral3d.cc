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
//Quadrilateral3d.cc

#include "Quadrilateral3d.h"
#include "Polygon3d.h"
#include "utility/geom/ref_sys/Ref2d3d.h"
#include "utility/geom/d1/Line2d.h"
#include "utility/geom/d1/Segment2d.h"
#include "utility/geom/d1/Segment3d.h"
#include "utility/geom/d1/Line3d.h"
#include "utility/geom/d3/GeomGroup3d.h"
#include "utility/geom/d3/HalfSpace3d.h"
#include "utility/geom/lists/auxiliary.h"


//! @brief Constructor.
Quadrilateral3d::Quadrilateral3d(const Pos3d &p1,const Pos3d &p2,const Pos3d &p3, const Pos3d &p4)
  : D2to3d(p1,p2,p3), quad2d()
  {
    const Pos2d p1_2D= to_2d(p1); const Pos2d p2_2D= to_2d(p2);
    const Pos2d p3_2D= to_2d(p3); const Pos2d p4_2D= to_2d(p4);
    this->quad2d= Quadrilateral2d(p1_2D, p2_2D, p3_2D, p4_2D);
  }

//! @brief Constructor.
Quadrilateral3d::Quadrilateral3d(const Ref2d3d &rf,const Quadrilateral2d &p)
  : D2to3d(rf), quad2d(p) {}

//! @brief Constructor.
Quadrilateral3d::Quadrilateral3d(const Ref3d3d &rf,const Quadrilateral2d &p)
  : D2to3d(rf), quad2d(p) {}

//! @brief Constructor.
Quadrilateral3d::Quadrilateral3d(const GeomObj::list_Pos3d &vertices)
  : D2to3d(vertices[0], vertices[1], vertices[2]), quad2d()
  {
    const size_t sz= vertices.size();
    if(sz>=4)
      {
	const Pos2d v1= to_2d(vertices[0]); const Pos2d v2= to_2d(vertices[1]);
	const Pos2d v3= to_2d(vertices[2]); const Pos2d v4= to_2d(vertices[3]);
	quad2d= Quadrilateral2d(v1, v2, v3, v4);
      }
    else
      std::cerr << getClassName() << "::" << __FUNCTION__
		<< " four vertices are needed." << std::endl;
  }

//! @brief Constructor.
Quadrilateral3d::Quadrilateral3d(const boost::python::list &l)
  : D2to3d(), quad2d()
  {
    GeomObj::list_Pos3d vertices;
    const size_t sz= len(l);
    for(size_t i=0; i<sz; i++)
      vertices.push_back(boost::python::extract<Pos3d>(l[i]));

    (*this)= Quadrilateral3d(vertices);
  }

//! @brief Return a Python list containing the positions
//! of the quadrilateral vertices.
GeomObj::list_Pos3d Quadrilateral3d::getVertexList(void) const
  {
    GeomObj::list_Pos3d retval;
    Quadrilateral2d::vertex_iterator i= quad2d.vertices_begin();
    for(;i!=quad2d.vertices_end();i++)
      retval.push_back(to_3d(Pos2d(*i)));
    return retval;
  }

//! @brief Return a Python list containing the positions
//! of the quadrilateral vertices.
boost::python::list Quadrilateral3d::getVertexListPy(void) const
  {
    boost::python::list retval;
    GeomObj::list_Pos3d lst= getVertexList();
    GeomObj::list_Pos3d::const_iterator i= lst.begin();
    for(;i!=lst.end();i++)
      retval.append(*i);
    return retval;
  }

//! @brief Return the i-th edge (i between 1 and num_sides).
Segment3d Quadrilateral3d::Lado(unsigned int i) const
  {
    Segment2d sg2d= quad2d.Lado(i);
    return to_3d(sg2d);
  }

//! @brief Return the i-th side (i between 0 and num_sides-1).
Segment3d Quadrilateral3d::Lado0(unsigned int i) const
  {
    Segment2d sg2d= quad2d.Lado0(i);
    return to_3d(sg2d);
  }

//! @brief Return the index of the distal edge with respect to the point
//! argument.
//! @param p: 2D point.
int Quadrilateral3d::getIndexOfDistalEdge(const Pos3d &p) const
  {
    const unsigned int nl= getNumEdges();
    int retval= 1;
    GEOM_FT d2= Lado0(1).dist2(p);
    GEOM_FT maxDist2= d2;
    for(unsigned int i= 2; i<=nl;i++)
      {
        d2= Lado0(i).dist2(p);
	if(d2>maxDist2)
	  {
	    retval= i;
	    maxDist2= d2;
	  }
      }
    return retval;
  }

//! @brief Return the proximal edge with respect to the point argument.
//! @param p: 2D point.
int Quadrilateral3d::getIndexOfProximalEdge(const Pos3d &p) const
  {
    const unsigned int nl= getNumEdges();
    int retval= 1;
    GEOM_FT d2= Lado0(1).dist2(p);
    GEOM_FT minDist2= d2;
    for(unsigned int i= 2; i<=nl;i++)
      {
        d2= Lado0(i).dist2(p);
	if(d2<minDist2)
	  {
	    retval= i;
	    minDist2= d2;
	  }
      }
    return retval;
  }

Polygon3d Quadrilateral3d::getPolygon3d(void) const
  {
    return Polygon3d(this->getRef(), this->quad2d);
  }

//! @brief Return the distal vertex with respect to the point argument.
//! @param p: 2D point.
int Quadrilateral3d::getIndexOfDistalVertex(const Pos3d &p) const
  {
    const unsigned int nl= getNumVertices();
    int retval= 1;
    GEOM_FT d2= Vertice0(1).dist2(p);
    GEOM_FT maxDist2= d2;
    for(unsigned int i= 2; i<=nl;i++)
      {
        d2= Vertice0(i).dist2(p);
	if(d2>maxDist2)
	  {
	    retval= i;
	    maxDist2= d2;
	  }
      }
    return retval;
  }
    
//! @brief Return the proximal vertex with respect to the point argument.
//! @param p: 2D point.
int Quadrilateral3d::getIndexOfProximalVertex(const Pos3d &p) const
  {
    const unsigned int nl= getNumVertices();
    int retval= 1;
    GEOM_FT d2= Vertice0(1).dist2(p);
    GEOM_FT minDist2= d2;
    for(unsigned int i= 2; i<=nl;i++)
      {
        d2= Vertice0(i).dist2(p);
	if(d2<minDist2)
	  {
	    retval= i;
	    minDist2= d2;
	  }
      }
    return retval;
  }

Plane Quadrilateral3d::getPlaneFromSide(unsigned int i) const
  {
    Segment3d lado= Lado(i);
    Vector3d v= -getPlane().Normal(); // interior points -> negative distance.
    return Plane(lado,v);
  }

Plane Quadrilateral3d::getPlaneFromSide0(unsigned int i) const
  { return getPlaneFromSide(i+1); }

//! @brief Return true if the point lies inside the quadrilateral
//! (i. e. the distance from the point to the quadrilateral is less
//! than the tolerance argument).
bool Quadrilateral3d::In(const Pos3d &p,const double &tol) const
  {
    bool retval= false;
    const Plane plane= getPlane();
    if(!plane.In(p,tol))
      { retval= false; }
    else
      {
	const Pos3d prj= plane.Projection(p);
        const Pos2d p2d(to_2d(prj));
        retval= quad2d.In(p2d,tol);
      }
    return retval;
  }

//! @brief Return the center of mass of the quadrilateral.
Pos3d Quadrilateral3d::getCenterOfMass(void) const
  {
    const Pos2d centroid= quad2d.getCenterOfMass();
    return to_3d(centroid);
  }

//! @brief Moment of inertia with respect to an axis parallel to
//! the x axis passing through the center of mass.
GEOM_FT Quadrilateral3d::Ix(void) const
  {
    std::cerr << getClassName() << "::" << __FUNCTION__
	      << "; not implemented, 0 is returned." << std::endl;
    return 0;
  }

//! @brief Moment of inertia with respect to an axis parallel to
//! the y axis passing through the center of mass.
GEOM_FT Quadrilateral3d::Iy(void) const
  {
    std::cerr << getClassName() << "::" << __FUNCTION__
	      << "; not implemented, 0 is returned." << std::endl;
    return 0;
  }

//! @brief Moment of inertia with respect to an axis parallel to
//! the z axis passing through the center of mass.
GEOM_FT Quadrilateral3d::Iz(void) const
  {
    std::cerr << getClassName() << "::" << __FUNCTION__
	      << "; not implemented, 0 is returned." << std::endl;
    return 0;
  }

GEOM_FT Quadrilateral3d::GetMax(unsigned short int i) const
  {
    const GeomObj::list_Pos3d lv= getVertexList();
    return get_max_i(i,lv.begin(),lv.end());
  }
GEOM_FT Quadrilateral3d::GetMin(unsigned short int i) const
  {
    const GeomObj::list_Pos3d lv= getVertexList();
    return get_min_i(i,lv.begin(),lv.end());
  }

void Quadrilateral3d::Print(std::ostream &os) const
  {
    unsigned int nv= getNumVertices();
    if(nv<1) return;
    os << Vertice(1);
    for(unsigned int i= 2; i <= nv; i++)
      os << ", " << Vertice(i);
  }

//! @brief Return the squared distance from from point to quadrilateral.
//!
//! The distance is computed as the maximum of:
//!  -The distance from the point to the plane that contains the quadrilateral.
//!  -The signed distances from the point to each of the half spaces
//!  defined by the plane that contains the quadrilateral.
//!
// If the vertices are in counterclockwise order, positive distances
// correspond to point AT THE SAME SIDE OF THE QUADRILATERAL with respect
// to the segment, otherwise the sign of the computed distance must
// be changed.
GEOM_FT Quadrilateral3d::distSigno2(const Pos3d &p) const
  {
    const short int signo= (this->quad2d.clockwise() ? 1 : -1);
    const size_t nv= getNumVertices();
    const size_t nl= getNumEdges();
    if(nv==0) return NAN;
    if(nv==1) return p.dist2(Vertice(1));
     
    //Distance to the plane that contains the quadrilateral.
    GEOM_FT d= getPlane().dist2(p);
    // Distance to the half spaces defined by the sides.
    for(unsigned int i=1; i<=nl; i++)
      {
        HalfSpace3d se3d(getPlaneFromSide(i));
        const GEOM_FT d_i= signo*se3d.distSigno2(p);
        d= std::max(d,d_i);
      }
    return d;
  }

GEOM_FT Quadrilateral3d::distSigno(const Pos3d &p) const
  { return sqrt_FT(::Abs(distSigno2(p))); }

//! @brief Return the distance from point to quadrilateral.
//! Distance is computed as the maximum of the distances
//! (signed) from the point to each of the planes
//! that contain a side and are normal to the plane 
//! that contains the quadrilateral.
//! If the point is inside the quadrilateral 0 is returned.
GEOM_FT Quadrilateral3d::dist2(const Pos3d &p) const
  {
    const GEOM_FT retval= distSigno2(p);
    return (retval >= 0 ? retval : 0);
  }


//! @brief Return the distance from point to quadrilateral.
//! This distance is computed as the maximum of the signed distances from the
//! point to each of the planes that contain a side and are perpendicular to the
//! plane that contains the quadrilateral.
//! In the point is inside the quadrilateral 0 is returned.
GEOM_FT Quadrilateral3d::dist(const Pos3d &p) const
  {
    const GEOM_FT retval= distSigno(p);
    return (retval >= 0 ? retval : 0);
  }

//! @brief Return the values of the shape functions for the point argument.
std::vector<double> Quadrilateral3d::Ni(const Pos3d &p) const
  { return this->quad2d.Ni(this->to_2d(p)); }

//! @brief Return a Python list containing the values of the shape functions for the point argument.
boost::python::list Quadrilateral3d::NiPy(const Pos3d &p) const
  { return this->quad2d.NiPy(this->to_2d(p)); }

//! @brief Return the intersection of the quadrilateral with the line.
Segment3d Quadrilateral3d::Clip(const Line3d &r) const
  {
    Segment3d retval;
    const GEOM_FT angle= getPlane().getAngle(r);
    const GEOM_FT angleTol= 1/180.0*M_PI; // one degree
    if(angle>angleTol)
      {
        std::cerr << getClassName() << "::" << __FUNCTION__
	          << "; line: " << r
	  	  << " is not contained in the quadrilateral plane."
	          << std::endl;
	retval.setExists(false);
      }
    else
      {
	Line2d l2d= to_2d(r);
	Segment2d s2d= quad2d.Clip(l2d);
	retval= to_3d(s2d);
      }	
    return retval;
  }

//! @brief Return the intersection of the quadrilateral and the ray.
Segment3d Quadrilateral3d::Clip(const Ray3d &sr) const
  {
    Segment3d retval;
    const GEOM_FT angle= getPlane().getAngle(sr);
    const GEOM_FT angleTol= 1/180.0*M_PI; // one degree
    if(angle>angleTol)
      {
        std::cerr << getClassName() << "::" << __FUNCTION__
	          << "; ray: " << sr
	  	  << " is not contained in the quadrilateral plane."
	          << std::endl;
	retval.setExists(false);
      }
    else
      {
	Ray2d r2d= to_2d(sr);
	Segment2d s2d= quad2d.Clip(r2d);
	retval= to_3d(s2d);
      }	
    return retval;
  }

//! @brief Return the intersection of the quadrilateral and the segment.
Segment3d Quadrilateral3d::Clip(const Segment3d &sg) const
  {
    Segment3d retval;
    const GEOM_FT angle= getPlane().getAngle(sg);
    const GEOM_FT angleTol= 1/180.0*M_PI; // one degree
    if(angle>angleTol)
      {
        std::cerr << getClassName() << "::" << __FUNCTION__
	          << "; segment: " << sg
	  	  << " is not contained in the quadrilateral plane."
	          << std::endl;
	retval.setExists(false);
      }
    else
      {
	Segment2d sg2d= to_2d(sg);
        Segment2d s2d= quad2d.Clip(sg2d);
	if(s2d.exists())
	  { retval= to_3d(s2d); }
	else
	  retval.setExists(false);
      }	
    return retval;
  }

//! @brief Return true if the line intersects the quadrilateral.
bool Quadrilateral3d::intersects(const Line3d &r) const
  {
    const Line2d r2d= to_2d(r);
    return quad2d.intersects(r2d);
  }

//! @brief Return the intersection with the line argument.
Segment3d Quadrilateral3d::getIntersection(const Line3d &r) const
  {
    const Line2d r2d= to_2d(r);
    const Segment2d sg2d= quad2d.getIntersection(r2d);
    return to_3d(sg2d);
  }

//! @brief Return true if the plane intersects the quadrilateral.
bool Quadrilateral3d::intersects(const Plane &p) const
  { return p.intersects(this->getPolygon3d()); }

//! @brief Return the intersection with the plane argument.
Segment3d Quadrilateral3d::getIntersection(const Plane &p) const
  { return p.getIntersection(this->getPolygon3d()); }

//! @brief Return true if alguno de los vertices toca el cuadrante
//! que se pasa como parámetro.
bool Quadrilateral3d::TocaCuadrante(const int &cuadrante) const
  {
    Quadrilateral2d::vertex_iterator i= quad2d.vertices_begin();
    for(;i!=quad2d.vertices_end();i++)
      if(to_3d(Pos2d(*i)).Cuadrante() == cuadrante)
        return true;
    return false;
  }

//! @brief Return true if the point list is oriented clockwise.
//! @param vPoint: position of the point of view.
bool Quadrilateral3d::clockwise(const Pos3d &vPoint) const
  { return !counterclockwise(vPoint); }

//! @brief Return true if the point list is oriented counterclockwise.
//! @param vPoint: position of the point of view.
bool Quadrilateral3d::counterclockwise(const Pos3d &vPoint) const
  {
    bool retval= quad2d.counterclockwise();
    const Pos3d O= getCenterOfMass();
    const Vector3d K= getKVector();
    const Vector3d vDir= vPoint-O;
    const GEOM_FT dot_product= K.GetDot(vDir);
    if(dot_product<0)
      retval= !retval;
    else
      if(dot_product<1e-6)
	{
	  std::cerr << getClassName() << "::" << __FUNCTION__
		    << "; the point of view: " << vPoint
		    << " is almost contained in the reference plane."
		    << std::endl;
	}
    return retval;
  }

void Quadrilateral3d::swap(void)
  { quad2d.swap(); }

//! @brief Return the orientation of the quadrilateral (clockwise or
//! counterclockwise).
std::string Quadrilateral3d::orientation(const Pos3d &vPoint) const
  {
    std::string retval= "counterclockwise";
    if(clockwise(vPoint))
      { retval= "clockwise"; }
    return retval;
  }
