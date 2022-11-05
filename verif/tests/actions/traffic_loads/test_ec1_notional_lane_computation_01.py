# -*- coding: utf-8 -*-
'''Bridge loads. Notional lane computation.'''

from __future__ import print_function
from __future__ import division

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AO_O)"
__copyright__= "Copyright 2015, LCPT and AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com ana.ortega@ciccp.es"

import math
import geom
from actions.roadway_traffic import EC1_load_models

p1= geom.Pos3d(0.0, 0.0, 0.0)
p2= geom.Pos3d(10.0, 0.0, 0.0)
p3= geom.Pos3d(0.0, 11.5, 0.0)
p4= geom.Pos3d(10.0, 11.5, 0.0)

border1= geom.Segment3d(p1, p2)
border2= geom.Segment3d(p3, p4)

carriagewayWidth= EC1_load_models.getCarriagewayWidth(firstBorder= border1, lastBorder= border2)
notionalLanesWidths= EC1_load_models.getNotionalLanesWidths(carriagewayWidth)
notionalLanesContours= EC1_load_models.getNotionalLanesContours(firstBorder= border1, lastBorder= border2)

err1= 0.0
refAreas= [30.0, 30.0, 30.0, 25]
areas= list()
for plg, refArea in zip(notionalLanesContours, refAreas):
    A= plg.getArea()
    areas.append(A)
    err1+= (A-refArea)**2
err1= math.sqrt(err1)

reversedNotionalLanesContours= EC1_load_models.getNotionalLanesContours(firstBorder= border1, lastBorder= border2, reverse= True)

err2= 0.0
reversedAreas= list()
refReversedAreas= [25, 30.0, 30.0, 30.0]
for plg, refArea in zip(reversedNotionalLanesContours, refReversedAreas):
    A= plg.getArea()
    reversedAreas.append(A)
    err2= (A-refArea)**2
err2= math.sqrt(err2)

'''
print('carriageway width: ', carriagewayWidth)
print('widths of the notional lanes: ', notionalLanesWidths)
print('areas: ', areas)
print('err1= ', err1)
print('reversed areas: ', reversedAreas)
print('err2= ', err2)
'''

import os
fname= os.path.basename(__file__)
if(err1<1e-6) & (err2<1e-6):
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')
