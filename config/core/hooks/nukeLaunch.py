import os
import sys
import tank
import nuke


def launchNuke():

    setEnvironment = nuke.root()
    setEnvironment.knob('project_directory').setValue('[python {nuke.script_directory()}]')
    setEnvironment.knob('name').setValue('[python {nuke.script_directory()}]')
    scanPath == '[python {nuke.script_directory()}]'
    Read1 == nuke.createNode('Read')
    Read1.knob('file').setValue(scanPath)