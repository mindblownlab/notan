import os
import json
import copy
from utils import util, actions
from PyQt5 import QtWidgets, QtCore, QtGui
from importlib import reload
from models import shots, assets, sequence, projects, engines
from importlib.machinery import SourceFileLoader
from modules import core
import webbrowser

reload(util)
reload(engines)
reload(projects)
reload(sequence)
reload(shots)
reload(assets)


class AppDesktop(QtWidgets.QMainWindow):
    project = None

    def __init__(self):
        super(AppDesktop, self).__init__()

        self.settings = util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))

        self.setStyleSheet(util.get_style(name='style'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.resize(400, 800)
        self.setMinimumSize(QtCore.QSize(400, 0))

        self.setWindowTitle(self.settings.get("studio").get("name"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(util.load_icon(name="logo", ext="ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.ui = util.load_ui(target=self)
        self.ui.panels.setCurrentIndex(0)
        self.setCentralWidget(self.ui.centralwidget)
        self.ui.btn_back.clicked.connect(self.back_home)

        self.ui.version.setText("v{}".format(self.settings.get("developer").get("version")))
        self.ui.develop_by.setText('<html><head/><body><p>Develop by <span style=" font-size:9pt; font-weight:600;">{company}</span></p></body></html>'.format(company=self.settings.get("developer").get("name")))

        util.logging.warning('START DESKTOP APPLICATION')

        QtCore.QCoreApplication.processEvents()
        self.model_projects = projects.ProjectsModel()
        self.model_engines = engines.EnginesModel()
        self.ui.panels.setCurrentIndex(0)
        self.setWindowTitle(self.settings.get("studio").get("name"))

        self.main_core = core.AppCore(self)
        self.ui.action_assets.triggered.connect(self.main_core.app_assets.open)
        self.ui.action_shots.triggered.connect(self.main_core.app_shots.open)
        self.ui.action_sequences.triggered.connect(self.main_core.app_sequences.open)
        self.ui.action_projects.triggered.connect(self.main_core.app_project.open)
        self.ui.action_published.triggered.connect(self.main_core.app_published.open)
        self.ui.action_templates.triggered.connect(self.main_core.app_templates.open)
        self.ui.action_settings.triggered.connect(lambda x: self.main_core.app_settings.open(self))
        self.ui.action_engines.triggered.connect(lambda x: self.main_core.app_engines.open(self))
        self.ui.action_animation.triggered.connect(lambda x: self.main_core.app_animation.open(self))
        self.ui.action_mindblown.triggered.connect(self.open_site)

        self.populate()
        self.ui.action_assets.setVisible(False)
        self.ui.action_shots.setVisible(False)
        self.ui.action_animation.setVisible(False)
        self.ui.action_sequences.setVisible(False)
        self.ui.action_published.setVisible(False)
        self.ui.action_templates.setVisible(True)
        self.ui.action_templates.setVisible(True)

        self.btn_back.setIcon(QtGui.QIcon(util.load_icon(name="arrow_left")))

    def open_site(self):
        webbrowser.open('https://mindblownlab.studio')

    def back_home(self):
        self.ui.panels.setCurrentIndex(0)
        self.ui.action_assets.setVisible(False)
        self.ui.action_shots.setVisible(False)
        self.ui.action_animation.setVisible(False)

        self.ui.action_sequences.setVisible(False)
        self.ui.action_published.setVisible(False)
        self.ui.action_templates.setVisible(True)
        self.ui.action_projects.setVisible(True)
        os.environ['MB_PROJECT'] = ""

    def populate(self):

        self.ui.projects.clear()
        self.ui.engines.clear()

        if len(self.model_projects.all()) <= 0:
            self.ui.projects.setStyleSheet("background-image: url(:/assets/empty_2.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
        else:
            self.ui.projects.setStyleSheet("")

        for project in list(self.model_projects.all()):
            self.item(project)

        for engine in list(self.model_engines.all()):
            self.item_engine(engine)

    def item(self, data):
        ui_item = util.load_ui(name="project_item")
        root_menu = QtWidgets.QTreeWidgetItem(self.ui.projects)
        text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{project}<br/></span><b>FPS:</b> {fps}<br/><b>Status:</b> {status}<br/>Created: {created}</p></body></html>""".format(
            fps=data.get("fps"),
            created=data.get("created"),
            status=data.get("status"),
            project=data.get("name"))

        ui_item.detail.setText(text)
        pixmap = QtGui.QPixmap(data.get("thumb"))
        ui_item.thumb.setPixmap(pixmap)

        ui_item.proj_open.setIcon(QtGui.QIcon(util.load_icon(name="arrow_open")))

        root_menu.setData(0, QtCore.Qt.UserRole, {**data})
        self.ui.projects.setItemWidget(root_menu, 0, ui_item)
        ui_item.proj_open.clicked.connect(lambda evt: self.open_project(data))

    def item_engine(self, data):
        ui_item = util.load_ui(name="item_engine")
        root_menu = QtWidgets.QTreeWidgetItem(self.ui.engines)
        main_item = ui_item.findChild(QtWidgets.QWidget, "main_engine_item")
        text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{engine}<br/></span><b>Version:</b> {version}</p></body></html>""".format(
            version=data.get("version"),
            engine=data.get("name"))

        ui_item.detail.setText(text)
        ui_item.detail.setStyleSheet("padding:5px")
        ui_item.thumb.setStyleSheet("margin:5px")

        icon_path = os.path.join(util.get_root_path(), "storage", "engines", "{}.png".format(data.get("type")))
        pixmap = QtGui.QPixmap(icon_path)
        ui_item.thumb.setPixmap(pixmap)

        ui_item.eng_open.setIcon(QtGui.QIcon(util.load_icon(name="arrow_open")))

        self.ui.engines.setItemWidget(root_menu, 0, main_item)
        ui_item.eng_open.clicked.connect(lambda evt: self.open_engine(data))

    def open_project(self, data):
        try:

            self.ui.action_assets.setVisible(True)
            self.ui.action_shots.setVisible(True)
            self.ui.action_animation.setVisible(True)
            self.ui.action_sequences.setVisible(True)
            self.ui.action_published.setVisible(True)
            self.ui.action_projects.setVisible(False)
            self.ui.action_templates.setVisible(False)

            self.project = data
            project = dict(copy.deepcopy(data))

            os.environ['MB_PROJECT'] = json.dumps(project)
            settings = util.get_settings()
            if project.get("path") is None:
                project.update({"path": os.path.join(settings.get("project_root"), project.get("name"))})

            self.ui.panels.setCurrentIndex(1)
            text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{project}<br/></span><b>FPS:</b> {fps}<br/>Status: {status}<br/>Created: {created}</p></body></html>""".format(
                fps=self.project.get("fps"),
                created=self.project.get("created"),
                status=self.project.get("status"),
                project=self.project.get("name"))

            self.ui.detail.setText(text)
            self.ui.project_name.setText("""<html><head/><body><p><span style=" font-size:11pt;">{project}</span></p></body></html>""".format(project=data.get("name")))
            pixmap = QtGui.QPixmap(data.get("thumb"))
            self.ui.thumb.setPixmap(pixmap)
            util.logging.warning('OPEN PROJECT, {}.'.format(data.get("name")))

        except Exception as error:
            util.message_log(error)

    def open_engine(self, data):
        try:
            launch = SourceFileLoader("engines.mb_{}".format(data.get("type")), os.path.join(util.get_root_path(), "engines", "mb_{}".format(data.get("type")), "launch.py")).load_module()
            launch.Startup(data)

            project = dict(copy.deepcopy(self.project))
            project.update({"engine": data})
            os.environ['MB_PROJECT'] = json.dumps(project)
            os.environ['MB_CONTEXT'] = json.dumps({'asset': None, 'asset_type': None, 'path': None, 'step': None, 'type': None})
            util.logging.warning('START PROJECT, {} with {}.'.format(project.get("name"), data.get("name")))
            util.logging.warning("-" * 100)

            cmd = 'start /B "App" "{}"'.format(data.get("path"))
            os.system(cmd)

        except Exception as error:
            util.message_log(error)

    def folder_structure(self):
        folders = ['assets', 'cache', 'images', 'movies', 'scenes', 'sourceimages', 'work', 'work/assets', 'work/scenes']
        project = dict(copy.deepcopy(self.project))
        settings = util.get_settings()
        if project.get("path") is None:
            project.update({"path": os.path.join(settings.get("project_root"), project.get("name"))})
        project_path = os.path.join(os.path.join(project.get("path")))
        for folder in folders:
            path = os.path.join(project_path, folder)
            if not os.path.exists(path):
                os.makedirs(path)

    def closeEvent(self, event):
        try:
            self.main_core.close()
        except Exception as error:
            util.message_log(error)
