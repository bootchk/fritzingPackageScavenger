'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
import os
from xml.dom.minidom import parse
# import xml.etree.ElementTree as ET  # alternative parsing

from fritzingFootprintLayer import FritzingFootprintLayer
      
      
class FritzingFootprint(object):
  '''
  Wrapper around DOM (from XML) that is a Fritzing footprint (SVG image for a view e.g. PCB)
  
  Knows:
    - isSMD
    - its copper layers, as FritzingFootprintLayer
    - connectorCount
    - pinpad
    - landPatternName
  '''

  def __init__(self, filename):
    '''
    Assert filename is XML meeting Fritzing DTD for a footprint (breadboard, schematic, or PCB image)
    '''
    self.filename = filename
    self.copperLayer = []
    
    self.dom = parse(filename)  # throws ExpatError on XML parsing failure
    self._parseCopperLayers()

    

  def _parseCopperLayers(self):
    '''
    Create objects for copper layers.
    At most two. None if absent.
    '''
    self.copperLayer.append(self._createCopperLayer(0))
    self.copperLayer.append(self._createCopperLayer(1))


  def isSMD(self):
    '''
    Is SMD/SMT:
    - has only one copper layer: copper1. By definition surface mount device has only one surface i.e. layer.
    - has no circles (through holes).  Some through hole components have only one layer (in err?)
    
    A heuristic.  Aberrant footprints use copper0, or both copper1 and copper0,
    or have holes.  Most will not be aberrant.
    
    Example: <g id="copper1"> etc.
    
    !!! Note groups may still be aberrant: fail to have connectors.
    '''
    if self.copperLayer[1] and not self.copperLayer[0] and not self.copperLayer[1].hasHole():
      return True


  def connectorCount(self):
    ''' !!! for copper1.  Could be more general, but then need to check consistency among layers. '''
    return self.copperLayer[1].connectorCount()
  
  def pinPad(self):
    ''' !!! for copper1.  Could be more general, but then need to check consistency among layers. '''
    return self.copperLayer[1].pinPad()
  
  def landPatternName(self):
    return self._basenameLessExtension(self.filename)
  
  
  def _basenameLessExtension(self, filename):
    ''' File specifier less path prefix less extension suffix. '''
    return os.path.splitext(os.path.basename(filename))[0]
  
  
  def _createCopperLayer(self, layerOrdinal):
    ''' Return object for copper layer with layerOrdinal  or None. '''
    for each in self._groupsSVG():
      if self._groupIsCopperLayer(each, layerOrdinal):
        return FritzingFootprintLayer(each, parentFootprint=self)
    return None
  
  
  def _groupsSVG(self):
    groups = self.dom.getElementsByTagName("g")
    for each in groups:
      yield each
  
  def _groupIsCopperLayer(self, group, layerOrdinal):
    ''' Is this group a Fritzing copper layer with attribute "id" equal "copper" suffixed by layerOrdinal. '''
    result = False
    if group.hasAttribute('id'):
      if group.getAttribute('id') == 'copper' + str(layerOrdinal):
        result = True
    return result
  
  
  
      