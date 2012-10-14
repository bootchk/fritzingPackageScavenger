'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
import re

class FritzingFootprintLayer(object):
  '''
  Fritzing layer of footprint
  !!! as represented by XML tree. 
  '''
  
  def __init__(self, group):
    self.group = group
    self.pinpad = None   
    self.connectorPattern = re.compile("connector[0-9]+(pin|pad)")
    
  
  def pinPad(self):
    '''
    "pin" or "pad" as consistently seen
    !!! Side effect of connectorCount()
    '''
    return self.pinpad
  
  
  def hasHole(self):
    '''
    Circle in copper layer is a drilled hole.
    Assert self is a copper layer, else result is meaningless,
    since circle in e.g. silkscreen layer is just art.
    '''
    return len(self.group.getElementsByTagName('circle')) > 0
  
  
  def connectorCount(self):
    '''
    Count connectors.
    
    !!! Side effect: check consistency and establish pinpad
    '''
    connectorCount = 0
    for each in self.group.childNodes:
      '''
      xml.minidom an element has child nodes of different types
      and only ELEMENT_NODE have attributes, TEXT_NODE is just text.
      We could use xml.etree instead, it is more Pythonic
      but might be less understandable to XML DOM programmers.
      '''
      if each.nodeType == each.ELEMENT_NODE:
        if each.hasAttribute('connectorname') and  self._checkConnectorID(each):
            connectorCount += 1
        
    if not connectorCount > 0:
      print "Fritzing PCB SVG without name on each connector???"
    return connectorCount
  
  
  def _checkConnectorID(self, element):
    '''
    Assert element is a connector.
    Check:
    - has an id
    - id matches canonical pattern
    - id is consistent with other connectors
    '''
    if not element.hasAttribute('id'): # associates to svgId in .fzp
      return False
    else:
      connectorId = element.getAttribute('id')
      matchResult = self.connectorPattern.match(connectorId)
      if not matchResult: # No match
        print "Connector id bad or inconsistent", connectorId
        return False
      elif not self._checkPinpad(matchResult.group(1)):
        print "Connector 'pin' or 'pad' inconsistent:", connectorId
        return False
      else:
        return True


  def _checkPinpad(self, pinpadValue):
    '''
    Does pinpadValue match what seen in previous connectors?
    '''
    if self.pinpad is None:
      self.pinpad = pinpadValue
      return True
    else:
      return self.pinpad == pinpadValue
      
        
    
    