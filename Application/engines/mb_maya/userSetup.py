import os
from maya import cmds, mel

if os.environ['MB_PROJECT_PATH']:
    mel.eval('setProject("{path}")'.format(path=os.environ['MB_PROJECT_PATH'].replace("\\", "/")))

cmds.evalDeferred('import startup')
