import copy
import json
import os.path
import uuid
from importlib import reload
from utils import util, context
from models import published
from PyQt5 import QtWidgets, QtCore, QtGui

reload(published)
reload(util)


class AppPublished:
    data_list = []
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_publish')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Published')

            self.model = published.PublishedModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
            # self.parent.resize(800, 600)
            # self.ui.query.textChanged.connect(self.searching)
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def searching(self, query):
        try:
            filtering = copy.deepcopy(self.model.all())
            self.data_list = list(filter(lambda flt: query.lower() in flt.get("name").lower(), filtering))
            self.populate()
        except Exception as error:
            util.message_log(error)

    def cance(self):
        self.ui.listing.clearSelection()
        self.id = str(uuid.uuid4())

    def save(self):
        try:
            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.cance()
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:
            settings = util.get_settings()
            self.ui.listing.clear()
            if len(self.data_list) <= 0:
                self.ui.listing.setStyleSheet("background-image: url(:/assets/empty.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            else:
                self.ui.listing.setStyleSheet("")
            if len(self.data_list) > 0:
                for ast in list(self.data_list):
                    item = QtWidgets.QTreeWidgetItem(self.ui.listing)
                    item.setIcon(0, QtGui.QIcon(ast.get("thumb")))
                    item.setData(0, QtCore.Qt.UserRole, ast)
                    item.setText(0, ast.get("name"))
                    item.setText(1, ast.get("filename"))
                    item.setText(2, ast.get("type"))
                    item.setText(3, ast.get("step"))
                    item.setText(4, ast.get("engine"))
                    item.setText(5, ast.get("status"))
                    item.setText(6, os.path.normpath(ast.get("path_storage")))
                    item.setText(7, str(ast.get("version")))
                    item.setText(8, ast.get("updated"))
                    item.setText(9, ast.get("created"))
        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            data_project = context.get_project()
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Published Files </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info="Manage Published Files"))
        except Exception as error:
            util.message_log(error)
