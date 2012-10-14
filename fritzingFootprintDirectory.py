'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
import os

from PySide.QtGui import *
from fritzingFootprint import FritzingFootprint


class FritzingFootprintDirectory(dict):
  '''
  Dictionary of Fritzing PCB footprints.
  
  Understands where Fritzing PCB image files live.
  Parses and stores them as objects in dictionary.
  
  Note: no __init__().  Call initSMDWithProgress before use, or another non-GUI init method.
  
  Cache attributes in dictionaries??
  This is a performance issue: we just keep the footprint objects,
  but they might be big and slow (since they are DOM objects.)
  '''
  
  
  def initSMDWithProgress(self, progress):
    '''
    Init for only SMD files.
    Show progress in GUI.
    '''
    count = 0
    
    for fileName in self._fritzingSvgPcbFiles():
      footprint = FritzingFootprint(fileName)
      if footprint.isSMD():
        QApplication.processEvents()
        progress.setValue(count)
        if progress.wasCanceled():
          break;
        print fileName
        self[fileName] = footprint
        count +=1
        #if count > 5:
        #  break
      else:
        print "Not SMD: ", fileName
  
  def initSMD(self):
    # TODO like the above, without GUI
    raise NotImplementedError
    
  '''
  Getters for attributes.
  '''
  def connectorCount(self, fileName):
    return self.footprint[fileName].connectorCount()
  
  
  def pinPad(self, fileName):
    return self.footprint[fileName].pinPad()
  
  
  def landPatternName(self, fileName):
    '''
    Assume fileName is unique and indicative of industry convention name for SMD land pattern.
    '''
    assert fileName in self.pinCount.keys()
    return self.footprint[fileName].landPatternName()
  
    
    
  def _fritzingSvgPcbFiles(self):
    ''' 
    List of filenames.
    All distributed PCB image files.
    '''
    # TODO also core/pcb ?
    # TODO find Fritzing install location
    home = os.path.expanduser('~')
    directoryName = home + '/fritzing-0.7.7b.linux.i386/parts/svg/contrib/pcb/*'
    import glob
    return glob.glob(directoryName)
      
    
  
  def _fritzingSMDSvgPcbFiles(self, desiredPinCount):
    ''' 
    List of filenames.
    Filtered: SMD files with given pin count
    '''
    result = []
    for fileName in self._fritzingSvgPcbFiles():
      footprint = FritzingFootprint(fileName)
      if self._isCompatiblePackage(footprint, connectorCount=desiredPinCount):
        result.append(fileName)
    return result
  
  
  def _isCompatiblePackage(self, footprint, connectorCount):
    '''
    Is a Fritzing package:
    - isSMD
    - connectorCount
    - connectors use canonical names (side effect of connectorCount)
    '''
    return footprint.isSMD() and footprint.connectorCount() == connectorCount