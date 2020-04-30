# -*- coding: utf-8 -*-
''' AISC's structural steel shapes (metric units).'''

from __future__ import print_function
from __future__ import division

# Section axis:

#    AISC            XC

#       ^ Y           ^ Y                    
#       |             |

#     -----         -----
#       |             | 
#       | -> X        | -> Z
#       |             |
#     -----         -----

# The axis used in AISC catalogue are different from those used in XC
# (strong axis parallel to z axis) in other words: values for Y and Z axis 
# are swapped with respect to those in the catalog.

import math
import aisc_shapes_dictionaries as shapes
import aisc_shapes_labels as labels
from materials.sections import structural_steel

# Shear areas.

# In y axis: Ay = depth of the section* web thickness
# In z axis: Az = 2/3 * combined area of the flanges. 

# *************************************************************************
# AISC W profiles.
# *************************************************************************
for item in shapes.W:
    shape= shapes.W[item]
    shape['Avy']= shape['h']*shape['tw'] # depth of the section* web thickness
    shape['Avz']= 2/3.0*(2*shape['b']*shape['tf']) # 2/3 * combined area of the flanges. 
    shape['alpha']= shape['Avy']/shape['A']
    shape['G']= shape['E']/(2*(1+shape['nu']))
    shape['hi']= shape['h']-2*shape['tf']
    shape['AreaQz']= 2*shape['b']*shape['tf'] 
    shape['AreaQy']= shape['A']-shape['AreaQz']
W= shapes.W

class WShape(structural_steel.IShape):
    '''W shape

    :ivar steel: steel material.
    :ivar name: shape name (i.e. W40X431).
    '''
    def __init__(self,steel,name):
        ''' Constructor.
        '''
        super(WShape,self).__init__(steel,name,W)

    def h(self):
        ''' Return overall depth of member (d in AISC tables).'''
        return self.get('h')
      
    def d(self):
        ''' Return internal web height: clear distance between flanges
        less the fillet at each flange (h in AISC tables).'''
        return self.get('d')
      
    def slendernessCheck(self):
        ''' Verify that the section doesn't contains slender elements
            according to table B4.1 a of AISC-360-16.'''
        E= self.get('E')
        Fy= self.steelType.fy
        lambda_r= 0.56*math.sqrt(E/Fy) # Case 1
        slendernessRatio= self.get('bSlendernessRatio')
        return slendernessRatio/lambda_r # OK if < 1.0

    def getAw(self):
        ''' Return A_w according to AISC specification Section G2.1b'''
        return self.h()*self.get('tw')
      
    def getShearResistanceFactor(self):
        ''' Return the resistance factor for shear according to
        section G2.1a.'''
        return 1.0
      
    def getWebShearStrengthCoefficient(self):
        ''' Return the web shear stress coefficient Cv1 according
            to equations G2-2, G2-3 and G2-4 of "Specification for 
            Structural Steel Buildings, July 7, 2016 AISC"
        '''
        Cv1= 1.0
        h_tw= self.get('d')/self.get('tw')
        h_tw_threshold= 2.24*math.sqrt(self.get('E')/self.steelType.fy)
        if(h_tw<h_tw_threshold):
            Cv1= 1.0;
        else:
            lmsg.error('getWebShearStrengthCoefficient not implemented yet for this type of sections.')
            Cv1= 0.0;
        return Cv1
          
    def getNominalShearStrengthWithoutTensionFieldAction(self):
        ''' Return the nominal shear strength according to equation
            2.1 of "Specification for Structural Steel Buildings,
            July 7, 2016 AISC"
        '''
        #
        Cv1= self.getWebShearStrengthCoefficient()
        return 0.6*self.steelType.fy*self.getAw()*Cv1
    def getTorsionalElasticBucklingStress(self, Lc):
        ''' Return the torsional or flexural-torsional elastic buckling stress
            of the member according to equations E4-2 of AISC-360-16.

        :param Lc: effective length of member for torsional buckling 
                   about longitudinal axis.
        '''
        E= self.get('E')
        G= self.get('G')
        Cw= self.get('Cw')
        J= self.get('It')
        Iy= self.get('Iy')
        Iz= self.get('Iz')
        return (math.pi**2*E*Cw/Lc**2+G*J)/(Iy+Iz)

# *************************************************************************
# AISC C profiles.
# *************************************************************************

for item in shapes.C:
    shape= shapes.C[item]
    shape['G']= shape['E']/(2*(1+shape['nu']))
    shape['hi']= shape['h']-2*shape['tf']
    shape['Avy']= shape['h']*shape['tw'] # depth of the section* web thickness
    shape['Avz']= 2/3.0*(2*shape['b']*shape['tf']) # 2/3 * combined area of the flanges. 
    shape['AreaQz']= 2*shape['b']*shape['tf']
    shape['AreaQy']= shape['A']-shape['AreaQz']
C= shapes.C

class CShape(structural_steel.UShape):
    '''C shape.

    :ivar steel: steel material.
    :ivar name: shape name (i.e. C15X50).
    '''
    def __init__(self,steel,name):
        ''' Constructor.

        '''
        super(CShape,self).__init__(steel,name,C)
        
    def slendernessCheck(self):
        ''' Verify that the section doesn't contains slender elements
            according to table B4.1 a of AISC-360-16.'''
        E= self.get('E')
        Fy= self.steelType.fy
        lambda_r= 0.56*math.sqrt(E/Fy) # Case 1
        slendernessRatio= self.get('bSlendernessRatio')
        return slendernessRatio/lambda_r # OK if < 1.0
    
    def getTorsionalElasticBucklingStress(self, Lc):
        ''' Return the torsional or flexural-torsional elastic buckling stress
            of the member according to equations E4-7 of AISC-360-16.

        :param Lc: effective length of member for torsional buckling 
                   about longitudinal axis.
        '''
        Ag= self.get('A')
        E= self.get('E')
        G= self.get('G')
        Cw= self.get('Cw')
        J= self.get('It')
        Iy= self.get('Iy')
        Iz= self.get('Iz')
        z0= self.get('x')-self.get('e0')
        # Polar radius of gyration about the shear center.
        r02= z0**2+(Iy+Iz)/Ag # E4-9
        return (math.pi**2*E*Cw/Lc**2+G*J)/(Ag*r02) # E4-7
    def getFlexuralConstant(self):
        ''' Return the flexural constant of the section according
            to equation E4-8 of AISC-360-16..'''
        Ag= self.get('A')
        Iy= self.get('Iy')
        Iz= self.get('Iz')
        z0= self.get('x')-self.get('e0')
        # Polar radius of gyration about the shear center.
        r02= z0**2+(Iy+Iz)/Ag # E4-9
        return 1-z0**2/r02

# *************************************************************************
# AISC Hollow Structural Sections.
# *************************************************************************

for item in shapes.HSS:
    shape= shapes.HSS[item]
    shape['alpha']= 5/12.0
    shape['G']= shape['E']/(2*(1+shape['nu']))
    if('h_flat' in shape): # rectangular
        shape['Avy']= 2*0.7*shape['h_flat']*shape['t']
        shape['Avz']= 2*0.7*shape['b_flat']*shape['t']
    else: # circular
        tmp= math.pi*(shape['OD']-shape['t'])/2.0*shape['t']
        shape['Avy']= tmp
        shape['Avz']= tmp
    shape['AreaQz']= shape['Avz']
    shape['AreaQy']= shape['Avy']
HSS= shapes.HSS

class HSSShape(structural_steel.QHShape):
    ''' Hollow structural section.

    :ivar steel: steel material.
    :ivar name: shape name (i.e. HSS2X2X_250).
    '''
    def __init__(self,steel,name):
        ''' Constructor.
        '''
        super(HSSShape,self).__init__(steel,name,HSS)
    def slendernessCheck(self):
        ''' Verify that the section doesn't contains slender elements
            according to table B4.1 a of AISC-360-16.'''
        E= self.get('E')
        Fy= self.steelType.fy
        lambda_r= 1.4*math.sqrt(E/Fy)
        if('h_flat' in shape): # rectangular
            slendernessRatio= max(shape['hSlendernessRatio'],shape['bSlendernessRatio'])
        else:
            slendernessRatio= shape['slendernessRatio']
        return slendernessRatio/lambda_r # OK if < 1.0
    
    def getTorsionalElasticBucklingStress(self, Lc):
        ''' Return the torsional or flexural-torsional elastic buckling stress
            of the member according to equations E4-2 of AISC-360-16.

        :param Lc: effective length of member for torsional buckling 
                   about longitudinal axis.
        '''
        E= self.get('E')
        G= self.get('G')
        Cw= self.get('C') #HSS torsional constant.
        J= self.get('It')
        Iy= self.get('Iy')
        Iz= self.get('Iz')
        return (math.pi**2*E*Cw/Lc**2+G*J)/(Iy+Iz)

# Label conversion metric->US customary | US customary -> metric.
def getUSLabel(metricLabel):
    '''Return the US customary label from the metric one.'''
    return labels.USLabel[metricLabel]

def getMetricLabel(USLabel):
    '''Return the metric label from the US customary one.'''
    return labels.MetricLabel[metricLabel]




