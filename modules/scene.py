import json

from models import shots, assets, types, steps, sequence, published
from PySide2 import QtWidgets, QtCore, QtGui
from utils import util, context
from importlib import reload
import os
import uuid


class AppScene:
    ui = None
    parent = None
    project = None
    context = None

    def __init__(self, parent=None):
        self.parent = parent
        self.project = context.get_project()
        self.context = context.get_context()

    def animation(self):
        self.parent.close()
        self.ui = util.load_ui_engine(name='animation', target=self.parent)
        self.parent.ui.main_layout.addWidget(self.ui)
        self.parent.setFixedSize(600, 350)
        self.navigator(title="EXPORT ANIMATION", subtitle="Management export")
        self.ui.btn_export.clicked.connect(self.export_animate)
        self.ui.btn_cancel.clicked.connect(self.parent.close)
        self.populate()
        self.parent.show()

    def populate(self):
        self.ui.listing.clear()
        # item_asset = QtWidgets.QTreeWidgetItem(self.ui.listing)
        # item_asset.setText(0, "{} - {}".format(self.context.get("type").capitalize(), self.context.get("name")))

        # icon = QtGui.QIcon()
        # if self.context.get("type") == "asset":
        #     icon.addPixmap(QtGui.QPixmap(":/assets/cube.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        # else:
        #     icon.addPixmap(QtGui.QPixmap(":/assets/movie.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        # item_asset.setIcon(0, icon)

        collect = self.parent.collect_meshs()
        collect = util.fix_duplicate_name(data=collect, field='name')

        for abc in collect:
            item_mesh = QtWidgets.QTreeWidgetItem(self.ui.listing)
            item_mesh.setText(0, abc.get("name"))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/assets/cube.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            item_mesh.setIcon(0, icon)
            item_mesh.setData(0, QtCore.Qt.UserRole, abc)
        self.ui.listing.expandAll()

    def export_animate(self):
        try:
            ctx = context.get_context()
            prj = context.get_project()
            collect = self.parent.collect_meshs()
            collect = util.fix_duplicate_name(data=collect, field='name')

            if len(collect) > 0:
                self.parent.export_animation(collect=collect, prj=prj, ctx=ctx, ui=self.ui)

        except Exception as error:
            util.message_log(error)

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
