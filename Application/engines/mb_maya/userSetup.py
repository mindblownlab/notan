import os
from maya import cmds, mel

print("-" * 10)
print("Pipeline Studio"
      "Version: 2.0.0"
      "By Mindblownlab Studio")
print("-" * 10)

if os.environ['MB_PROJECT_PATH']:
    mel.eval('setProject("{path}")'.format(path=os.environ['MB_PROJECT_PATH'].replace("\\", "/")))

cmds.evalDeferred('import startup')
