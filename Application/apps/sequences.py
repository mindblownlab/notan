import json
import os.path
import uuid
from importlib import reload
from utils import util, context
from models import sequence
from PyQt5 import QtWidgets, QtCore, QtGui
import copy

reload(sequence)
reload(util)


class AppSequence:
    data_list = []
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_sequences')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Sequences')

            self.model = sequence.SequenceModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
            # self.parent.resize(500, 600)
            self.ui.save.clicked.connect(self.save)
            self.ui.cancel.clicked.connect(self.cancel)
            self.ui.listing.itemDoubleClicked.connect(self.editing)
            self.ui.query.textChanged.connect(self.searching)
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def searching(self, query):
        filtering = copy.deepcopy(self.model.all())
        self.data_list = list(filter(lambda flt: query.lower() in flt.get("name").lower(), filtering))
        self.populate()

    def cancel(self):
        self.ui.name.setText("")
        self.ui.save.setText("CREATE")
        self.id = str(uuid.uuid4())
        self.ui.listing.clearSelection()

    def editing(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            self.ui.name.setText(data.get("name"))
            self.ui.save.setText("UPDATE")
        except Exception as error:
            util.message_log(error)

    def save(self):
        try:

            templates = util.get_template()
            settings = util.get_settings()
            project = context.get_project()
            name = self.ui.name.text()
            name = name.replace(" ", "_").upper()
            engines = util.get_project_template().get("template")
            engines = list(filter(lambda eng: eng.get("engine"), engines))
            softwares = settings.get("engines")

            if self.ui.name.text() == "":
                util.message(title="Name is empty", message="Fill in the name field to create.", parent=self.parent)
                return

            self.model = sequence.SequenceModel()
            self.data_list = copy.deepcopy(self.model.all())

            exists = list(filter(lambda qry: qry.get("name").lower() == name.lower(), self.data_list))
            if len(exists) > 0:
                util.message(title="Sequence already exists", message="Unable to add this sequence as it has already been created", parent=self.parent)
                return

            fields = {
                "sequence": name,
                "shot": "",
            }

            for eng in engines:
                get_engine_type = list(filter(lambda s: s.get("work") == eng.get("name"), softwares))
                if get_engine_type:
                    get_engine_type = get_engine_type[0]
                    path_shot = templates.get(get_engine_type.get("type")).get("root_shot_work")
                    path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), eng.get("name"), path_shot.format(**fields))
                    path = os.path.normpath(path)
                    if self.ui.save.text() == "CREATE":
                        if not os.path.exists(path):
                            os.makedirs(path)

            data_sequence = {
                "_id": self.id,
                "status": "active",
                "name": name,
                "date": util.current_date()
            }
            util.context_storage(
                item=data_sequence,
                file=os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), settings.get("database"), "sequences.yml")
            )
            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.cancel()
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:
            self.ui.listing.clear()
            if len(self.data_list) <= 0:
                self.ui.listing.setStyleSheet("background-image: url(:/assets/empty.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            else:
                self.ui.listing.setStyleSheet("")
            if len(self.data_list) > 0:
                for ast in list(self.data_list):
                    item = QtWidgets.QTreeWidgetItem(self.ui.listing)
                    item.setData(0, QtCore.Qt.UserRole, ast)
                    item.setText(0, ast.get("name"))
                    item.setText(1, ast.get("status"))
                    item.setText(2, ast.get("created"))

        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            data_project = context.get_project()
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Create Sequence </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info="Manage Sequence"))
        except Exception as error:
            util.message_log(error)
