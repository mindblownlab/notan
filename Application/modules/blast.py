import json
import os.path
from glob import glob
from models import shots, assets, types, steps, sequence
from PySide2 import QtWidgets, QtCore, QtGui
from utils import util, context
from importlib import reload

reload(util)
reload(steps)
reload(sequence)
reload(shots)
reload(assets)
reload(types)


class AppBlast:
    ui = None
    parent = None
    project = None
    context = None
    query = ""

    def __init__(self, parent=None):
        self.parent = parent
        self.project = context.get_project()
        self.context = context.get_context()

    def open(self):
        self.parent.close()
        self.ui = util.load_ui_engine(name='blast', target=self.parent)
        self.parent.ui.main_layout.addWidget(self.ui)
        self.navigator(title="PLAYBLAST SHOT", subtitle="Management preview")
        self.ui.play_pause.clicked.connect(self.play_pause)
        self.ui.export_blast.clicked.connect(self.create_blast)
        self.parent.setFixedSize(500, 200)
        self.populate()
        self.parent.show()

    def populate(self):
        step_shot = ""
        try:
            if "." in self.context.get("step"):
                step_shot = self.context.get("step").split(".")[1]
            elif "_" in self.context.get("step"):
                step_shot = self.context.get("step").split("_")[1]
        except:
            step_shot = self.context.get("step")

        self.ui.sequence.setText(self.context.get("sequence"))
        self.ui.shot.setText(self.context.get("name"))
        self.ui.step.setText(step_shot)

        all_cameras = self.parent.get_all_cameras()
        for cam in all_cameras:
            self.ui.cameras.addItem(cam.get("name"))

        resolutions = util.resolutions.keys()
        self.ui.resolution.clear()
        self.ui.resolution.addItems(resolutions)

        if len(all_cameras) > 0:
            first_cam = all_cameras[0]
            self.ui.cameras.setCurrentText(first_cam.get("name"))

    def navigator(self, title="OPEN", subtitle="Open files"):
        try:
            data_project = context.get_project()
            data_context = dict(context.get_context())

            try:
                step = data_context.get("step").split("_")[1]
            except:
                step = data_context.get("step")

            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">{title} </span><span style=" font-size:10pt;">{navigate}</span></p></body></html>'.format(title=title, navigate=data_context.get("type").capitalize()))
            if data_context.get("type"):
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style="font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{step}, {type} {name}</span></p></body></html>'.format(project=data_project.get("name"), step=step, type=data_context.get('type'), name=data_context.get('name')))
            else:
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info=subtitle))
        except Exception as error:
            util.message_log(error)

    def play_pause(self):
        if self.ui.play_pause.isChecked():
            name = "pause"
            self.parent.play_pause(True)
        else:
            name = "play"
            self.parent.play_pause(False)
        QtCore.QCoreApplication.processEvents()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/assets/{}".format(name)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.play_pause.setIcon(icon)

    def create_blast(self):
        ctx = context.get_context()
        prj = context.get_project()
        info = util.get_info_context(ctx, prj)
        template = util.get_template()
        settings = util.get_settings()

        context_template = template.get(prj.get("engine").get("type")).get("playblast")
        blast_path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), context_template.format(**info.get("info")))
        blast_path = os.path.normpath(blast_path)
        blast_path_dir = os.path.dirname(blast_path)
        if not os.path.exists(blast_path_dir):
            os.makedirs(blast_path_dir)

        files = glob("{}/*.mp4".format(blast_path_dir))
        if len(files) >= 1:
            version = (len(files) + 1)
        else:
            version = 1

        fields = info.get("info")
        fields["version"] = "{:03d}".format(version)

        blast_path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), context_template.format(**fields))
        self.parent.playblast(path=blast_path, ctx=ctx, prj=prj, ui=self.ui)
