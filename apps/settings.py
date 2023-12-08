import copy
import json
import uuid
from importlib import reload
from utils import util, context
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from copy import deepcopy
from functools import partial

reload(util)


class AppSettings:
    tabs = ["asset", "shot", "types_assets"]
    engine = None

    def __init__(self, parent=None):
        self.parent = parent

    def open(self, root):
        try:
            self.root = root
            self.parent.close()
            self.ui = util.load_ui(name='app_settings')
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setWindowTitle('Manager • Settings')
            self.ui.create.clicked.connect(self.create_item)
            self.ui.tab_settings.currentChanged.connect(self.check_add_item)
            self.ui.open_project.clicked.connect(self.open_project)
            self.ui.studio_name.textChanged.connect(self.save_text)
            self.ui.folder_production.textChanged.connect(self.save_text)
            self.ui.create_folder.clicked.connect(self.create_folder)
            self.ui.project_template.itemClicked.connect(self.set_folder_engine)

            self.navigator()
            self.populate()
            self.ui.tab_settings.setCurrentIndex(0)
            self.parent.show()

        except Exception as error:
            util.message_log(error)

    def check_add_item(self):
        tab_index = self.ui.tab_settings.currentIndex()
        if tab_index == 3:
            self.ui.name.setDisabled(True)
            self.ui.create.setDisabled(True)
        else:
            self.ui.name.setDisabled(False)
            self.ui.create.setDisabled(False)

        if tab_index == 4:
            settings = util.get_settings()
            step_assets = settings.get("steps").get("asset")
            step_shots = settings.get("steps").get("shot")
            relations = settings.get("relations")

            steps_assets = ["model", "lookdev", "rigging"]
            steps_shots = ["animation", "assembly", "light"]

            fields_clear = steps_assets + steps_shots
            for field in fields_clear:
                c_field = self.ui.findChild(QtWidgets.QComboBox, "relation_{}".format(field))
                c_field.clear()

            for step in steps_assets:
                field_asset = self.ui.findChild(QtWidgets.QComboBox, "relation_{}".format(step))
                field_asset.currentTextChanged.connect(partial(self.update_relation, field_asset, step))
                field_asset.addItems(step_assets)
                field_asset.setCurrentText(relations.get(step))

            for shot in steps_shots:
                field_shot = self.ui.findChild(QtWidgets.QComboBox, "relation_{}".format(shot))
                field_shot.currentTextChanged.connect(partial(self.update_relation, field_shot, shot))
                field_shot.addItems(step_shots)
                field_shot.setCurrentText(relations.get(shot))

    def delete_event(self):
        try:
            tab_index = self.ui.tab_settings.currentIndex()
            settings = util.get_settings()
            item = None
            if tab_index == 0:
                item = self.ui.template_step_assets.currentItem()
            elif tab_index == 1:
                item = self.ui.template_step_shots.currentItem()
            elif tab_index == 2:
                item = self.ui.template_type_assets.currentItem()
            elif tab_index == 3:
                item = self.ui.project_template.currentItem()
            name = item.text(0)
            if item:
                result = QtWidgets.QMessageBox.question(self.parent, "Delete item?", "Do you want to remove this item now?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.Yes:
                    if tab_index in [0, 1]:
                        data = deepcopy(settings["steps"][self.tabs[tab_index]])
                        data = list(filter(lambda r: r != name, data))
                        settings["steps"][self.tabs[tab_index]] = data
                        util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
                    elif tab_index == 3:
                        structure = util.get_project_template()
                        structure = structure.get("template")
                        data = item.data(0, QtCore.Qt.UserRole)
                        if item.parent():
                            for s in range(len(structure)):
                                folder = structure[s]

                                if len(folder.get("children")) > 0:
                                    for sf in range(len(folder.get("children"))):
                                        sub_folder = structure[s]["children"][sf]
                                        if sub_folder.get("_id") == data.get("_id"):
                                            del structure[s]["children"][sf]

                                if folder.get("_id") == data.get("_id"):
                                    del structure[s]
                        else:
                            structure = list(filter(lambda r: r.get("_id") != data.get("_id"), structure))
                        structure = {
                            "template": structure
                        }
                        util.storage(data=structure, path=os.path.join(util.get_root_path(), 'config', 'structure.yml'), replace=True)
                    else:
                        data = deepcopy(settings[self.tabs[tab_index]])
                        data = list(filter(lambda r: r != name, data))
                        settings[self.tabs[tab_index]] = data
                        util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
                    self.populate()
        except Exception as error:
            util.message_log(error)

    def open_project(self):
        try:
            dialog = QtWidgets.QFileDialog()
            dialog.setWindowTitle('Select project root')
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)
            dialog.setDirectory(self.ui.project_root.text() or "C:/")
            filename = None
            settings = util.get_settings()
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                filename = dialog.selectedFiles()
            if filename:
                self.ui.project_root.setText(filename[0])
                settings.update({"project_root": filename[0]})
                util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
                self.populate()
                self.parent.reload()
        except Exception as error:
            util.message_log(error)

    def save_text(self):
        try:
            settings = util.get_settings()
            settings.update({"studio": {"name": self.ui.studio_name.text()}, "folder_production": self.ui.folder_production.text()})
            util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)

            self.parent.ui.studio_name.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">{studio}  </span><span style=" font-size:9pt;"><br/></span></p></body></html>'.format(studio=settings.get("studio").get("name")))

        except Exception as error:
            util.message_log(error)

    def create_item(self):
        try:
            tab_index = self.ui.tab_settings.currentIndex()
            settings = util.get_settings()
            name = self.ui.name.text()

            if name == "":
                QtWidgets.QMessageBox.question(self.parent, "Name is empty", "Fill in the name field to continue!", QtWidgets.QMessageBox.Ok)
                return

            if tab_index in [0, 1]:
                settings["steps"][self.tabs[tab_index]].append(name)
            else:
                settings[self.tabs[tab_index]].append(name)
            util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
            self.ui.name.setText("")
            self.populate()
        except Exception as error:
            util.message_log(error)

    def delete_item(self):
        try:
            tab_index = self.ui.tab_settings.currentIndex()
            settings = util.get_settings()
            item = None
            if tab_index == 0:
                item = self.ui.template_step_assets.currentItem()
            elif tab_index == 1:
                item = self.ui.template_step_shots.currentItem()
            elif tab_index == 2:
                item = self.ui.template_type_assets.currentItem()
            name = item.text(0)

            if tab_index in [0, 1]:
                data = deepcopy(settings["steps"][self.tabs[tab_index]])
                data = list(filter(lambda r: r != name, data))
                settings["steps"][self.tabs[tab_index]] = data
            else:
                data = deepcopy(settings[self.tabs[tab_index]])
                data = list(filter(lambda r: r != name, data))
                settings[self.tabs[tab_index]] = data
            util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
            self.populate()
        except Exception as error:
            util.message_log(error)

    def cancel_engine(self):
        self.ui.folder_name.setText("")
        self.ui.folder_children.setCurrentIndex(0)
        self.populate()

    def create_folder(self):
        try:
            project_template = util.get_project_template()
            name = self.ui.folder_name.text()
            children = self.ui.folder_children.currentText()

            if project_template is None:
                project_template = {
                    "template": []
                }

            data_folder = {
                "_id": str(uuid.uuid4()),
                "name": name,
                "engine": False,
                "root": True,
                "children": [],
            }

            try:
                if children not in ["ROOT", "", None]:
                    data_folder.update({"root": False, "engine": False})
                    folder_index = next((index for (index, d) in enumerate(project_template["template"]) if d["name"] == children), None)
                    project_template["template"][folder_index]["children"].append(data_folder)
                else:
                    project_template["template"].append(data_folder)
            except Exception as error:
                util.message_log(error)
            util.storage(data=project_template, path=os.path.join(util.get_root_path(), 'config', 'structure.yml'), replace=True)
            self.cancel_engine()
        except Exception as error:
            util.message_log(error)

    def edit_engine(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            self.engine = data
            self.ui.code.setText(data.get("folder_path").get("code") or "0")
            self.ui.name_engine.setText(data.get("folder_path").get("name") or data.get("type").upper())
            self.ui.engine_widget.setEnabled(True)
        except Exception as error:
            util.message_log(error)

    def populate(self):
        try:

            settings = util.get_settings()

            self.ui.studio_name.setText(settings.get("studio").get("name"))
            self.ui.project_root.setText(settings.get("project_root"))
            self.ui.project_root.setText(settings.get("project_root"))
            self.ui.folder_production.setText(settings.get("folder_production"))

            step_assets = settings.get("steps").get("asset")
            step_shots = settings.get("steps").get("shot")
            types_assets = settings.get("types_assets")

            self.ui.template_step_assets.clear()
            self.ui.template_step_shots.clear()
            self.ui.template_type_assets.clear()
            self.ui.project_template.clear()
            self.ui.folder_children.clear()

            for tsa in step_assets:
                item_tsa = QtWidgets.QTreeWidgetItem(self.ui.template_step_assets)
                item_tsa.setText(0, tsa)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                item_tsa.setIcon(0, icon)

            for tss in step_shots:
                item_tss = QtWidgets.QTreeWidgetItem(self.ui.template_step_shots)
                item_tss.setText(0, tss)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                item_tss.setIcon(0, icon)

            for tta in types_assets:
                item_tta = QtWidgets.QTreeWidgetItem(self.ui.template_type_assets)
                item_tta.setText(0, tta)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                item_tta.setIcon(0, icon)

            structure = util.get_project_template()
            self.ui.folder_children.addItem("ROOT")
            if structure:
                structure_template = util.get_project_template().get("template")
                structure_template = sorted(structure_template, key=lambda d: d['name'])
                structure_roots = copy.deepcopy(structure_template)
                structure_roots = list(filter(lambda rto: rto.get("root"), structure_roots))
                structure_roots_names = list(map(lambda rton: rton.get("name"), structure_roots))
                self.ui.folder_children.addItems(structure_roots_names)

                for tpl in structure_template:
                    item_tpl = QtWidgets.QTreeWidgetItem(self.ui.project_template)
                    item_tpl.setData(0, QtCore.Qt.UserRole, tpl)
                    item_tpl.setText(0, tpl.get("name"))
                    icon_tpl = QtGui.QIcon()
                    icon_tpl.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    item_tpl.setIcon(0, icon_tpl)
                    if tpl.get("engine"):
                        item_tpl.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        item_tpl.setCheckState(0, QtCore.Qt.Unchecked)

                    if len(tpl.get("children")) > 0:
                        sub_folder = sorted(tpl.get("children"), key=lambda d: d['name'])
                        for sub in sub_folder:
                            item_sub = QtWidgets.QTreeWidgetItem(item_tpl)
                            item_sub.setData(0, QtCore.Qt.UserRole, sub)
                            item_sub.setText(0, sub.get("name"))
                            icon_sub = QtGui.QIcon()
                            icon_sub.addPixmap(QtGui.QPixmap(":/assets/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                            item_sub.setIcon(0, icon_sub)

        except Exception as error:
            util.message_log(error)

    def update_relation(self, value, field):
        try:
            settings = util.get_settings()
            if "relations" not in settings.keys():
                settings.update({"relations": {}})
            settings["relations"][field] = value.currentText()
            util.storage(data=settings, path=os.path.join(util.get_root_path(), 'config', 'settings.yml'), replace=True)
        except Exception as error:
            util.message_log(error)

    def set_folder_engine(self, it):
        if it.parent() is None:
            project_template = util.get_project_template()
            data = dict(it.data(0, QtCore.Qt.UserRole))
            data.update({"engine": it.checkState(0) == QtCore.Qt.Checked})
            folder_index = next((index for (index, d) in enumerate(project_template["template"]) if d["_id"] == data.get("_id")), None)
            project_template["template"][folder_index] = data
            util.storage(data=project_template, path=os.path.join(util.get_root_path(), 'config', 'structure.yml'), replace=True)
            self.populate()

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Settings </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;"> | {project}</span><span style=" font-size:9pt;"><br/>{info}</span></p></body></html>'.format(project="General Settings", info="Manage settings"))
        except Exception as error:
            util.message_log(error)


from utils import resources
