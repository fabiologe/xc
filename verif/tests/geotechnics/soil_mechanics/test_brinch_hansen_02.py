# -*- coding: utf-8 -*-
'''
Verification of the Brinch Hansen formula.

See Brinch Hansen. A general formula for bearing capacity. The Danish Geotechnical Institute. Bulletin 11. Copenhagen 1961. Example on page 45
'''

from __future__ import division
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2016, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

from geotechnics import frictional_cohesive_soil as fcs
import math

# Short-term bearing capacity.
shortTermSoil= fcs.FrictionalCohesiveSoil(0.0,c=10.3,rho= (2.2-1.0)/9.81)

D= 2.0 # Foundation depth
Beff= 5.5 # Effective foundation width
Leff= 9.0 # Effective foundation length
V= 3000.0 # Vertical load
H= 225.0 # Horizontal load.
deltaB= math.atan(H/V)
deltaL= 0.0
q= 4.4

NgammaSTS= shortTermSoil.Ngamma(1.8) # wedge weight multiplier for the Brinch-Hasen formula
NqSTS= shortTermSoil.Nq() # overburden multiplier for the Brinch-Hasen formula
NcSTS= shortTermSoil.Nc() # cohesion multiplier for the Brinch-Hasen formula.
dcSTS= shortTermSoil.dc(D,Beff) # depth factor for cohesion
scSTS= shortTermSoil.sc(Beff,Leff) # factor that introduces the effect of foundation shape on the cohesion component.
icSTS= shortTermSoil.ic(Vload= V, HloadB= H, HloadL= 0.0,Beff= Beff, Leff= Leff) # factor that introduces the effect of load inclination on the cohesion component.
quSTS= shortTermSoil.qu(q,D,Beff,Leff,V,H,0.0,1.8) # Ultimate bearing capacity pressure of the soil

err= abs(NgammaSTS)**2 
err+= abs(NqSTS-1.0)**2
err+= (abs(NcSTS-5.1)/5.1)**2
err+= (abs(dcSTS-1.13)/1.13)**2
err+= (abs(scSTS-1.12)/1.12)**2
err+= (abs(icSTS-0.89)/0.89)**2 #Better approximation of i_c than
                                #those employed in reference example
err+= (abs(quSTS-64.0)/64.0)**2 #Better approximation of i_c than
                                #those employed in reference example

# Long-term bearing capacity.
longTermSoil= fcs.FrictionalCohesiveSoil(math.radians(30.0),c=1.7,rho= (2.2-1.0)/9.81)

NgammaLTS= longTermSoil.Ngamma(1.8) # wedge weight multiplier for the Brinch-Hasen formula.
NqLTS= longTermSoil.Nq() # overburden multiplier for the Brinch-Hasen formula
NcLTS= longTermSoil.Nc()  # cohesion multiplier for the Brinch-Hasen formula
dcLTS= longTermSoil.dc(D,Beff) # depth factor for cohesion
scLTS= longTermSoil.sc(Beff,Leff) # factor that introduces the effect of foundation shape on the cohesion component.
sgammaLTS= longTermSoil.sgamma(Beff,Leff) # factor that introduces the effect of foundation shape on the self weight component
dgammaLTS= longTermSoil.dgamma() # factor that introduces the effect of foundation depth on the self weight component.
iqLTS= longTermSoil.iq(Vload= V, HloadB= H, HloadL= 0.0) # factor that introduces the effect of load inclination on the overburden component
sqLTS= longTermSoil.sq(Beff,Leff) # Factor that introduces the effect of foundation shape on the overburden component.
dqLTS= longTermSoil.dq(D,Beff) # overburden factor for foundation depth.
igammaLTS= longTermSoil.igamma(Vload= V, HloadB= H, HloadL= 0.0, Beff= Beff, Leff= Leff) # Factor that introduces the effect of load inclination on    the self weight component.
icLTS= longTermSoil.ic(Vload= V, HloadB= H, HloadL= 0.0, Beff= Beff, Leff= Leff) # Factor that introduces the effect of load inclination on the cohesion component
quGammaLTS= longTermSoil.quGamma(D,Beff,Leff,V,H,0.0,1.8) # gamma "component" of the ultimate bearing capacity pressure of the soil.
quGammaTeorLTS= 0.5*1.2*Beff*NgammaLTS*sgammaLTS*dgammaLTS*igammaLTS
quCohesionLTS= longTermSoil.quCohesion(D= D, Beff= Beff, Leff= Leff, Vload= V, HloadB= H, HloadL= 0.0, psi= 0.0, eta= 0.0) # Cohesion "component" of the ultimate bearing capacity pressure of the soil.
quCohesionTeorLTS= 1.7*NcLTS*scLTS*dcLTS*icLTS
quQLTS= longTermSoil.quQ(q,D,Beff,Leff,V,H,0.0) # Overburden component of the ultimate bearing capacity pressure of the soil.
quQTeorLTS= q*NqLTS*sqLTS*dqLTS*iqLTS
quLTS= longTermSoil.qu(q,D,Beff,Leff,V,H,0.0,1.8) # Ultimate bearing capacity pressure of the soil.
quTeorLTS= quGammaTeorLTS+quCohesionTeorLTS+quQTeorLTS

err+= (abs(NgammaLTS-18)/18)**2
err+= (abs(NqLTS-18.5)/18.5)**2
err+= (abs(NcLTS-30)/30)**2
err+= (abs(dcLTS-1.11)/1.11)**2 #dc calculated as in reference [3]
                                #(see module documentation).
err+= (abs(scLTS-1.37)/1.37)**2 #sc calculated as in reference [3]
                                #(see module documentation).
err+= (abs(sgammaLTS-0.82)/0.82)**2 # sgamma calculated as in reference [3]
                                    # (see module documentation).
err+= (abs(iqLTS-0.87)/0.87)**2
err+= (abs(igammaLTS-0.80)/0.80)**2 #igamma calculated as in reference [3]
                                    #(see module documentation).
err+= (abs(icLTS-0.86)/0.86)**2
err+= (abs(quGammaLTS-quGammaTeorLTS)/quGammaTeorLTS)**2
err+= (abs(quCohesionLTS-quCohesionTeorLTS)/quCohesionTeorLTS)**2
err+= (abs(quQLTS-quQTeorLTS)/quQTeorLTS)**2
err+= (abs(quLTS-quTeorLTS)/quTeorLTS)**2

'''
print('NgammaSTS= ', NgammaSTS)
print('NqSTS= ', NqSTS)
print('NcSTS= ', NcSTS)
print('dcSTS= ', dcSTS)
print('scSTS= ', scSTS)
print('icSTS= ', icSTS)
print('quSTS=',quSTS)
print('NgammaLTS= ', NgammaLTS)
print('NqLTS= ', NqLTS)
print('NcLTS= ', NcLTS)
print('dcLTS= ', dcLTS)
print('scLTS= ', scLTS)
print('sgammaLTS= ', sgammaLTS)
print('iqLTS= ', iqLTS)
print('igammaLTS= ', igammaLTS)
print('icLTS= ', icLTS)
print('quGammaLTS=',quGammaLTS)
print('quGammaTeorLTS=',quGammaTeorLTS)
print('quCohesionLTS=',quCohesionLTS)
print('quCohesionTeorLTS=',quCohesionTeorLTS)
print('quQLTS=',quQLTS)
print('quQTeorLTS=',quQTeorLTS)
print('quLTS=',quLTS)
print('quTeorLTS=',quTeorLTS)
print('err= ', err)
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (err<0.0005):
    print('test: '+fname+': ok.')
else:
    lmsg.error('test: '+fname+' ERROR.')
