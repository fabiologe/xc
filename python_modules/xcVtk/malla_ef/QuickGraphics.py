# -*- coding: utf-8 -*-

'''Providing the user with a quick and easy way to 
   display results (internal forces, displacements) of an user-defined
   load case.'''

__author__= "Ana Ortega (AO_O) and Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2016 AO_O LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "ana.Ortega@ciccp.es    l.pereztato@ciccp.es"

from miscUtils import LogMessages as lmsg
from solution import predefined_solutions
from xcVtk.malla_ef import vtk_grafico_ef
from xcVtk.malla_ef import Fields
from xcVtk import ControlVarDiagram as cvd


class QuickGraphics(object):
  '''This class is aimed at providing the user with a quick and easy way to 
  display results (internal forces, displacements) of an user-defined
  load case.
  
  :ivar loadCaseName:   name of the load case to be created
  :ivar loadCaseExpr:   expression that defines de load case as a
                   combination of previously defined actions
                   e.g. '1.0*GselfWeight+1.0*GearthPress'
  '''
  def __init__(self,feProblem):
    self.feProblem= feProblem
    self.xcSet= self.feProblem.getPreprocessor.getSets.getSet('total')

  def solve(self,loadCaseName='',loadCaseExpr=''):
    self.loadCaseName=loadCaseName
    self.loadCaseExpr=loadCaseExpr
    preprocessor= self.feProblem.getPreprocessor
    combs=preprocessor.getLoadLoader.getLoadCombinations
    lCase=combs.newLoadCombination(self.loadCaseName,self.loadCaseExpr)
    preprocessor.resetLoadCase()
    combs.addToDomain(self.loadCaseName)
    #Solution
    analysis= predefined_solutions.simple_static_linear(self.feProblem)
    result= analysis.analyze(1)
    combs.removeFromDomain(self.loadCaseName)

  def getDispComponentFromName(self,compName):
    if compName == 'uX':
      return 0
    elif compName == 'uY':
      return 1
    elif compName == 'uZ':
      return 2
    elif compName == 'rotX':
      return 3
    elif compName == 'rotY':
      return 4
    elif compName == 'rotZ':
      return 5
    else:
      lmsg.error('Item '+str(compName) +'is not a valid component. Displayable items are: uX, uY, uZ, rotX, rotY, rotZ')
      return 2

  def getIntForceComponentFromName(self,componentName):
    if componentName[0] in ['N','M']:
      return componentName.lower()
    elif componentName == 'Q1':
      return 'q13'
    elif componentName == 'Q2':
      return 'q23'
    else: #LCPT I don't like this too much, I prefer let the user make the program to crass. Maybe a Warning? 
      lmsg.error('Item '+str(componentName) +'is not a valid component. Displayable items are: N1, N2, N12, M1, M2, M12, Q1, Q2')
      return 'N1'


  def displayDispRot(self,itemToDisp='',setToDisplay=None,fConvUnits=1.0,unitDescription= '',fileName=None):
    '''displays the component of the displacement or rotations in the 
    set of entities.
    
    :param itemToDisp:  component of the displacement ('uX', 'uY' or 'uZ') or the 
                  rotation ('rotX', rotY', 'rotZ') to be depicted 
    :param setToDisplay:   set of entities to be represented (default to all entities)
    :param fConvUnits:     factor of conversion to be applied to the results (defalts to 1)
    :param unitDescription: string describing units like '[mm] or [cm]'
    :param fileName:        name of the file to plot the graphic. Defaults to None,
                            in that case an screen display is generated
    '''
    if(setToDisplay):
      self.xcSet= setToDisplay
    else:
      lmsg.warning('QuickGraphics::displayDispRot; set to display not defined; using previously defined set (total if None).')
    vCompDisp= self.getDispComponentFromName(itemToDisp)
    nodSet= self.xcSet.getNodes
    for n in nodSet:
      n.setProp('propToDisp',n.getDisp[vCompDisp])
    field= Fields.ScalarField('propToDisp',"getProp",None,fConvUnits)
    defDisplay= vtk_grafico_ef.RecordDefDisplayEF()
    defDisplay.displayMesh(xcSet=self.xcSet,field=field,diagrams= None, fName=fileName,caption=self.loadCaseName+' '+itemToDisp+' '+unitDescription+' '+self.xcSet.name)

  def displayIntForc(self,itemToDisp='',setToDisplay=None,fConvUnits=1.0,unitDescription= '',fileName=None):
    '''displays the component of internal forces in the 
    set of entities as a scalar field (i.e. appropiated for shell elements).
    
    :param itemToDisp:   component of the internal forces ('N1', 'N2', 'N12', 'M1', 'M2', 'M12', 'Q1', 'Q2')
                         to be depicted 
    :param setToDisplay: set of entities to be represented (default to all entities)
    :param fConvUnits:   factor of conversion to be applied to the results (defalts to 1)
    :param unitDescription: string like '[kN/m] or [kN m/m]'
    :param fileName:        name of the file to plot the graphic. Defaults to None,
                            in that case an screen display is generated
    '''
    if(setToDisplay):
      self.xcSet= setToDisplay
    else:
      lmsg.warning('QuickGraphics::displayIntForc; set to display not defined; using previously defined set (total if None).')
    vCompDisp= self.getIntForceComponentFromName(itemToDisp)
    elSet= self.xcSet.getElements
    propName= 'propToDisp_'+str(itemToDisp)
    for e in elSet:
      e.getResistingForce()
      mat= e.getPhysicalProperties.getVectorMaterials
      e.setProp(propName,mat.getMeanGeneralizedStressByName(vCompDisp))
    field= Fields.ExtrapolatedProperty(propName,"getProp",self.xcSet,fUnitConv= fConvUnits)
    defDisplay= vtk_grafico_ef.RecordDefDisplayEF()
    field.display(defDisplay=defDisplay,fName=fileName,caption=self.loadCaseName+' '+itemToDisp+' '+unitDescription +' '+self.xcSet.name)

  def displayIntForcDiag(self,itemToDisp='',setToDisplay=None,fConvUnits=1.0,scaleFactor=1.0,unitDescription= '',viewName='XYZPos',fileName=None):
    '''displays the component of internal forces in the 
    set of entities as a diagram over lines (i.e. appropiated for beam elements).
    
    :param itemToDisp:   component of the internal forces ('N', 'Qy' (or 'Vy'), 'Qz' (or 'Vz'), 
                         'My', 'Mz', 'T') to be depicted 
    :param setToDisplay: set of entities (elements of type beam) to be represented
    :param fConvUnits:   factor of conversion to be applied to the results (defalts to 1)
    :param scaleFactor:  factor of scale to apply to the diagram display
    :param unitDescription: string like '[kN/m] or [kN m/m]'
    :param viewName:     name of the view  that contains the renderer (possible
                         options: "XYZPos", "XPos", "XNeg","YPos", "YNeg",
                         "ZPos", "ZNeg") (defaults to "XYZPos")
    :param fileName:     name of the file to plot the graphic. Defaults to None,
                         in that case an screen display is generated
    '''
    if(setToDisplay):
      self.xcSet= setToDisplay
    else:
      lmsg.warning('QuickGraphics::displayIntForc; set to display not defined; using previously defined set (total if None).')
    diagram= cvd.ControlVarDiagram(scaleFactor= scaleFactor,fUnitConv= fConvUnits,sets=[self.xcSet],attributeName= "intForce",component= itemToDisp)
    diagram.agregaDiagrama()
    defDisplay= vtk_grafico_ef.RecordDefDisplayEF()
    defDisplay.viewName=viewName
    defDisplay.setupGrid(self.xcSet)
    defDisplay.defineEscenaMalla(None)
    defDisplay.appendDiagram(diagram) #Append diagram to the scene.

    caption= self.loadCaseName+' '+itemToDisp+' '+unitDescription +' '+self.xcSet.name
    defDisplay.displayScene(caption=caption,fName=fileName)

