import copy
import json
import os.path
import uuid
from importlib import reload
from utils import util, context
from models import assets
from PyQt5 import QtWidgets, QtCore, QtGui

reload(assets)
reload(util)


class AppAssets:
    data_list = []
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_assets')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Assets')

            self.model = assets.AssetsModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
            # self.parent.resize(800, 600)
            self.ui.save.clicked.connect(self.save)
            self.ui.cancel.clicked.connect(self.cance)
            self.ui.listing.itemDoubleClicked.connect(self.editing)
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
        self.ui.asset_type.setCurrentIndex(0)
        self.ui.save.setText("CREATE")
        self.ui.listing.clearSelection()
        self.id = str(uuid.uuid4())

    def editing(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            self.ui.asset_type.setCurrentText(data.get("asset_type"))
            self.ui.name.setText(data.get("name"))
            self.id = data.get("id")
            self.ui.save.setText("UPDATE")
        except Exception as error:
            util.message_log(error)

    def save(self):
        try:
            templates = util.get_template()
            project = context.get_project()
            settings = util.get_settings()
            name = self.ui.name.text()
            name = name.replace(" ", "_").capitalize()
            type = self.ui.asset_type.currentText()
            engines = util.get_project_template().get("template")
            engines = list(filter(lambda eng: eng.get("engine"), engines))
            softwares = settings.get("engines")

            if name == "":
                util.message(title="Name is empty", message="Fill in the name field to create.", parent=self.parent)
                return

            self.model = assets.AssetsModel()
            self.data_list = copy.deepcopy(self.model.all())

            exists = list(filter(lambda qry: qry.get("name").lower() == name.lower(), self.data_list))
            if len(exists) > 0:
                util.message(title="Asset already exists", message="Unable to add this asset as it has already been created", parent=self.parent)
                return

            fields = {
                "asset_type": type,
                "asset": name,
            }

            for eng in engines:
                get_engine_type = list(filter(lambda s: s.get("work") == eng.get("name"), softwares))
                if get_engine_type:
                    get_engine_type = get_engine_type[0]
                    path_asset = templates.get(get_engine_type.get("type")).get("root_asset_work")
                    path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), eng.get("name"), path_asset.format(**fields))
                    path = os.path.normpath(path)
                    if self.ui.save.text() == "CREATE":
                        if not os.path.exists(path):
                            os.makedirs(path)

            data_asset = {
                "_id": self.id,
                "name": name,
                "type": "asset",
                "status": "active",
                "asset_type": type,
                "created": util.current_date()
            }

            util.context_storage(
                item=data_asset,
                file=os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), settings.get("database"), "assets.yml")
            )

            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.cance()
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:
            settings = util.get_settings()
            self.ui.listing.clear()
            self.ui.asset_type.clear()
            self.ui.asset_type.addItems(settings.get("types_assets"))
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
                    item.setText(1, ast.get("asset_type"))
                    item.setText(2, ast.get("status"))
                    item.setText(3, ast.get("created"))

        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            data_project = context.get_project()
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Create Assets </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info="Manage Assets"))
        except Exception as error:
            util.message_log(error)
