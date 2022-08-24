# -*- coding: utf-8 -*-
''' home made test
    vector3d_uniform_load_global function verification.'''

from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import xc
from solution import predefined_solutions
from model import predefined_spaces
from actions import loads
import math

# Load
f= 2e3 # Load magnitude.

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler
modelSpace= predefined_spaces.StructuralMechanics2D(nodes)
n1= nodes.newNodeXY(-1,0.0)
n2= nodes.newNodeXY(1,0.0)


# Constraints
modelSpace.fixNode000(n1.tag)
modelSpace.fixNode000(n2.tag)

# Load definition.
lp0= modelSpace.newLoadPattern(name= '0')
modelSpace.setCurrentLoadPattern("0")
lVector= xc.Vector([0,-f, 0])
slidingVectorLoad= loads.SlidingVectorLoad(name= 'test', nodes= [n1,n2], pntCoord= [0.0,0.0], loadVector= lVector)
slidingVectorLoad.appendLoadToCurrentLoadPattern()

# We add the load case to domain.
modelSpace.addLoadCaseToDomain(lp0.name)
# Solution
result= modelSpace.analyze(1, calculateNodalReactions= True)
if(result!=0):
    print('Can\'t solve.')
    exit(1)

R1= n1.getReaction
R2= n2.getReaction

ratio1= abs(R1[1]-f/2.0)/(f/2.0)
ratio2= abs(R2[1]-f/2.0)/(f/2.0)
ratio3= (R1+R2+lVector).Norm()

'''
print("R1: ",R1)
print("ratio1= ",ratio1)
print("R2: ",R2)
print("ratio2= ",ratio2)
print("ratio3= ",ratio3)
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1)<1e-6) & (abs(ratio2)<1e-10) & (abs(ratio3)<1e-10):
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')
