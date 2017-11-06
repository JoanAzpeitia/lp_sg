def customRead():

    r=nuke.createNode('Read')
    r['frame_mode'].setValue('1')
    r['frame'].setValue('1')
    r['file'].setValue('[python {nuke.script_directory()}]scan/filename.ext')
