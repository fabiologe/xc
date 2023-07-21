# -*- coding: utf-8 -*-
from __future__ import print_function

''' Classes and functions for limit state checking according to Eurocode 2. '''

__author__= "Ana Ortega (AO_O) "
__copyright__= "Copyright 2016, AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "ana.ortega@ciccp.es "

import sys
import math
import scipy.interpolate
from materials import limit_state_checking_base as lscb
from materials.ec2 import EC2_materials
from materials.sections.fiber_section import fiber_sets
from postprocess import control_vars as cv
from misc_utils import log_messages as lmsg
from materials import concrete_base
from materials.sections import rebar_family as rf

class RebarController(lscb.EURebarController):
    '''Control of some parameters as development length 
       minimum reinforcement and so on.

    :ivar eta1: coefficient related to the quality of the bond condition 
                 and the position of the bar during concreting.
                 eta1= 1,0 when 'good' conditions are obtained and
                 eta1= 0,7 for all other cases.
    '''

    def __init__(self, concreteCover= 35e-3, spacing= 150e-3, eta1= 0.7, compression= True, alpha_1= 1.0, alpha_3= 1.0, alpha_4= 1.0, alpha_5= 1.0):
        '''Constructor.

        :param concreteCover: the distance from center of a bar or wire to 
                             nearest concrete surface.
        :param spacing: center-to-center spacing of bars or wires being 
                       developed, in.
        :param eta1: coefficient related to the quality of the bond condition 
                     and the position of the bar during concreting.
                     eta1= 1,0 when 'good' conditions are obtained and
                     eta1= 0,7 for all other cases.
        :param compression: true if reinforcement is compressed.
        :param alpha_1: effect of the form of the bars assuming adequate cover.
        :param alpha_3: effect of confinement by transverse reinforcement.
        :param alpha_4: influence of one or more welded transverse bars along 
                        the design anchorage length.
        :param alpha_5: effect of the pressure transverse to the plane of 
                        splitting along the design anchorage length.
        '''
        super(RebarController,self).__init__(concreteCover= concreteCover, spacing= spacing, compression= compression, alpha_1= alpha_1, alpha_3= alpha_3, alpha_4= alpha_4, alpha_5= alpha_5)
        self.eta1= eta1

    def getBasicAnchorageLength(self, concrete, rebarDiameter, steel, steelEfficiency= 1.0):
        '''Returns basic required anchorage length in tension according to 
           clause 8.4.3 of EC2:2004 (expression 8.3).

        :param concrete: concrete material.
        :param rebarDiameter: nominal diameter of the bar.
        :param steel: reinforcement steel.
        :param steelEfficiency: working stress of the reinforcement that it is 
                                intended to anchor, on the most unfavourable 
                                load hypothesis, in the section from which 
                                the anchorage length will be determined divided
                                by the steel design yield 
                                strength: (sigma_sd/fyd).
        '''
        return steel.getBasicAnchorageLength(concrete= concrete, rebarDiameter= rebarDiameter, eta1= self.eta1, steelEfficiency= steelEfficiency)

    def getConcreteMinimumCoverEffect(self, rebarDiameter, barShape= 'bent', lateralConcreteCover= None):
        ''' Return the value of the alpha_2 factor that introduces the effect
            of concrete minimum cover according to figure 8.3 and table 8.2
            of EC2:2004.

        :param rebarDiameter: nominal diameter of the bar.
        :param barShape: 'straight' or 'bent' or 'looped'.
        :param lateralConcreteCover: lateral concrete cover (c1 in figure 8.3
                                     of EC2:2004). If None make it equal to
                                     the regular concrete cover.
        '''
        return super(RebarController, self).getConcreteMinimumCoverEffect(rebarDiameter= rebarDiameter, barShape= barShape, lateralConcreteCover= lateralConcreteCover)
    
    def getDesignAnchorageLength(self, concrete, rebarDiameter, steel, steelEfficiency= 1.0, barShape= 'bent', lateralConcreteCover= None):
        '''Returns design  anchorage length according to clause 8.4.4
           of EC2:2004 (expression 8.4).

        :param concrete: concrete material.
        :param rebarDiameter: nominal diameter of the bar.
        :param steel: reinforcement steel.
        :param steelEfficiency: working stress of the reinforcement that it is 
                                intended to anchor, on the most unfavourable 
                                load hypothesis, in the section from which 
                                the anchorage length will be determined divided
                                by the steel design yield 
                                strength: (sigma_sd/fyd).
        :param barShape: 'straight' or 'bent' or 'looped'.
        :param lateralConcreteCover: lateral concrete cover (c1 in figure 8.3
                                     of EC2:2004). If None make it equal to
                                     the regular concrete cover.
        '''
        alpha_2= self.getConcreteMinimumCoverEffect(rebarDiameter, barShape= barShape, lateralConcreteCover= lateralConcreteCover)
        return steel.getDesignAnchorageLength(concrete= concrete, rebarDiameter= rebarDiameter, eta1= self.eta1, steelEfficiency= steelEfficiency, compression= self.compression, alpha_1= self.alpha_1, alpha_2= alpha_2, alpha_3= self.alpha_3, alpha_4= self.alpha_4, alpha_5= self.alpha_5)

    def getLapLength(self ,concrete, rebarDiameter, steel, steelEfficiency= 1.0, ratioOfOverlapedTensionBars= 1.0, lateralConcreteCover= None):
        '''Returns the value of the design lap length according to clause
           8.7.3 of EC2:2004 (expression 8.10).

        :param concrete: concrete material.
        :param rebarDiameter: nominal diameter of bar, wire, or prestressing strand.
        :param steel: reinforcement steel.
        :param distBetweenNearestSplices: distance between the nearest splices
                                          according to figure 69.5.2.2.a.
        :param steelEfficiency: working stress of the reinforcement that it is 
                                intended to anchor, on the most unfavourable 
                                load hypothesis, in the section from which 
                                the anchorage length will be determined divided
                                by the steel design yield 
                                strength: (sigma_sd/fyd).
        :param ratioOfOverlapedTensionBars: ratio of overlapped tension bars 
                                            in relation to the total steel
                                            section.
        :param lateralConcreteCover: lateral concrete cover (c1 in figure 8.3
                                     of EC2:2004). If None make it equal to
                                     the regular concrete cover.
        '''
        alpha_2= self.getConcreteMinimumCoverEffect(rebarDiameter= rebarDiameter, barShape= 'straight', lateralConcreteCover= lateralConcreteCover)
        return steel.getLapLength(concrete= concrete, rebarDiameter= rebarDiameter, eta1= self.eta1, steelEfficiency= steelEfficiency, ratioOfOverlapedTensionBars= ratioOfOverlapedTensionBars, alpha_1= self.alpha_1, alpha_2= alpha_2, alpha_3= self.alpha_3, alpha_5= self.alpha_5)

# EC2:2004 part 1-1. Clause 7.3.3. Control of cracking without direct calculation.

table7_2NSteelStresses= [160e6, 200e6, 240e6, 280e6, 320e6, 360e6, 400e6, 450e6]
table7_2NMaxBarSize04mm= [40e-3, 32e-3, 20e-3, 16e-3, 12e-3, 10e-3, 8e-3, 6e-3]
table7_2NColumn04mm= scipy.interpolate.interp1d(table7_2NSteelStresses, table7_2NMaxBarSize04mm, fill_value='extrapolate')
table7_2NMaxBarSize03mm= [32e-3, 25e-3, 16e-3, 12e-3, 10e-3, 8e-3, 6e-3, 5e-3]
table7_2NColumn03mm= scipy.interpolate.interp1d(table7_2NSteelStresses, table7_2NMaxBarSize03mm, fill_value='extrapolate')
table7_2NMaxBarSize02mm= [25e-3, 16e-3, 12e-3, 8e-3, 6e-3, 5e-3, 4e-3, 1e-6]
table7_2NColumn02mm= scipy.interpolate.interp1d(table7_2NSteelStresses, table7_2NMaxBarSize02mm, fill_value='extrapolate')

def getMaximumBarDiameterForCrackControl(steelStress, wk= 0.3e-3):
    ''' Return the maximum diameter of the bar according to table 7.2N of
        of EC2:2004 part 1-1. (clause 7.3.3).

    :param steelStress: maximum stress permitted in the reinforcement
                        immediately after formation of the crack.
    :param wk: crack width (m)
    '''
    if (steelStress<table7_2NSteelStresses[0]) or (steelStress>table7_2NSteelStresses[-1]):
        methodName= sys._getframe(0).f_code.co_name
        lmsg.warning(methodName+'; maximum stress permitted in the reinforcement immediately after formation of the crack. steelStress= '+str(steelStress/1e6)+' MPa. Out of range ('+str(table7_2NSteelStresses[0]/1e6)+','+str(table7_2NSteelStresses[-1]/1e6)+') MPa. Value computed by EXTRAPOLATION.')
    if (wk<=0.4e-3) and (wk>0.3e-3): # 0.4 and 0.3 columns.
        diam04= float(table7_2NColumn04mm(steelStress))
        diam03= float(table7_2NColumn03mm(steelStress))
        retval= (diam04-diam03)*1e4*(wk-0.3e-3)+diam03
    elif (wk<=0.3e-3) and (wk>=0.2e-3): # 0.3 and 0.2 columns.
        diam03= float(table7_2NColumn03mm(steelStress))
        diam02= float(table7_2NColumn02mm(steelStress))
        retval= (diam03-diam02)*1e4*(wk-0.2e-3)+diam02
    else:
        retval= None
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; value of crack width: wk= '+str(wk*1e3)+' mm. Out of range (0.2e-3,0.4e-3) meters.')
    return retval

table7_3NSteelStresses= [160e6, 200e6, 240e6, 280e6, 320e6, 360e6]
table7_3NMaxBarSpacing04mm= [0.30, 0.30, 0.25, 0.2, 0.15, 0.1]
table7_3NColumn04mm= scipy.interpolate.interp1d(table7_3NSteelStresses, table7_3NMaxBarSpacing04mm, fill_value='extrapolate')
table7_3NMaxBarSpacing03mm= [0.30, 0.25, 0.20, 0.15, 0.10, 0.05]
table7_3NColumn03mm= scipy.interpolate.interp1d(table7_3NSteelStresses, table7_3NMaxBarSpacing03mm, fill_value='extrapolate')
table7_3NMaxBarSpacing02mm= [0.20, 0.15, 0.10, 0.05, 1e-3, 1e-4]
table7_3NColumn02mm= scipy.interpolate.interp1d(table7_3NSteelStresses, table7_3NMaxBarSpacing02mm, fill_value='extrapolate')

def getMaximumBarSpacingForCrackControl(steelStress, wk= 0.3e-3):
    ''' Return the maximum bar spacing according to table 7.3N of
        of EC2:2004 part 1-1. (clause 7.3.3).

    :param steelStress: maximum stress permitted in the reinforcement
                        immediately after formation of the crack.
    :param wk: crack width (m)
    '''
    if (steelStress<table7_3NSteelStresses[0]) or (steelStress>table7_3NSteelStresses[-1]):
        methodName= sys._getframe(0).f_code.co_name
        lmsg.warning(methodName+'; maximum stress permitted in the reinforcement immediately after formation of the crack. steelStress= '+str(steelStress/1e6)+' MPa. Out of range ('+str(table7_3NSteelStresses[0]/1e6)+','+str(table7_3NSteelStresses[-1]/1e6)+') MPa. Value computed by EXTRAPOLATION.')
    if (wk<=0.4e-3) and (wk>0.3e-3): # 0.4 and 0.3 columns.
        spacing04= float(table7_3NColumn04mm(steelStress))
        spacing03= float(table7_3NColumn03mm(steelStress))
        retval= (spacing04-spacing03)*1e4*(wk-0.3e-3)+spacing03
    elif (wk<=0.3e-3) and (wk>=0.2e-3): # 0.3 and 0.2 columns.
        spacing03= float(table7_3NColumn03mm(steelStress))
        spacing02= float(table7_3NColumn02mm(steelStress))
        retval= (spacing03-spacing02)*1e4*(wk-0.2e-3)+spacing02
    else:
        retval= None
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; value of crack width: wk= '+str(wk*1e3)+' mm. Out of range (0.2e-3,0.4e-3) meters.')
    return retval
    
#These functions  should disappear               
def h_c_eff(depth_tot,depht_eff,depth_neutral_axis):
    '''
    Returns the depth of the effective area of concrete in tension surrounding
    the reinforcement or prestressing tendons, according to EC2

    :param depth_tot: overall depth of the cross-section [h]
    :param depht_eff: effective depth of the cross-section [d]
    :param depth_neutral_axis: depht of the neutral axis[x]
    '''
    h,d,x=depth_tot,depht_eff,depth_neutral_axis
    retval=min(2.5*(h-d),(h-x)/3.,h/2.)
    return retval

def ro_eff(A_s, width, h_c_eff):
    '''
    Returns the effective reinforcement ratio [A_s/A_ceff] depth of the 
    effective area of concrete in tension surrounding
    the reinforcement or prestressing tendons, according to EC2

    :param A_s: area of reinforcment steel
    :param width: width of the RC cross-section
    :param ,h_c_eff: depth of the effective area of concrete in 
    tension surrounding the reinforcement or prestressing tendons
    '''
    retval=A_s/width/h_c_eff
    return retval

def s_r_max(k1,k2,k3,k4,cover,fiReinf,ro_eff):
    ''' Returns the maximum crack spacing, according to expresion 7.11 of
    clause 7.34 of EC2:2004
 
    :param k1: coefficient which takes account of the bond properties
               of the bonded reinforcement:

               - =0.8 for high bond bars
               - =1.6 for bars with an effectively plain surface (e.g. 
                      prestressing tendons)

    :param k2: coefficient that takes account of the distribution of strain:

               - =0.5 for bending
               - =1.0 for pure tension
               - for cases of eccentric tension or for local areas, intermediate values of k2 should be used (see clause 7.3.4 EC2)
    :param k3: recommended k3=3.4
    :param k4: recommended k4=0.425 
    :param cover: cover of the longitudinal reinforcement
    :param fiReinf: bar diameter. Where a mixture of bar diameters is used in a
                    section, an equivalent diameter is used (see clause 7.3.4 EC2)
    :param ro_eff: effective reinforcement ratio
    '''
    retval= k3*cover + k1*k2*k4*fiReinf/ro_eff
    return retval

class CrackController(lscb.LimitStateControllerBase):
    '''Definition of variables involved in the verification of the cracking
    serviceability limit state according to EC2.

    :ivar k1: coefficient that takes account of the bound properties of the 
          bonded reinforcement. k1=0.8 for high bond bars, k1=1.0 for bars with
          effectively plain surface (e.g. prestressing tendons). Defaults to 0.8
    :ivar k3: defaults to the value recommended by EC2 and in EHE k3=3.4
    :ivar k4: defaults to the value recommended by EC2 and EHE k4=0.425
    '''
    def __init__(self, limitStateLabel):
        ''' Constructor.
        
        :param limitStateLabel: label that identifies the limit state.
        :param k1: coefficient which takes account of the bond properties
                   of the bonded reinforcement:

               - = 0.8 for high bond bars
               - = 1.6 for bars with an effectively plain surface (e.g. 
                      prestressing tendons)
        '''
        super(CrackController,self).__init__(limitStateLabel,fakeSection= False)
        self.k1= 0.8
        self.k3= 3.4
        self.k4= 0.425

    def EC2_k2(self, eps1, eps2):
        '''Return the coefficient k2 involved in the calculation of the mean 
        crack distance according to EC2. This coefficient represents the 
        effect of the tension diagram in the section.

        :param eps1: maximum deformation calculated in the section at the 
                     limits of the tension zone
        :param eps2: minimum deformation calculated in the section at the
                     limits of the tension zone
        '''
        k2= (eps1+eps2)/(2.0*eps1)
        return k2

    def EC2_hceff(self, h, d,x):
        '''Return the maximum height to be considered in the calculation of the 
        concrete effective area in tension. See paragraph (3) of clause 7.3.2 
        of EC2.
     
        :param width: section width
        :param h: lever arm
        :param d: effective depth of the cross-section 
        :param x: depth of the neutral fiber.

        '''
        hceff= min(2.5*(h-d),abs(h+x)/3.,h/2.)
        return hceff

    def s_r_max(self, k2, cover, reinfPhi, spacing , ro_eff, h= None, x= None):
        ''' Returns the maximum crack spacing, according to expressions 7.11 
            and 7.14 of clause 7.3.4 of EC2:2004 part 1.

        :param k2: coefficient that takes account of the distribution of strain:

                   - =0.5 for bending
                   - =1.0 for pure tension
                   - for cases of eccentric tension or for local areas, 
                     intermediate values of k2 should be used 
                     (see clause 7.3.4 EC2)
        :param cover: cover of the longitudinal reinforcement
        :param reinfPhi: bar diameter. Where a mixture of bar diameters is used
                        in a section, an equivalent diameter is used (see 
                        clause 7.3.4 EC2).
        :param spacing: spacing of the bonded reinforcement.
        :param ro_eff: effective reinforcement ratio.
        :param h: overall depth of the section.
        :param x: depth of the neutral axis.
        '''
        influenceWidth= 5.0*(cover+reinfPhi/2.0)
        if(reinfPhi==0.0) or (spacing>influenceWidth):
            retval= 1.3*(h-x) # Expression 7.14
        else:
            retval= self.k3*cover + self.k1*k2*self.k4*reinfPhi/ro_eff
        return retval

    def meanStrainDifference(self, sigma_s, steel, concrete, ro_eff, shortTermLoading= False):
        ''' Returns the mean strain difference according to expression 7.9 of
            clause 7.3.4 of EC2:2004.

        :param sigma_s: stress in the tension reinforcement assuming a cracked
                        section. For pretensioned members, as may be replaced 
                         by Delta(sigma_p) the stress variation in prestressing
                         tendons from the state of zero strain of the concrete
                         at the same level.
        :param steel: steel type of the reinforcement.
        :param As: steel reinforcement area 
        :param concrete: concrete of the section.
        :param ro_eff: effective reinforcement ratio computed according to
                       expression 7.10 of EC2:2004 part 1.
        :param shortTermLoading: if true, consider short therm loading 
                                 (k_t= 0.6), otherwise consider long term 
                                 loading (k_t= 0.4).
        '''
        kt= 0.4
        if(shortTermLoading):
            kt= 0.6
        fct_eff= concrete.fctm() # mean value of the tensile strength of the
                                 # concrete effective at the time when the
                                 # cracks may first be expected to occur.
        Es= steel.Es # steel elastic modulus.
        alpha_e= Es/concrete.Ecm() # ratio between elastic moduli.
        retval= (sigma_s - kt*fct_eff/ro_eff*(1+alpha_e*ro_eff))/Es
        retval= max(retval, 0.6*sigma_s/Es)
        return retval

    def computeWk(self, sigma_s, steel, concrete, ro_eff, k2, cover, reinfPhi, spacing, h= None, x= None, shortTermLoading= False):
        '''Computes the characteristic value of the crack width according to the
           expression 7.8 of EC2:2004 part 1.

        :param sigma_s: stress in the tension reinforcement assuming a cracked
                        section. For pretensioned members, as may be replaced 
                         by Delta(sigma_p) the stress variation in prestressing
                         tendons from the state of zero strain of the concrete
                         at the same level.
        :param steel: steel type of the reinforcement.
        :param As: steel reinforcement area 
        :param concrete: concrete of the section.
        :param ro_eff: effective reinforcement ratio computed according to
                       expression 7.10 of EC2:2004 part 1.
        :param k2: coefficient that takes account of the distribution of strain:

                   - =0.5 for bending
                   - =1.0 for pure tension
                   - for cases of eccentric tension or for local areas, 
                     intermediate values of k2 should be used 
                     (see clause 7.3.4 EC2)
        :param cover: cover of the longitudinal reinforcement
        :param reinfPhi: bar diameter. Where a mixture of bar diameters is used
                        in a section, an equivalent diameter is used (see 
                        clause 7.3.4 EC2).
        :param spacing: spacing of the bonded reinforcement.
        :param h: overall depth of the section.
        :param x: depth of the neutral axis.
        :param shortTermLoading: if true, consider short therm loading 
                                 (k_t= 0.6), otherwise consider long term 
                                 loading (k_t= 0.4).
        '''
        s_r_max= self.s_r_max(k2= k2, cover= cover, reinfPhi= reinfPhi, spacing= spacing, ro_eff= ro_eff)
        meanStrainDifference= self.meanStrainDifference(sigma_s= sigma_s, steel= steel, concrete= concrete, ro_eff= ro_eff, shortTermLoading= shortTermLoading)
        return meanStrainDifference*s_r_max

class CrackStraightController(CrackController):
    '''Definition of variables involved in the verification of the cracking
    serviceability limit state according to EC2 when considering a concrete
    stress-strain diagram that takes account of the effects of tension 
    stiffening.

    :ivar k1: coefficient that takes account of the bound properties of the 
          bonded reinforcement. k1=0.8 for high bond bars, k1=1.0 for bars with
          effectively plain surface (e.g. prestressing tendons). Defaults to 0.8
    :ivar k3: defaults to the value recommended by EC2 and in EHE k3=3.4
    :ivar k4: defaults to the value recommended by EC2 and EHE k4=0.425
    '''
    ControlVars= cv.RCCrackStraightControlVars
    def __init__(self, limitStateLabel):
        ''' Constructor.
        
        :param limitStateLabel: label that identifies the limit state.
        '''
        super(CrackStraightController,self).__init__(limitStateLabel)

    def check(self,elements,nmbComb):
        ''' For each element in the set 'elememts' passed as first parameter and 
        the resulting internal forces for the load combination 'nmbComb'  
        passed as second parameter, this method calculates all the variables 
        involved in the crack-SLS checking and obtains the crack width.
        In the case that the calculated crack width is greater than the 
        biggest obtained for the element in previous load combinations, this value
        is saved in the element results record. 

        Elements processed are those belonging to the phantom model, that is to 
        say, of type xc.ZeroLengthSection. As we have defined the variable 
        fakeSection as False, a reinfoced concrete fiber section is generated
        for each of these elements. 
        '''
        if(self.verbose):
          lmsg.log('Postprocessing combination: '+nmbComb)
        for e in elements:
            Aceff=0  #initial  value
            R=e.getResistingForce()
            sct=e.getSection()
            sctCrkProp=lscb.fibSectLSProperties(sct)
            sctCrkProp.setupStrghCrackDist()
            hceff=self.EC2_hceff(sctCrkProp.h,sctCrkProp.d,sctCrkProp.x)
            # Acgross=sct.getGrossEffectiveConcreteArea(hceff)
            Aceff=sct.getNetEffectiveConcreteArea(hceff,'tensSetFb',15.0)
            concrete=EC2_materials.concrOfName[sctCrkProp.concrName]
            rfSteel=EC2_materials.steelOfName[sctCrkProp.rsteelName]
            k2= self.EC2_k2(sctCrkProp.eps1, sctCrkProp.eps2)
            # print('elem= ',e.tag, ' Aceff= ',Aceff)
            if(Aceff<=0):
                s_rmax=0
            else:
                ro_s_eff=sctCrkProp.As/Aceff #effective ratio of reinforcement
                s_rmax=self.k3*sctCrkProp.cover+self.k1*k2*self.k4*sctCrkProp.fiEqu/ro_s_eff
                #Parameters for tension stiffening of concrete
                paramTS= concrete_base.paramTensStiffness(concrMat=concrete,reinfMat=rfSteel,reinfRatio=ro_s_eff,diagType='K')
                concrete.tensionStiffparam=paramTS #parameters for tension
                #stiffening are assigned to concrete
                ftdiag=concrete.tensionStiffparam.pointOnsetCracking()['ft']                    #stress at the adopted point for concrete onset cracking
                Etsdiag=abs(concrete.tensionStiffparam.regresLine()['slope'])
                fiber_sets.redefTensStiffConcr(setOfTenStffConcrFibSect=sctCrkProp.setsRC.concrFibers,ft=ftdiag,Ets=Etsdiag)
            e.setProp('ResF',R)   #vector resisting force
            e.setProp('s_rmax',s_rmax)  #maximum crack distance
        self.preprocessor.getDomain.revertToStart()
        self.solutionProcedure.solveComb(nmbComb)
        for e in elements:
            sct=e.getSection()
            rfset=sct.getFiberSets()['reinfSetFb']
            eps_sm=rfset.getStrainMax()
            srmax=e.getProp('s_rmax')
#            eps_cm=concrete.fctm()/2.0/concrete.E0()
#            wk=srmax*(eps_sm-eps_cm)
            wk=srmax*eps_sm
#            print(' eps_sm= ',eps_sm, ' srmax= ', srmax, ' wk= ',wk)
#            print('e.getProp(self.limitStateLabel).wk', e.getProp(self.limitStateLabel).wk)
            if (wk>e.getProp(self.limitStateLabel).wk):
                R=e.getProp('ResF')
                e.setProp(self.limitStateLabel, self.ControlVars(idSection=e.getProp('idSection'),combName=nmbComb,N=-R[0],My=-R[4],Mz=-R[5],s_rmax=srmax,eps_sm=eps_sm,wk=wk))
                
###################
# Rebar families. #
###################

class EC2RebarFamily(rf.RebarFamily):
    ''' Family or reinforcement bars with checking according to EC2.

       :ivar pos: reinforcement position according to clause 66.5.1
                  of EC2.
    '''
    def __init__(self,steel, diam, spacing, concreteCover, pos= 'II'):
        ''' Constructor.

        :param steel: reinforcing steel material.
        :param diam: diameter of the bars.
        :param spacing: spacing of the bars.
        :param concreteCover: concrete cover of the bars.
        :param pos: reinforcement position according to clause 66.5.1
                   of EC2.
        '''
        super(EC2RebarFamily,self).__init__(steel,diam,spacing,concreteCover)
        self.pos= pos

    def getCopy(self):
        return EC2RebarFamily(steel= self.steel, diam= self.diam, spacing= self.spacing, concreteCover= self.concreteCover, pos= self.pos)

def define_rebar_families(steel, cover, diameters= [8e-3, 10e-3, 12e-3, 14e-3, 16e-3, 20e-3, 25e-3, 32e-3], spacings= [0.1, 0.15, 0.2]):
    ''' Creates a dictionary with predefined rebar families.

    :param steel: rebars steel material.
    :param cover: concrete cover for the families.
    :param diameters: list of diameters.
    :param spacings: list of spacings between bars. 
    '''
    retval= dict()
    for diameter in diameters:
        diameterText= str(int(diameter*1e3))
        for spacing in spacings:
            spacingText= str(int(spacing*1e2))
            familyName= 'A'+diameterText+'_'+spacingText
            retval[familyName]= EC2RebarFamily(steel= steel, diam= diameter, spacing= spacing, concreteCover= cover)
    return retval


# EC2:2004 6.2 Shear

# EC2:2004 6.2.2 Members not requiring design shear reinforcement
def getShearResistanceCrackedNoShearReinf(concrete, NEd, Ac, Asl, bw, d, nationalAnnex= None):
    ''' Return the design value of the shear resistance VRdc for cracked 
        sections subjected to bending moment, according to expressions 6.2.a 
        and 6.2.b of EC2:2004.

    :param concrete: concrete material.
    :param NEd: axial force in the cross-section due to loading or prestressing.
    :param Ac: area of concrete cross-section. 
    :param Asl: area of the tensile reinforcement, which extends beyond
                the section considered (see clause 6.2.2 of EC2:2004).
    :param bw: smallest width of the cross-section in the tensile area.
    :param d: effective depth of the cross-section.
    :param nationalAnnex: identifier of the national annex.
    '''
    k= min(1.0+math.sqrt(0.2/d),2) # d in meters.
    ro_l= min(Asl/bw/d,.02)
    fcdMPa= -concrete.fcd()/1e6 # design value of concrete compressive strength (MPa).
    sigma_cp= min(-NEd/Ac/1e6,.2*fcdMPa)
    gamma_c= concrete.gmmC
    CRdc= 0.18/gamma_c # Recommended value and Spanish national annex.
    k1= 0.15
    fckMPa= -concrete.fck/1e6 # concrete characteristic compressive strength (MPa).
    if(nationalAnnex=='Spain'):
        v_min= 0.075/gamma_c*math.pow(k,1.5)*math.sqrt(min(fckMPa,60))
    else:
        v_min= 0.035*math.pow(k,1.5)*math.sqrt(fckMPa)
    
    VRdc_62a= (CRdc*k*math.pow(100.0*ro_l*fckMPa,1/3.0)+k1*sigma_cp)*bw*d*1e6
    VRdc_62b= (v_min+k1*sigma_cp)*bw*d*1e6
    return max(VRdc_62a, VRdc_62b)
    
def getShearResistanceNonCrackedNoShearReinf(concrete, I, S, NEd, Ac, bw, alpha_l= 1.0):
    ''' Return the design value of the shear resistance VRdc for non-cracked 
        sections subjected to bending moment, according to expression 6.4 of
        EC2:2004.

    :param concrete: concrete material.
    :param I: second moment of area.
    :param S: first moment of area above and about the centroidal axis.
    :param NEd: axial force in the cross-section due to loading or prestressing.
    :param Ac: area of concrete cross-section. 
    :param bw: smallest width of the cross-section in the tensile area.
    :param alpha_l: see expression 6.4 in EC2:2004.
    '''
    sigma_cp= -NEd/Ac/1e6 # concrete compressive stress at the centroidal
                          # axis due to axial loading and/or prestressing
    fctdMPa= concrete.fctd()/1e6 #design tensile strength (MPa)
    return (I/S*bw)*math.sqrt(fctdMPa**2+alpha_l*sigma_cp*fctdMPa)*1e6

# EC2:2004 6.2.3 Members requiring design shear reinforcement.
def getWebStrutAngleForSimultaneousCollapse(concrete, bw, s, Asw, shearReinfSteel, shearReinfAngle= math.pi/2.0, nationalAnnex= None):
    ''' Return the web strut angle that makes web concrete collapse at the same
        time that the shear reinforcement (V_{Rd,s}= V_{Rd,max})

    :param concrete: concrete material.
    :param bw: smallest width of the cross-section in the tensile area.
    :param s: spacing of the stirrups.
    :param Asw: cross-sectional area of the shear reinforcement.
    :param shearReinfSteel: reinforcing steel material.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    # nu1: strength reduction factor for concrete cracked in shear
    nu= concrete.getShearStrengthReductionFactor(nationalAnnex)
    fcd= -concrete.fcd() # design value of concrete compressive strength (MPa).
    fywd= shearReinfSteel.fyd() # design yield strength of the shear reinforcement
    ratio= (bw*s*nu*fcd)/(Asw*fywd*math.sin(shearReinfAngle))
    if(ratio<1):
        methodName= sys._getframe(0).f_code.co_name
        lmsg.error(methodName+'; Warning, cross-sectional area of the shear reinforcement too big: '+str(Asw*1e6)+' mm2. Returning math.pi/4.0.')
        ratio= 2.0
    cotgTheta= math.sqrt(ratio-1)
    return math.atan(1.0/cotgTheta)   

def getMaximumShearWebStrutCrushing(concrete, NEd, Ac, bw, z, shearReinfAngle= math.pi/2.0, webStrutAngle= math.pi/4.0, nationalAnnex= None):
    ''' Return the maximum shear force due to diagonal compression in the web
        (strut crushing) according to expression 6.14 and 6.9 of EC2:2004.

    :param concrete: concrete material.
    :param NEd: axial force in the cross-section due to loading or prestressing.
    :param Ac: area of concrete cross-section. 
    :param bw: smallest width of the cross-section in the tensile area.
    :param z: internal lever arm.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param webStrutAngle: (theta) angle between the concrete compression strut and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    # alpha_cw: coefficient taking account of the state of the stress in the compression chord
    alpha_cw= concrete.getAlphaCw(NEd, Ac, nationalAnnex)
    # nu1: strength reduction factor for concrete cracked in shear
    nu1= concrete.getShearStrengthReductionFactor(nationalAnnex)
    fcd= -concrete.fcd() # design value of concrete compressive strength (MPa).
    webStrutAngle= checkWebStrutAngleLimits(webStrutAngle, nationalAnnex)
    cotgTheta= 1/math.tan(webStrutAngle)
    cotgAlpha= 1/math.tan(shearReinfAngle)
    return alpha_cw*bw*z*nu1*fcd*(cotgTheta+cotgAlpha)/(1+cotgTheta**2)

def getMaximumEffectiveShearReinforcement(concrete, NEd, Ac, bw, s, shearReinfSteel, shearReinfAngle= math.pi/2.0, nationalAnnex= None):
    ''' Return the maximum effective shear reinforcement according to expression
        6.15 and 6.12 of EC2:2004.

    :param concrete: concrete material.
    :param NEd: axial force in the cross-section due to loading or prestressing.
    :param Ac: area of concrete cross-section. 
    :param bw: smallest width of the cross-section in the tensile area.
    :param s: spacing of the stirrups.
    :param Asw: cross-sectional area of the shear reinforcement.
    :param shearReinfSteel: reinforcing steel material.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    # alpha_cw: coefficient taking account of the state of the stress in the compression chord
    alpha_cw= concrete.getAlphaCw(NEd, Ac, nationalAnnex)
    # nu1: strength reduction factor for concrete cracked in shear
    nu1= concrete.getShearStrengthReductionFactor(nationalAnnex)
    fcd= -concrete.fcd() # design value of concrete compressive strength (MPa).
    fywd= shearReinfSteel.fyd()
    return 0.5*alpha_cw*nu1*fcd/fywd*bw*s

def getWebStrutAngleLimits(nationalAnnex= None):
    ''' Return the limits specified in the expression 6.7N of EC2:2004
        for the web strut angle.

    :param nationalAnnex: identifier of the national annex.
    '''
    if(nationalAnnex=='Spain'): #EN 1992-1-1:2004 Apartado 6.2.3 (2)
        limSup= math.atan(1/0.5)
        limInf= math.atan(1/2.0)
    else:
        limSup= math.pi/4.0 # math.atan(1.0)
        limInf= math.atan(1/2.5)
    return limInf, limSup

def checkWebStrutAngleLimits(webStrutAngle, nationalAnnex= None):
    ''' Check that the strut angle is inside the limits specified
        in the expression 6.7N of EC2:2004. Otherwise, issue a
        warning and return a suitable strut angle.

    :param webStrutAngle: (theta) angle between the concrete compression web strut and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    retval= webStrutAngle
    limInf, limSup= getWebStrutAngleLimits(nationalAnnex)
    if((webStrutAngle<limInf) or (webStrutAngle>limSup)): # eq 6.7N
        methodName= sys._getframe(0).f_code.co_name
        errString= methodName+'; strut angle: '+str(math.degrees(webStrutAngle))+' out of range: ['+str(math.degrees(limInf))+','+str(math.degrees(limSup))+']'
        if(webStrutAngle<limInf):
            retval= limInf
        elif(webStrutAngle>limSup):
            retval= limSup
        errString+= ' using '+str(math.degrees(retval))
        lmsg.warning(errString)
    return retval

def getShearResistanceShearReinf(concrete, NEd, Ac, bw, Asw, s, z, shearReinfSteel, shearReinfAngle= math.pi/2.0, webStrutAngle= math.pi/4.0, nationalAnnex= None):
    ''' Return the design value of the shear resistance VRds for shear 
        reinforced members according to expressions 6.7N, 6.13 and 6.14 of
        EC2:2004.

    :param concrete: concrete material.
    :param NEd: axial force in the cross-section due to loading or prestressing.
    :param Ac: area of concrete cross-section. 
    :param bw: smallest width of the cross-section in the tensile area.
    :param Asw: cross-sectional area of the shear reinforcement.
    :param s: spacing of the stirrups.
    :param z: inner lever arm, for a member with constant depth, corresponding to the bending moment in the element under consideration.
    :param shearReinfSteel: reinforcing steel material.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param webStrutAngle: (theta) angle between the concrete compression web strut and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    webStrutAngle= checkWebStrutAngleLimits(webStrutAngle, nationalAnnex)
    cotgTheta= 1/math.tan(webStrutAngle)
    cotgAlpha= 1/math.tan(shearReinfAngle)
    sinAlpha= math.sin(shearReinfAngle)
    fywd= shearReinfSteel.fyd()
    cotgThetaPluscotgAlpha= cotgTheta+cotgAlpha
    VRds= Asw/s*z*fywd*cotgThetaPluscotgAlpha*sinAlpha
    # nu1: strength reduction factor for concrete cracked in shear
    nu1= concrete.getShearStrengthReductionFactor(nationalAnnex)
    
    # if(sigma_reinf<0.8*shearReinfSteel.fyk):
    #     if(fckMPa<=60):
    #         nu1= 0.6
    #     else:
    #         nu1= max(0.9-fckMPa/200,0.5)
    
    # alpha_cw: coefficient taking account of the state of the stress in the compression chord
    alpha_cw= concrete.getAlphaCw(NEd, Ac, nationalAnnex)
    fcdMPa= -concrete.fcd()/1e6 # design value of concrete compressive strength (MPa).
    VRdmax= alpha_cw*bw*z*nu1*fcdMPa*cotgThetaPluscotgAlpha/(1+cotgTheta**2)*1e6
    return min(VRds, VRdmax)

def getMinShearReinforcementArea(concrete, shearReinfSteel, s, bw, shearReinfAngle= math.pi/2.0, nationalAnnex= None):
    ''' Return the cross-sectional area of the shear reinforcement 
        according to expression 9.4 of EC2:2004.

    :param concrete: concrete material.
    :param shearReinfSteel: reinforcing steel material.
    :param s: spacing of the stirrups.
    :param bw: smallest width of the cross-section in the tensile area.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param nationalAnnex: identifier of the national annex.
    '''
    # minimum shear reinforcement ratio
    ro_w= concrete.getMinShearReinfRatio(shearReinfSteel, nationalAnnex)
    return ro_w*s*bw*math.sin(shearReinfAngle)

def getAdditionalTensileForceMainReinf(VEd, shearReinfAngle= math.pi/2.0, webStrutAngle= math.pi/4.0):
    ''' Return the additional tensile force, in the longitudinal reinforcement
        due to shear VEd according to expression 6.18 of EC2:2004.

    :param VEd: design value of the applied shear force.
    :param shearReinfAngle: (alpha) angle between shear reinforcement and the beam axis perpendicular to the shear force.
    :param webStrutAngle: (theta) angle between the concrete web compression strut and the beam axis perpendicular to the shear force.
    '''
    return 0.5*VEd*(1.0/math.tan(webStrutAngle)-1.0/math.tan(shearReinfAngle))

# EC2:2004 6.2.4 Shear between web and flanges.
def getFlangeStrutAngleLimits(compressionFlange= True, nationalAnnex= None):
    ''' Return the limits specified in the clause 6.2.4(4) of EC2:2004 for
        the angle of the struts in the flange.

    :param compressionFlange: true if flange is compressed.
    :param nationalAnnex: identifier of the national annex.
    '''
    if(compressionFlange):
        limSup= math.pi/4.0 # math.atan(1.0)
        limInf= math.atan(1/2.0) # 26.5º
    else:
        limSup= math.pi/4.0 # math.atan(1.0)
        limInf= math.atan(1/1.25) # 38.6º
    return limInf, limSup

def checkFlangeStrutAngleLimits(flangeStrutAngle, compressionFlange= True, nationalAnnex= None):
    ''' Check that the strut angle is inside the limits specified
        in the expression 6.7N of EC2:2004. Otherwise, issue a
        warning and return a suitable strut angle.

    :param flangeStrutAngle: (theta_f) angle between the concrete flange compression strut and the shear plane (see figure 6.7 on EC2:2004).
    :param compressionFlange: true if flange is compressed.
    :param nationalAnnex: identifier of the national annex.
    '''
    retval= flangeStrutAngle
    limInf, limSup= getFlangeStrutAngleLimits(compressionFlange, nationalAnnex)
    if((flangeStrutAngle<limInf) or (flangeStrutAngle>limSup)): # eq 6.7N
        methodName= sys._getframe(0).f_code.co_name
        errString= methodName+'; flange strut angle: '+str(math.degrees(flangeStrutAngle))+' out of range: ['+str(math.degrees(limInf))+','+str(math.degrees(limSup))+']'
        if(flangeStrutAngle<limInf):
            retval= limInf
        elif(flangeStrutAngle>limSup):
            retval= limSup
        errString+= ' using '+str(math.degrees(retval))
        lmsg.warning(errString)
    return retval

def getMaximumShearFlangeStrutCrushingStress(concrete, flangeStrutAngle= math.pi/4.0, compressionFlange= True, nationalAnnex= None):
    ''' Return the maximum shear force due to diagonal compression in the web
        (strut crushing) according to expression 6.22 of EC2:2004.

    :param concrete: concrete material.
    :param flangeStrutAngle: (theta_f) angle between the concrete flange compression strut and the shear plane (see figure 6.7 on EC2:2004).
    :param compressionFlange: true if flange is compressed.
    :param nationalAnnex: identifier of the national annex.
    '''
    # nu1: strength reduction factor for concrete cracked in shear
    nu1= concrete.getShearStrengthReductionFactor(nationalAnnex)
    fcd= -concrete.fcd() # design value of concrete compressive strength (MPa).
    flangeStrutAngle= checkFlangeStrutAngleLimits(flangeStrutAngle, compressionFlange, nationalAnnex)
    return nu1*fcd*math.sin(flangeStrutAngle)*math.cos(flangeStrutAngle)

def getConcreteFlangeShearStrength(concrete, hf, DeltaX, nationalAnnex= None):
    ''' Return the shear stress resisted by plain concrete according to
        clause 6.2.4 (6) of EC2:2004.

    :param concrete: concrete material.
    :param hf: flange thickness at the shear plane.
    :param DeltaX: length under consideration (see figure 6.7 on EC2:2004).
    :param nationalAnnex: identifier of the national annex.
    '''
    return concrete.getConcreteFlangeShearStressStrength(nationalAnnex)*DeltaX*hf

def getFlangeShearResistanceShearReinfStress(concrete, hf, Asf, sf, shearReinfSteel, flangeStrutAngle= math.pi/4.0, compressionFlange= True, nationalAnnex= None):
    ''' Return the design value of the flange shear resistance  
        according to expressions 6.21 of EC2:2004.

    :param concrete: concrete material.
    :param hf: flange thickness at the shear plane.
    :param Asf: cross-sectional area of the flange transverse reinforcement.
    :param sf: spacing of the reinforcement.
    :param shearReinfSteel: reinforcing steel material.
    :param flangeStrutAngle: (theta_f) angle between the concrete flange compression strut and the shear plane (see figure 6.7 on EC2:2004).
    :param compressionFlange: true if flange is compressed.
    :param nationalAnnex: identifier of the national annex.
    '''
    flangeStrutAngle= checkFlangeStrutAngleLimits(flangeStrutAngle, compressionFlange, nationalAnnex)
    cotgThetaF= 1/math.tan(flangeStrutAngle)
    fyd= shearReinfSteel.fyd()
    vRds= Asf/sf*fyd*cotgThetaF/hf # expression 6.21 of EC2:2004
    vRdmax= getMaximumShearFlangeStrutCrushingStress(concrete, flangeStrutAngle, compressionFlange, nationalAnnex) # expression 6.22 of EC2:2004
    return min(vRds, vRdmax)

# 7.3.2 Minimum reinforcement areas

def getAsMinCrackControl(concrete, reinfSteel, h, Act, stressDistribution, sigma_s= None):
    ''' Return the minimum area of reinforcing steel within the tensile zone
        according to expression 7.1 of clause 7.3.2 of EC2:2004.

    :param concrete: concrete material.
    :param reinfSteel: reinforcing steel material.
    :param h: section depth.
    :param Act: area of concrete within tensile zone. The tensile zone is 
                that part of the section which is calculated to be in tension 
                just before formation of the first crack.
    :param stressDistribution: string indentifying the stress distribution
                               (bending or pure tension) of the cross-section.
    :param sigma_s: absolute value of the maximum stress permitted in the 
                    reinforcement immediately after formation of the crack. 
                    This may be taken as the yield strength of the 
                    reinforcement, f_yk, A lower value may, however, be needed 
                    to satisfy the crack width limits according to the maximum 
                    bar size or the maximum bar spacing (see 7.3.3 (2) 
                    of EN 1992-1-1).
    '''
    kc= 0.4 # coefficient which takes account of the stress distribution
            # within the section immediately prior to cracking and of the
            # change of the lever arm
    if(stressDistribution=='simple_tension'):
        kc= 1.0
    k= 1.0 # coefficient which allows for the effect of non-uniform
           # self-equilibrating stresses, which lead to a reduction of
           # restraint forces.
    if(h>=0.8):
        k= 0.65
    elif(h>0.3):
        k= -0.7*h+1.21 # linear interpolation.
    fctef= concrete.fctm() # mean value of the tensile strength of the
                           # concrete effective at the time when the cracks
                           # may first be expected to occur.
    sigma_s= reinfSteel.fyk
    return kc*k*fctef/sigma_s*Act

def getAsMinBeams(concrete, reinfSteel, h, z, bt, d, nationalAnnex= None):
    ''' Return the minimum area of reinforcing steel within the tensile zone
        according to expression 9.1N of EC2:2004.

    :param concrete: concrete material.
    :param reinfSteel: reinforcing steel material.
    :param h: section depth.
    :param z: inner lever arm.
    :param bt: mean width of the tension zone.
    :param d: effective depth.
    :param nationalAnnex: identifier of the national annex.
    '''
    if(nationalAnnex=='Spain'):
        W= bt*h**2/6.0
        fctmfl= max(1.6-h,1.0)*concrete.fctm()
        return W/z*fctmfl/reinfSteel.fyd()
    else:
        return max(0.26*concrete.fctm()/reinfSteel.fyk,0.0013)*bt*d
    
def getAsMaxBeams(Ac, nationalAnnex= None):
    ''' Return the minimum area of reinforcing steel within the tensile zone
        according to expression 9.1N of EC2:2004.

    :param Ac: area of concrete cross-section. 
    :param nationalAnnex: identifier of the national annex.
    '''
    return .04*Ac

# Check normal stresses limit state.
class BiaxialBendingNormalStressController(lscb.BiaxialBendingNormalStressControllerBase):
    '''Object that controls normal stresses limit state.'''

    def __init__(self,limitStateLabel):
        ''' Constructor.
        
        :param limitStateLabel: label that identifies the limit state.
        '''
        super(BiaxialBendingNormalStressController,self).__init__(limitStateLabel)

class UniaxialBendingNormalStressController(lscb.UniaxialBendingNormalStressControllerBase):
    '''Object that controls normal stresses limit state (uniaxial bending).'''

    def __init__(self,limitStateLabel):
        ''' Constructor.
        
        :param limitStateLabel: label that identifies the limit state.
        '''
        super(UniaxialBendingNormalStressController,self).__init__(limitStateLabel)



# Shear checking.

class ShearController(lscb.ShearControllerBase):
    '''Shear control according to EHE-08.'''

    ControlVars= cv.RCShearControlVars
    def __init__(self, limitStateLabel, nationalAnnex= None):
        ''' Constructor.
        
        :param limitStateLabel: label that identifies the limit state.
        :param nationalAnnex: identifier of the national annex.
        '''
        super(ShearController,self).__init__(limitStateLabel,fakeSection= False)
        self.concreteFibersSetName= "concrete" # Name of the concrete fibers set.
        self.rebarFibersSetName= "reinforcement" # Name of the rebar fibers set.
        self.nationalAnnex= nationalAnnex # national annex.
        
    def getShearStrengthCrackedNoShearReinf(self, scc, concrete, reinfSteel, Nd, Md, Vd, Td, rcSets, circular= False):
        '''Return the design value of the shear resistance VRdc for cracked 
           sections subjected to bending moment, according to expressions 6.2.a 
           and 6.2.b of EC2:2004.

         :param scc: fiber model of the section.
         :param concrete: concrete material.
         :param reinfSteel: shear reinforcement steel.
         :param Nd: Design value of axial force (here positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
         :param rcSets: fiber sets in the reinforced concrete section.
         :param circular: if true we reduce the efectiveness of the shear 
                          reinforcement due to the transverse inclination of
                          its elements.
        '''
        Ac= rcSets.getConcreteArea(1) # Ac
        strutWidth= scc.getCompressedStrutWidth() # b0
        # area of the tensile reinforcement
        tensileReinforcementArea= 0.0
        if(rcSets.getNumTensionRebars()>0):
            tensileReinforcementArea= rcSets.tensionFibers.getArea(1)
        return getShearResistanceCrackedNoShearReinf(concrete= concrete, NEd= Nd, Ac= Ac, Asl= tensileReinforcementArea, bw= strutWidth, d= scc.getEffectiveDepth(), nationalAnnex= self.nationalAnnex)
    
    def getShearStrengthNonCrackedNoShearReinf(self, scc, concrete, reinfSteel, Nd, Md, Vd, Td, rcSets, circular= False):
        ''' Return the design value of the shear resistance VRdc for non-cracked 
            sections subjected to bending moment, according to expression 6.4 of
            EC2:2004.

         :param scc: fiber model of the section.
         :param concrete: concrete material.
         :param reinfSteel: shear reinforcement steel.
         :param Nd: Design value of axial force (here positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
         :param rcSets: fiber sets in the reinforced concrete section.
         :param circular: if true we reduce the efectiveness of the shear 
                          reinforcement due to the transverse inclination of
                          its elements.
        '''
        Ac= rcSets.getConcreteArea(1) # Ac
        strutWidth= scc.getCompressedStrutWidth() # b0
        E0= rcSets.getConcreteInitialTangent()
        # second moment of area.
        I= scc.getHomogenizedI(E0)
        # first moment of area above and about the centroidal axis.
        S= scc.getSPosHomogenized(E0)
        alpha_l= 1.0 # see expression 6.4 in EC2:2004.
        return getShearResistanceNonCrackedNoShearReinf(concrete= concrete, I= I, S= S, NEd= Nd, Ac= Ac, bw= strutWidth, alpha_l= alpha_l)
    
    def getShearStrengthNoShearReinf(self, scc, concrete, reinfSteel, Nd, Md, Vd, Td, rcSets, circular= False):
        ''' Return the design value of the shear resistance VRdc for cracked
            or non-cracked sections subjected to bending moment, according 
            to expression 6.4 of EC2:2004.

         :param scc: fiber model of the section.
         :param concrete: concrete material.
         :param reinfSteel: shear reinforcement steel.
         :param Nd: Design value of axial force (here positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
         :param rcSets: fiber sets in the reinforced concrete section.
         :param circular: if true we reduce the efectiveness of the shear 
                          reinforcement due to the transverse inclination of
                          its elements.
        '''
        retval= 0.0
        #tensionedReinforcement= rcSets.tensionFibers
        self.isBending= scc.isSubjectedToBending(0.1)
        #numberOfTensionedRebars= rcSets.getNumTensionRebars()
        if(self.isBending):
            self.eps1= rcSets.getMaxConcreteStrain()
            # design tensile strength of the concrete.
            fctdH= concrete.fctd()
            E0= rcSets.getConcreteInitialTangent()
            if((E0*self.eps1)<fctdH): # Non cracked section
                retval= self.getShearStrengthNonCrackedNoShearReinf(scc= scc, concrete= concrete, reinfSteel= reinfSteel, Nd= Nd, Md= Md, Vd= Vd, Td= Td, rcSets= rcSets, circular= circular)
            else: # cracked
                retval= self.getShearStrengthCrackedNoShearReinf(scc= scc, concrete= concrete, reinfSteel= reinfSteel, Nd= Nd, Md= Md, Vd= Vd, Td= Td, rcSets= rcSets, circular= circular)
        else: # not bending.
            # In real problems you don't need to check the shear strength right
            # over the pinned support (M= 0) so, normally, this code is not
            # reach. Anyway, we return a safe estimation based on the shear
            # strength of a T-beam flange in its plane.
            hf= scc.getCompressedStrutWidth()
            Ac= rcSets.getConcreteArea(1) # Ac
            DeltaX= Ac/hf
            retval= getConcreteFlangeShearStrength(concrete= concrete, hf= hf, DeltaX= DeltaX, nationalAnnex= None)
        return retval
        
    def getShearStrengthShearReinf(self, scc, concrete, reinfSteel, Nd, Md, Vd, Td, rcSets, circular= False):
        ''' Compute the shear strength at failure WITH shear reinforcement.
         XXX Presstressing contribution not implemented yet.

         :param scc: fiber model of the section.
         :param concrete: concrete material.
         :param reinfSteel: shear reinforcement steel.
         :param Nd: Design value of axial force (here positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
         :param rcSets: fiber sets in the reinforced concrete section.
         :param circular: if true we reduce the efectiveness of the shear 
                          reinforcement due to the transverse inclination of
                          its elements.
        '''
        Ac= rcSets.getConcreteArea(1) # Ac
        strutWidth= scc.getCompressedStrutWidth() # b0
        isBending= scc.isSubjectedToBending(0.1)
        if(isBending):
            innerLeverArm= scc.getMechanicLeverArm() # z
        else: # not bending
            # In real problems you don't need to check the shear strength right
            # over the pinned support (M= 0) so, normally, this code is not
            # reach. Anyway, we return a safe estimation of the lever arm.
            sectionDepth= Ac/strutWidth
            innerLeverArm= 0.7*sectionDepth
        return getShearResistanceShearReinf(concrete= concrete, NEd= Nd, Ac= Ac, bw= strutWidth, Asw= self.Asw, s= self.stirrupSpacing, z= innerLeverArm, shearReinfSteel= reinfSteel, shearReinfAngle= self.alpha, webStrutAngle= math.pi/4.0, nationalAnnex= self.nationalAnnex)

    def getShearStrength(self, scc, concrete, reinfSteel, Nd, Md, Vd, Td, rcSets, circular= False):
        ''' Compute the shear strength at failure WITH or WITHIOUT shear 
            reinforcement.
         XXX Presstressing contribution not implemented yet.

         :param scc: fiber model of the section.
         :param concrete: concrete material.
         :param reinfSteel: shear reinforcement steel.
         :param Nd: Design value of axial force (here positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
         :param rcSets: fiber sets in the reinforced concrete section.
         :param circular: if true we reduce the efectiveness of the shear 
                          reinforcement due to the transverse inclination of
                          its elements.
        '''
        if(self.Asw==0):
            retval= self.getShearStrengthNoShearReinf(scc= scc, concrete= concrete, reinfSteel= reinfSteel, Nd= Nd, Md= Md, Vd= Vd, Td= Td, rcSets= rcSets, circular= circular)
        else:
            retval= self.getShearStrengthShearReinf(scc= scc, concrete= concrete, reinfSteel= reinfSteel, Nd= Nd, Md= Md, Vd= Vd, Td= Td, rcSets= rcSets, circular= circular)
        return retval
        
    def checkInternalForces(self, sct, Nd, Md, Vd, Td):
        '''  Compute the shear strength at failure.
         XXX Presstressing contribution not implemented yet.

         :param sct: reinforced concrete section object to chech shear on.
         :param Nd: Design value of axial force (positive if in tension)
         :param Md: Absolute value of design value of bending moment.
         :param Vd: Absolute value of effective design shear (clause 42.2.2).
         :param Td: design value of torsional moment.
        '''
        section= sct.getProp('sectionData')
        concreteCode= section.fiberSectionParameters.concrType
        reinforcementCode= section.fiberSectionParameters.reinfSteelType
        shReinf= section.getShearReinfY()
        circular= section.isCircular()
        strutWidth= sct.getCompressedStrutWidth() # bw
        self.Asw= shReinf.getAs()
        self.stirrupSpacing= shReinf.shReinfSpacing
        self.alpha= shReinf.angAlphaShReinf
        #Searching for the best theta angle (concrete strut inclination).
        if(self.Asw>0.0):
            self.theta= getWebStrutAngleForSimultaneousCollapse(concrete= concreteCode, bw= strutWidth, s= self.stirrupSpacing, Asw= self.Asw, shearReinfSteel= reinforcementCode, shearReinfAngle= shReinf.angAlphaShReinf)
        else:
            self.theta= math.pi/4.0
        #We calculate Vu for several values of theta and chose the highest Vu with its associated theta
        rcSets= self.extractFiberData(sct, concreteCode, reinforcementCode)
        self.Vu= self.getShearStrength(sct, concreteCode,reinforcementCode,Nd,Md,Vd,Td, rcSets, circular)
        VuTmp= self.Vu
        if(VuTmp!=0.0):
            FCtmp= Vd/VuTmp
        else:
            FCtmp= 1e99
        return FCtmp, VuTmp
        
    def checkSection(self, sct, elementDimension):
        ''' Check shear on the section argument.

        :param sct: reinforced concrete section object to chech shear on.
        :param elementDimension: dimension of the element (1, 2 or 3).
        '''
        NTmp= sct.getStressResultantComponent("N")
        MyTmp= sct.getStressResultantComponent("My")
        MzTmp= sct.getStressResultantComponent("Mz")
        MTmp= math.sqrt((MyTmp)**2+(MzTmp)**2)
        VyTmp= sct.getStressResultantComponent("Vy")
        VzTmp= sct.getStressResultantComponent("Vz")
        VTmp= self.getShearForce(Vy= VyTmp, Vz= VzTmp, elementDimension= elementDimension)
        TTmp= sct.getStressResultantComponent("Mx")
        #Searching for the best theta angle (concrete strut inclination).
        #We calculate Vu for several values of theta and chose the highest Vu with its associated theta
        FCtmp, VuTmp= self.checkInternalForces(sct= sct, Nd= NTmp, Md= MTmp, Vd= VTmp, Td= TTmp)
        return FCtmp, VuTmp, NTmp, VyTmp, VzTmp, TTmp, MyTmp, MzTmp 

    def check(self, elements, combName):
        ''' For each element in the set 'elements' passed as first parameter
        and the resulting internal forces for the load combination 'combName'  
        passed as second parameter, this method calculates all the variables 
        involved in the shear-ULS checking and obtains the capacity factor.
        In the case that the calculated capacity factor is smaller than the 
        smallest obtained for the element in previous load combinations, this 
        value is saved in the element results record.

        Elements processed are those belonging to the phantom model, that is to 
        say, of type xc.ZeroLengthSection. As we have defined the variable 
        fakeSection as False, a reinfoced concrete fiber section is generated
        for each of these elements. 

        XXX Rebar orientation not taken into account yet.
        '''
        if(self.verbose):
            lmsg.log("Postprocessing combination: "+combName)
        for e in elements:
            # Call getResisting force to update the internal forces.
            R= e.getResistingForce() 
            if(__debug__):
                if(not R):
                    AssertionError('Can\'t get the resisting force.')        
            scc= e.getSection()
            idSection= e.getProp("idSection")
            masterElementDimension= e.getProp("masterElementDimension")
            FCtmp, VuTmp, NTmp, VyTmp, VzTmp, TTmp, MyTmp, MzTmp= self.checkSection(sct= scc, elementDimension= masterElementDimension)
            Mu= 0.0 #Apparently EC2 doesn't use Mu
            if(FCtmp>=e.getProp(self.limitStateLabel).CF):
                e.setProp(self.limitStateLabel, self.ControlVars(idSection= idSection, combName= combName, CF= FCtmp, N= NTmp, My= MyTmp, Mz= MzTmp, Mu= Mu, Vy= VyTmp, Vz= VzTmp, theta= self.theta, Vu=VuTmp)) # Worst case
