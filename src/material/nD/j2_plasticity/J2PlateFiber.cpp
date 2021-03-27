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
** ****************************************************************** */
                                                                        
// $Revision: 1.5 $
// $Date: 2003/02/14 23:01:25 $
// $Source: /usr/local/cvs/OpenSees/SRC/material/nD/J2PlateFiber.cpp,v $

// Written: Ed "C++" Love
//
// J2PlateFiber isotropic hardening material class
// 
//  Elastic Model
//  sigma = K*trace(epsilion_elastic) + (2*G)*dev(epsilon_elastic)
//
//  Yield Function
//  phi(sigma,q) = || dev(sigma) ||  - sqrt(2/3)*q(xi) 
//
//  Saturation Isotropic Hardening with linear term
//  q(xi) = simga_infty + (sigma_0 - sigma_infty)*exp(-delta*xi) + H*xi 
//
//  Flow Rules
//  \dot{epsilon_p} =  gamma * d_phi/d_sigma
//  \dot{xi}        = -gamma * d_phi/d_q 
//
//  Linear Viscosity 
//  gamma = phi / eta  ( if phi > 0 ) 
//
//  Backward Euler Integration Routine 
//  Yield condition enforced at time n+1 
//
//  Send strains in following format :
// 
//     strain_vec = {   eps_00
//                      eps_11
//                    2 eps_01   }   <--- note the 2
// 
//  set eta := 0 for rate independent case
//

#include <material/nD/j2_plasticity/J2PlateFiber.h>

#include <cstdio> 
#include <cstdlib> 
#include <cmath> 

#include <utility/matrix/Vector.h>
#include <utility/matrix/Matrix.h>
#include "material/nD/NDMaterialType.h"

XC::Vector XC::J2PlateFiber::strain_vec(order);
XC::Vector XC::J2PlateFiber::stress_vec(order);
XC::Matrix XC::J2PlateFiber::tangent_matrix(order,order);

//! @brief Default constructor.
XC::J2PlateFiber::J2PlateFiber(int tag)
  : XC::J2Plasticity(tag,ND_TAG_J2PlateFiber) 
  { commitEps22 =0.0; }

//! @brief full constructor
 XC::J2PlateFiber::J2PlateFiber(   int    tag, 
                 double K,
                 double G,
                 double yield0,
                 double yield_infty,
                 double d,
                 double H,
                 double viscosity ) : 
 XC::J2Plasticity(tag, ND_TAG_J2PlateFiber, K, G, yield0, yield_infty, d, H, viscosity )
  { commitEps22 =0.0; }


//! @brief elastic constructor
XC::J2PlateFiber::J2PlateFiber(int tag, double K, double G ) :
XC::J2Plasticity(tag, ND_TAG_J2PlateFiber, K, G )
  { commitEps22 =0.0; }

//! @brief make a clone of this material
XC::NDMaterial *XC::J2PlateFiber::getCopy(void) const
  { return new J2PlateFiber(*this); }


//! @brief send back type of material
const std::string &XC::J2PlateFiber::getType(void) const 
  { return strTypePlateFiber; }


//! @brief send back order of strain in vector form
int XC::J2PlateFiber::getOrder(void) const 
  { return order; } 

//! @brief get the strain and integrate plasticity equations
int XC::J2PlateFiber::setTrialStrain( const Vector &strain_from_element ) 
  {
    const double tolerance = 1e-8;

    const int max_iterations= 25;
    int iteration_counter= 0;

    int i, j, k, l;
    int ii, jj;

    double eps22  =  strain(2,2);
    strain.Zero( );

    strain(0,0) =        strain_from_element(0);
    strain(1,1) =        strain_from_element(1);

    strain(0,1) = 0.50 * strain_from_element(2);
    strain(1,0) =        strain(0,1);

    strain(1,2) = 0.50 * strain_from_element(3);
    strain(2,1) =        strain(1,2);

    strain(2,0) = 0.50 * strain_from_element(4);
    strain(0,2) =        strain(2,0);

    strain(2,2) =        eps22; 

    //enforce the plane stress condition sigma_22 = 0 
    //solve for epsilon_22 
    iteration_counter = 0;  
    do
      {
       this->plastic_integrator( );

       strain(2,2) -= stress(2,2) / tangent[2][2][2][2];

       //std::cerr << stress(2,2) << std::endl;;

       iteration_counter++;
       if( iteration_counter > max_iterations ) {
	 std::cerr << "More than " << max_iterations;
	 std::cerr << " iterations in setTrialStrain of XC::J2PlateFiber \n";
	 break;
       }// end if 

      } while( fabs(stress(2,2)) > tolerance );

    //modify tangent for plane stress 
    for( ii = 0; ii < order; ii++ )
      {
	for( jj = 0; jj < order; jj++ )
	  {
	    index_map( ii, i, j );
	    index_map( jj, k, l );

	    tangent[i][j][k][l] -=   tangent[i][j][2][2] 
				   * tangent[2][2][k][l] 
				   / tangent[2][2][2][2];

	    //minor symmetries 
	    tangent [j][i][k][l] = tangent[i][j][k][l];
	    tangent [i][j][l][k] = tangent[i][j][k][l];
	    tangent [j][i][l][k] = tangent[i][j][k][l];
	  } // end for jj
      } // end for ii 

    return 0;
  }


//! @brief unused trial strain functions
int XC::J2PlateFiber::setTrialStrain( const XC::Vector &v, const XC::Vector &r )
{ 
   return this->setTrialStrain( v );
} 

int XC::J2PlateFiber::setTrialStrainIncr( const XC::Vector &v ) 
  { return -1; }

int XC::J2PlateFiber::setTrialStrainIncr( const XC::Vector &v, const XC::Vector &r ) 
  { return -1; }



//! @brief send back the strain
const XC::Vector &XC::J2PlateFiber::getStrain(void) const
  {
    strain_vec(0) =       strain(0,0);
    strain_vec(1) =       strain(1,1);

    strain_vec(2) = 2.0 * strain(0,1);

    strain_vec(3) = 2.0 * strain(1,2);

    strain_vec(4) = 2.0 * strain(2,0);

    return strain_vec;
  } 


//! @brief send back the stress 
const XC::Vector &XC::J2PlateFiber::getStress(void) const 
  {

    stress_vec(0) = stress(0,0);
    stress_vec(1) = stress(1,1);

    stress_vec(2) = stress(0,1);

    stress_vec(3) = stress(1,2);

    stress_vec(4) = stress(2,0);

    return stress_vec;
  }

//! @brief send back the tangent 
const XC::Matrix &XC::J2PlateFiber::getTangent(void) const
  {

    // matrix to tensor mapping
    // Matrix      Tensor
    // -------     -------
    //   0           0 0
    //   1           1 1
    //   2           0 1  ( or 1 0 )
    //   3           1 2  ( or 2 1 )
    //   4           2 0  ( or 0 2 ) 

    int ii, jj;
    int i, j, k, l;

    for( ii = 0; ii < order; ii++ )
      {
      for( jj = 0; jj < order; jj++ )
	{

	index_map( ii, i, j );
	index_map( jj, k, l );

	tangent_matrix(ii,jj) = tangent[i][j][k][l];

      } //end for j
    } //end for i


    return tangent_matrix;
  } 


//! @brief Reurn the tangent 
const XC::Matrix &XC::J2PlateFiber::getInitialTangent(void) const
  {

    // matrix to tensor mapping
    //  Matrix      Tensor
    // -------     -------
    //   0           0 0
    //   1           1 1
    //   2           0 1  ( or 1 0 )
    //   3           1 2  ( or 2 1 )
    //   4           2 0  ( or 0 2 ) 

    int ii, jj;
    int i, j, k, l;

    this->doInitialTangent();

    for( ii = 0; ii < order; ii++ ) {
      for( jj = 0; jj < order; jj++ ) {

	index_map( ii, i, j );
	index_map( jj, k, l );

	tangent_matrix(ii,jj) = initialTangent[i][j][k][l];

      } //end for j
    } //end for i


    return tangent_matrix;
  } 

int XC::J2PlateFiber::commitState( ) 
  {
    epsilon_p_n = epsilon_p_nplus1;
    xi_n        = xi_nplus1;

    commitEps22 = strain(2,2);

    return 0;
  }

int XC::J2PlateFiber::revertToLastCommit( )
 {
   strain(2,2) = commitEps22;
   return 0;
 }

//! @brief Revert the material to its initial state.
int XC::J2PlateFiber::revertToStart( )
  {
    int retval= J2Plasticity::revertToStart();
    commitEps22 = 0.0;
    this->zero( );
    return retval;
  }

//! @brief Send object members through the communicator argument.
int XC::J2PlateFiber::sendData(Communicator &comm)
  {
    int res= J2Plasticity::sendData(comm);
    res+= comm.sendDouble(commitEps22,getDbTagData(),CommMetaData(88));
    return res;
  }

//! @brief Receives object members through the communicator argument.
int XC::J2PlateFiber::recvData(const Communicator &comm)
  {
    int res= J2Plasticity::recvData(comm);
    res+= comm.receiveDouble(commitEps22,getDbTagData(),CommMetaData(88));
    return res;
  }

//! @brief Sends object through the communicator argument.
int XC::J2PlateFiber::sendSelf(Communicator &comm)
  {
    setDbTag(comm);
    const int dataTag= getDbTag();
    inicComm(89);
    int res= sendData(comm);

    res+= comm.sendIdData(getDbTagData(),dataTag);
    if(res < 0)
      std::cerr << getClassName() << "::" << __FUNCTION__
		<< "; failed to send data\n";
    return res;
  }

//! @brief Receives object through the communicator argument.
int XC::J2PlateFiber::recvSelf(const Communicator &comm)
  {
    inicComm(89);
    const int dataTag= getDbTag();
    int res= comm.receiveIdData(getDbTagData(),dataTag);

    if(res<0)
      std::cerr << getClassName() << "::" << __FUNCTION__
		<< "; failed to receive ids.\n";
    else
      {
        setTag(getDbTagDataPos(0));
        res+= recvData(comm);
        if(res<0)
          std::cerr << getClassName() << "::" << __FUNCTION__
		    << "; failed to receive data.\n";
       }
    return res;
  }


//! @brief Mapping between matrix and tensor
//! indices: matrix_index ---> tensor indices i,j
//! Plane stress different because of condensation on tangent
//! case 3 switched to 1-2 and case 4 to 3-3 
void XC::J2PlateFiber::index_map( int matrix_index, int &i, int &j ) const
  {
    switch(matrix_index+1) //add 1 for standard tensor indices
      { 
      case 1:
	i = 1; j = 1;
	break;

      case 2:
	i = 2; j = 2; 
	break;

      case 3:
	i = 1; j = 2;
	break;

      case 4:
	i = 2; j = 3;
	break;

      case 5:
	i = 3; j = 1;
	break;

      case 6:
	i = 3; j = 3;
	break;

      default:
	i = 1; j = 1;
	break;
      } //end switch
    i--; //subtract 1 for C-indexing
    j--;
  }

