# -*- coding: utf-8 -*-
''' Test path time series. '''
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import xc

feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor

#Load modulation.
timeValues= [0.0, 0.13888889, 0.27777778, 0.41666667, 0.55555556, 0.69444444, 0.83333333, 0.97222222, 1.11111111, 1.25, 1.38888889, 1.52777778, 1.66666667, 1.80555556, 1.94444444, 2.08333333, 2.22222222, 2.36111111, 2.5, 2.63888889, 2.77777778, 2.91666667, 3.05555556, 3.19444444, 3.33333333, 3.47222222, 3.61111111, 3.75, 3.88888889, 4.02777778, 4.16666667, 4.30555556, 4.44444444, 4.58333333, 4.72222222, 4.86111111, 5., 5.13888889, 5.27777778, 5.41666667, 5.55555556, 5.69444444, 5.83333333, 5.97222222, 6.11111111, 6.25, 6.38888889, 6.52777778, 6.66666667, 6.80555556, 6.94444444, 7.08333333, 7.22222222, 7.36111111, 7.5, 7.63888889, 7.77777778, 7.91666667, 8.05555556, 8.19444444, 8.33333333, 8.47222222, 8.61111111, 8.75, 8.88888889, 9.02777778, 9.16666667, 9.30555556, 9.44444444, 9.58333333, 9.72222222, 9.86111111, 10., 10.13888889, 10.27777778, 10.41666667, 10.55555556, 10.69444444, 10.83333333, 10.97222222, 11.11111111, 11.25, 11.38888889, 11.52777778, 11.66666667, 11.80555556, 11.94444444, 12.08333333, 12.22222222, 12.36111111, 12.5, 12.63888889, 12.77777778, 12.91666667, 13.05555556, 13.19444444, 13.33333333, 13.47222222, 13.61111111, 13.75, 13.88888889]
loadValues= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 78.79296057779986, 118.96357325970033, 207.7719942356257, 311.49999999999994, 346.28665705937533, 356.8907197791001, 551.5507240445967, 616.0000000000001, 461.76790037029866, 805.182133701498, 725.7794717226295, 385.00000000000006, 564.495144673155, 483.1092802208992, 256.5377224279428, 308.0000000000003, 236.37888173339815, 118.96357325970004, 69.2573314118754, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

loadHandler= preprocessor.getLoadHandler
lPatterns= loadHandler.getLoadPatterns
ts= lPatterns.newTimeSeries("path_time_ts","ts")
ts.path= xc.Vector(loadValues)
ts.time= xc.Vector(timeValues)

duration= ts.getDuration()
refDuration= timeValues[-1]-timeValues[0]
ratio1= abs(duration-refDuration)/refDuration
peakFactor= ts.getPeakFactor()
peakFactorRef= ts.path[30]
ratio2= abs(peakFactor-peakFactorRef)/peakFactorRef

''' 
print('duration: ', duration)
print('ratio1= ', ratio1)
print('ratio2= ', ratio2)
print('peak factor: ', peakFactor)
print('reference peak factor: ', peakFactorRef)
print('ratio2= ', ratio2)
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1)<1e-15) and (abs(ratio2)<1e-15):
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')
