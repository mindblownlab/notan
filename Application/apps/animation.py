import copy
import uuid
from importlib import reload
from utils import util, context

reload(util)


class AppAnimation:

    def __init__(self, parent=None):
        self.parent = parent

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui(name='app_animation')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Export')
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    # def navigator(self):
    #     try:
    #         data_project = context.get_project()
    #         self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Export animation </span></p></body></html>')
    #         self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info="Manage Export"))
    #     except Exception as error:
    #         util.message_log(error)
