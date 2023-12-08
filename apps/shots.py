import os.path
from importlib import reload
from utils import util, context
from models import shots, sequence
from PyQt5 import QtWidgets, QtCore, QtGui
import copy
import uuid

reload(shots)
reload(sequence)
reload(util)


class AppShots:
    id = str(uuid.uuid4())
    data_list = []

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_shots')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Shots')

            self.model = shots.ShotsModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
            # self.parent.resize(800, 600)
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
        self.ui.frame_start.setValue(1)
        self.ui.frame_end.setValue(120)
        self.ui.sequence.setCurrentIndex(0)
        self.ui.listing.clearSelection()
        self.ui.multiple.setChecked(False)
        self.id = str(uuid.uuid4())
        self.ui.save.setText("CREATE")

    def editing(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            frame_start, frame_end = data.get("frames")
            self.ui.sequence.setCurrentText(data.get("sequence"))
            self.ui.name.setText(data.get("name"))
            self.ui.frame_start.setValue(frame_start)
            self.ui.frame_end.setValue(frame_end)

            self.id = data.get("id")
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
            sequence = self.ui.sequence.currentText()
            engines = util.get_project_template().get("template")
            engines = list(filter(lambda eng: eng.get("engine"), engines))
            softwares = settings.get("engines")

            if self.ui.name.text() == "":
                util.message(title="Name is empty", message="Fill in the name field to create.", parent=self.parent)
                return

            self.model = shots.ShotsModel()
            self.data_list = copy.deepcopy(self.model.all())

            exists = list(filter(lambda qry: qry.get("name").lower() == name.lower(), self.data_list))
            if len(exists) > 0:
                util.message(title="Shot already exists", message="Unable to add this shot as it has already been created", parent=self.parent)
                return

            fields = {"sequence": sequence, "shot": ""}

            count_shot = 10
            for eng in engines:
                get_engine_type = list(filter(lambda s: s.get("work") == eng.get("name"), softwares))
                if get_engine_type:
                    get_engine_type = get_engine_type[0]
                    path_shot = templates.get(get_engine_type.get("type")).get("root_shot_work")
                    if self.ui.multiple.isChecked():
                        total = int(name)
                        count = 1
                        increment = int(count_shot)
                        while count <= total:
                            path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), eng.get("name"), path_shot.format(**fields), "SHOT_{:03d}".format(increment))
                            path = os.path.normpath(path)
                            if self.ui.save.text() == "CREATE":
                                if not os.path.exists(path):
                                    os.makedirs(path)
                            increment += int(count_shot)
                            count += 1
                    else:
                        path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), eng.get("name"), path_shot.format(**fields), name)
                        path = os.path.normpath(path)
                        if self.ui.save.text() == "CREATE":
                            if not os.path.exists(path):
                                os.makedirs(path)
            data_shot = []
            if self.ui.multiple.isChecked():
                total = int(name)
                increment = int(count_shot)
                for sht in range(total):
                    data_shot.append({
                        "_id": self.id,
                        "name": "SHOT_{:03d}".format(increment),
                        "status": "active",
                        "type": "shot",
                        "sequence": sequence,
                        "created": util.current_date(),
                        "frames": [self.ui.frame_start.value(), self.ui.frame_end.value()]
                    })
                    increment += int(count_shot)
            else:
                data_shot = {
                    "_id": self.id,
                    "name": name,
                    "status": "active",
                    "type": "shot",
                    "sequence": sequence,
                    "frames": [self.ui.frame_start.value(), self.ui.frame_end.value()]
                }

            util.context_storage(
                item=data_shot,
                file=os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), settings.get("database"), "shots.yml")
            )
            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.cancel()
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:
            model_sequence = sequence.SequenceModel()
            sequences = list(map(lambda sqn: sqn.get("name"), model_sequence.all()))
            self.ui.listing.clear()
            self.ui.sequence.clear()
            self.ui.sequence.addItems(sequences)
            self.ui.frame_start.setValue(1)
            self.ui.frame_end.setValue(120)
            if len(self.data_list) <= 0:
                self.ui.listing.setStyleSheet("background-image: url(:/assets/empty.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            else:
                self.ui.listing.setStyleSheet("")
            if len(self.data_list) > 0:
                for sht in list(self.data_list):
                    frames = "-".join(list(map(lambda r: str(r), sht.get("frames"))))
                    item = QtWidgets.QTreeWidgetItem(self.ui.listing)
                    item.setIcon(0, QtGui.QIcon(sht.get("thumb")))
                    item.setData(0, QtCore.Qt.UserRole, sht)
                    item.setText(0, sht.get("name"))
                    item.setText(1, sht.get("status"))
                    item.setText(2, sht.get("sequence"))
                    item.setText(3, frames)
                    item.setText(4, sht.get("created"))

        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            data_project = context.get_project()
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Create Shots </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info="Manage Shots"))
        except Exception as error:
            util.message_log(error)


from utils import resources
