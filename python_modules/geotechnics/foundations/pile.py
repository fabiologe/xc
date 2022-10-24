# -*- coding: utf-8 -*-

from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2022, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import sys
import math
from misc_utils import log_messages as lmsg
from materials.sections import section_properties as sp
from materials import typical_materials
from model import predefined_spaces

class Pile(object):
    '''Pile basic properties.
    
    :ivar crossSection: cross-section of the pile.
    :ivar E: elastic modulus of pile material.
    :ivar pileType: "endBearing" for end bearing piles 
                    "friction" for friction piles
    :ivar groundLevel: ground elevation.
    :ivar pileSet: set of nodes and elements defining a single pile.
    '''
    def __init__(self, E, crossSection, pileType, groundLevel, pileSet= None):
        ''' Constructor.

        :param crossSection: cross-section of the pile.
        :param E: elastic modulus of pile material
        :param pileType: "endBearing" for end bearing piles 
                        "friction" for friction piles
        :param groundLevel: ground elevation
        :param pileSet: set of nodes and elements defining a single pile.
        '''
        self.E=E
        self.crossSection= crossSection
        self.pileType= pileType
        self.groundLevel= groundLevel
        self.pileSet= None
        if(pileSet):
            self.pileSet= pileSet

    def getZMax(self):
        ''' Return the maximum value of z for the pile nodes.'''
        retval= None
        if(self.pileSet):
            retval= max([n.get3dCoo[2] for n in self.pileSet.nodes])
        else:
            className= type(self).__name__
            methodName= sys._getframe(0).f_code.co_name
            lmsg.error(className+'.'+methodName+'; pile element set not defined.')
        return retval
    
    def getZMin(self):
        ''' Return the minimum value of z for the pile nodes.'''
        retval= None
        if(self.pileSet):
            retval= min([n.get3dCoo[2] for n in self.pileSet.nodes])
        else:
            className= type(self).__name__
            methodName= sys._getframe(0).f_code.co_name
            lmsg.error(className+'.'+methodName+'; pile element set not defined.')
        return retval
            
    def getAerialLength(self):
        '''Return the length of pile above the ground surface'''
        zMax= self.getZMax()
        return max(0,zMax-self.groundLevel)

    def getBuriedLength(self):
        '''Return the length of pile below the ground surface'''
        zMax= self.getZMax()
        zMin= self.getZMin()
        return min(zMax-zMin,self.groundLevel-zMin)
    
    def getTotalLength(self):
        '''Return the total length of the pile.'''
        aerL= self.getAerialLength()
        burL= self.getBuriedLength()
        return aerL+burL
    
    def getCrossSectionArea(self):
        '''Return the cross-sectional area of the pile'''
        return self.crossSection.A()
    
    def getPileElasticLengthInClay(self, Eterrain, L, majorAxis= False):
        ''' Return the equivalent elastic length of the pile embedded in
        cohesive soil.

        :param Eterrain: elastic modulus of the terrain. 
        :param majorAxis: true if the required inertia corresponds to the
                          bending around major axis. 
        '''
        Ipile= self.crossSection.I(majorAxis= majorAxis)
        LePA= math.pow(self.E*Ipile/(Eterrain/3.),0.25)
        if(LePA>2*self.getBuriedLength()):
            lmsg.error("Pile is too short to compute its elastic length.")
        return(LePA)

    def getPileAnchorageLengthInClay(self, Eterrain, majorAxis= False):
        ''' Return the equivalent anchorage length of the pile embedded in
        cohesive soil.

        :param Eterrain: elastic modulus of the terrain. 
        :param majorAxis: true if the required inertia corresponds to the
                          bending around major axis. 
        '''
        return 1.2*self.getPileElasticLengthInClay(Eterrain)

    def computeTributaryLengths(self, initialGeometry= False):
        ''' Compute the tributary lengths for the nodes of the finite
            element set.

        :param initialGeometry: if true compute lengths on the initial geometry
                                of the model. Otherwise use its current 
                                geometry.
        '''
        self.pileSet.resetTributaries()
        self.pileSet.computeTributaryLengths(initialGeometry)

    def getNodeZs(self):
        ''' Return a list of tuples containing the node an its z coordinate
            sorted in descending order.'''
        def takeSecond(tupla):
           return tupla[1]
        retval= [(n,n.get3dCoo[2]) for n in self.pileSet.nodes]
        retval.sort(key=takeSecond,reverse=True) #z in descending order
        return retval
    
    def getLinearSpringsConstants(self, alphaKh_x= 1.0, alphaKh_y= 1.0, alphaKv_z= 1.0):
        '''Compute the spring contants that simulate the soils along the pile

        :param alphaKh_x: coefficient to be applied to the horizontal stiffness
                          of a single pile in X direction
        :param alphaKh_y: coefficient to be applied to the horizontal stiffness
                          of a single pile in Y direction
        :param alphaKh_Z: coefficient to be applied to the vertical stiffness of
                          a single pile in Z direction
        '''
        raise Exception('Abstract method, please override')
        
    def generateSpringsPile(self, alphaKh_x, alphaKh_y, alphaKv_z):
        '''Generate the springs that simulate the soils along the pile

        :param alphaKh_x: coefficient to be applied to the horizontal stiffness
                          of a single pile in X direction
        :param alphaKh_y: coefficient to be applied to the horizontal stiffness
                          of a single pile in Y direction
        :param alphaKh_Z: coefficient to be applied to the vertical stiffness of
                          a single pile in Z direction
        '''
        linearSpringsConstants= self.getLinearSpringsConstants(alphaKh_x= alphaKh_x, alphaKh_y= alphaKh_y, alphaKv_z= alphaKv_z)
        #init spring elastic materials
        prep= self.pileSet.getPreprocessor
        springX= typical_materials.defElasticMaterial(prep,'springX',1e-5)
        springY= typical_materials.defElasticMaterial(prep,'springY',1e-5)
        springZ= typical_materials.defElasticMaterial(prep,'springZ',1e-5)
        self.springs= list() # Spring elements.
        modelSpace= predefined_spaces.getModelSpace(prep)
        for n in self.pileSet.nodes:
            if(n.tag in linearSpringsConstants):
                k_i= linearSpringsConstants[n.tag]
                springX.E= k_i[0]
                springY.E= k_i[1]
                springZ.E= k_i[2]
                nn= modelSpace.setBearing(n.tag,['springX','springY','springZ'])
                self.springs.append(nn[1])
        

class CircularPile(Pile):
    ''' Pile with circular cross-section.'''
    def __init__(self, E, pileType, groundLevel, diameter, pileSet):
        ''' Constructor.

        :param E: elastic modulus of pile material
        :param pileType: "endBearing" for end bearing piles 
                        "friction" for friction piles
        :param groundLevel: ground elevation.
        :param diameter: diameter of the pile cross-section.
        :param pileSet: set of nodes and elements defining a single pile.
        '''
        cs= sp.CircularSection(name= None, Rext= diameter/2.0,Rint=0.0)

        super(CircularPile, self).__init__(E= E, crossSection= cs, pileType= pileType, groundLevel= groundLevel, pileSet= pileSet)

    def getDiameter(self):
        ''' Return the pile diameter.'''
        return self.crossSection.getDiameter()
        
    
