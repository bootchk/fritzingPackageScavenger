'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
import os
import glob
from xml.parsers.expat import ExpatError

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
      try:
        footprint = FritzingFootprint(fileName)
      except ExpatError:
        print "Failed to parse", fileName
        continue
      
      if footprint.isSMD():
        QApplication.processEvents()
        progress.setValue(count)
        if progress.wasCanceled():
          break;
        print fileName
        
        '''
        !!! If there are many files with same name in different directories,
        a later one (in order directories are searched) replaces earlier one.
        TODO tell later directory
        '''
        if fileName in self:
          print "Replacing earlier definition with: ", fileName
          
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
    
    result = []
    for directoryName in self._fritzingSvgPcbDirectories():
      print "Searching directory for svg files: ", directoryName
      # !!! Don't return extraneous .txt etc. files
      # !!! Does not catch .SVG
      result = result + glob.glob(directoryName + '/*.svg')
    return result
  
  
  def _fritzingSvgPcbDirectories(self):
    ''' 
    Generates directories where Fritzing PCB SVG files can be found. 
    
    !!! Note order defines what we believe to be the most authoritative,
    since later files replace earlier with same name (see note elsewhere.)
    Thus the order defines user created files as most authoritative.
    '''
    # TODO also core/pcb ?
    # TODO find Fritzing install location
    home = os.path.expanduser('~')
    # Distributed with Fritzing
    yield home + '/fritzing-0.7.7b.linux.i386/parts/svg/contrib/pcb'
    yield home + '/fritzing-0.7.7b.linux.i386/parts/svg/core/pcb'
    # Local user created
    yield home + '/.config/Fritzing/parts/svg/user/pcb'
    
  
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