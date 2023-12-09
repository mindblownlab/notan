import json
import os
import uuid

import utils.util
from models import shots, assets, types, steps, sequence
from PySide2 import QtWidgets, QtCore, QtGui
from utils import util, context
from importlib import reload
from glob import glob

reload(util)
reload(steps)
reload(sequence)
reload(shots)
reload(assets)
reload(types)


class AppWorkfiles:
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
        try:
            self.parent.close()
            self.ui = util.load_ui_engine(name='workfiles', target=self.parent)
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(800, 600)
            self.populate()
            self.navigator(title="OPEN")
            self.ui.work_tab.currentChanged.connect(lambda x: self.navigator(title="OPEN"))
            self.ui.files_tab.currentChanged.connect(self.reload_files)
            self.ui.assets.itemClicked.connect(self.collect)
            self.ui.shots.itemClicked.connect(self.collect)
            self.ui.file_open_button.clicked.connect(self.file_open_click)
            self.ui.new_file.clicked.connect(self.new_file)
            self.ui.work_files.itemDoubleClicked.connect(self.file_open_click)
            self.ui.publish_files.itemDoubleClicked.connect(self.file_open_click)
            self.ui.query.textChanged.connect(self.searching)
            self.ui.file_open_button.setDisabled(False)
            self.ui.new_file.setDisabled(True)
            self.ui.file_open_button.setDisabled(True)

            self.parent.show()

        except Exception as error:
            util.message_log(error)

    # SAVE

    def open_save(self):
        try:
            self.parent.close()
            ctx = context.get_context()
            prj = context.get_project()
            info = util.get_info_context(ctx, prj)
            template = utils.util.get_template()

            context_template = template.get(prj.get("engine").get("type")).get("{}_work".format(ctx.get("type")))

            self.ui = util.load_ui_engine(name='save', target=self.parent)
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(500, 250)
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">FILE SAVE </span><span style=" font-size:10pt;">{name}</span></p></body></html>'.format(name=""))
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=prj.get("name").upper(), info="Saving file"))

            self.ui.asset_name.setText(os.path.basename(info.get("path")))
            self.ui.asset_version.setValue(info.get("version"))
            self.ui.asset_preview.setText(context_template.format(**info.get("info")))
            self.ui.save.clicked.connect(self.save)
            self.ui.cancel.clicked.connect(self.parent.close)

            self.parent.show()
        except Exception as error:
            util.message_log(error)

    def save(self):
        try:
            ctx = context.get_context()
            prj = context.get_project()
            info = util.get_info_context(ctx, prj)
            path = info.get("path")
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            self.parent.save_scene(path)
            util.thumbnail(path=os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(path)), "thumb.png")))
            self.parent.close()
        except Exception as error:
            util.message_log(error)

    def searching(self, query):
        self.populate()
        self.ui.assets.expandAll()
        self.ui.shots.expandAll()

    def populate(self):
        try:
            model_assets = assets.AssetsModel()
            model_sequence = sequence.SequenceModel()
            model_types = types.TypesModel()
            model_shots = shots.ShotsModel()
            model_steps = steps.StepsModel()

            self.ui.assets.clear()
            self.ui.shots.clear()
            self.ui.publish_files.clear()
            self.ui.work_files.clear()

            self.ui.work_files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            self.ui.publish_files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")

            all_assets = model_assets.all()
            all_sequences = model_sequence.all()
            all_types = model_types.all()
            all_shots = model_shots.all()
            all_steps_assets = model_steps.all(type="asset")
            all_steps_shots = model_steps.all(type="shot")

            for typ in all_types:
                type_menu = QtWidgets.QTreeWidgetItem(self.ui.assets)
                type_menu.setText(0, os.path.basename(typ.get("name")))
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                type_menu.setIcon(0, icon)
                typ.update({"uuid": "asset_type"})
                type_menu.setData(0, QtCore.Qt.UserRole, typ)

                get_assets = list(filter(lambda ast: ast.get("asset_type") == typ.get("name") and self.ui.query.text().lower() in ast.get("name").lower(), all_assets))
                if len(get_assets) > 0:
                    for ast in get_assets:
                        asset_menu = QtWidgets.QTreeWidgetItem(type_menu)
                        asset_menu.setText(0, os.path.basename(ast.get("name")))
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(":/assets/cube.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                        asset_menu.setIcon(0, icon)
                        ast.update({"uuid": "asset"})
                        asset_menu.setData(0, QtCore.Qt.UserRole, ast)

                        if len(all_steps_assets) > 0:
                            for stpa in all_steps_assets:
                                step_shot_menu = QtWidgets.QTreeWidgetItem(asset_menu)
                                step_shot_menu.setText(0, stpa.get("name"))

                                icon_shot_step = QtGui.QIcon()
                                icon_shot_step.addPixmap(QtGui.QPixmap(":/assets/step.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                                step_shot_menu.setIcon(0, icon_shot_step)
                                stpa.update({"uuid": "step"})
                                step_shot_menu.setData(0, QtCore.Qt.UserRole, stpa)

            for sqc in all_sequences:
                sec_menu = QtWidgets.QTreeWidgetItem(self.ui.shots)
                sec_menu.setText(0, os.path.basename(sqc.get("name")))
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                sec_menu.setIcon(0, icon)
                sqc.update({"uuid": "sequence"})
                sec_menu.setData(0, QtCore.Qt.UserRole, sequence)

                get_shots = list(filter(lambda sht: sht.get("sequence") == sqc.get("name") and self.ui.query.text().lower() in ast.get("name").lower(), all_shots))
                if len(get_shots) > 0:
                    for sht in get_shots:
                        shot_menu = QtWidgets.QTreeWidgetItem(sec_menu)
                        shot_menu.setText(0, os.path.basename(sht.get("name")))
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(":/assets/movie.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                        shot_menu.setIcon(0, icon)
                        sht.update({"uuid": "shot"})
                        shot_menu.setData(0, QtCore.Qt.UserRole, sht)

                        if len(all_steps_assets) > 0:
                            for stps in all_steps_shots:
                                step_shot_menu = QtWidgets.QTreeWidgetItem(shot_menu)
                                step_shot_menu.setText(0, stps.get("name"))
                                icon_shot_step = QtGui.QIcon()
                                icon_shot_step.addPixmap(QtGui.QPixmap(":/assets/step.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                                step_shot_menu.setIcon(0, icon_shot_step)
                                stps.update({"uuid": "step"})
                                step_shot_menu.setData(0, QtCore.Qt.UserRole, stps)
        except Exception as error:
            pass
            # util.message_log(error)

    def collect(self, it):
        try:
            self.ui.work_files.clear()
            self.ui.publish_files.clear()
            self.ui.work_files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
            self.ui.publish_files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")

            if it:
                data_project = context.get_project()
                data_context = context.get_context()
                if it.parent():
                    data_type = dict(it.data(0, QtCore.Qt.UserRole)) or None
                    if data_type.get("uuid") == "step":
                        data = dict(it.parent().data(0, QtCore.Qt.UserRole))
                        settings = util.get_settings()

                        type_file = self.ui.files_tab.currentIndex()

                        if it.parent() is None:
                            self.ui.new_file.setEnabled(False)
                        else:
                            self.ui.new_file.setEnabled(True)
                        if type_file == 0:
                            target = self.ui.work_files
                            local = "work"
                        else:
                            target = self.ui.publish_files
                            local = "publish"

                        template = util.get_template()
                        context_path = template.get(data_project.get("engine").get("type")).get("{}_{}".format(data.get("type"), local))
                        step_shot = data_type.get("name")
                        try:
                            if "." in data_type.get("name"):
                                step_shot = data_type.get("name").split(".")[1]
                            elif "_" in data_type.get("name"):
                                step_shot = data_type.get("name").split("_")[1]
                        except:
                            pass

                        data_field = {
                            "asset": {
                                "asset_type": data.get("asset_type"),
                                "asset": data.get("name"),
                                "filename": data.get("name"),
                                "step": data_type.get("name"),
                                "version": "{:03d}".format(1),
                                "ext": data_project.get("engine").get("ext")
                            },
                            "shot": {
                                "sequence": data.get("sequence"),
                                "shot": data.get("name"),
                                "step": step_shot,
                                "filename": data.get("name"),
                                "version": "{:03d}".format(1),
                                "ext": data_project.get("engine").get("ext")
                            }
                        }

                        path = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), data_project.get("engine").get(local), context_path.format(**data_field.get(data.get("type"))))
                        path = os.path.normpath(path)

                        files = util.get_files(project=data_project, context=data_context, path=path)
                        if len(files) <= 0:
                            target.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
                        else:
                            target.setStyleSheet("")

                        if len(files) > 0:
                            self.ui.file_open_button.setDisabled(False)
                        else:
                            self.ui.file_open_button.setDisabled(True)

                        for file in files:
                            item_file = QtWidgets.QTreeWidgetItem(target)
                            item_file.setText(0, " {filename}\n Version: {version}\n Update: {date}\n Size: {bytes}".format(filename=file.get("filename"), version=file.get("version"), date=file.get("date").get("last_modified"), bytes=file.get("size").get("bytes")))
                            icon_file = QtGui.QIcon()
                            thumbnail = os.path.join(os.path.dirname(os.path.dirname(file.get("path"))), "thumb.png")
                            if not os.path.exists(thumbnail):
                                image = QtGui.QPixmap(":/assets/ico_{}.png".format(data_project.get("engine").get("type")))
                                target.setIconSize(QtCore.QSize(60, 60))
                            else:
                                image = QtGui.QPixmap(thumbnail)
                                target.setIconSize(QtCore.QSize(120, 60))
                            icon_file.addPixmap(image, QtGui.QIcon.Normal, QtGui.QIcon.On)
                            item_file.setIcon(0, icon_file)
                            item_file.setData(0, QtCore.Qt.UserRole, {**data, **file})
        except Exception as error:
            util.message_log(error)

    def file_open_click(self):
        type_file = self.ui.files_tab.currentIndex()
        if type_file == 0:
            target = self.ui.work_files.currentItem()
        else:
            target = self.ui.publish_files.currentItem()
        self.file_open(target)

    def reload_files(self):
        try:
            tab_index = self.ui.work_tab.currentIndex()
            if tab_index == 0:
                item = self.ui.assets.currentItem()
            else:
                item = self.ui.shots.currentItem()

            self.collect(item)
        except Exception as error:
            util.message_log(error)

    def file_open(self, target):
        try:
            tab_index = self.ui.work_tab.currentIndex()
            data = dict(target.data(0, QtCore.Qt.UserRole))
            if tab_index == 0:
                item = self.ui.assets.currentItem()
            else:
                item = self.ui.shots.currentItem()
            data_type = dict(item.data(0, QtCore.Qt.UserRole))
            data.update({"step": data_type.get("name")})
            os.environ['MB_CONTEXT'] = json.dumps(data)
            self.parent.open_scene(data)
            self.parent.close()
        except Exception as error:
            util.message_log(error)

    def new_file(self):
        try:
            tab_index = self.ui.work_tab.currentIndex()
            if tab_index == 0:
                item = self.ui.assets.currentItem()
            else:
                item = self.ui.shots.currentItem()
            data_type = dict(item.data(0, QtCore.Qt.UserRole))
            data = dict(item.parent().data(0, QtCore.Qt.UserRole))
            data.update({"step": data_type.get("name")})
            prj = context.get_project()
            os.environ['MB_CONTEXT'] = json.dumps(data)
            self.parent.create_new_file(ctx=data, prj=prj)
            self.parent.close()
        except Exception as error:
            util.message_log(error)

    # OTHERS
    def navigator(self, title="OPEN", subtitle="Open files"):
        try:
            tab_index = self.ui.work_tab.currentIndex()
            data_project = context.get_project()
            data_context = dict(context.get_context())

            try:
                step = data_context.get("step").split("_")[1]
            except:
                step = data_context.get("step")

            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">{title} </span><span style=" font-size:10pt;">{navigate}</span></p></body></html>'.format(title=title, navigate=self.ui.work_tab.tabText(tab_index)))
            if data_context.get("type"):
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style="font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{step}, {type} {name}</span></p></body></html>'.format(project=data_project.get("name"), step=step, type=data_context.get('type'), name=data_context.get('name')))
            else:
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">| {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project=data_project.get("name").upper(), info=subtitle))
        except Exception as error:
            util.message_log(error)


from utils import resources
