# -*- coding: utf-8 -*-
from __future__ import division

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2016, AOO and LCPT"
__license__= "GPL"
__version__= "1.0"
__email__= "l.pereztato@gmail.com  ana.Ortega.Ort@gmail.com"

#based on the Maria Garlock's papers:
#file: L4_-_Arches_Jan_11_-_final.pdf
#file: L8-_Tied_Arches_Jan_10.pdf

import math

class ArchBridgeRoughModelBase(object):
  ''' Base class for arch bridge rough models
  Attributes:
    d: rise (depth) of the arch at midspan
    L: horizontal distance between supports
  '''
  def __init__(self,L,d):
    self.d= d # rise (depth) of the arch at midspan
    self.L= L # horizontal distance between supports

  #*Uniformly distributed loads
  #Abutment reactions
  def getQunfVabtm(self,qunif):
    '''Vertical reaction at each abutment due to a uniform load.
    Attributes:
       qunif: uniformly distributed load applied on the deck
    '''
    return qunif*self.L/2.0
  def getQunfHabtm(self,qunif):
    '''Horizontal reaction at each abutment due to a uniform load.
    Attributes:
       qunif: uniformly distributed load applied to the arch
    '''
    return qunif*self.L**2/8.0/self.d
