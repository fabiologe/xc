# -*- coding: utf-8 -*-
''' Horizontal cantilever under horizontal load at its tip.'''

from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import math
import xc
from solution import predefined_solutions
from model import predefined_spaces
from materials import typical_materials

# Material properties
E= 2.1e6*9.81/1e-4 # Elastic modulus (Pa)
nu= 0.3 # Poisson's ratio
G= E/(2*(1+nu)) # Shear modulus

# Cross section properties (IPE-80)
A= 7.64e-4 # Cross section area (m2)
Iy= 80.1e-8 # Cross section moment of inertia (m4)
Iz= 8.49e-8 # Cross section moment of inertia (m4)
J= 0.721e-8 # Cross section torsion constant (m4)

# Geometry
L= 1.5 # Bar length (m)

# Load
M= 1.5e3 # Moment magnitude (kN)

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor   
nodes= preprocessor.getNodeHandler
modelSpace= predefined_spaces.StructuralMechanics3D(nodes)
n1= nodes.newNodeXYZ(0,0.0,0.0)
n2= nodes.newNodeXYZ(L,0.0,0.0)


# Geometric transformation(s)
lin= modelSpace.newLinearCrdTransf("lin",xc.Vector([0,-1,0]))
# Materials
sectionProperties= xc.CrossSectionProperties3d()
sectionProperties.A= A; sectionProperties.E= E; sectionProperties.G= G
sectionProperties.Iz= Iz; sectionProperties.Iy= Iy; sectionProperties.J= J
section= typical_materials.defElasticSectionFromMechProp3d(preprocessor, "section",sectionProperties)

# Elements definition
elements= preprocessor.getElementHandler
elements.defaultTransformation= lin.name
elements.defaultMaterial= section.name
beam3d= elements.newElement("ElasticBeam3d",xc.ID([n1.tag,n2.tag]))


# Constraints
modelSpace.fixNode000_000(n1.tag)

# Load definition.
lp0= modelSpace.newLoadPattern(name= '0')

lp0.newNodalLoad(n2.tag, xc.Vector([0,0,0,0,M,0]))
# We add the load case to domain.
modelSpace.addLoadCaseToDomain(lp0.name)

# Solution
analysis= predefined_solutions.simple_static_linear(feProblem)
result= analysis.analyze(1)


delta= n2.getDisp[2]  # z displacement of node 2
theta= n2.getDisp[4]  # y rotation of the node

elements= preprocessor.getElementHandler

beam3d.getResistingForce()
M1= beam3d.getMz1
V= beam3d.getVz()



deltaRef= -(M*L**2/(2*E*Iz))
ratio1= abs(delta-deltaRef)/deltaRef
ratio2= abs(M1+M)/M
thetaRef= (M*L/(E*Iz))
ratio3= abs(theta-thetaRef)/thetaRef

# Check getMz1 and getMz2 (LP 28/04/2024).
Mz1= beam3d.getMz1
MRef= -M
Mz2= beam3d.getMz2
ratio4= math.sqrt((MRef-Mz1)**2+(MRef-Mz2)**2)

# Check getVy1 and getVy2 (LP 28/04/2024).
Vy1= beam3d.getVy1
Vy2= beam3d.getVy2
ratio5= math.sqrt(Vy1**2+Vy2**2)

''' 
print("delta prog.= ", delta)
print("delta ref.= ", deltaRef)
print("ratio1= ",ratio1)
print("M1= ",M1)
print("ratio2= ",ratio2)
print("theta prog.= ", theta)
print("theta ref.= ", thetaRef)
print("ratio3= ",ratio3)
print('MRef= ', MRef/1e3, 'Mz1= ', Mz1/1e3, ' Mz2= ', Mz2/1e3, ' ratio4= ', ratio4)
print('Vy1Ref= ', 0/1e3, 'Vy1= ', Vy1/1e3, ' Vy2= ', Vy2/1e3, ' ratio5= ', ratio5)
 '''

cumple= (abs(ratio1)<1e-5) & (abs(ratio2)<1e-5) & (abs(ratio3)<1e-10) & (abs(ratio4)<1e-10) & (abs(ratio5)<1e-10)
import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if cumple:
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')

# # Graphic stuff.
# from postprocess import output_handler
# oh= output_handler.OutputHandler(modelSpace)
# # oh.displayFEMesh()#setsToDisplay= [columnSet, pileSet])
# # oh.displayDispRot(itemToDisp='uX', defFScale= 100.0)
# oh.displayLocalAxes()
# oh.displayLoads()
# # oh.displayIntForcDiag('N')
# oh.displayIntForcDiag('Mz')
# oh.displayIntForcDiag('Vy')
# # # oh.displayIntForcDiag('My')
# # # oh.displayIntForcDiag('Vz')
# #oh.displayIntForcDiag('T')
# #oh.displayLocalAxes()
