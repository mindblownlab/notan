import copy
import json
import uuid
from importlib import reload
from utils import util, context
from models import engines
from PyQt5 import QtWidgets, QtCore, QtGui
import os

reload(util)
reload(engines)


class AppEngines:
    data_list = []
    engine = None
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self, root):
        try:
            self.root = root
            self.parent.close()
            self.ui = util.load_ui(name='app_engines')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Engines')

            self.model = engines.EnginesModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
            # self.parent.resize(800, 600)
            self.ui.save.clicked.connect(self.save)
            self.ui.cancel.clicked.connect(self.cance)
            self.ui.listing.itemDoubleClicked.connect(self.editing)
            self.ui.load_engine.clicked.connect(self.load_engine)
            self.ui.query.textChanged.connect(self.searching)
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def searching(self, query):
        filtering = copy.deepcopy(self.model.all())
        self.data_list = list(filter(lambda flt: query.lower() in flt.get("name").lower(), filtering))
        self.populate()

    def cance(self):
        self.ui.name.setText("")
        self.ui.ext.setText("")
        self.ui.version.setText("")
        self.ui.path.setText("")
        self.ui.type.setText("")
        self.id = str(uuid.uuid4())
        self.ui.save.setText("CREATE")
        self.ui.listing.clearSelection()
        self.ui.folder_engine.setCurrentIndex(0)
        self.ui.folder_publish.setCurrentIndex(0)
        self.engine = None

    def editing(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            self.ui.name.setText(data.get("name"))
            self.ui.ext.setText(data.get("ext"))
            self.ui.version.setText(data.get("version"))
            self.ui.path.setText(data.get("path"))
            self.ui.type.setText(data.get("type"))
            self.ui.save.setText("UPDATE")
            self.ui.folder_engine.setCurrentText(data.get("work"))
            self.ui.folder_publish.setCurrentText(data.get("publish"))
            self.engine = data
        except Exception as error:
            util.message_log(error)

    def save(self):
        try:

            if self.ui.name.text() == "":
                util.message(title="Name is empty", message="Fill in the name field to create.", parent=self.parent)
                return

            settings = util.get_settings()
            _engines = settings.get("engines")

            name = self.ui.name.text()
            type = self.ui.type.text()
            version = self.ui.version.text()
            ext = self.ui.ext.text()
            path = self.ui.path.text()
            folder_engine = self.ui.folder_engine.currentText()
            folder_publish = self.ui.folder_publish.currentText()

            data_engine = {
                "_id": self.id,
                "name": name,
                "type": type,
                "ext": ext,
                "work": folder_engine,
                "publish": folder_publish,
                "version": version,
                "path": path
            }

            if self.ui.save.text() == "CREATE":
                _engines.append(data_engine)
            else:
                folder_index = next((index for (index, d) in enumerate(_engines) if d["_id"] == self.engine.get("_id")), None)
                _engines[folder_index] = data_engine

            settings["engines"] = _engines

            util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.parent.settings = settings
            self.cance()
        except Exception as error:
            util.message_log(error)

    def load_engine(self):
        try:
            dialog = QtWidgets.QFileDialog()
            dialog.setWindowTitle('Select software')
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
            dialog.setDirectory(self.ui.path.text() or "C:/")
            dialog.setNameFilter("Executaveis (*.exe)")
            dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
            filename = None
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                filename = dialog.selectedFiles()
            if filename:
                self.ui.path.setText(filename[0])
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:

            templates = util.get_project_template().get("template")
            engines = list(filter(lambda eng: eng.get("engine"), templates))
            engines = list(map(lambda eng: eng.get("name"), engines))

            self.ui.folder_engine.clear()
            self.ui.folder_publish.clear()
            self.ui.listing.clear()

            self.ui.folder_engine.addItems(engines)
            self.ui.folder_publish.addItems(engines)

            if len(self.data_list) <= 0:
                self.ui.listing.setStyleSheet("background-image: url(:/assets/empty.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            else:
                self.ui.listing.setStyleSheet("")
            if len(self.data_list) > 0:
                for eng in list(self.data_list):
                    item = QtWidgets.QTreeWidgetItem(self.ui.listing)
                    item.setIcon(0, QtGui.QIcon(eng.get("icon")))
                    item.setText(0, eng.get("name"))
                    item.setText(1, eng.get("version"))
                    item.setText(2, eng.get("ext"))
                    item.setText(3, eng.get("path"))
                    item.setData(0, QtCore.Qt.UserRole, eng)

        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Create Engines </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project="Engine for projects", info="Manage Engines"))
        except Exception as error:
            util.message_log(error)


from utils import resources
