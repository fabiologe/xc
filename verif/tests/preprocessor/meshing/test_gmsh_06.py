# -*- coding: utf-8 -*-
'''Gusset plate mesh generation using Gmsh. Home cooked test.'''

from __future__ import division
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2020, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import math
import xc_base
import geom
import xc
from materials.astm_aisc import ASTM_materials
from model import predefined_spaces
from materials import typical_materials
from helper_funcs import getHoleAsPolygonalSurface
#from postprocess import output_handler


p1= geom.Pos3d(-1.5950,-2.0450,0)
p2= geom.Pos3d(-1.4376,-2.0450,0)
p3= geom.Pos3d(-1.4376,-1.8140,0)
p4= geom.Pos3d(-1.5290,-1.7734,0)
p5= geom.Pos3d(-1.5950, -1.7734, 0)

bolts= list()
boltDiameter= 0.016
bolts.append(ASTM_materials.BoltFastener(diameter= boltDiameter, pos3d= geom.Pos3d(-1.4909,-1.8724,0.0)))
bolts.append(ASTM_materials.BoltFastener(diameter= boltDiameter, pos3d= geom.Pos3d(-1.4706,-1.8267,0.0)))
bolts.append(ASTM_materials.BoltFastener(diameter= boltDiameter, pos3d= geom.Pos3d(-1.5163,-1.8064,0.0)))
bolts.append(ASTM_materials.BoltFastener(diameter= boltDiameter, pos3d= geom.Pos3d(-1.5366,-1.8521,0.0)))

# Test paving routine inside XC modeler.

## Problem type
feProblem= xc.FEProblem()
preprocessor= feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler

modelSpace= predefined_spaces.StructuralMechanics3D(nodes)

### Define k-points.
points= modelSpace.getPointHandler()

#### Exterior contour
pt1= points.newPntFromPos3d(p1)
pt2= points.newPntFromPos3d(p2)
pt3= points.newPntFromPos3d(p3)
pt4= points.newPntFromPos3d(p4)
pt5= points.newPntFromPos3d(p5)

### Define polygonal surfaces
surfaces= modelSpace.getSurfaceHandler()
polyFace= surfaces.newPolygonalFacePts([pt1.tag, pt2.tag, pt3.tag, pt4.tag, pt5.tag])
pFaceHoles= list()
for b in bolts:
    pFace= getHoleAsPolygonalSurface(b,surfaces, points)
    pFaceHoles.append(pFace)
    
### Define material
mat= typical_materials.defElasticMembranePlateSection(preprocessor, "mat",E=2.1e9,nu=0.3,rho= 7850,h= 0.015)

### Define template element
seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= mat.name
elem= seedElemHandler.newElement("ShellMITC4",xc.ID([0,0,0,0]))

### Generate mesh.
polyFace.setElemSize(1.5*boltDiameter, True)
for h in pFaceHoles:
    h.setNDiv(1)
    polyFace.addHole(h)
polyFace.genMesh(xc.meshDir.I,False)

xcTotalSet= modelSpace.getTotalSet()
nNodes= len(xcTotalSet.nodes)
nElements= len(xcTotalSet.elements)

nNodesRef= [347, 348] # Different Gmsh versions give different results
nElementsRef= [312, 313, 315]

nNodesOk= False
if nNodes in nNodesRef:
   nNodesOk= True
nElementsOk= False
if nElements in nElementsRef:
   nElementsOk= True

'''
print('number of nodes: ', nNodes)
print('number of elements: ', nElements)
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if nNodesOk & nElementsOk :
    print("test "+fname+": ok.")
else:
    lmsg.error(fname+' ERROR.')

# Graphic stuff.
#oh= output_handler.OutputHandler(modelSpace)

#oh.displayBlocks()#setToDisplay= )
#oh.displayFEMesh()#setsToDisplay=[])
#oh.displayLocalAxes()
