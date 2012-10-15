'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
import sys
from fritzingFootprintDirectory import FritzingFootprintDirectory
from partFactory import AnySMDPartFactory
from gui import App

'''
TODO

generated .fzp filename follow conventions?


more robust, cross-platform find Fritzing package directory.

cross-platform finding user home/.config/Fritzing directory: see partFactory

Mystery Part 3 schematic is flaky?

Generate XML in bins/user so part is immediately visible? (for now, Fritzing part search for "SMD")
'''


class PackageScavengerApp(object):
  '''
  app to scavenge existing SMD packages and generate SMD packages for Mystery Part ( TODO and generic ic's)
  
  A utility for use with Fritzing app.
  '''
  
  def __init__(self):
    self.partFactory = AnySMDPartFactory()
  
  

  def runBatch(self):
    ''' Produce Mystery SMD package for all existing SMD footprints. '''
    desiredPinCount = 2 # should be arg.  For now, use 2 or 3.  For Generic IC, many?
    directory = FritzingFootprintDirectory()
    directory.initSMD()
    count = 0
    for filename, footprint in directory.iteritems():
      if footprint.connectorCount() == desiredPinCount:
        outFileNameFzp = self.partFactory.produce(footprint)
        # Sanity check written fzp file is valid XML.  Uncomment for debug
        from xml.dom.minidom import parse
        outDom = parse(outFileNameFzp)
        count += 1
        if count > 5: # Temporary: limit to 5
          break
      

  def runInteractive(self):
    # Create and run GUI
    App(sys.argv)  # exec_'s itself
    return
  

if __name__ == '__main__':
    app = PackageScavengerApp()
    app.runInteractive()