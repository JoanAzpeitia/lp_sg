import sgtk

# get the engine we are currently running in
currentEngine = sgtk.platform.current_engine()
# get hold of the shotgun api instance used by the engine, (or we could have created a new one)
sg = currentEngine.shotgun
# get the current context so we can find the highest version in relation to the context
ctx = currentEngine.context


def getVersions():
    types = ['scan', 'cg', 'publish', 'out', 'elements']
    versionDict = {}
    shotDir = ctx
    for t in types:
        versionDict[t] = [] # THIS WILL HOLD THE FOUND SEQUENCES
        typeDir = os.path.join( shotDir, t ) # GET THE CURRENT DIRECTORY PATH
        for d in os.listdir(typeDir):  # LOOP THROUGH IT'S CONTENTS
            path = os.path.join(typeDir, d)
            if os.path.isdir(path):  # LOOP THROUGH SUB DIRECTORIES
                versionDict[t].append(
                    getFileSeq(path))  # RUN THE getFileSeq() FUNCTION AND APPEND IT'S OUTPUT TO THE LIST
    return versionDict

def getFileSeq( dirPath ):
    '''Return file sequence with same name as the parent directory. Very loose example!!'''
    dirName = os.path.basename( dirPath )
    # COLLECT ALL FILES IN THE DIRECTORY THAT HVE THE SAME NAME AS THE DIRECTORY
    files = glob( os.path.join( dirPath, '%s.*.*' % dirName ) )
    # GRAB THE RIGHT MOST DIGIT IN THE FIRST FRAME'S FILE NAME
    firstString = re.findall( r'\d+', files[0] )[-1]
    # GET THE PADDING FROM THE AMOUNT OF DIGITS
    padding = len( firstString )
    # CREATE PADDING STRING FRO SEQUENCE NOTATION
    paddingString = '%02s' % padding
    # CONVERT TO INTEGER
    first = int( firstString )
    # GET LAST FRAME
    last = int( re.findall( r'\d+', files[-1] )[-1] )
    # GET EXTENSION
    ext = os.path.splitext( files[0] )[-1]
    # BUILD SEQUENCE NOTATION
    fileName = '%s.%%%sd%s %s-%s' % ( dirName, str(padding).zfill(2), ext, first, last )
    # RETURN FULL PATH AS SEQUENCE NOTATION
    return os.path.join( dirPath, fileName )