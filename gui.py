'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''
from PySide.QtCore import *
from PySide.QtGui import *

from fritzingFootprintDirectory import FritzingFootprintDirectory
from partFactory import AnySMDPartFactory


class PackageListWidget(QListWidget):
  
  def __init__(self, directory, initialConnectorCount):
    super(PackageListWidget, self).__init__()
    self.directory = directory  # from which populated
    self.model = {} # map from displayedName to footprint
    self.populate(initialConnectorCount)


  def populate(self, count):
    '''
    sorted list filtered by count
    '''
    self.clear()
    self.model.clear()
    
    # filter on connectorCount
    for footprint in self.directory.values():
      if footprint.connectorCount() == count:
        displayedName = footprint.landPatternName()
        self.addItem(displayedName)
        self.model[displayedName] = footprint
    
    self.sortItems()
    return self.count()


  def chosenFootprint(self):
    return self.model[self.currentItem().text()]
    
    
    
class ScavengeDialog(QDialog):
  '''
  Let user choose SMD package to add to Mystery SMD family.
  '''

  initialConnectorCount = 2
  
  def __init__(self, directory):
    QDialog.__init__(self)
    
    # Create component widgets
    connectorCountSpinBox = QSpinBox()
    connectorCountSpinBox.setRange(1, 132)  # 132 is arbitrary
    connectorCountSpinBox.setValue(ScavengeDialog.initialConnectorCount)
    
    spinLayout = QHBoxLayout()
    spinLayout.addWidget(QLabel("Connector count: "))
    spinLayout.addWidget(connectorCountSpinBox)
    
    listWidget = PackageListWidget(directory, ScavengeDialog.initialConnectorCount)
    self.listWidget = listWidget
    
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                 | QDialogButtonBox.Cancel)
    self.buttonBox = buttonBox
    
    # Layout components
    dialogLayout = QVBoxLayout()
    dialogLayout.addItem(spinLayout)
    dialogLayout.addWidget(listWidget)
    dialogLayout.addWidget(buttonBox)
    self.setLayout(dialogLayout)
    
    # signals
    connectorCountSpinBox.valueChanged.connect(self.connectorCountValueChanged)
    buttonBox.accepted.connect(self.accept)
    buttonBox.rejected.connect(self.reject)
    listWidget.currentItemChanged.connect(self.currentItemChanged)
    
    # initial state
    buttonBox.button(QDialogButtonBox.Ok).setEnabled(False) # until user chooses list item
    
    self.setWindowTitle("Mystery SMD Package Scavenger")


  '''
  Signal handlers.
  '''
  def connectorCountValueChanged(self, value):
    count = self.listWidget.populate(value)
    if not count > 0:
      self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)


  def currentItemChanged(self, current, previous):
    self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    
      
  def accept(self):
    footprint = self.listWidget.chosenFootprint()
    partFactory = AnySMDPartFactory()
    partFactory.produce(footprint)
    QDialog.accept(self)
    
    
    

class App(QApplication):
  
  def __init__(self, args):
    super(App, self).__init__(args)
    
    # Read SMD packages.  Since ScavengeDialog is not shown, effectively modal
    # TODO 1000 is arbitrary, seems large enough for the contrib directory, but fragile
    progress = QProgressDialog("Reading SMD packages...", "Abort", 0, 1000)
    # progress.setWindowModality(Qt.WindowModal)
    progress.show()
    progress.setValue(0)
    directory = FritzingFootprintDirectory()
    directory.initSMDWithProgress(progress)
    progress.setValue(1000) # close progress
    
    dialog = ScavengeDialog(directory)
    dialog.exec_()

        