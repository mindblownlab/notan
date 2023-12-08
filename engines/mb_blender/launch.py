import json
import os
import sys
from utils import util


class Startup:

    def __init__(self, data=None):
        try:
            root_path = os.path.join(util.get_root_path())
            engine_root = os.path.join(root_path, "engines", "mb_blender")
            PYTHONPATH = []

            PYTHONPATH.insert(0, root_path)

            lib_path = os.path.join(root_path, "env", "Lib", "site-packages")
            if lib_path not in PYTHONPATH:
                sys.path.append(lib_path)
                PYTHONPATH.append(lib_path)

            if engine_root not in PYTHONPATH:
                sys.path.append(engine_root)
                PYTHONPATH.append(engine_root)


            os.environ['PYTHONPATH'] = ";".join(PYTHONPATH)
            os.environ['BLENDER_USER_SCRIPTS'] = engine_root
            os.environ['MB_ROOT'] = root_path

        except Exception as error:
            util.message_log(error)
