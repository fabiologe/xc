# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import geom
import xc
from model import predefined_spaces
from materials import typical_materials
from misc_utils import integra_simpson as isimp

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2014, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler
modelSpace= predefined_spaces.SolidMechanics3D(nodes)
# Define materials
elast= typical_materials.defElasticMaterial(preprocessor, "elast",3000)


seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= elast.name
seedElemHandler.dimElem= 3 # Dimension of element space
truss= seedElemHandler.newElement("Truss",xc.ID([0,0]))
truss.sectionArea= 10.0

unifGrids= preprocessor.getMultiBlockTopology.getUniformGrids
uGrid= unifGrids.newUniformGrid()

uGrid.org= geom.Pos3d(0.0,0.0,3.0)
uGrid.Lx= 1
uGrid.Ly= 1
uGrid.Lz= 3
uGrid.nDivX= 0
uGrid.nDivY= 0
uGrid.nDivZ= 3



total= preprocessor.getSets.getSet("total")
total.genMesh(xc.meshDir.I)

 
abscissae= []
gridNodes= uGrid.getNodeLayers
nNodes= uGrid.nDivZ+1
for i in range(1,nNodes+1):
  n= gridNodes.getAtIJK(i,1,1)
  abscissae.append(n.getInitialPos3d.z)


def func(z):
  return z-1.0

#pesos= uGrid.getSimpsonWeights("i",'z-1.0',1,1,10)
pesos= isimp.getSimpsonWeights(abscissae,func,10)
suma= pesos[0]+pesos[1]+pesos[2]+pesos[3]

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if abs(suma-(9/8.0+3+4+19/8.0))<1e-5:
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')



