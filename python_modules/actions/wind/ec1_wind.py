# -*- coding: utf-8 -*-
'''Functions to compute wind loads according to EN 1991-1-4:2005.'''

from __future__ import print_function
from __future__ import division

__author__= "Luis C. Pérez Tato (LCPT) , Ana Ortega (AO_O) "
__copyright__= "Copyright 2024, LCPT, AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@ciccp.es, ana.ortega@ciccp.es "

import sys
import math
import scipy.interpolate
from misc_utils import log_messages as lmsg
from actions.wind import base_wind
from actions.wind import IAP_wind

# Probability factor

def get_probability_factor(T:float, K= 0.2, n= 0.5):
    ''' Return the probability factor according to NOTE 4 to clause 4.2 (2) 
        of EN 1991-1-4:2005.

    :param T: return period expressed in years.
    :param K: parameter (defaults to 0.2).
    :param n: parameter (defaults to 0.5)
    '''
    return math.pow((1.0-K*math.log(-math.log(1-1/T)))/(1-K*math.log(-math.log(0.98))),n)

def get_basic_velocity_pressure(vb, rho= 1.25):
    ''' Return the basic velocity pressure according to expression (4.10)
        of EN 1991-1-4:2005.

    :param vb: basic wind velocity.
    :param rho: air density.
    '''
    return 0.5*rho*vb**2

def get_z0(terrainCategory:str):
    ''' Return the rugosity length according to table 4.1 of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    '''
    return IAP_wind.getZ0(terrainCategory= terrainCategory)


def get_zmin(terrainCategory:str):
    ''' Return the minimum height according to table 4.1 of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    '''
    return IAP_wind.getZmin(terrainCategory= terrainCategory)

def get_kr(terrainCategory:str):
    ''' Return the terrain factor according to expression (4.5) of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    '''
    z0= get_z0(terrainCategory= terrainCategory)
    z0II= get_z0(terrainCategory= 'II')
    return 0.19*pow(z0/z0II, 0.07)

def get_roughness_factor(terrainCategory:str, z, zMax= 200.0):
    ''' Return the ground roughness factor according to expression (4.4) of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    :param z: height above ground.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    '''
    zMin= get_zmin(terrainCategory= terrainCategory)
    z0= get_z0(terrainCategory= terrainCategory)
    kr= get_kr(terrainCategory= terrainCategory)
    retval= None
    if((z>=zMin) and (z<zMax)):
        retval= kr*math.log(z/z0)
    elif(z<zMin):
        retval= kr*math.log(zMin/z0)
    else:
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; value of z= '+str(z)+' out of range (0,200] m.')
    return retval

def get_turbulence_intensity(terrainCategory:str, z, zMax= 200.0, k1= 1.0, c0= 1.0):
    ''' Return the turbulence intensity according to expression (4.7)
        of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    :param z: height above ground.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param k1: turbulence factor.
    :param c0: orography factor.
    '''
    zMin= get_zmin(terrainCategory= terrainCategory)
    z0= get_z0(terrainCategory= terrainCategory)
    retval= None
    if((z>=zMin) and (z<zMax)):
        retval= k1/(c0*math.log(z/z0))
    elif(z<zMin):
        retval= k1/(c0*math.log(zMin/z0))
    else:
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; value of z= '+str(z)+' out of range (0,200] m.')
    return retval

def get_peak_velocity_pressure(terrainCategory:str, vb, z, zMax= 200.0, rho= 1.25, k1= 1.0, c0= 1.0):
    ''' Return the basic velocity pressure according to expression (4.10)
        of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    :param vb: basic wind velocity.
    :param z: height above ground.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param rho: air density.
    :param k1: turbulence factor.
    :param c0: orography factor.
    '''
    Cr= get_roughness_factor(terrainCategory= terrainCategory, z= z)
    vm= Cr*c0*vb
    Iv= get_turbulence_intensity(terrainCategory= terrainCategory, z= z, k1= k1, c0= c0)
    return (1+7*Iv)*0.5*rho*vm**2
    

def get_exposure_factor(terrainCategory:str, vb, z, zMax= 200.0, rho= 1.25, k1= 1.0, c0= 1.0):
    ''' Return the exposure factor pressure according to expression (4.9),
        clause 45 of EN 1991-1-4:2005.

    :param terrainCategory: terrain category.
    :param vb: height above ground.
    :param z: height above ground.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param rho: air density.
    :param k1: turbulence factor.
    :param c0: orography factor.
    '''    
    retval= get_peak_velocity_pressure(terrainCategory= terrainCategory, vb= vb, z= z, zMax= zMax, rho= rho, k1= k1, c0= c0)
    retval/= get_basic_velocity_pressure(vb= vb, rho= rho)
    return retval

cfx0_a= scipy.interpolate.interp1d([0.0, 0.3627, 4.0, 12.0], [2.4, 2.4, 1.3, 1.3], kind='linear')
cfx0_b= scipy.interpolate.interp1d([0.0, 0.3627, 5.0, 12.0], [2.4, 2.4, 1.0, 1.0], kind='linear')

def get_bridge_deck_transverse_force_coefficient(b, dtot, solidParapets= True):
    ''' Return the value of the transverse force coefficient for bridge decks 
        according to figure 8.3 of EN 1991-1-4:2005.

    :param b: deck width.
    :param dtot: sum of the projected (windward) depth of the structure
    '''
    b_dtot= b/dtot
    if(solidParapets):
        return cfx0_b(b_dtot)
    else:
        return cfx0_a(b_dtot)
    
cfz_10= scipy.interpolate.interp1d([0.0, 4, 22.0, 1e3], [0.75, 0.9, 0.9, 0.9], kind='linear')
cfz_6= scipy.interpolate.interp1d([0.0, 22.0, 1e3], [0.75, 0.9, 0.9], kind='linear')
cfz_0= scipy.interpolate.interp1d([0.0, 14.0, 22.0, 1e3], [0.75, 0.15, 0.15, 0.15], kind='linear')

def get_bridge_deck_vertical_force_coefficient(b, dtot, alpha= math.radians(10), beta= 0.0):
    ''' Return the value of the vertical force coefficient for bridge decks 
        according to figure 8.6 of EN 1991-1-4:2005.

    :param b: deck width.
    :param dtot: sum of the projected (windward) depth of the structure.
    :parma alpha: angle of the wind with the horizontal (see figure 8.6 of EN 1991-1-4:2005).
    :param beta: superelevation of the bridge deck (see figure 8.6 of EN 1991-1-4:2005).
    '''
    angle10= math.radians(10)
    angle6= math.radians(6)
    b_dtot= b/dtot
    theta= abs(beta+alpha)
    if(theta>=angle10):
        retval= cfz_10(b_dtot)
    elif(theta>=angle6):
        topValue= cfz_10(b_dtot)
        bottomValue= cfz_6(b_dtot)
        retval= (topValue-bottomValue)/(angle10-angle6)*(theta-angle6)+bottomValue
    else:
        topValue= cfz_6(b_dtot)
        bottomValue= cfz_0(b_dtot)
        retval= (topValue-bottomValue)/angle6*theta+bottomValue
    return retval

def get_vertical_pressure(terrainCategory:str, b:float, dtot:float, z:float, vb:float, zMax= 200.0, rho= 1.25, k1:float= 1.0, c0:float= 1.0, alpha= math.radians(10), beta= 0.0):
    ''' Return the value of the average vertical pressure according to clause
        4.2.5.1.2 of IAP-11.

    :param terrainCategory: terrain category according to clause 4.2.2 
                            of IAP-11.
    :param b: deck width.
    :param dtot: sum of the projected (windward) depth of the structure.
    :param z: Height above ground surface at the site of the building or 
              other structure.
    :param v_b: basic wind velocity according to clause 4.2.1 of IAP-11.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param rho: density of air (defaults to 1.25 kg/m3).
    :param k1: turbulence factor.
    :param c0: orography factor.
    :parma alpha: angle of the wind with the horizontal (see figure 8.6 of EN 1991-1-4:2005).
    :param beta: superelevation of the bridge deck (see figure 8.6 of EN 1991-1-4:2005).
    '''
    # Compute peak velocity pressure (qp= qb*ce).
    qp= get_peak_velocity_pressure(terrainCategory= terrainCategory, vb= vb, z= z, zMax= zMax, rho= rho, k1= k1, c0= c0)
    # Compute vertical force coefficient
    cfz= get_bridge_deck_vertical_force_coefficient(b= b, dtot= dtot, alpha= alpha, beta= beta)
    return (qp*-cfz, qp*cfz)

def get_vertical_pressure_distribution(terrainCategory:str, x0: float, x1: float, dtot:float, z:float, vb:float, zMax= 200.0, rho= 1.25, k1:float= 1.0, c0:float= 1.0, alpha= math.radians(10), beta= 0.0):
    ''' Return the vertical pressure distribution over a bridge deck, so 
        the resultant force has a horizontal eccentricity of a quarter 
        of the deck width.

    :param terrainCategory: terrain category according to clause 4.2.2 
                            of IAP-11.
    :param x0: leftmost point of the deck.
    :param x1: rigthmost point of the deck.
    :param dtot: sum of the projected (windward) depth of the structure.
    :param z: Height above ground surface.
    :param vb: basic wind velocity.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param rho: density of air (defaults to 1.25 kg/m3).
    :param k1: turbulence factor.
    :param c0: orography factor.
    :parma alpha: angle of the wind with the horizontal (see figure 8.6 of EN 1991-1-4:2005).
    :param beta: superelevation of the bridge deck (see figure 8.6 of EN 1991-1-4:2005).
    '''
    b= x1-x0 # Deck width
    # Compute vertical pressure.
    averagePressure= get_vertical_pressure(terrainCategory= terrainCategory, b= b, dtot= dtot, z= z, vb= vb, zMax= zMax, rho= rho, k1= k1, c0= c0, alpha= alpha, beta= beta)
    (a,b)= base_wind.getLinearDistribution(h= b, hR= 0.75*b)
    xi= [x0, x1]
    y0i= [averagePressure[0]*a, averagePressure[0]*b]
    pressureDistrib0= scipy.interpolate.interp1d(xi, y0i, kind='linear')
    y1i= [averagePressure[1]*a, averagePressure[1]*b]
    pressureDistrib1= scipy.interpolate.interp1d(xi, y1i, kind='linear')
    return (pressureDistrib0, pressureDistrib1)

def get_cylinder_reynolds_number(b, v, nu= 15e-6):
    ''' Return the reynolds number of the flow around a cylinder based on the
        equation 7.15 of EN 1991-1-4:2005.
 
    :param b: diameter of the cylinder.
    :param v: wind velocity.
    :param nu: kinematic viscosity of the air (ν=15*10-6 m2/s).
    '''
    return b*v/nu

def get_cylinder_lambda(b, l):
    ''' Return the value of lambdar for a cylinder according to table 7.16
        of EN 1991-1-4:2005.

    :param b: diameter of the cylinder.
    :param l: length of the cylinder.
    '''
    if(l>=50):
        retval= min(0.7*l/b, 70)
    elif(l<15):
        retval= min(l/b, 70)
    else:
        v50= min(0.7*l/b, 70)
        v15= min(l/b, 70)
        retval= (v50-v15)/35*(l-15)+v15
    return retval

def logarithmic_expression(x0, F0, x1, F1, x):
    ''' Computes the value of a function defined by a linear-log plot.

    See: https://en.wikipedia.org/wiki/Semi-log_plot

    :param (x0, F0): first point of a straight line in the graph.
    :param (x1, F1): second point of a straight line in the graph.
    '''
    return (F1-F0)/math.log10(x1/x0)*math.log10(x/x0)+F0


def get_cylinder_end_effect_factor(b, l, solidityRatio= 1.0):
    ''' Return the end effect factor for a cylinder according to table 7.36
        of EN 1991-1-4:2005.

    :param b: diameter of the cylinder.
    :param l: length of the cylinder.
    :param solidityRatio: ratio between the projected areas of the member and the area of the evelope.
    '''
    retval= None
    l= get_cylinder_lambda(b= b, l= l)
    if(solidityRatio == 1.0):
        if(l<=10):
            retval= logarithmic_expression(x0= 1, F0= 0.6, x1= 10, F1=  0.698, x= l)
        elif(l<=70.0):
            retval= logarithmic_expression(x0= 10, F0= 0.698, x1= 70, F1=  0.9182, x= l)
        else:
            methodName= sys._getframe(0).f_code.co_name
            lmsg.error(methodName+'; not yet implementd for lambda greater than 70.')
            

    else:
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; not yet implementd for solidity ratios different from 1.0.')
    return retval  

def get_cylinder_force_coefficient_without_free_end_flow(b, v, k, nu= 15e-6):
    ''' Return the force coefficient of the flow around a cylinder based on the
        expressions in the figurea 7.28 of EN 1991-1-4:2005.
 
    :param b: diameter of the cylinder.
    :param v: wind velocity.
    :param k: equivalent surface roughness.
    :param nu: kinematic viscosity of the air (ν=15*10-6 m2/s).
    '''
    retval= 0.18*math.log10(10*k/b)
    Re= get_cylinder_reynolds_number(b= b, v= v, nu= nu)
    retval/= 1+0.4*math.log10(Re/1e6)
    retval+= 1.2
    return retval

def get_cylinder_force_coefficient(b, l, v, k, nu= 15e-6, solidityRatio= 1.0):
    ''' Return the force coefficient of the flow around a cylinder according to 
        expression (7.19) of EN 1991-1-4:2005.
 
    :param b: diameter of the cylinder.
    :param l: length of the cylinder.
    :param v: peak wind velocity.
    :param k: equivalent surface roughness.
    :param nu: kinematic viscosity of the air (ν=15*10-6 m2/s).
    :param solidityRatio: ratio between the projected areas of the member and the area of the evelope.
    '''
    cf0= get_cylinder_force_coefficient_without_free_end_flow(b=b, v= v, k= k, nu= nu)
    endEffectFactor= get_cylinder_end_effect_factor(b= b, l= l, solidityRatio= solidityRatio)
    return cf0*endEffectFactor

def get_cylinder_effective_wind_pressure(terrainCategory:str, vb, z, b, l, k, zMax= 200.0, rho= 1.25, k1= 1.0, c0= 1.0, nu= 15e-6, solidityRatio= 1.0, structuralFactor= 1.0):
    ''' Return the effective wind pressure on a circular cylinder according to 
        expression (7.19) of EN 1991-1-4:2005.
 
    :param terrainCategory: terrain category.
    :param vb: basic wind velocity.
    :param z: height above ground.
    :param b: diameter of the cylinder.
    :param l: length of the cylinder.
    :param k: equivalent surface roughness.
    :param zMax: maximum height according to clause 4.3.2 of EN 1991-1-4:2005.
    :param rho: air density.
    :param k1: turbulence factor.
    :param c0: orography factor.
    :param nu: kinematic viscosity of the air (ν=15*10-6 m2/s).
    :param solidityRatio: ratio between the projected areas of the member and the area of the evelope.
    :param structuralFactor: structural factor as defined in Section 6 of EN 1991-1-4:2005.
    '''
    qp= get_peak_velocity_pressure(terrainCategory= terrainCategory, vb= vb, z= z, zMax= zMax, rho= rho, k1= k1, c0= c0)
    v= math.sqrt(2.0*qp/rho)
    cf= get_cylinder_force_coefficient(b=b, l= l, v= v, k= k, nu= nu, solidityRatio= solidityRatio)
    return cf*qp*structuralFactor
