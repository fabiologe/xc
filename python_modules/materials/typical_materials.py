# -*- coding: utf-8 -*-
''' Convenience functions to define common materials.'''

from __future__ import print_function
from __future__ import division

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AO_O)"
__copyright__= "Copyright 2015, LCPT and AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@ciccp.es" "ana.Ortega@ciccp.es"

from misc_utils import log_messages as lmsg
import uuid

# Typical material definition.

class BasicElasticMaterial(object):
    '''Basic elastic material

     :ivar E:            Young’s modulus of the material
     :ivar nu:           Poisson’s ratio
     :ivar rho:          mass density
    '''
    def __init__(self, E, nu, rho= 0.0):
        '''Base class to construct some material definition classes

         :param E:            Young’s modulus of the material
         :param nu:           Poisson’s ratio
         :param rho:          mass density
        '''
        self.E= E
        self.nu= nu
        self.rho= rho
        
    def G(self):
        '''shear modulus.'''
        return self.E/(2*(1+self.nu))

    def defElasticMaterial(self, preprocessor, name= None, overrideRho= None):
        ''' Return an elastic material appropriate for example for
            truss elements

        :param preprocessor: preprocessor of the finite element problem.
        :param name: name for the new material.
        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''        
        materialHandler= preprocessor.getMaterialHandler
        matName= name
        if(not matName):
            matName= uuid.uuid1().hex
        retval= materialHandler.newMaterial("elastic_material",matName)
        retval.E= self.E
        matRho= self.rho
        if(overrideRho):
            matRho= overrideRho
        retval.rho= matRho
        return retval
    
    def defElasticIsotropic3d(self, preprocessor, name= None, overrideRho= None):
        ''' Return an elastic isotropic 3D material appropriate for example for
            brick elements

        :param preprocessor: preprocessor of the finite element problem.
        :param name: name for the new material.
        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''        
        matName= name
        if(not matName):
            matName= uuid.uuid1().hex
        matRho= self.rho
        if(overrideRho):
            matRho= overrideRho
        return defElasticIsotropic3d(preprocessor= preprocessor, name= matName, E= self.E, nu= self.nu,rho= matRho)


    def defElasticMembranePlateSection(self, preprocessor, thickness, name= None, overrideRho= None):
        ''' Return an elastic membrane plate section material appropriate
            for example for shell elements.

        :param preprocessor: preprocessor of the finite element problem.
        :param thickness: plate thickness.
        :param name: name for the new material.
        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''        
        matName= name
        if(not matName):
            matName= uuid.uuid1().hex
        rho= self.rho
        if(overrideRho):
            rho= overrideRho
        return defElasticMembranePlateSection(preprocessor= preprocessor, name= matName, E= self.E, nu= self.nu, rho= rho, h= thickness)
    
    def defMembranePlateFiberSection(self, preprocessor, thickness, name= None, overrideRho= None):
        ''' Return an elastic membrane plate section material appropriate
            for example for shell elements.

        :param preprocessor: preprocessor of the finite element problem.
        :param thickness: plate thickness.
        :param name: name for the new material.
        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''
        baseMaterial= self.defElasticIsotropic3d(preprocessor= preprocessor, overrideRho= overrideRho)
        matName= name
        if(not matName):
            matName= uuid.uuid1().hex
        return defMembranePlateFiberSection(preprocessor= preprocessor, name= matName, h= thickness, nDMaterial= baseMaterial)        

    def getDict(self):
        ''' Returns a dictionary whith the values of the internal forces.
            Makes easier export it to json.'''
        return {'E':self.E,'nu':self.nu,'rho':self.rho}
    
    def setFromDict(self,dct):
        '''Sets the internal forces from the dictionary argument.'''
        self.E= dct['E']
        self.nu= dct['nu']
        self.rho= dct['rho']
        

def defElasticMaterial(preprocessor, name:str, E:float, rho= 0.0, nu= 0.3):
    '''Constructs an elastic uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param E:            tangent in the stress-strain diagram
    :param rho:          mass density
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''
    tmp= BasicElasticMaterial(E, nu, rho)
    return tmp.defElasticMaterial(preprocessor, name)

def defElasticPPMaterial(preprocessor,name,E,fyp,fyn):
    '''Constructs an elastic perfectly-plastic uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param E:            tangent in the elastic zone of the stress-strain diagram
    :param fyp:          stress at which material reaches plastic state in tension
    :param fyn:          stress at which material reaches plastic state in compression
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elasticpp_material",name)
    retval.E= E
    retval.fyp= fyp
    retval.fyn= fyn
    retval.revertToStart() # Compute material derived parameters.
    return retval

def defElastNoTensMaterial(preprocessor,name,E):
    '''Constructs a uniaxial elastic - no tension material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param E:            tangent in the elastic zone of the stress-strain diagram
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_no_traction_material",name)
    retval.E= E
    return retval

#Cable material.
def defCableMaterial(preprocessor,name,E,prestress,rho):
    '''Constructs a uniaxial bilinear prestressed material. 
    The stress strain ranges from slack (large strain at zero stress) 
    to taught (linear with modulus E).

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param E:            elastic modulus
    :param prestress:    prestress
    :param rho:          mass density
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("cable_material",name)
    retval.E= E
    retval.prestress= prestress
    retval.rho= rho
    return retval


#Steel 01.
def defSteel01(preprocessor,name,E,fy,b):
    '''Constructs a uniaxial bilinear steel material object with kinematic hardening

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param E:            initial elastic tangent 
    :param fy:           yield strength 
    :param b:            strain-hardening ratio: ratio between post-yield tangent
                    and initial elastic tangent
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("steel01",name)
    retval.E= E
    retval.fy= fy
    retval.b= b
    return retval

#Steel 02.
def defSteel02(preprocessor,name,E,fy,b,initialStress):
    '''Constructs a uniaxial bilinear Giuffre-Menegotto-Pinto steel material with 
    isotropic strain hardening

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name identifying the material
    :param E:  initial elastic tangent 
    :param fy: yield strength 
    :param b:  strain-hardening ratio: ratio between post-yield tangent
               and initial elastic tangent
    :param initialStress: initial stress
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("steel02",name)
    retval.E= E
    retval.fy= fy
    retval.b= b
    retval.initialStress= initialStress
    return retval


#Concrete 01.
def defConcrete01(preprocessor,name,epsc0,fpc,fpcu,epscu):
    ''''Constructs an uniaxial Kent-Scott-Park concrete material object 
    with degraded linear unloading/reloading stiffness according to 
    the work of Karsan-Jirsa and no tensile strength

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param epsc0:        concrete strain at maximum strength 
    :param fpc:          concrete compressive strength at 28 days (compression is negative)
    :param fpcu:         concrete crushing strength 
    :param epscu:        concrete strain at crushing strength 
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("concrete01_material",name)
    retval.epsc0= epsc0
    retval.fpc= fpc
    retval.fpcu= fpcu
    retval.epscu= epscu
    return retval


#Concrete 02.
def defConcrete02(preprocessor,name,epsc0,fpc,fpcu,epscu,ratioSlope= 0.1, ft= None, Ets= None):
    ''''Constructs an uniaxial concrete material with linear tension
    softening. Compressive concrete parameters should be input as negative values.
    The initial slope for this model is (2*fpc/epsc0) 

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param epsc0:        concrete strain at maximum strength 
    :param fpc:          concrete compressive strength at 28 days (compression is negative)
    :param fpcu:         concrete crushing strength 
    :param epscu:        concrete strain at crushing strength 
    :param ratioSlope:   ratio between unloading slope at epscu and initial slope (defaults to 0.1).
    :param ft:           tensile strength (defaults to None in which case the value is set to -0.1*fpc)
    :param Ets:          tension softening stiffness (absolute value) (slope of the linear tension softening branch) (defaults to None in which case the value is set to 0.1*fpc/epsc0)

    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("concrete02_material",name)
    retval.epsc0= epsc0
    retval.fpc= fpc
    retval.fpcu= fpcu
    retval.epscu= epscu
    retval.ratioSlope= ratioSlope
    if(ft):
        retval.ft= ft
    else:
        retval.ft= -0.1*fpc
    if(Ets):
        retval.Ets= Ets
    else:
        retval.Ets= 0.1*fpc/epsc0
    if(fpc==fpcu):
        lmsg.warning("concrete02 compressive strength fpc is equal to crushing strength fpcu => the solver can return wrong stresses or have convergence problems ")
    return retval

#Elastic section 1d.
def defElasticSection1d(preprocessor,name,A,E, linearRho= 0.0):
    '''Constructs an elastic section appropriate for 1D beam analysis.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param A:            cross-sectional area of the section
    :param E:            Young’s modulus of material
    :param linearRho:    mass per unit length.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_section_1d",name)
    retval.sectionProperties.A= A
    retval.sectionProperties.E= E
    retval.sectionProperties.linearRho= linearRho
    return retval

#Elastic section 2d.
def defElasticSection2d(preprocessor,name,A,E,I, linearRho= 0.0):
    '''Constructs an elastic section appropriate for 2D beam analysis.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param A:            cross-sectional area of the section
    :param E:            Young’s modulus of material
    :param I:            second moment of area about the local z-axis
    :param linearRho:    mass per unit length.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_section_2d",name)
    retval.sectionProperties.A= A
    retval.sectionProperties.E= E
    retval.sectionProperties.I= I
    retval.sectionProperties.linearRho= linearRho
    return retval

#Elastic shear section 2d.
def defElasticShearSection2d(preprocessor,name,A,E,G,I,alpha, linearRho= 0.0):
    '''Constructs an elastic section appropriate for 2D beam analysis, 
    including shear deformations.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param A:            cross-sectional area of the section
    :param E:            Young’s modulus of the material
    :param G:            Shear modulus of the material          
    :param I:            second moment of area about the local z-axis
    :param alpha:        shear shape factor
    :param linearRho:    mass per unit length.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elasticShearSection2d",name)
    retval.sectionProperties.A= A
    retval.sectionProperties.E= E
    retval.sectionProperties.G= G
    retval.sectionProperties.I= I
    retval.sectionProperties.Alpha= alpha
    retval.sectionProperties.linearRho= linearRho
    return retval

def defElasticSectionFromMechProp1d(preprocessor,name,mechProp1d, overrideRho= None):
    '''Constructs an elastic section appropriate for 1D beam analysis, 
    taking mechanical properties of the section form a MechProp1d object.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param mechProp1d:   object of type MechProp1d that contains the mechanical 
                    properties of the section
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''  
    rho= mechProp1d.linearRho
    if(overrideRho):
        rho= overrideRho
    retval= defElasticSection1d(preprocessor,name,mechProp1d.A,mechProp1d.E, linearRho= rho)
    return retval

def defElasticSectionFromMechProp2d(preprocessor, name, mechProp2d, overrideRho= None):
    '''Constructs an elastic section appropriate for 2D beam analysis, 
    taking mechanical properties of the section form a MechProp2d object.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param mechProp2d:   object of type MechProp2d that contains the mechanical 
                    properties of the section
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''  
    rho= mechProp2d.linearRho
    if(overrideRho):
        rho= overrideRho
    retval= defElasticSection2d(preprocessor,name,mechProp2d.A,mechProp2d.E,mechProp2d.I,linearRho= rho)
    return retval

def defElasticShearSectionFromMechProp2d(preprocessor, name, mechProp2d, overrideRho= None):
    '''Constructs an elastic section appropriate for 2D beam analysis, 
    taking mechanical properties of the section form a MechProp2d object.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param mechProp2d:   object of type MechProp2d that contains the mechanical 
                         properties of the section
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''  
    rho= mechProp2d.linearRho
    if(overrideRho):
        rho= overrideRho
    retval= defElasticShearSection2d(preprocessor,name= name, A= mechProp2d.A, E= mechProp2d.E, G= mechProp2d.G, I= mechProp2d.I, alpha= mechProp2d.Alpha, linearRho= rho)
    return retval

#Elastic section 3d.
def defElasticSection3d(preprocessor,name,A,E,G,Iz,Iy,J, linearRho= 0.0):
    '''Constructs an elastic section appropriate for 3D beam analysis

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param A:            cross-sectional area of the section
    :param E:            Young’s modulus of the material
    :param G:            Shear modulus of the material          
    :param Iz:           second moment of area about the local z-axis
    :param Iy:           second moment of area about the local y-axis
    :param J:            torsional moment of inertia of the section
    :param linearRho:    mass per unit length.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_section_3d",name)
    retval.sectionProperties.A= A
    retval.sectionProperties.E= E
    retval.sectionProperties.G= G
    retval.sectionProperties.Iz= Iz
    retval.sectionProperties.Iy= Iy
    retval.sectionProperties.J= J
    retval.sectionProperties.linearRho= linearRho
    return retval

def defElasticSectionFromMechProp3d(preprocessor, name, mechProp3d, overrideRho= None):
    '''Constructs an elastic section appropriate for 3D beam analysis, 
    taking mechanical properties of the section form a MechProp3d object.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param mechProp2d:   instance of the class MechProp3d that contains the 
                         mechanical properties of the section
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''  
    rho= mechProp3d.linearRho
    if(overrideRho):
        rho= overrideRho
    return defElasticSection3d(preprocessor,name,mechProp3d.A,mechProp3d.E,mechProp3d.G,mechProp3d.Iz,mechProp3d.Iy,mechProp3d.J,linearRho= rho)

def defElasticShearSectionFromMechProp3d(preprocessor, name, mechProp3d, overrideRho= None):
    '''Constructs an elastic section appropriate for 3D beam analysis, 
    taking mechanical properties of the section form a MechProp3d object.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param mechProp2d:   instance of the class MechProp3d that contains the 
                         mechanical properties of the section
    :param overrideRho: if defined (not None), override the value of 
                        the material density.
    '''  
    rho= mechProp3d.linearRho
    if(overrideRho):
        rho= overrideRho
    return defElasticShearSection3d(preprocessor, name= name, A= mechProp3d.A, E= mechProp3d.E, G= mechProp3d.G, Iz= mechProp3d.Iz, Iy= mechProp3d.Iy, J= mechProp3d.J, alpha_y= mechProp3d.AlphaY, alpha_z= mechProp3d.AlphaZ, linearRho= rho)

#Elastic shear section 3d.
def defElasticShearSection3d(preprocessor, name, A, E, G, Iz, Iy, J, alpha_y, alpha_z, linearRho= 0.0):
    '''Constructs an elastic section appropriate for 3D beam analysis, 
    including shear deformations.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the section
    :param A:            cross-sectional area of the section
    :param E:            Young’s modulus of the material
    :param G:            shear modulus of the material          
    :param Iz:           second moment of area about the local z-axis
    :param Iy:           second moment of area about the local y-axis
    :param J:            torsional moment of inertia of the section
    :param alpha_y:      shear shape factor on y axis.
    :param alpha_z:      shear shape factor on z axis.
    :param linearRho:    mass per unit length.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elasticShearSection3d",name)
    retval.sectionProperties.A= A
    retval.sectionProperties.E= E
    retval.sectionProperties.G= G
    retval.sectionProperties.Iz= Iz
    retval.sectionProperties.Iy= Iy
    retval.sectionProperties.J= J
    retval.sectionProperties.AlphaY= alpha_y
    retval.sectionProperties.AlphaZ= alpha_z
    retval.sectionProperties.linearRho= linearRho
    return retval


#Linear elastic isotropic plane strain material.
def defElasticIsotropicPlaneStrain(preprocessor,name,E,nu, rho= 0.0):
    '''Constructs an linear elastic isotropic plane-strain material.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the material
    :param  E:            Young’s modulus of the material
    :param  nu:           Poisson’s ratio
    :param  rho:          mass density, optional (defaults to 0.0)
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_isotropic_plane_strain_2d",name)
    retval.E= E
    retval.nu= nu
    retval.rho= rho
    return retval

#Linear elastic isotropic plane stress material.
def defElasticIsotropicPlaneStress(preprocessor,name,E,nu, rho= 0.0):
    '''Constructs an linear elastic isotropic plane-stress material.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the material
    :param  E:            Young’s modulus of the material
    :param  nu:           Poisson’s ratio
    :param  rho:          mass density, optional (defaults to 0.0)
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_isotropic_plane_stress_2d",name)
    retval.E= E
    retval.nu= nu
    retval.rho= rho
    return retval

# Linear elastic isotropic 3d material.
def defElasticIsotropic3d(preprocessor, name, E, nu, rho= 0.0):
    '''Constructs an linear elastic isotropic 3D material.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the material
    :param  E:            Young’s modulus of the material
    :param  nu:           Poisson’s ratio
    :param  rho:          mass density, optional (defaults to 0.0)
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_isotropic_3d",name)
    retval.E= E
    retval.nu= nu
    retval.rho= rho
    return retval

#Elastic plate section.
def defElasticPlateSection(preprocessor,name,E,nu,rho,h):
    '''Constructs an elastic isotropic section material appropriate 
       for plate analysis.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the section
    :param  E:            Young’s modulus of the material
    :param  nu:           Poisson’s ratio
    :param  rho:          mass density
    :param  h:            overall depth of the section
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_plate_section",name)
    retval.E= E
    retval.nu= nu
    retval.rho= rho
    retval.h= h
    return retval

#Elastic plate section.
def defJ2PlateFibre(preprocessor, name, E, nu, fy, alpha= .01, rho= 0.0):
    '''Constructs a J2 (Von Mises) material with a linear-strain
       hardening rule appropriate for plate analysis.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the material.
    :param  E:            Young’s modulus of the material.
    :param  nu:           Poisson’s ratio.
    :param  fy:           material yield stress.
    :param  alpha:        strain hardening ratio (default: (0.01), 
                          range: 0 to 1).
    :param  rho:          mass density (defaults to 0.0).
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("J2_plate_fibre",name)
    retval.E= E
    retval.nu= nu
    retval.fy= fy
    if(alpha<0 or alpha>1):
        lmsg.error('alpha value: '+str(alpha)+' out of range (0,1)')
    retval.Hiso= alpha*E/(1.0-alpha)
    retval.rho= rho
    return retval

#Elastic membrane plate section.
def defElasticMembranePlateSection(preprocessor, name:str, E:float, nu:float, rho:float, h:float):
    '''Constructs an elastic isotropic section material appropriate 
       for plate and shell analysis.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the section
    :param  E:            Young’s modulus of the material
    :param  nu:           Poisson’s ratio
    :param  rho:          mass density
    :param  h:            overall depth of the section
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("elastic_membrane_plate_section",name)
    retval.E= E
    if(nu>0.5):
        lmsg.warning('Poisson\'s ratio: '+str(nu)+' is very high.') 
    retval.nu= nu
    retval.rho= rho
    retval.h= h
    return retval

#Elastic membrane plate section.
def defMembranePlateFiberSection(preprocessor, name:str, nDMaterial, h:float):
    '''Constructs a membrane plate fiber section appropriate 
       for plate and shell analysis.

    :param  preprocessor: preprocessor of the finite element problem.
    :param  name:         name identifying the section
    :param  nDMaterial:   material to put in the section fibers.
    :param  h:            overall depth of the section
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("membrane_plate_fiber_section",name)
    retval.setMaterial(nDMaterial)
    retval.h= h
    return retval

def defMultiLinearMaterial(preprocessor, name, points):
    '''Constructs an elastic perfectly-plastic uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param points:       list of tuples defining the (strain, stress) or
                         (displacement, force) points.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("multi_linear",name)
    retval.setValues(points)
    return retval

def defInitStrainMaterial(preprocessor, name, materialToEncapsulate):
    '''Constructs an initial strain uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialToEncapsulate: material that will name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("init_strain_material",name)
    retval.setMaterial(materialToEncapsulate)
    return retval

def defInitStressMaterial(preprocessor, name, materialToEncapsulate):
    '''Constructs an initial strain uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialToEncapsulate: material that will name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("init_stress_material",name)
    retval.setMaterial(materialToEncapsulate)
    return retval

def defInvertMaterial(preprocessor, name, materialToEncapsulate):
    '''Constructs an inverted uniaxial material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialToEncapsulate: material that will name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("invert_material",name)
    retval.setMaterial(materialToEncapsulate)
    return retval

def defCompressionOnlyMaterial(preprocessor, name, materialToEncapsulate):
    '''Constructs a compression-only material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialToEncapsulate: material that will name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("compression_only_material",name)
    retval.setMaterial(materialToEncapsulate)
    return retval

def defTensionOnlyMaterial(preprocessor, name, materialToEncapsulate):
    '''Constructs a compression-only material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialToEncapsulate: material that will name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("tension_only_material",name)
    retval.setMaterial(materialToEncapsulate)
    return retval

def defSeriesMaterial(preprocessor, name, materialsToConnect):
    '''Constructs an series material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param materialsToConnect: name of the materials to be connected.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("series_material",name)
    retval.setMaterials(materialsToConnect)
    return retval

def defHorizontalSoilReactionMaterial(preprocessor, name, samplePoints, initStrain, noTension= False):
    ''' Return a material that represents the force-displacement
        diagram of the soil reaction in a point.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param samplePoints: points defining the soil response diagram.
    :param initStrain: initial strain of the soil.
    '''
    ## Material definition
    if(initStrain>0.0):
        lmsg.warning('initStrain ('+str(initStrain)+') must be negative.')
    encapsulatedMaterialName= name+'_encapsulated'
    encapsulated= defMultiLinearMaterial(preprocessor, name= encapsulatedMaterialName, points= samplePoints) # We'll set the points AGAIN, AFTER specifying the initial strain
    invertedMaterialName= encapsulatedMaterialName+'_inverted'
    inverted= defInvertMaterial(preprocessor, name= invertedMaterialName, materialToEncapsulate= encapsulated.name)
    if(noTension):
        initStrainMaterialName= invertedMaterialName+'_e0'
        initStrainMaterial= defInitStrainMaterial(preprocessor, name= initStrainMaterialName, materialToEncapsulate= inverted.name)
        retval= defCompressionOnlyMaterial(preprocessor, name= name, materialToEncapsulate= initStrainMaterial.name) 
        retval.material.initialStrain= initStrain # displacement at rest.
        mLinearMat= retval.material.material.material
        mLinearMat.setValues(samplePoints) # and now we set the points AGAIN.
    else:
        retval= defInitStrainMaterial(preprocessor, name= name, materialToEncapsulate= inverted.name)
        retval.initialStrain= initStrain # displacement at rest.
        retval.material.material.setValues(samplePoints) # and now we set the points AGAIN.
    return retval

def defPressureIndependentMultiYieldMaterial(preprocessor, name, nd, rho, refShearModul,refBulkModul,cohesi,peakShearStra,frictionAng = 0.,refPress = 100, pressDependCoe = 0.0, numberOfYieldSurf = 20, gredu= []):
    ''' Define a pressure independent yield material for soil analysis.

    :param name: name identifying the material.
    :param nd: number of dimensions, 2 for plane-strain, and 3 for 3D analysis.
    :param rho: Saturated soil mass density.
    :param refShearModul: Reference low-strain shear modulus, specified at a reference mean effective confining pressure refPress.
    :param refBulkModul: Reference bulk modulus, specified at a reference mean effective confining pressure refPress.
    :param cohesi: apparent cohesion at zero effective confinement.
    :param peakShearStra: an octahedral shear strain at which the maximum shear strength is reached, specified at a reference mean effective confining pressure refPress.
    :param frictionAng: friction angle at peak shear strength in degrees. (optional: default is 0.0).
    :param refPress: reference mean effective confining pressure at which refShearModul, refBulModul, and peakShearStra are defined.
    :param pressDependCoe: a positive constant defining variations of G and B as a function of instantaneous effective confinement p’(default is 0.0). see notes 4 and 5 in https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/PressureIndependentMultiYield.html
    :param numberOfYieldSurf: Number of yield surfaces, optional (must be less than 40: default is 20). The surfaces are generated based on the hyperbolic relation defined in https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/PressureIndependentMultiYield.html
    :param gredu: instead of automatic surfaces generation (Note 2), you can define yield surfaces directly based on desired shear modulus reduction curve. To do so, add a minus sign in front of numberOfYieldSurf, then provide numberOfYieldSurf pairs of shear strain (γ) and modulus ratio (Gs) values. For example, to define 10 surfaces: … -10γ1Gs1 … γ10Gs10 …
    '''
    parameterDict= {'nd':nd, 'rho':rho, 'refShearModul':refShearModul,'refBulkModul':refBulkModul,'cohesi':cohesi,'peakShearStra':peakShearStra,'frictionAng':frictionAng, 'refPress':refPress, 'pressDependCoe':pressDependCoe, 'numberOfYieldSurf':numberOfYieldSurf, 'gredu':gredu}
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("pressure_independ_multi_yield",name)
    retval.setup(parameterDict)
    return retval

def defPressureDependentMultiYield02Material(preprocessor, name, nd, rho, refShearModul, refBulkModul, frictionAng, peakShearStra, refPress, pressDependCoe, phaseTransformAngle, contractionParam1, contractionParam3, dilationParam1, dilationParam3, numberOfYieldSurf= 20, gredu= [], contractionParam2= 5., dilationParam2= 3., liquefactionParam1= 1., liquefactionParam2= 0., e= 0.6, volLimit1= 0.9, volLimit2= .02, volLimit3= 0.7, atm= 101., cohesi= 0.1, hv= 0., pv= 1.):
    '''
    :param nd: Number of dimensions, 2 for plane-strain, and 3 for 3D analysis.
    :param rho: Saturated soil mass density.
    :param refShearModul: Reference low-strain shear modulus, specified at a reference mean effective confining pressure refPress.
    :param refBulkModul: Reference bulk modulus, specified at a reference mean effective confining pressure refPress.
    :param frictionAng: Friction angle at peak shear strength, in degrees.
    :param peakShearStra: An octahedral shear strain at which the maximum shear strength is reached, specified at a reference mean effective confining pressure refPress.
    :param refPress: reference mean effective confining pressure at which refShearModul, refBulModul, and peakShearStra are defined.
    :param pressDependCoe: A positive constant defining variations of G and B as a function of instantaneous effective confinement p’.
    :param phaseTransformAngle: Phase transformation angle, in degrees.
    :param contractionParam1: A non-negative constant defining the rate of shear-induced volume decrease (contraction) or pore pressure buildup. A larger value corresponds to faster contraction rate.
    :param contractionParam3: See contractionParam1.
    :param dilationParam1: Non-negative constants defining the rate of shear-induced volume increase (dilation). Larger values correspond to stronger dilation rate.
    :param dilationParam2: see dilationParam1.
    :param numberOfYieldSurf: Number of yield surfaces, optional (must be less than 40, default is 20). The surfaces are generated based on the hyperbolic relation defined in Note 2 in https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/PressureDependentMultiYield.html
    :param liquefactionParam1: Parameters controlling the mechanism of liquefaction-induced perfectly plastic shear strain accumulation, i.e., cyclic mobility. Set liquefac1 = 0 to deactivate this mechanism altogether.
    :param liquefactionParam2: see liquefactionParam1.
    :param e: Initial void ratio, optional (default is 0.6).
    :param cohesi: Cohesion.
    '''
    parameterDict= {'nd':nd, 'rho':rho, 'refShearModul':refShearModul, 'refBulkModul':refBulkModul, 'frictionAng':frictionAng, 'peakShearStra':peakShearStra, 'refPress':refPress, 'pressDependCoe':pressDependCoe, 'phaseTransformAngle':phaseTransformAngle, 'contractionParams':[contractionParam1, contractionParam2, contractionParam3], 'dilationParams':[dilationParam1, dilationParam2, dilationParam3], 'numberOfYieldSurf':numberOfYieldSurf, 'gredu':gredu, 'dilationParam2':dilationParam2, 'liquefactionParams':[liquefactionParam1, liquefactionParam2], 'e':e, 'volLimits':[volLimit1,volLimit2, volLimit3], 'atm':atm, 'cohesi':cohesi, 'hv':hv, 'pv':pv}
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("pressure_depend_multi_yield02",name)
    retval.setup(parameterDict)
    return retval

def defViscousMaterial(preprocessor, name, C, Alpha= 1.0):
    '''Constructs a viscous material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name: name for the new material.
    :param C: damping coeficient.
    :param Alpha: power factor (=1 means linear damping).
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("viscous_material", name)
    retval.dampingCoeff= C
    retval.alpha= Alpha
    return retval

# Create nDMaterial using Template Elastic-Plastic Model
def defTemplate3Dep(preprocessor, name, elasticMaterial, yieldSurface, potentialSurface, elasticPlasticState, scalarEvolutionLaws, tensorialEvolutionLaws):
    '''Constructs an linear elastic isotropic 3D material.

    :param preprocessor: preprocessor of the finite element problem.
    :param name:         name identifying the material
    :param elasticMaterial: elastic material.
    :param yieldSurface: yield surface.
    :param potentialSurface: potential surface.
    :param elasticPlasticState: elastic-plastic state.
    :param scalarEvolutionLaws: list with up to four scalar evolution laws.
    :param tensorialEvolutionLaws: list with up to four tensorial evolution laws.
    '''
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("template_3d_ep",name)
    retval.elasticMaterial= elasticMaterial
    retval.yieldSurface= yieldSurface
    retval.potentialSurface= potentialSurface
    retval.elasticPlasticState= elasticPlasticState
    if(len(scalarEvolutionLaws)):
      retval.scalarEvolutionLaw1= scalarEvolutionLaws.pop(0)
    if(len(scalarEvolutionLaws)):
      retval.scalarEvolutionLaw2= scalarEvolutionLaws.pop(0)
    if(len(scalarEvolutionLaws)):
      retval.scalarEvolutionLaw3= scalarEvolutionLaws.pop(0)
    if(len(scalarEvolutionLaws)):
      retval.scalarEvolutionLaw4= scalarEvolutionLaws.pop(0)
    if(len(tensorialEvolutionLaws)):
      retval.tensorialEvolutionLaw1= tensorialEvolutionLaws.pop(0)
    if(len(tensorialEvolutionLaws)):
      retval.tensorialEvolutionLaw2= tensorialEvolutionLaws.pop(0)
    if(len(tensorialEvolutionLaws)):
      retval.tensorialEvolutionLaw3= tensorialEvolutionLaws.pop(0)
    if(len(tensorialEvolutionLaws)):
      retval.tensorialEvolutionLaw4= tensorialEvolutionLaws.pop(0)
    return retval

# Create nDMaterial using Template Elastic-Plastic Model
def defDruckerPrager3d(preprocessor, name, k, G, sigY, mRho, mRhoBar, Kinf, Ko, delta1, H, theta, delta2, mDen):
    materialHandler= preprocessor.getMaterialHandler
    retval= materialHandler.newMaterial("drucker-prager_3d", name)
    retval.k= k
    retval.G= G
    retval.sigY= sigY
    retval.mrho= mRho
    retval.mrhoBar= mRhoBar
    retval.Kinf= Kinf
    retval.Ko= Ko
    retval.delta1= delta1 
    retval.Hard= H
    retval.theta= theta
    retval.delta2= delta2
    retval.rho= mDen
    retval.setup()
    retval.initialize()
    return retval

class MaterialData(BasicElasticMaterial):
    '''Base class to construct some material definition classes

     :ivar name:         name identifying the material
     :ivar xc_material:  pointer to XC material.    
    '''
    def __init__(self, name, E, nu, rho):
        '''Base class to construct some material definition classes

         :param name:         name identifying the material
         :param E:            Young’s modulus of the material
         :param nu:           Poisson’s ratio
         :param rho:          mass density
        '''
        super(MaterialData,self).__init__(E,nu,rho)
        self.name= name
        self.xc_material= None

class DeckMaterialData(MaterialData):
    '''Material for Isotropic elastic sections

    :ivar name:         name identifying the section
    :ivar thickness:    overall depth of the section
    :ivar material:     instance of a class that defines the elastic modulus, 
                        shear modulus and mass density of the material
    '''
    def __init__(self,name,thickness,material):
        super(DeckMaterialData,self).__init__(name,material.E,material.nu,material.rho)
        self.name= name
        self.thickness= thickness
        self.material= material
    def getAreaDensity(self):
        '''return the mass per unit area'''
        lmsg.warning('DeckMaterialData.getAreaDensity will be deprecated soon. Use the XC material method.')
        return self.rho*self.thickness
    def setupElasticSection(self,preprocessor, overrideRho= None):
        '''create an elastic isotropic section appropriate for plate 
           and shell analysis.

        :param preprocessor: preprocessor of the finite element problem.
        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''
        if(not self.xc_material):
            materialHandler= preprocessor.getMaterialHandler
            if(materialHandler.materialExists(self.name)):
                lmsg.warning("Section: "+self.name+" already defined.")
                self.xc_material= materialHandler.getMaterial(self.name)
            else:
                rho= self.rho
                if(overrideRho):
                    rho= overrideRho
                self.xc_material= defElasticMembranePlateSection(preprocessor, name= self.name,E= self.E, nu= self.nu, rho= rho, h= self.thickness)
        else:
            lmsg.warning('Material: '+ self.name+ ' already defined.')
        return self.xc_material

class BeamMaterialData(MaterialData):
    '''Elastic section appropriate for 3D beam analysis, including shear deformations.

    :ivar name:         name identifying the section.
    :ivar section:      instance of a class that defines the geometric and
                        mechanical characteristiscs of a section
                        e.g: RectangularSection, CircularSection, ISection, ...
    :ivar material:     instance of a class that defines the elastic modulus, 
                        shear modulus and mass density of the material
    '''
    def __init__(self,name,section,material):
        super(BeamMaterialData,self).__init__(name,material.E,material.nu,material.rho)
        self.name= name
        self.section= section
        self.material= material
        
    def getRho(self):
        '''return the mass per unit length'''
        return self.rho*self.section.A()
    
    def setupElasticShear3DSection(self,preprocessor, overrideRho= None):
        '''Return an elastic section appropriate for 3D beam linear 
           elastic analysis.

        :param overrideRho: if defined (not None), override the value of 
                            the material density.
        '''
        if(not self.xc_material):
            materialHandler= preprocessor.getMaterialHandler
            if(materialHandler.materialExists(self.name)):
                lmsg.warning("Section: "+self.name+" already defined.")
                self.xc_material= materialHandler.getMaterial(self.name)
            else:
                rho= self.getRho()
                if(overrideRho):
                    rho= overrideRho
                self.xc_material= defElasticShearSection3d(preprocessor,name= self.name, A= self.section.A(), E= self.material.E, G= self.material.G(), Iz= self.section.Iz(), Iy= self.section.Iy(), J= self.section.J(), alpha_y= self.section.alphaY(), alpha_z= self.section.alphaZ(), linearRho= rho)
        else:
            lmsg.warning('Material: '+ self.name+ ' already defined.')
        return self.xc_material
