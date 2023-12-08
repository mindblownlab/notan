import json
import os
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


class AppLoader:
    ui = None
    parent = None
    project = None
    context = None
    query = ""

    def __init__(self, parent=None):
        self.parent = parent
        self.project = context.get_project()
        self.context = context.get_context()

    def searching(self, query):
        self.populate()
        self.ui.assets.expandAll()
        self.ui.shots.expandAll()

    def open(self):
        try:
            self.parent.close()
            self.ui = util.load_ui_engine(name='load', target=self.parent)
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(800, 600)
            self.navigator(title="LOAD FILE", subtitle="Loading files")

            self.ui.assets.itemClicked.connect(self.open_files)
            self.ui.shots.itemClicked.connect(self.open_files)
            self.ui.cache_type.currentIndexChanged.connect(self.check_type)
            self.ui.load_type.currentIndexChanged.connect(self.check_type)
            self.ui.load_engine.currentIndexChanged.connect(self.check_type)
            self.ui.button_reference.clicked.connect(self.reference_file)
            self.ui.button_import.clicked.connect(self.import_file)
            self.ui.load_type.setEnabled(False)

            templates = util.get_project_template().get("template")
            engines = list(filter(lambda eng: eng.get("engine"), templates))
            engines = list(map(lambda eng: eng.get("name"), engines))
            self.ui.load_engine.clear()
            self.ui.load_engine.addItems(engines)
            self.ui.load_engine.setCurrentText(self.project.get("engine").get("work"))

            self.populate()
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def open_files(self, it):
        try:
            if it.parent():
                data = dict(it.data(0, QtCore.Qt.UserRole))
                data_project = context.get_project()
                settings = util.get_settings()

                if it.parent():
                    self.ui.load_type.setEnabled(True)
                    self.ui.files.clear()
                    load_type = self.ui.load_type.currentText()
                    load_type = load_type.lower()
                    load_engine = self.ui.load_engine.currentText()
                    load_type_name = load_type

                    try:
                        engine_type = load_engine.split(".")[1]
                        engine_type = engine_type.lower()
                    except:
                        engine_type = data_project.get("engine").get("type")

                    template = util.get_template()
                    context_path = template.get(engine_type).get("{}_{}".format(data.get("type"), load_type_name))
                    data_field = {
                        "asset": {
                            "asset_type": data.get("asset_type"),
                            "asset": data.get("name"),
                            "name": data.get("name"),
                            "filename": data.get("name"),
                            "step": "*",
                            "version": "{:03d}".format(1),
                            "ext": data_project.get("engine").get("ext")
                        },
                        "shot": {
                            "sequence": data.get("sequence"),
                            "shot": data.get("name"),
                            "name": data.get("name"),
                            "step": "*",
                            "filename": data.get("name"),
                            "version": "{:03d}".format(1),
                            "ext": data_project.get("engine").get("ext")
                        }
                    }
                    ctx = context.get_context()
                    if util.get_relation("assembly") in ctx.get("step"):
                        data_field[data.get("type")].update({"type": self.ui.cache_type.currentText()})
                        path = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), load_engine, context_path.format(**data_field.get(data.get("type"))))
                    else:
                        path = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), load_engine, context_path.format(**data_field.get(data.get("type"))))
                    path = os.path.normpath(path)
                    files = self.files_published(path=path, type=data.get("type"))
                    if data.get("type") == "shot":
                        path_sounds = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), str(load_engine), "sound", "scenes", data.get("sequence"), data.get("name"))
                        path_sounds = os.path.normpath(path_sounds)
                        souds = self.files_sounds(path=path_sounds)
                        if len(souds) > 0:
                            files += souds

                    if len(files) <= 0:
                        self.ui.files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")
                    else:
                        self.ui.files.setStyleSheet("")

                    if len(files) > 0:
                        for file in files:
                            step_name = str(os.path.basename(os.path.dirname(file.get("path"))))
                            try:
                                if "." in step_name:
                                    step_name = step_name.split(".")[1]
                                elif "_" in step_name:
                                    step_name = step_name.split("_")[1]
                            except:
                                pass

                            item_file = QtWidgets.QTreeWidgetItem(self.ui.files)
                            item_file.setText(0, "{step} | {filename} | Size: {bytes}\n Update: {date}".format(step=step_name, filename=file.get("filename"), version=file.get("version"), date=file.get("date").get("last_modified"), bytes=file.get("size").get("bytes")))
                            filename, ext = os.path.splitext(file.get("path"))
                            icon = QtGui.QIcon()
                            icon.addPixmap(QtGui.QPixmap(util.load_icon_ext(name=ext.replace(".", ""))), QtGui.QIcon.Normal, QtGui.QIcon.On)
                            item_file.setIcon(0, icon)
                            item_file.setData(0, QtCore.Qt.UserRole, {**data, **file})
                else:
                    self.ui.load_type.setEnabled(False)
        except Exception as error:
            util.message_log(error)

    def check_type(self):
        try:
            tab_index = self.ui.work_tab.currentIndex()
            if tab_index == 0:
                item = self.ui.assets.selectedItems()[0]
            else:
                item = self.ui.shots.selectedItems()[0]
            self.open_files(item)
        except:
            pass

    def reference_file(self):
        if len(self.ui.files.selectedItems()) > 0:
            ctx = context.get_context()
            for file in self.ui.files.selectedItems():
                data = dict(file.data(0, QtCore.Qt.UserRole))
                for i in range(self.ui.limit.value()):
                    self.parent.reference_file(data=data, ctx=ctx, index=i)

    def import_file(self):
        if len(self.ui.files.selectedItems()) > 0:
            ctx = context.get_context()
            for file in self.ui.files.selectedItems():
                data = dict(file.data(0, QtCore.Qt.UserRole))
                for i in range(self.ui.limit.value()):
                    self.parent.import_file(data=data, ctx=ctx)

    def populate(self):
        try:
            model_assets = assets.AssetsModel()
            model_sequence = sequence.SequenceModel()
            model_types = types.TypesModel()
            model_shots = shots.ShotsModel()

            self.ui.assets.clear()
            self.ui.shots.clear()
            self.ui.files.clear()

            self.ui.files.setStyleSheet("background-image: url(:/assets/empty_engine.png);\nbackground-position: center;\nbackground-repeat: no-repeat;")

            all_assets = model_assets.all()
            all_sequences = model_sequence.all()
            all_types = model_types.all()
            all_shots = model_shots.all()

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

        except Exception as error:
            util.message_log(error)

    def files_sounds(self, path):
        file_path = "{}.wav".format(path)
        files = glob(file_path)
        files = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, files))
        files = list(map(lambda sec: os.path.normpath(sec), files))
        files = sorted(files, key=lambda file: os.path.getctime(file))
        files.reverse()
        data_file = []
        for file_path in files:
            filename = os.path.basename(file_path)
            file_data = {
                "filename": filename,
                "type": "sound",
                "version": 1,
                "path": file_path,
                "date": util.get_data_file(file_path),
                "size": util.get_size_file(file_path),
            }
            data_file.append(file_data)
        return data_file

    def files_published(self, path, type=None):
        filename, ext = os.path.splitext(path)
        file_path = os.path.join(os.path.dirname(path), "*{}".format(ext))
        files = glob(file_path)
        files = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, files))
        files = list(map(lambda sec: os.path.normpath(sec), files))
        files = sorted(files, key=lambda file: os.path.getctime(file))
        files.reverse()
        data_file = []
        for file_path in files:
            filename = os.path.basename(file_path)
            version = int(filename.split(".")[1].replace("v", ""))
            file_data = {
                "filename": filename,
                "version": version,
                "type": type,
                "path": file_path,
                "date": util.get_data_file(file_path),
                "size": util.get_size_file(file_path),
            }
            data_file.append(file_data)
        return data_file

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
