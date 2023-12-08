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


class AppTemplates:
    data_list = []
    id = str(uuid.uuid4())

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_templates')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Templates')

            self.ui.save.clicked.connect(self.save)
            self.ui.engines.currentTextChanged.connect(self.populate)
            settings = util.get_settings()
            engines = settings.get("engines")
            engines = list(map(lambda eng: eng.get("type").capitalize(), engines))
            engines = list(set(engines))
            self.ui.engines.addItems(engines)

            self.navigator()
            self.populate()
            # self.parent.resize(700, 300)
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def populate(self):

        engine = self.ui.engines.currentText().lower()
        templates = util.get_template().get(engine)

        self.ui.temp_root_asset_work.setText(templates.get("root_asset_work"))
        self.ui.temp_asset_work.setText(templates.get("asset_work"))
        self.ui.temp_root_asset_publish.setText(templates.get("root_asset_publish"))
        self.ui.temp_asset_publish.setText(templates.get("asset_publish"))
        self.ui.temp_asset_alembic.setText(templates.get("asset_alembic"))

        self.ui.temp_root_shot_work.setText(templates.get("root_shot_work"))
        self.ui.temp_shot_work.setText(templates.get("shot_work"))
        self.ui.temp_root_shot_publish.setText(templates.get("root_shot_publish"))
        self.ui.temp_shot_publish.setText(templates.get("shot_publish"))
        self.ui.temp_shot_alembic.setText(templates.get("shot_alembic"))

        self.ui.temp_playblast.setText(templates.get("playblast"))

    def save(self):
        try:
            engine = self.ui.engines.currentText().lower()
            templates = util.get_template()

            data = {
                "root_asset_work": self.ui.temp_root_asset_work.text(),
                "asset_work": self.ui.temp_asset_work.text(),
                "root_asset_publish": self.ui.temp_root_asset_publish.text(),
                "asset_publish": self.ui.temp_asset_publish.text(),
                "asset_alembic": self.ui.temp_asset_alembic.text(),

                "root_shot_work": self.ui.temp_root_shot_work.text(),
                "shot_work": self.ui.temp_shot_work.text(),
                "root_shot_publish": self.ui.temp_root_shot_publish.text(),
                "shot_publish": self.ui.temp_shot_publish.text(),
                "shot_alembic": self.ui.temp_shot_alembic.text(),

                "playblast": self.ui.temp_playblast.text(),
            }

            templates[engine] = data
            util.storage(data=templates, path=os.path.join(util.get_root_path(), 'config', 'templates.yml'), replace=True)
        except Exception as error:
            util.message_log(error)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Project template </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project="Configuring templates", info="Manage template"))
        except Exception as error:
            util.message_log(error)


from utils import resources
