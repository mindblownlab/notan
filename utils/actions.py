import json
import os
from importlib import reload, import_module
from utils import util

try:
    from PyQt5 import uic, QtCore, QtGui, QtWidgets
except:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtUiTools import QUiLoader


def menu_action(name, app):
    context = None
    project = None

    if 'MB_CONTEXT' in os.environ.keys():
        if os.environ['MB_CONTEXT'] != "null":
            context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

    if 'MB_PROJECT' in os.environ.keys():
        if os.environ['MB_PROJECT'] != "null":
            project = dict(json.loads(os.environ['MB_PROJECT'])) or None

    layout = app.ui.main_layout
    if layout.count() > 0:
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            layout.removeWidget(widget)
            widget.setParent(None)

    if app:
        app.close()

    try:
        module = import_module(name)
        reload(module)
        instance = getattr(module, name.capitalize())(app=app, data=project, context=context)
        return instance
    except Exception as error:
        util.message_log(error)


def menu_desktop(name, app):
    layout = app.ui.main_layout
    if layout.count() > 0:
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            layout.removeWidget(widget)
            widget.setParent(None)

    if app:
        app.close()

    try:
        module = import_module(name)
        reload(module)
        instance = getattr(module, name.capitalize())(app=app, data=None, context=None)
        return instance
    except Exception as error:
        util.message_log(error)