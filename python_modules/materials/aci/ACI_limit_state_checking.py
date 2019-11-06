# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2016, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

from materials.aci import ACI_materials
from materials.sections import rebar_family as rf
import geom
from materials import limit_state_checking_base as lsc
from postprocess import control_vars as cv
from rough_calculations import ng_simple_bending_reinforcement
import math
import xc_base
import geom
from materials.sections.fiber_section import fiber_sets
from materials.sections import stressCalc as sc
from miscUtils import LogMessages as lmsg
from postprocess.reports import common_formats as fmt

class RebarController(object):
    '''Control of some parameters as development lenght 
       minimum reinforcement and so on.

       :ivar psi_t: reinforcement location factor; "concrete below" is 
                    taken as the depth from the rebar center to the bottom 
                    of the concrete section.
                    * 1.3 for concrete below ≥ 12 inches 
                    * 1.0 for concrete below < 12 inches 
       :ivar psi_e: coating factor 
                    * 1.5 for epoxy coated bars with cover (to center of bar)
                          less than 3db (spacing is not calculated)
                    * 1.2 for all other epoxy coated bars 
                    * 1.0 for uncoated bars
       :ivar Ktr: transverse reinforcement index. Factor that represents the 
                  contribution of confining reinforcement across potential 
                  splitting planes; is conservatively assumed to be zero.
       :ivar concreteCover: the distance from center of a bar or wire to 
                            nearest concrete surface.
       :ivar spacing: center-to-center spacing of bars or wires being 
                      developed, in.
    '''

    def __init__(self, psi_t= 1.3, psi_e= 1.0, concreteCover= 35e-3, spacing= 150e-3):
        '''Constructor.'''
        self.psi_t= psi_t
        self.psi_e= psi_e
        self.concreteCover= concreteCover
        self.spacing= spacing

    def getKtr(self, n= 1, Atr= 0.0):
        '''Return the transverse reinforcing index according to
           clause 25.4.2.3 of ACI 318-14.

        :param n: number of bars or wires being developed or
                  lap spliced along the plane of splitting.
        :param Atr: total cross-sectional area of all transverse reinforcement
                    within spacing s that crosses the potential plane of
                    splitting through the reinforcement being developed.
        '''
        Atr_inch2= Atr*(1.0/0.0254)**2
        return (40.0*Atr/self.spacing/n)*0.0254 #To meters.

    def getConfinementTerm(self, phi, n= 1, Atr= 0.0):
        '''Return the confinement term as defined in clause 25.4.2.3 
           of ACI 318-14.

        :param phi: nominal diameter of bar, wire, or prestressing strand.
        :param n: number of bars or wires being developed or
                  lap spliced along the plane of splitting.
        :param Atr: total cross-sectional area of all transverse reinforcement
                    within spacing s that crosses the potential plane of
                    splitting through the reinforcement being developed.
        '''
        Ktr= self.getKtr(n,Atr)
        return (self.concreteCover+Ktr)/phi
    def getBasicAnchorageLength(self, concrete, phi, steel):
        """Returns anchorage length in tension according to ACI-318 25.4.2.3.

        :param concrete: concrete material.
        :param phi: nominal diameter of bar, wire, or prestressing strand.
        :param fck: concrete characteristic compressive strength.
        :param steel: reinforcement steel.
        """
        psi_t_psi_e= min(self.psi_t*self.psi_e,1.7)
        psi_t_psi_e_psi_s= psi_t_psi_e*ACI_materials.getPsi_sFromDiameter(phi)
        #Clause 25.4.1.4:
        l= min(concrete.getLambdaSqrtFck(),concrete.Lambda*ACI_materials.toPascal*100.0)
        retval= 3.0/40.0*(steel.fyk/l)
        retval*= psi_t_psi_e_psi_s/self.getConfinementTerm(phi)
        retval*= phi
        return max(retval,12*0.0254) #Clause 25.4.2.1b

#Check normal stresses limit state.

class BiaxialBendingNormalStressController(lsc.BiaxialBendingNormalStressControllerBase):
  '''Object that controls normal stresses limit state.'''

  def __init__(self,limitStateLabel):
    super(BiaxialBendingNormalStressController,self).__init__(limitStateLabel)

class UniaxialBendingNormalStressController(lsc.UniaxialBendingNormalStressControllerBase):
  '''Object that controls normal stresses limit state (uniaxial bending).'''

  def __init__(self,limitStateLabel):
    super(UniaxialBendingNormalStressController,self).__init__(limitStateLabel)

# Shear checking.

def VcNoShearRebars(concrete,Nd,b,d):
    '''Return concrete shear capacity on a (b x thickness)
       rectangular section according to clause 22.5.5.1 of ACI 318-14.

    :param concrete: concrete material.
    :param Nd: design axial force.
    :param b: width of the rectangular section.
    :param d: effective thickness of the RC section.
    '''
    retval= 2.0*concrete.getLambdaSqrtFck()*b*d
    if(Nd<0.0):
        retval*=(1-Nd/b/d/(2000.0*ACI_materials.toPascal))
    return retval

def V_max(concrete,Nd,b,d):
    '''Return the ultimate shear strength of the section 
       a (b x thickness) rectangular section according to clause 
       22.5.1.2 of ACI 318-14.

    :param concrete: concrete material.
    :param Nd: design axial force.
    :param b: width of the rectangular section.
    :param d: effective thickness of the RC section.
    '''
    retval= VcNoShearRebars(concrete,Nd,b,d)
    retval+= 8.0*concrete.getLambdaSqrtFck()*b*d
    retval/= concrete.gmmC
    return retval

class ShearController(lsc.ShearControllerBase):
    '''Object that controls shear limit state according to ACI 318.'''
    def __init__(self,limitStateLabel):
        super(ShearController,self).__init__(limitStateLabel)
    def setSection(self,rcSection):
        self.concrete= rcSection.concrType #Fix
        self.steel= rcSection.reinfSteelType
        self.width= rcSection.b
        self.effectiveDepth= 0.9*rcSection.h
        self.mechanicLeverArm= 0.9*self.effectiveDepth #Enhance
        self.AsTrsv= rcSection.shReinfY.getAs()
        self.s= rcSection.shReinfY.shReinfSpacing
        self.Vc= 0.0 # Concrete contribution to the shear strength.
        self.Vu= 0.0 # Ultimate shear strength.
        
    def getVcNoShearRebars(self,Nd):
        '''Return the shear resistance carried by the concrete on a (b x thickness)
           rectangular section according to clause 22.5.5.1 of ACI 318-14.

        :param Nd: design axial force.
        '''
        return VcNoShearRebars(self.concrete, Nd, self.width, self.effectiveDepth)
    
    def getV_max(self,Nd):
        '''Return the maximum shear resistance that can be carried by 
           the concrete of the section according to clause 
           22.5.1.2 of ACI 318-14.

        :param Nd: design axial force.
        '''
        return V_max(self.concrete, Nd, self.width, self.effectiveDepth)
        
    def calcVc(self, Nd):
        ''' Computes the shear strength of the section without 
            shear reinforcement.

        :param concrete: concrete material.
        :param Nd: design axial force.
        '''
        self.Vc= self.getVcNoShearRebars(Nd)
        return self.Vc
    
    def getVu(self,Nd):
        '''Return the shear strength of the concrete section
           according to clause 16.5.2.3 of ACI 318-14.

        :param Nd: design axial force.
        '''
        self.calcVc(Nd)
        V_max= self.getV_max(Nd)
        retval= self.Vc/self.concrete.gmmC # ACI 9.6.3.1
        Av= self.AsTrsv*self.effectiveDepth
        if(Av>0.0): # ACI 22.5.1.1, 22.5.10.1, 20.5.10.5.3
            retval+= Av*self.steel.fyd()
        retval= min(V_max,retval) #ACI 22.5.1.2
        self.Vsu= retval-self.Vc
        return retval
    
    def calcVu(self, Nd):
        '''Return the ultimate shear resistance carried by the concrete on 
           a (b x thickness) rectangular section according to clause 
           22.5.1.2 of ACI 318-14.

        :param Nd: design axial force.
        '''
        self.Vu= self.getVu(Nd)
        return self.Vu
    
    def check(self,elements,nmbComb):
        '''
        Check the shear strength of the RC section.
           Transverse reinforcement is not
           taken into account yet.
        '''
        lmsg.log("Postprocesing combination: "+nmbComb)
        # XXX torsional deformation ingnored.

        for e in elements:
            e.getResistingForce()
            scc= e.getSection()
            idSection= e.getProp("idSection")
            section= scc.getProp("datosSecc")
            self.setSection(section)
            NTmp= scc.getStressResultantComponent("N")
            VuTmp= self.calcVu(NTmp) 
            VyTmp= scc.getStressResultantComponent("Vy")
            VzTmp= scc.getStressResultantComponent("Vz")
            VTmp= math.sqrt((VyTmp)**2+(VzTmp)**2)
            if(VuTmp!=0.0):
              FCtmp= abs(VTmp)/VuTmp
            else:
              FCtmp= 10
            if(FCtmp>=e.getProp(self.limitStateLabel).CF):
              MyTmp= scc.getStressResultantComponent("My")
              MzTmp= scc.getStressResultantComponent("Mz")
              Mu= 0.0 # Not used in ACI-318
              theta= None # Not used in ACI-318
              e.setProp(self.limitStateLabel,cv.RCShearControlVars(idSection,nmbComb,FCtmp,NTmp,MyTmp,MzTmp,Mu,VyTmp,VzTmp,theta,self.Vc,self.Vsu,VuTmp)) # Worst cas

##################
# Rebar families.#
##################

class ACIRebarFamily(rf.RebarFamily):
    ''' Family or reinforcement bars with checking according to ACI 318-14.

       :ivar barNumber: bar number in ACI 318 code.
       :ivar psi_t: reinforcement location factor; "concrete below" is 
                    taken as the depth from the rebar center to the bottom 
                    of the concrete section.
                    * 1.3 for concrete below ≥ 12 inches 
                    * 1.0 for concrete below < 12 inches 
       :ivar psi_e: coating factor 
                    * 1.5 for epoxy coated bars with cover (to center of bar)
                          less than 3db (spacing is not calculated)
                    * 1.2 for all other epoxy coated bars 
                    * 1.0 for uncoated bars
    '''
    def __init__(self,steel,barNumber,spacing,concreteCover):
      ''' Constructor.

      :param steel: reinforcing steel material.
      :param barNumber: diameter of the bars.
      :param spacing: spacing of the bars.
      :param concreteCover: concrete cover of the bars.
      '''
      self.barNumber= barNumber
      diam= ACI_materials.standard_bars_diameters[barNumber]
      super(ACIRebarFamily,self).__init__(steel,diam,spacing,concreteCover)
      self.psi_t= 1.3
      self.psi_e= 1.0 # uncoated bars.

    def getCopy(self,barController):
      return ACIRebarFamily(self.steel,self.barNumber,self.spacing,self.concreteCover)
    def getRebarController(self):
      return RebarController(psi_t= self.psi_t, psi_e= self.psi_e, concreteCover= self.concreteCover, spacing= self.spacing)
    def getBasicAnchorageLength(self,concrete):
      ''' Return the basic anchorage length of the bars.'''
      rebarController= self.getRebarController()
      return rebarController.getBasicAnchorageLength(concrete,self.getDiam(),self.steel)
    def getMinReinfAreaUnderFlexion(self, thickness, b= 1.0, type= 'slab', concrete= None):
        '''Return the minimun amount of bonded reinforcement to control cracking
           for reinforced concrete sections under flexion per unit length 
           according to clauses 7.6.1.1, 8.6.1.1, 9.6.1.2, 10.6.1.1, 11.6.1,
           12.6.1 

        :param steel: reinforcement steel.
        :param thickness: gross thickness of concrete section (doesn't include 
                          the area of the voids).
        '''
        retval= 0.0025*thickness*b
        fy= self.steel.fyk
        if(type=='slab'):
            limit= ACI_materials.toPascal*60e3
            retval= thickness # b= 1
            if(fy<limit):
                retval*= 0.0020
            else:
                retval*= max(0.0018*limit/fy,0.0014)
        elif(type=='wall'):
            retval= 0.0025*thickness # b= 1
        elif(type=='beam'):
            d= 0.9*thickness
            retval= d*b
            retval*= max(3.0*concrete.getSqrtFck(),ACI_materials.toPascal*200)
        elif(type=='column'):
            retval= 0.01*thickness*b
        return retval

    def getMinReinfAreaUnderTension(self,thickness, type= 'slab', concrete= None):
        '''Return the minimun amount of bonded reinforcement to control cracking
           for reinforced concrete sections under tension.

        :param concrete: concrete material.
        :param thickness: thickness of the tensioned member.
        '''
        return 2.0*self.getMinReinfAreaUnderFlexion(thickness= thickness, type= type, concrete= concrete)

    def getVR(self,concrete,Nd,Md,b,thickness):
        '''Return the shear resistance carried by the concrete on a (b x thickness)
           rectangular section according to clause 22.5.5.1 of ACI 318-14.

        :param concrete: concrete material.
        :param Nd: design axial force.
        :param Md: design bending moment.
        :param b: width of the rectangular section.
        :param thickness: height of the rectangular section.
        '''
        return VcNoShearRebars(concrete,Nd,b,0.9*thickness)

    def writeRebars(self, outputFile,concrete,AsMin):
        '''Write rebar family data.'''
        self.writeDef(outputFile,concrete)
        outputFile.write("  area: As= "+ fmt.Areas.format(self.getAs()*1e4) + " cm2/m areaMin: " + fmt.Areas.format(AsMin*1e4) + " cm2/m")
        rf.writeF(outputFile,"  F(As)", self.getAs()/AsMin)

class ACIFamNBars(ACIRebarFamily):
    n= 2 #Number of bars.
    def __init__(self,steel,n,barNumber,spacing,concreteCover):
        RebarFamily.__init__(self,steel,barNumber,spacing,concreteCover)
        self.n= int(n)
    def __repr__(self):
        return str(n) + " x " + self.steel.name + ", diam: " + str(int(self.diam*1e3)) + " mm, e= " + str(int(self.spacing*1e3))
    def writeDef(self,outputFile,concrete):
        outputFile.write("  n= "+str(self.n)+" diam: "+ fmt.Diam.format(self.getDiam()*1000) + " mm, spacing: "+ fmt.Diam.format(self.spacing*1e3)+ " mm")
        reinfDevelopment= self.getBasicAnchorageLength(concrete)
        outputFile.write("  reinf. development L="+ fmt.Lengths.format(reinfDevelopment) + " m ("+ fmt.Diam.format(reinfDevelopment/self.getDiam())+ " diameters).\\\\\n")

class ACIDoubleRebarFamily(rf.DoubleRebarFamily):
    ''' Two reinforcement bars families.'''
    def getCopy(self,barController):
        return ACIDoubleRebarFamily(self.f1, self.f2)
    def getVR(self,concrete,Nd,Md,b,thickness):
        '''Return the shear resistance of the (b x thickness) rectangular section.
        :param concrete: concrete material.
        :param Nd: design axial force.
        :param Md: design bending moment.
        :param b: width of the rectangular section.
        :param thickness: height of the rectangular section.
        '''
        return self.f1.getVR(concrete,Nd,Md,b,thickness)
    def writeRebars(self, outputFile,concrete,AsMin):
        '''Write rebar family data.'''
        self.writeDef(outputFile,concrete)
        outputFile.write("  area: As= "+ fmt.Areas.format(self.getAs()*1e4) + " cm2/m areaMin: " + fmt.Areas.format(AsMin*1e4) + " cm2/m")
        rf.writeF(outputFile,"  F(As)", self.getAs()/AsMin)

class ShearPlane(object):
    ''' Shear plane according to seciont 22.9 of ACI 318-14

    :ivar phi: strength reduction factor
    :ivar concrete: concrete material.
    :ivar reinfSteel: reinforcement steel material.
    :ivar Avf: area of reinforcement crossing the shear plane.
    :ivar alpha: angle between the reinforcement and the shear plane.
    :ivar lambda_c: 1.0 for normal weight concrete
    :ivar monolithic: true if no construction joint in the shear plane.
    :ivar contact_condition: contact condition as in table 22.9.4.2
    '''
    phi= 0.75
    def __init__(self, concrete, steel,avf,alpha= math.pi/2.0, lambda_c= 1.0, monolithic= True, contact_condition= 'a'):
        ''' Constructor.

        :param concrete: concrete material.
        :param steel: reinforcement steel material.
        :param avf: area of reinforcement crossing the shear plane.
        :param alpha: angle between the reinforcement and the shear plane.
        :param lambda_c: 1.0 for normal weight concrete
        :param monolithic: true if no construction joint in the shear plane.
        :param contact_condition: contact condition as in table 22.9.4.2
        '''
        self.concrete= concrete
        self.reinfSteel= steel
        self.Avf= avf
        self.alpha= alpha
        self.lambda_c= lambda_c
        self.monolithic= monolithic
        self.contact_condition= contact_condition

    def getCoefficientOfFriction(self):
        ''' Return the coefficient of friction according to
            table 22.9.4.2 for ACI 318-14.'''
        retval= 1.0
        if(self.contact_condition=='a'): # Concrete placed monolithically
            retval= 1.4
        elif(self.contact_condition=='b'): # Concrete placed against hardened
                                      # concrete that is clean, free of
                                      # laitance, and intentionally roughened
                                      # to a full amplitude of approximately
                                      # 1/4 in.
            retval= 1.0
        elif(self.contact_condition=='c'):  # Concrete placed against hardened
                                       # concrete that is clean, free of
                                       # laitance, but not  intentionally
                                       # roughened
            retval= 0.6
        elif(self.contact_condition=='d'):  # Concrete placed against as-rolled
                                       # structural steel that is clean, free
                                       # of paint, and with shear transferred
                                       # across the contact surface by headed
                                       # studs or by welded deformed bars or
                                       # wires.
            retval= 0.7
        return retval*self.lambda_c
        
    def getMaximumShearTransferStrength(self, Ac):
        ''' Return the maximum shear-transfer strength permitted
            across a shear plane monolithically according to table 22.9.4.4
            of ACI-318-14

            :param Ac: area of the shear plane.
        '''
        fck= -self.concrete.fck
        lim1= 0.2*fck # (a) and (d) in table
        lim2= 1600*ACI_materials.toPascal
        if(not self.monolithic):
            lim2*=0.5 #(c) in table
        retval= min(lim1,lim2)
        if(self.monolithic):
            retval= min(retval,(480.0*ACI_materials.toPascal+0.08*fck))
        return retval*Ac

    def getNominalShearStrength(self):
        ''' Return the nominal shear strength according to section
            22.9.4.3 of ACI 318-14.'''
        # Steel stress limitation according to table 20.2.2.4a
        fy= min(413.6856e6,self.reinfSteel.fyk)
        mu= self.getCoefficientOfFriction()
        return self.Avf*fy*(mu*math.sin(self.alpha)+math.cos(self.alpha))
    
    def getShearCapacityFactor(self, Vd):
        ''' Return the capacity factor for shear according
            to section 16.5.4.4 of ACI 318-14.

        :param Vd: design shear force.
        '''
        Vn= self.getNominalShearStrength()*self.phi
        return Vd/Vn
        

class Corbel(ShearPlane):
    ''' Reinforcing concrete corbel design to ACI 318

    :ivar width: width of corbel.
    :ivar thickness: total thickness of corbel.
    :ivar depth: depth to main reinforcement.
    '''
    def __init__(self, concrete, steel, width, thickness, depth, Asc, Ah, alpha= math.pi/2.0, lambda_c= 1.0, monolithic= True, contact_condition= 'a'):
        ''' Constructor.

        :param concrete: concrete material.
        :param steel: reinforcement steel material.
        :param width: width of corbel.
        :param thickness: total thickness of corbel.
        :param depth: depth to main reinforcement.
        :param Asc: area of primary reinforcement.
        :param Ah: area of shear reinforcement.
        :param alpha: angle between the reinforcement and the shear plane.
        :param lambda_c: 1.0 for normal weight concrete
        :param monolithic: true if no construction joint in the shear plane.
        :param contact_condition: contact condition as in table 22.9.4.2

        '''
        super(Corbel,self).__init__(concrete, steel,Ah,alpha, lambda_c, monolithic, contact_condition)
        self.width= width
        self.thickness= thickness
        self.depth= depth
        self.monolithic= True
        self.Asc= Asc        

    def getNominalVerticalLoadCapacity(self):
        ''' Return the nominal vertical load capacity of the corbel
            according to section 16.5.2.4 of ACI 318-14.
        '''
        Ac= self.width*self.depth
        return self.getMaximumShearTransferStrength(Ac)

    def getBendingMoment(self,Vd,Nd,av):
        ''' Return the bending moment on the corbel.

        :param Vd: design value of vertical load.
        :param Nd: design value of axial load.
        :param av: eccentricity of the vertical load with respect
                   to the corbel shear plane.
        '''
        N= max(Nd,0.2*Vd)
        return Vd*av+N*(self.thickness-self.depth)

    def getAn(self,Nd):
        ''' Return the area or the required reinforcement
            according to section 16.5.4.3 of ACI 318-14.

        :param Nd: design value of axial load.
        '''
        return Nd/self.reinfSteel.fyk/self.phi

    def getRequiredPrimaryReinforcement(self, Vd, Nd, av):
        ''' Return the area or the required reinforcement
            according to sections 16.5.4.3 and 16.5.4.5
            of ACI 318-14.

        :param Vd: design value of vertical load.
        :param Nd: design value of axial load.
        :param av: eccentricity of the vertical load with respect
                   to the corbel shear plane.
        '''
        fy= self.reinfSteel.fyk
        An= Nd/fy/self.phi
        Md= self.getBendingMoment(Vd,Nd,av)
        j= 0.85 # Balanced condition
        Af= Md/(self.phi*fy*j*self.depth)
        return An+Af
        
    def getMinimumPrimaryReinforcement(self, Vd, Nd, av):
        ''' Return the minimum area of the primary reinforcement
            according to section 16.5.5.1 of ACI 318-14.

        :param Vd: design value of vertical load.
        :param Nd: design value of axial load.
        :param av: eccentricity of the vertical load with respect
                   to the corbel shear plane.
        '''
        retval= self.getRequiredPrimaryReinforcement(Vd, Nd, av)
        retval= max(retval,2.0/3.0*self.Avf+self.getAn(Nd))
        Ac= self.width*self.depth
        retval= max(retval,0.04*self.concrete.fck/self.reinfSteel.fyk*Ac)
        return retval

    def getMinimumShearReinforcement(self, Vd, Nd, av):
        ''' Return the minimum area of shear reinforcement
            according to section 16.5.5.2 of ACI 318-14.

        :param Vd: design value of vertical load.
        :param Nd: design value of axial load.
        :param av: eccentricity of the vertical load with respect
                   to the corbel shear plane.
        '''
        Asc= self.getMinimumPrimaryReinforcement(Vd, Nd, av)
        An= self.getAn(Nd)
        return 0.5*(Asc-An)

class AnchorBolt(object):
    ''' Anchor bolt design according to ACI 349-97

    :ivar ca1: distance from the center of an anchor shaft to the edge of 
               concrete in one direction. If shear is applied to anchor, ca1 
               is taken in the direc-tion of the applied shear. If the
               tension isapplied to the anchor, ca1 is the minimum edge 
               distance.
    :ivar ca2: distance from center of an anchor shaft to the edge of concrete
               in the direction orthogonal to ca1.
    :ivar ha: thickness  of  member  in  which  an  anchor  is
              located, measured parallel to anchor axis.

    :ivar concrete: concrete material.
    :ivar steel: anchor steel.
    :ivar diam: anchor diameter.
    :ivar hef: effective embedment depth of anchor.
    :ivar cast_in: true if cast-in anchor false for post-installed
                        anchors.
    '''
    def __init__(self, ca1, ca2, ha, concrete, steel, diam, hef, cast_in= False):
        ''' Constructor.

        :parameter ca1: distance from the center of an anchor shaft to the 
                   edge of concrete in one direction. If shear is applied to 
                   anchor, ca1 is taken in the direc-tion of the applied shear.
                   If the tension isapplied to the anchor, ca1 is the minimum
                   edge distance.
        :parameter ca2: distance from center of an anchor shaft to the edge of
                   concrete in the direction orthogonal to ca1.
        :parameter ha: thickness  of  member  in  which  an  anchor  is
                  located, measured parallel to anchor axis.

        :parameter concrete: concrete material.
        :parameter steel: anchor steel.
        :parameter diam: anchor diameter.
        :parameter hef: effective embedment depth of anchor.
        :parameter cast_in: true if cast-in anchor false for post-installed
                            anchors.
        '''
        self.ca1= ca1
        self.ca2= ca2
        self.ha= ha
        self.concrete= concrete
        self.steel= steel
        self.diam= diam
        self.hef= hef
        self.cast_in= cast_in

    def getAnchorArea(self):
        ''' Return the anchor area.'''
        return math.pi*(self.diam/2.0)**2
    def getNominalSteelStrength(self):
        ''' Return the nominal steel strength of the anchor
            according to section D.3.6.1.'''
        return self.getAnchorArea()*self.steel.fmaxk()

    def getDesignSteelStrength(self):
        ''' Return the design steel strength of the anchor
            according to section D.3.6.1.'''
        phi= 0.8 # partial safety factor for tension
        return phi*self.getNominalSteelStrength()

    def getBasicConcreteBreakoutStrength(self):
        ''' Return the asic concrete breakout strength of a single
            anchor in tension in cracked concrete.'''
        kc= 17.0
        if(self.cast_in):
            kc= 24.0
        hef_in= self.hef/0.0254
        fc_psi= -self.concrete.fck*ACI_materials.fromPascal
        return kc*math.sqrt(fc_psi)*math.pow(hef_in,1.5)*ACI_materials.pound2Newton
    

