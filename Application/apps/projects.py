import json
from importlib import reload
from utils import util, context
from models import projects
from PyQt5 import QtWidgets, QtCore, QtGui
import uuid
import os
import copy

reload(util)
reload(projects)


class AppProjects:
    data_list = []
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_projects')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Projects')

            self.model = projects.ProjectsModel()
            self.data_list = copy.deepcopy(self.model.all())

            self.navigator()
            self.populate()
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
        self.ui.hes_width.setValue(1920)
        self.ui.res_height.setValue(1080)
        self.ui.aspect.setValue(1)
        self.ui.fps.setValue(24)
        self.ui.save.setText("CREATE")
        self.id = str(uuid.uuid4())
        self.ui.listing.clearSelection()

    def editing(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            hes_width, res_height = data.get("resolution")
            self.ui.name.setText(data.get("name"))
            self.ui.hes_width.setValue(hes_width)
            self.ui.res_height.setValue(res_height)
            self.ui.aspect.setValue(int(data.get("aspect")))
            self.ui.fps.setValue(float(data.get("fps")))
            self.id = data.get("id")
            self.ui.save.setText("UPDATE")
        except Exception as error:
            util.message_log(error)

    def save(self):
        try:

            if self.ui.name.text() == "":
                util.message(title="Name is empty", message="Fill in the name field to register a project.", parent=self.parent)
                return

            settings = util.get_settings()
            name = self.ui.name.text()
            name = name.replace(" ", "_").upper()
            resolution = [self.ui.hes_width.value(), self.ui.res_height.value()]
            aspect = self.ui.aspect.text()
            fps = self.ui.fps.text()

            data_project = {
                "id": self.id,
                "name": name,
                "resolution": resolution,
                "status": "active",
                "created": util.current_date(),
                "aspect": str(aspect),
                "fps": str(fps)
            }

            projecty_path = os.path.join(settings.get("project_root"), name, settings.get("folder_production"))
            projecty_path = os.path.normpath(projecty_path)

            if self.ui.save.text() == "CREATE":
                if not os.path.exists(projecty_path):
                    os.makedirs(projecty_path)
                    self.folder_structure(data_project)

            util.storage(data=data_project, path=os.path.join(projecty_path, settings.get("database"), 'project.yml'), replace=True)
            self.data_list = copy.deepcopy(self.model.all())
            self.populate()
            self.parent.reload()
            self.cance()

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
                for prj in list(self.data_list):
                    item = QtWidgets.QTreeWidgetItem(self.ui.listing)
                    fps = str(prj.get("fps"))
                    resolution = "x".join(list(map(lambda r: str(r), prj.get("resolution"))))
                    item.setData(0, QtCore.Qt.UserRole, prj)
                    item.setIcon(0, QtGui.QIcon(prj.get("thumb")))
                    item.setText(0, prj.get("name"))
                    item.setText(1, prj.get("status"))
                    item.setText(2, fps)
                    item.setText(3, resolution)
                    item.setText(5, prj.get("created"))

        except Exception as error:
            util.message_log(error)

    def open_project(self):
        try:
            dialog = QtWidgets.QFileDialog()
            dialog.setWindowTitle('Select project root')
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)
            dialog.setDirectory(self.ui.path.text() or "C:/")
            dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
            filename = None
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                filename = dialog.selectedFiles()
            if filename:
                self.ui.path.setText(filename[0])
        except Exception as error:
            util.message_log(error)

    def folder_structure(self, data):
        try:
            project = dict(copy.deepcopy(data))
            settings = util.get_settings()
            project_template = util.get_project_template()

            if project_template:
                projecty_path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"))
                projecty_path = os.path.normpath(projecty_path)
                database_path = os.path.join(projecty_path, settings.get("database"))
                templates = project_template.get("template")

                if not os.path.exists(database_path):
                    os.makedirs(database_path)

                for tpl in templates:
                    root_path = os.path.join(projecty_path, tpl.get("name"))
                    if not os.path.exists(root_path):
                        os.makedirs(root_path)
                    if len(tpl.get("children")) > 0:
                        for sub in tpl.get("children"):
                            sub_path = os.path.join(projecty_path, tpl.get("name"), sub.get("name"))
                            if not os.path.exists(sub_path):
                                os.makedirs(sub_path)

        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Create Projects </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;"> | {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project="All projects root", info="Manage projects"))
        except Exception as error:
            util.message_log(error)


from utils import resources
