from models import shots, assets, types, steps, sequence
from PySide2 import QtWidgets, QtCore, QtGui
from utils import util, context
from importlib import reload
import os
import uuid

reload(util)
reload(steps)
reload(sequence)
reload(shots)
reload(assets)
reload(types)


class AppManager:
    ui = None
    parent = None
    project = None
    context = None
    query = ""

    def __init__(self, parent=None):
        self.parent = parent
        self.project = context.get_project()
        self.context = context.get_context()

    def open(self):
        self.parent.close()
        self.ui = util.load_ui_engine(name='manager', target=self.parent)
        self.parent.ui.main_layout.addWidget(self.ui)
        self.parent.setFixedSize(800, 600)
        self.navigator(title="MANAGER FILE", subtitle="Management file")
        self.populate()
        self.parent.show()

    def populate(self):
        pass

    def navigator(self, title="OPEN", subtitle="Open files"):
        try:
            data_project = context.get_project()
            data_context = dict(context.get_context())

            try:
                step = data_context.get("step").split("_")[1]
            except:
                step = data_context.get("step")

            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">{title} </span><span style=" font-size:10pt;">{navigate}</span></p></body></html>'.format(title=title, navigate=data_context.get("type").capitalize()))
            if data_context.get("type"):
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style="font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{step}, {type} {name}</span></p></body></html>'.format(project=data_project.get("name"), step=step, type=data_context.get('type'), name=data_context.get('name')))
            else:
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info=subtitle))
        except Exception as error:
            util.message_log(error)
