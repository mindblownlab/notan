from importlib import reload
from utils import util
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from apps import assets, shots, sequences, projects, settings, engines, published, templates, animation

reload(util)
reload(assets)
reload(shots)
reload(sequences)
reload(projects)
reload(settings)
reload(engines)
reload(published)
reload(templates)
reload(animation)


class AppCore(QtWidgets.QMainWindow):
    ui = None
    settings = None

    def __init__(self, parent=None):
        super(AppCore, self).__init__(parent)
        self.setStyleSheet(util.get_style(name='style'))
        self.parent = parent
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.ui = util.load_ui(name="core")
        self.setCentralWidget(self.ui.main_container)

        self.settings = util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))
        self.ui.studio_name.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">{studio}  </span><span style=" font-size:9pt;"><br/></span></p></body></html>'.format(studio=self.settings.get("studio").get("name")))
        self.ui.version.setText("v{}".format(self.settings.get("developer").get("version")))
        self.ui.develop_by.setText('<html><head/><body><p>Develop by <span style=" font-size:9pt; font-weight:600;">{company}</span></p></body></html>'.format(company=self.settings.get("developer").get("name")))

        self.setWindowTitle(self.settings.get("studio").get("name"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/assets/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.app_assets = assets.AppAssets(self)
        self.app_shots = shots.AppShots(self)
        self.app_sequences = sequences.AppSequence(self)
        self.app_project = projects.AppProjects(self)
        self.app_settings = settings.AppSettings(self)
        self.app_engines = engines.AppEngines(self)
        self.app_published = published.AppPublished(self)
        self.app_templates = templates.AppTemplates(self)
        self.app_animation = animation.AppAnimation(self)

    def reload(self):
        self.parent.populate()

    def keyPressEvent(self, e):
        apps = [method for method in dir(self) if method.startswith('app_') is True]
        for app in apps:
            method_list = [method for method in dir(getattr(self, app)) if method.startswith('__') is False]
            if "delete_event" in method_list:
                if e.key() == QtCore.Qt.Key_Delete:
                    getattr(self, app).delete_event()

    def closeEvent(self, event):
        try:
            if self.ui.main_layout.count() > 0:
                for i in range(self.ui.main_layout.count()):
                    item = self.ui.main_layout.takeAt(i)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
        except Exception as error:
            util.message_log(error)


from utils import resources
