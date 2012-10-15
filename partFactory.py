'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''

from string import Template
import os
import uuid


'''
TODO 

Uses "Mystery Part" images.  Support also "Generic IC", or just "Generic IC"
As noted on net, there is overlap, both are not needed.
But Mystery Part is only 2,3,4 pins.
Need switch to Generic IC for greater pin count.

<property name="editable chip label">true</property>     not working?  typo?
'''

'''
other parameters in the template:
  Fritzing version: Fritzing doesn't check it and soon generates a different one internally
  date: same as above
  <property name="layout">Single Row</property> ??? Allows switching of Mystery Part breadboard image ???
'''

class AnySMDPartFactory(object):
  '''
  Creates Fritzing part:
  - Any: breadboard and schematic are generic images
  - SMD: PCB image is specified, but shared.
  
  !!! Note that some (all?) SMD SVG files use svgID=...pad... not ...pin...
  '''
  
  '''
  Template: $ or ${} markers for substitutions.
  
  !!! No blanks between """ and <?xml and no blank lines not enclosed by <? ?>
  
  Note iterative substituting connectorTemplate into template drafts.
  '''
  
  mainTemplate = Template(r"""<?xml version="1.0" encoding="UTF-8"?>
<module moduleId="$moduleId" fritzingVersion="0.7.7b.08.14.6293">
    <version>0</version> 
    <author>Fritzing SMD Part-o-matic</author>
    <title>Mystery SMD $connectorCount pads</title>
    <label>U</label>
    <date>2012-09-03</date>
    <tags>
      <tag>SMD</tag>
    </tags>
    <properties>
        <property name="family">$family</property>
        <property name="package">$packageName</property>
        <property name="pins">${connectorCount}</property>
        <property name="editable pin labels">true</property>
        <property name="chip label">?</property>
        <property name="part number">?</property>
    </properties>
    <description>"Any": package is SMD on PCB and adapted or undecided on breadboard. </description>
    <views>
        <iconView>
            <layers image="icon/mystery_part_icon.svg">
                <layer layerId="icon"/>
            </layers>
        </iconView>
        <breadboardView>
            <layers image="breadboard/mystery_part${connectorCount}.svg">
                <layer layerId="breadboard"/>
            </layers>
        </breadboardView>
        <schematicView>
            <layers image="schematic/mystery_part${connectorCount}.svg">
                <layer layerId="schematic"/>
            </layers>
        </schematicView>
        <pcbView>
            <layers image="pcb/$pcbSvgFilename.svg">
                <layer layerId="copper1"/>
                <layer layerId="silkscreen"/>
            </layers>
        </pcbView>
    </views>
    <connectors>
        $connector
    </connectors>
</module>
""")

 
  '''
  !!! Note $connector at end, for iteration
  '''
  connectorTemplate = Template(r"""<connector id="connector${ordinal}" type="none" name="unnamed">
            <description>none</description>
            <views>
                <breadboardView>
                    <p layer="breadboard" svgId="connector${ordinal}pin" terminalId="connector${ordinal}terminal"/>
                </breadboardView>
                <schematicView>
                    <p layer="schematic" svgId="connector${ordinal}pin" terminalId="connector${ordinal}terminal"/>
                </schematicView>
                <pcbView>
                    <p layer="copper1" svgId="connector${ordinal}$pinpad"/>
                </pcbView>
            </views>
        </connector>
        $connector
  """)
  
  
    
    
  def produce(self, footprint):
    '''
    Create Fritzing .fzb file, return its name.
    
    assert pcbSvgFilename is for Fritzing PCB image: SVG, XML of a certain but undocumented DTD
    assert pcbSvgFilename contains:
    - layer: copper1
    - connectors: with name connectorx... where x is a numeral and ... is "pad" or "pin"
    - connector count matches
    assert prefix of filename is similar to real world, industry standard(?) package name, e.g. 0602
    '''
    #print "produce", pcbSvgFilename
    
    familyName = "Mystery SMD"  # TODO parameter
    
    packageName = footprint.landPatternName()
    
    moduleId = self._uniqueModuleId()
    
    templateDraft1 = self.prepareTemplateForConnectors(connectorCount=footprint.connectorCount())
    
    '''
    Note that template includes suffix of relative path to pcbSvgFilename.
    Assert Fritzing searches same directories (e.g. parts/svg/contrib)
    that we searched to find pcbSvgFilename.
    ? Is that true. ?
    '''
    fzpFileContents = templateDraft1.substitute(pcbSvgFilename=packageName,
                                               packageName=packageName,
                                               moduleId = moduleId,
                                               family = familyName,
                                               connectorCount = footprint.connectorCount(),
                                               pinpad = footprint.pinPad())
    
    home = os.path.expanduser('~')
    # TODO cross platform
    # TODO remove spaces from names?
    outFilename = home + "/.config/Fritzing/parts/user/" + familyName + packageName + ".fzp"

    with open(outFilename, "w") as f:
      f.write(fzpFileContents)
    
    # assert outFilename is valid XML conforming to Fritzing DTD i.e. .fzp format
    return outFilename
  
  
  
  def _uniqueModuleId(self):
    '''
    Fritzing wants unique ID on user created .fzp part files in .../parts/user.
    Internally, Fritzing will generate another unique moduleId.
    
    Implementation 1:
    First part: unique to this factory?
    Second part: unique pad count
    Third part: the unique? name of the SMD footprint
    This emulates what "Fritzing Part-o-matic" factory does.
    
    #moduleId = "Any_SMD" + "_2pad_" # + name
    
    Implementation 2:
    generate uuid (since otherwise, because Fritzing caches its hash table,
    if the factory is run more than once, Fritzing declares non-unique moduleId's.)
    '''
    return uuid.uuid1()
    
    
    
  def prepareTemplateForConnectors(self, connectorCount):
    '''
    Multiplex connector template into main template, once for each connector.
    '''
    workingTemplate = AnySMDPartFactory.mainTemplate
    for i in range(connectorCount):
      # specialize connector template with ordinal
      # safe_substitute doesn't throw KeyError for placeholders we want to remain
      connectorDraft = AnySMDPartFactory.connectorTemplate.safe_substitute(ordinal=i)
      # substitute into mainTemplate
      draft = workingTemplate.safe_substitute(connector=connectorDraft)
      # assert draft still has a $connector placeholder (since connectorDraft has one)
      workingTemplate = Template(draft) # Roll new draft into workingTemplate
      
    # assert draft has $connector, now extraneous.  Substitute XML comment.
    finalDraft = workingTemplate.safe_substitute(connector="<!-- end generated connectors -->")
      
    # assert finalDraft still has many placeholders, including in the connectorDrafts
    # assert finalDraft is string (but return a Template)
    return Template(finalDraft)

    
    
    