# -*- coding: utf-8 -*-

''' Display nice images of the model. '''

__author__= "Luis C. Pérez Tato (LCPT) Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com  ana.Ortega.Ort@gmail.com"


import sys
import vtk
import xc_base
import geom
from xcVtk import ScreenAnnotation as sa
from miscUtils import LogMessages as lmsg


class RecordDefGrid(object):
  '''Provides the variables involved in the VTK grid representation
  Attributes:
    xcSet:     set to be represented
    entToLabel:  entities to be labeled (defaults to "nodos")
    cellType:    specifies the type of data cells (defaults to "nil"). Data cells are simple 
                 topological elements like points, lines, polygons and tetrahedra of which 
                 visualization data sets are composed.
    uGrid:       unstructure grid (defaults to None). An unstructure grid is a concrete 
                 implementation of a vtk data set; represents any combination of any cell
                 types. This includes 0D (e.g. points), 1D (e.g., lines, polylines), 
                 2D (e.g., triangles, polygons), and 3D (e.g., hexahedron, tetrahedron, polyhedron, etc.).
    dispScale:   (defaults to 0.0)

  '''
  def __init__(self):
    self.xcSet= None
    self.entToLabel= "nodos"
    self.cellType= "nil"
    self.uGrid= None
    self.dispScale= 0.0

  def getBND(self):
    ''' Returns the grid boundary'''
    bounds= self.uGrid.GetPoints().GetBounds()
    retval= geom.BND3d(geom.Pos3d(bounds[0],bounds[2],bounds[4]),geom.Pos3d(bounds[1],bounds[3],bounds[5]))
    return retval    

class RecordDefDisplay(object):
  ''' Provides de variables to define the output device.
  Attributes:
    renderer:    specification of renderer. A renderer is an object that
                 controls the rendering process for objects. Rendering is the 
                 process of converting geometry, a specification for lights, and
                 a camera view into an image. (defaults to None)
    renWin:      rendering window (defaults to None). A rendering window is a window in a
                 graphical user interface where renderers draw their images. 
    windowWidth: resolution expresed in pixels in the width direction of the window 
                 (defaults to 800)
    windowHeight: resolution expresed in pixels in the height direction of the window 
                 (defaults to 600)
    viewName:    name of the view that contains the renderer (defaults to "XYZPos")
    zoom:        (defaults to 1.0)
    bgRComp:     red component (defaults to 0.65)
    bgGComp:     green component (defaults to 0.65)
    bgBComp:     blue component (defaults to 0.65)
  '''
  def __init__(self):
    self.renderer= None
    self.renWin= None
    self.windowWidth= 800
    self.windowHeight= 600
    self.annotation= sa.ScreenAnnotation()
    self.viewName= "XYZPos"
    self.zoom= 1.0
    self.bgRComp= 0.65
    self.bgGComp= 0.65
    self.bgBComp= 0.65

  def ViewYNeg(self):
    '''View from negative Y axis (Y-)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,0,1)
    cam.SetPosition(0,-100,0)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewYPos(self):
    '''View from positive Y axis (Y+)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,0,1)
    cam.SetPosition(0,100,0)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewXNeg(self):
    '''View from negative X axis (X-)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,0,1)
    cam.SetPosition(-100,0,0)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewXPos(self):
    '''View from positive X axis (X+)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,0,1)
    cam.SetPosition(100,0,0)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewZPos(self):
    '''View from positive Z axis (Z+)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,1,0)
    cam.SetPosition(0,0,100)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewZNeg(self):
    '''View from negative Z axis (Z-)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(0,1,0)
    cam.SetPosition(0,0,-100)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def ViewXYZPos(self):
    '''View from point (1,1,1)'''
    self.renderer.ResetCamera()
    cam= self.renderer.GetActiveCamera()
    cam.SetViewUp(-1,-1,1)
    cam.SetPosition(100,100,100)
    cam.SetParallelProjection(1)
    cam.Zoom(self.zoom)
    self.renderer.ResetCameraClippingRange()

  def defineView(self):
    '''Sets the view for the following predefined viewNames:
    "ZPos","ZNeg","YPos","YNeg","XPos","XNeg","XYZPos"
    '''
    if(self.viewName=="ZPos"):
      self.ViewZPos()
    elif(self.viewName=="ZNeg"):
      self.ViewZNeg()
    elif(self.viewName=="YPos"):
      self.ViewYPos()
    elif(self.viewName=="YNeg"):
      self.ViewYNeg()
    elif(self.viewName=="XPos"):
      self.ViewXPos()
    elif(self.viewName=="XNeg"):
      self.ViewXNeg()
    elif(self.viewName=="XYZPos"):
      self.ViewXYZPos()
    else:
      sys.stderr.write("View name: '"+self.viewName+"' unknown.")

  def setupAxes(self):
    '''Add an vtkAxesActor to the renerer.'''
    bnd= self.gridRecord.getBND()
    offsetVector= bnd.diagonal*0.1
    offset= offsetVector.getModulo()
    axesPosition= bnd.pMin-offsetVector
    transform = vtk.vtkTransform()
    transform.Translate(axesPosition.x, axesPosition.y, axesPosition.z)
    axes= vtk.vtkAxesActor()
    #  The axes are positioned with a user transform
    axes.SetUserTransform(transform)

    length= offset
    axes.SetTotalLength(length,length,length)

    textSize= 10*offset
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleMode(False)
    axes.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(textSize)
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleMode(False)
    axes.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(textSize)
    axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleMode(False)
    axes.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(textSize)

    # properties of the axes labels can be set as follows
    # this sets the x axis label to red
    # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(1,0,0);
 
    # the actual text of the axis label can be changed:
    # axes.SetXAxisLabelText("test");
    self.renderer.AddActor(axes)

  def setupWindow(self,caption= ''):
    '''sets the rendering window. A rendering window is a window in a
       graphical user interface where renderers draw their images.
    '''
    self.renWin= vtk.vtkRenderWindow()
    self.renWin.SetSize(self.windowWidth,self.windowHeight)
    self.renWin.AddRenderer(self.renderer)
    #Axes
    self.setupAxes()

    #Time stamp and window decorations.
    if(caption==''):
      lmsg.warning('setupWindow; window caption empty.')
    vtkCornerAnno= self.annotation.getVtkCornerAnnotation(caption)
    self.renderer.AddActor(vtkCornerAnno)
    return self.renWin

  def setupWindowInteractor(self):
    '''sets the window interactor, which provides a platform-independent
    interaction mechanism for mouse/key/time events.
    '''
    iren= vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(self.renWin)
    iren.SetSize(self.windowWidth,self.windowHeight)
    iren.Initialize()
    return iren

  def displayScene(self,caption= '', fName= None):
    self.defineView()
    self.setupWindow(caption)
    if(fName):
      self.plot(fName)
    else:
      iren= self.setupWindowInteractor()
      iren.Start()

  def muestraEscena(self):
    lmsg.warning('muestraEscena is deprecated. Use displayScene')
    self.displayScene('noCaption', None)

  def setupGrid(self,xcSet):
    ''' Parameters:
       xcSet:     set to be represented
    '''
    self.gridRecord= RecordDefGrid()
    self.gridRecord.xcSet= xcSet
    return self.gridRecord

  def displayGrid(self, caption= ''):
    '''Displays the grid in the output device'''
    self.defineEscenaMalla(None)
    self.displayScene(caption)

  def plot(self,fName):
    '''Plots window contents'''
    w2i = vtk.vtkWindowToImageFilter()
    writer = vtk.vtkJPEGWriter()
    w2i.SetInput(self.renWin)
    w2i.Update()
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.SetFileName(fName)
    self.renWin.Render()
    w2i.Update()
    writer.Write()
 
 
