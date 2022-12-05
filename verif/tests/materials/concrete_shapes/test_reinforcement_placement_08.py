# -*- coding: utf-8 -*-
''' Trivial test to check that shear reinforcing bars are modelled as intended
    (shear reinforcement in direction I is placed perpendicular to bottom reinforcement at the bottom and so on...).

'''
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2022, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import math
import geom
import xc
from model import predefined_spaces
from materials.ec2 import EC2_materials
from materials.ec2 import EC2_limit_state_checking
from materials.sections.fiber_section import def_simple_RC_section
from actions import load_cases
from actions import combinations as combs
from postprocess import limit_state_data as lsd
from postprocess.config import default_config
from postprocess import RC_material_distribution

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler

modelSpace= predefined_spaces.StructuralMechanics3D(nodes)

# Define materials
## Materials.
concrete= EC2_materials.C20
steel= EC2_materials.S500C
## Geometry
b= 1.0
h= 0.5
## RC section.
rcSection= def_simple_RC_section.RCRectangularSection(name='BeamSection', width= 1.0, depth= h, concrType= concrete, reinfSteelType= steel)
dummySection= rcSection.defElasticMembranePlateSection(preprocessor) # Elastic membrane plate section.


# Problem geometry.
span= 2.5

## K-points.
points= preprocessor.getMultiBlockTopology.getPoints
pt1= points.newPoint(geom.Pos3d(0,0,0))
pt2= points.newPoint(geom.Pos3d(span,0,0))
pt3= points.newPoint(geom.Pos3d(span,b,0))
pt4= points.newPoint(geom.Pos3d(0,b,0))
## Surface.
surfaces= preprocessor.getMultiBlockTopology.getSurfaces
s= surfaces.newQuadSurfacePts(pt1.tag,pt2.tag,pt3.tag,pt4.tag)
s.nDivI= 20
s.nDivJ= 10

# Generate mesh.
seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= rcSection.name
elem= seedElemHandler.newElement("ShellMITC4",xc.ID([0,0,0,0]))
s.genMesh(xc.meshDir.I)

# Constraints.
fixedNodes= list()
for n in s.nodes:
    pos= n.getInitialPos3d
    if(abs(pos.x)<1e-3):
        fixedNodes.append(n)
for n in fixedNodes:
    modelSpace.fixNode000_F0F(n.tag)

# Actions
loadCaseManager= load_cases.LoadCaseManager(preprocessor)
loadCaseNames= ['load']
loadCaseManager.defineSimpleLoadCases(loadCaseNames)

## load pattern.
load= xc.Vector([0,0,-160e3])
cLC= loadCaseManager.setCurrentLoadCase('load')
for e in s.elements:
    e.vector3dUniformLoadGlobal(load)

## Load combinations
combContainer= combs.CombContainer()
### ULS combination.
combContainer.ULS.perm.add('combULS01','1.6*load')
xcTotalSet= preprocessor.getSets.getSet('total')
cfg= default_config.get_temporary_env_config()
lsd.LimitStateData.envConfig= cfg
### Save internal forces.
limitState= lsd.shearResistance # Shear limit state.
#limitState= lsd.normalStressesResistance # Normal stresses limit state.
limitState.saveAll(combContainer,xcTotalSet) 

# Define reinforcement.
# Reinforcement row scheme:
#
#    |  o    o    o    o    o    o    o    o    o    o  |
#    <->           <-->                               <-> 
#    lateral      spacing                           lateral
#     cover                                          cover
#

# Geometry of the reinforcement.
nBarsA= 7 # number of bars.
cover= 0.035 # concrete cover.
lateralCover= cover # concrete cover for the bars at the extremities of the row.
spacing= (rcSection.b-2.0*lateralCover)/(nBarsA-1)

## First row.
mainBarDiameter= 25e-3 # Diameter of the reinforcement bar.
rowA= def_simple_RC_section.ReinfRow(rebarsDiam= mainBarDiameter, rebarsSpacing= spacing, width= rcSection.b, nominalCover= cover, nominalLatCover= lateralCover)

## Second row.
rowB= def_simple_RC_section.ReinfRow(rebarsDiam= mainBarDiameter, rebarsSpacing= spacing, width= rcSection.b-spacing, nominalCover= cover, nominalLatCover= lateralCover+spacing/2.0)

## Third row.
smallBarDiameter= 10e-3
rowC= def_simple_RC_section.ReinfRow(rebarsDiam= smallBarDiameter, rebarsSpacing= spacing, width= rcSection.b, nominalCover= cover, nominalLatCover= lateralCover+spacing/2.0)

## Longitudinal shear reinforcement.
shearReinfABarDiameter= 8e-3
shearReinfABarArea=  math.pi*(shearReinfABarDiameter/2.0)**2
shearReinfA= def_simple_RC_section.ShearReinforcement(familyName= "shearReinfA", nShReinfBranches= 3, areaShReinfBranch= shearReinfABarArea, shReinfSpacing= 0.15, angAlphaShReinf= math.pi/2.0)

## Transverse shear reinforcement.
shearReinfBBarDiameter= 6e-3
shearReinfBBarArea=  math.pi*(shearReinfBBarDiameter/2.0)**2
shearReinfB= def_simple_RC_section.ShearReinforcement(familyName= "shearReinfB", nShReinfBranches= 2, areaShReinfBranch= shearReinfBBarArea, shReinfSpacing= 0.15, angAlphaShReinf= math.pi/2.0)

## Define reinforcement directions.
reinforcementUpVector= geom.Vector3d(0,0,1) # Z+ this vector defines the meaning
                                            # of top reinforcement ot bottom
                                            # reinforcement.
reinforcementIVector= geom.Vector3d(1,0,0) # Y+ this vector defines the meaning
                                           # of reinforcement I (parallel to
                                           # this vector) and
                                           # reinforcement II (normal to this
                                           # vector)

## Store element reinforcement. Assign to each element the properties
# that will be used to define its reinforcement on each direction:
#
# - baseSection: RCSectionBase derived object containing the geometry
#                and the material properties of the reinforcec concrete
#                section.
# - reinforcementUpVector: reinforcement "up" direction which defines
#                          the position of the positive reinforcement
#                          (bottom) and the negative reinforcement
#                          (up).
# - reinforcementIVector: (for slabs) direction corresponding to 
#                         the first RC section
# - bottomReinforcement: LongReinfLayers objects defining the 
#                        reinforcement at the bottom of the section.
# - topReinforcement: LongReinfLayers objects defining the 
#                     reinforcement at the top of the section.
# - shearReinforcement: ShearReinforcement objects defining the 
#                       reinforcement at the bottom of the section.
for e in s.elements:
    e.setProp("baseSection", rcSection)
    e.setProp("reinforcementUpVector", reinforcementUpVector) 
    e.setProp("reinforcementIVector", reinforcementIVector)
    e.setProp("bottomReinforcementI", def_simple_RC_section.LongReinfLayers([rowC]))
    e.setProp("topReinforcementI", def_simple_RC_section.LongReinfLayers([rowA]))
    e.setProp("bottomReinforcementII", def_simple_RC_section.LongReinfLayers([rowC]))
    e.setProp("topReinforcementII", def_simple_RC_section.LongReinfLayers([rowC]))
    x= e.getPosCentroid(True).x
    if(x<2.0):
        topReinforcementI= e.getProp("topReinforcementI")
        topReinforcementI.append(rowB)
        e.setProp("topReinforcementI", topReinforcementI)
        e.setProp('shearReinforcementI',shearReinfA)
        if(x<0.25):
            e.setProp('shearReinforcementII',shearReinfB)
        
#### Define sections.

# Define spatial distribution of reinforced concrete sections.
reinfConcreteSectionDistribution= RC_material_distribution.RCMaterialDistribution()
reinfConcreteSectionDistribution.assignFromElementProperties(elemSet= xcTotalSet.getElements)

# Checking shear.
outCfg= lsd.VerifOutVars(listFile='N',calcMeanCF='Y')
outCfg.controller= EC2_limit_state_checking.ShearController(limitState.label)
#outCfg.controller= EC2_limit_state_checking.BiaxialBendingNormalStressController(limitState.label)
outCfg.controller.verbose= False # Don't display log messages.
feProblem.logFileName= "/tmp/erase.log" # Ignore warning messagess about computation of the interaction diagram.
feProblem.errFileName= "/tmp/erase.err" # Ignore warning messagess about maximum error in computation of the interaction diagram.
meanCFs= lsd.shearResistance.check(reinfConcreteSectionDistribution, outCfg)
#meanCFs= lsd.normalStressesResistance.check(reinfConcreteSectionDistribution, outCfg)
feProblem.errFileName= "cerr" # From now on display errors if any.
feProblem.logFileName= "clog" # From now on display warnings if any.

relError= list() # Relative errors.
refMeanCFs= [0.3466510216208219, 0.0803971610130269]
for meanCF, refMeanCF in zip(meanCFs, refMeanCFs):
    relError.append(abs(meanCF-refMeanCF)/refMeanCF)

'''
print('meanCFs= ', meanCFs)
print("relError[0]= ",relError[0])
print("relError[1]= ",relError[1])
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (relError[0]<1e-4) and (relError[1]<1e-4):
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')

# #########################################################
# # Graphic stuff.
# from postprocess import output_handler
# from postprocess.control_vars import *
# oh= output_handler.OutputHandler(modelSpace)

# ## Uncomment to display the mesh
# #oh.displayFEMesh()

# ## Uncomment to display the element axes
# oh.displayLocalAxes()

# ## Uncomment to display the loads
# #oh.displayLoads()

# ## Uncomment to display the vertical displacement
# #oh.displayDispRot(itemToDisp='uY')
# #oh.displayNodeValueDiagram(itemToDisp='uX')

# ## Uncomment to display the reactions
# #oh.displayReactions()

# ## Uncomment to display the internal force
# #oh.displayIntForcDiag('Mz')
# #oh.displayIntForcDiag('Vy')

# # Uncomment to display the results for the limit state
# argument= 'CF'
# #Load properties to display:
# exec(open(cfg.projectDirTree.getVerifShearFile()).read())
# #exec(open(cfg.projectDirTree.getVerifNormStrFile()).read())
# oh.displayFieldDirs1and2(limitStateLabel= limitState.label,argument=argument,setToDisplay=xcTotalSet,component=None,fileName=None,defFScale=0.0,rgMinMax= None)

cfg.cleandirs()  # Clean after yourself.
