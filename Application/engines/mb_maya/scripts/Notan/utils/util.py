import json
import os
import sys
from glob import glob

try:
    import maya.OpenMayaUI as omui
    from maya import cmds, mel
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except:
    pass


def get_last_version(path):
    try:
        path = os.path.normpath(path)
        root_path = os.path.dirname(path)
        file_name, file_extension = os.path.splitext(path)
        files = glob("{}/*{}".format(root_path, file_extension))
        if len(files) >= 1:
            return (len(files) + 1)
        else:
            return 1
    except:
        return 1


def get_context_from_path(path):
    path = os.path.normpath(path)
    root_path = os.path.dirname(path)
    file_name, file_extension = os.path.splitext(path)
    filename = os.path.basename(file_name).split(".")[0]
    context = root_path.split("\\")
    context = context[-4:]
    version = get_last_version(path)

    type = context[0]
    convert_version = "{:03d}".format(version)
    convert_type = {
        "assets": "asset",
        "scenes": "shot"
    }

    if convert_type.get(type) == "asset":
        data_info = {
            "asset_type": context[1],
            "asset": context[2],
            "step": context[3],
            "version": convert_version,
            "filename": filename,
            "ext": file_extension.replace(".", "")
        }
    else:
        try:
            shot_name = context[2].replace("SHOT_", "SH")
        except:
            shot_name = context[2]

        data_info = {
            "sequence": context[1],
            "shot": context[2],
            "step": context[3],
            "step_shot": context[3],
            "version": convert_version,
            "filename": "{}{}".format(shot_name, context[3]),
            "ext": file_extension.replace(".", "")
        }

    return {
        "type": convert_type.get(type),
        "path": root_path,
        "info": data_info,
        "version": version
    }


def main_maya():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)