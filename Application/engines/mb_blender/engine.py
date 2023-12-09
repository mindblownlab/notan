import json
import bpy
import os
from PySide2 import QtWidgets, QtGui
from utils import util
from utils import context as ctx
from modules import workfiles, project, loader, publish, manager
from importlib import reload

reload(workfiles)
reload(project)
reload(loader)
reload(publish)
reload(manager)


class BlenderEngine(QtWidgets.QMainWindow):
    ui = None
    settings = None
    app_workfile = None
    app_project = None
    app_loader = None
    app_publish = None
    app_manager = None

    def __init__(self, parent=None):
        super(BlenderEngine, self).__init__(parent)
        self.setStyleSheet(util.get_style())
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.ui = util.load_ui_engine(target=self, name="core")
        self.setCentralWidget(self.ui.main_container)
        self.settings = util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))

        self.ui.studio_name.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">{studio}  </span><span style=" font-size:9pt;"><br/></span></p></body></html>'.format(studio=self.settings.get("studio").get("name")))
        self.ui.version.setText("v{}".format(self.settings.get("developer").get("version")))
        self.ui.develop_by.setText('<html><head/><body><p>Develop by <span style=" font-size:9pt; font-weight:600;">{company}</span></p></body></html>'.format(company=self.settings.get("developer").get("name")))

        self.setWindowTitle(self.settings.get("studio").get("name"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/assets/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.app_workfile = workfiles.AppWorkfiles(self)
        self.app_project = project.AppProject(self)
        self.app_loader = loader.AppLoader(self)
        self.app_publish = publish.AppPublish(self)
        self.app_manager = manager.AppManager(self)

    def open_scene(self, ctx=None):
        try:
            bpy.ops.wm.open_mainfile(filepath=ctx.get("path"))
            bpy.ops.object.select_all(action='DESELECT')
        except Exception as error:
            util.message_log(error)
        bpy.ops.script.reload()

    def save_scene(self, file=None):
        try:
            self.thumbnail(file)
            bpy.ops.wm.save_as_mainfile(filepath=file)
        except Exception as error:
            util.message_log(error)
        bpy.ops.script.reload()

    def publish_scene(self, file=None, ctx=None, prj=None):
        try:
            bpy.ops.object.select_all(action='DESELECT')
            if ctx.get("step") == util.get_relation("lookdev"):
                for collection in bpy.context.scene.collection.children:
                    for obj in collection.all_objects:
                        if ctx.get("step") == "LookDev":
                            if obj.type == "MESH":
                                is_cache = list(filter(lambda m: "_Cache" in m[0], obj.modifiers.items()))
                                if len(is_cache) <= 0:
                                    try:
                                        bpy.ops.object.select_all(action='DESELECT')
                                        bpy.context.view_layer.objects.active = obj
                                        obj.select_set(True)
                                        obj.name = "{}_{}".format(ctx.get("name"), obj.name)
                                        cache_name = "{}_Cache".format(obj.name)
                                        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
                                        bpy.ops.object.modifier_add(type='SUBSURF')
                                        bpy.context.object.modifiers["MeshSequenceCache"].name = cache_name
                                    except:
                                        pass
                                else:
                                    if ctx.get("asset") not in obj.name:
                                        obj.name = "{}_{}".format(ctx.get("asset"), obj.name)
                                        modifie = list(filter(lambda mdf: mdf.type == "MESH_SEQUENCE_CACHE", obj.modifiers))
                                        if modifie:
                                            modifie = modifie[0]
                                            modifie.name = "{}_Cache".format(obj.name)
                                    else:
                                        modifie = list(filter(lambda mdf: mdf.type == "MESH_SEQUENCE_CACHE", obj.modifiers))
                                        if modifie:
                                            modifie = modifie[0]
                                            modifie.name = "{}_Cache".format(obj.name)

                        if ctx.get("step") == util.get_relation("model"):
                            if obj.type == "EMPTY":
                                template = util.get_template()
                                project = ctx.get_project()
                                template = template.get("asset_cache")
                                settings = util.get_settings()
                                fields = {
                                    "asset_type": ctx.get("asset_type"),
                                    "asset": ctx.get("name"),
                                    "name": ctx.get("name"),
                                    "ext": "abc",
                                }

                                abc_path = os.path.join(util.get_root_path(), settings.get("project_root"), project.get("name"), settings.get("folder_production"), project.get("engine").get("publish"), template.format(**fields))
                                abc_path = os.path.normpath(abc_path)

                                abc_path_dir = os.path.dirname(abc_path)
                                if not os.path.exists(abc_path_dir):
                                    os.makedirs(abc_path_dir)
            else:
                if ctx.get("step") == util.get_relation("model"):
                    template = util.get_template()
                    template = template.get(prj.get("engine").get("type")).get("{}_alembic".format(ctx.get("type")))
                    settings = util.get_settings()
                    fields = {
                        "asset_type": ctx.get("asset_type"),
                        "asset": ctx.get("name"),
                        "name": ctx.get("name"),
                        "ext": "abc",
                    }

                    abc_path = os.path.join(util.get_root_path(), settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), template.format(**fields))
                    abc_path = os.path.normpath(abc_path)

                    data_publish = {
                        "_id": ctx.get("_id"),
                        "path": abc_path.replace("/", "\\"),
                        "path_storage": str(abc_path.split(prj.get("name"))[1]).replace("/", "\\"),
                        "name": ctx.get("name"),
                        "filename": os.path.basename(abc_path),
                        "type": ctx.get("type"),
                        "status": "active",
                        "engine": prj.get("engine").get("type"),
                        "step": "Alembic",
                        "created": util.current_date(),
                        "updated": util.current_date(),
                        "version": ctx.get("version"),
                    }

                    if not os.path.exists(os.path.dirname(abc_path)):
                        os.makedirs(os.path.dirname(abc_path))

                    context = self.get_context()
                    obj = bpy.data.objects["{}_master_grp".format(ctx.get("name"))]
                    obj.select_set(True)
                    if len(obj.children) > 0:
                        for chd in obj.children:
                            chd.select_set(True)

                    bpy.ops.wm.alembic_export(context, filepath=abc_path, vcolors=True, selected=True, start=1, end=1)

                    util.context_storage(
                        item=data_publish,
                        file=os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), settings.get("database"), "published.yml")
                    )

            bpy.ops.object.select_all(action='DESELECT')
            #bpy.ops.wm.save_as_mainfile(filepath=file, copy=True)

        except Exception as error:
            util.message_log(error)
        bpy.ops.script.reload()

    def create_new_file(self, ctx=None, prj=None):
        bpy.ops.wm.read_homefile(app_template="")
        try:
            for collect in bpy.data.collections:
                if collect.name == "Collection":
                    bpy.data.collections.remove(collect)
            if ctx.get("type") == "asset" and ctx.get("step") == util.get_relation("model"):
                assetName = "{}".format(ctx.get("name"))
                if assetName not in list(filter(lambda asset: asset.name, bpy.data.collections)):
                    bpy.ops.collection.create(name=assetName)
                    bpy.context.scene.collection.children.link(bpy.data.collections[assetName])

                    empty_obj = bpy.data.objects.new("empty", None, )
                    empty_obj.name = "{}_master_grp".format(ctx.get("name"))
                    empty_obj.empty_display_size = 1
                    bpy.data.objects[empty_obj.name]["Export"] = True
                    bpy.data.objects[empty_obj.name]["AssetId"] = str(ctx.get("_id"))

                    bpy.data.collections[assetName].objects.link(empty_obj)

            if ctx.get("type") == "asset" and ctx.get("step") == util.get_relation("lookdev"):
                try:
                    light_path = os.path.join(os.environ['MB_ROOT'], "studio_light", "blender", "scene.blend")
                    settings = util.get_settings()
                    template = util.get_template()
                    context_path = template.get(prj.get("engine").get("type")).get("{}_{}".format(ctx.get("type"), "publish"))
                    data_field = {
                        "asset_type": ctx.get("asset_type"),
                        "asset": ctx.get("name"),
                        "filename": ctx.get("name"),
                        "step": util.get_relation("model"),
                        "ext": prj.get("engine").get("ext")
                    }

                    if os.path.exists(light_path):
                        with bpy.data.libraries.load(light_path, link=True) as (data_from, data_to):
                            data_to.collections.append("Studio")
                        collection = bpy.data.collections.get("Studio")
                        collection.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable=True)

                    model_path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), context_path.format(**data_field))
                    model_path = os.path.normpath(model_path)
                    if os.path.exists(model_path):
                        with bpy.data.libraries.load(model_path, link=True) as (data_from, data_to):
                            data_to.collections.append(ctx.get("name"))
                        collection = bpy.data.collections.get(ctx.get("name"))
                        collection.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable=True)
                        bpy.ops.object.select_all(action='DESELECT')
                except Exception as error:
                    util.message_log(error)

            bpy.ops.object.select_all(action='DESELECT')
        except Exception as error:
            util.message_log(error)
        bpy.ops.script.reload()

    def reference_file(self, data=None):
        try:
            if ".abc" in data.get("path"):
                context = self.get_context()
                bpy.ops.wm.alembic_import(context, filepath=data.get("path"), as_background_job=False)

                bpy.ops.collection.create(name=data.get("name"))
                bpy.context.scene.collection.children.link(bpy.data.collections[data.get("name")])

                obj_name = "{}_master_grp".format(data.get("name"))
                obj = bpy.data.objects[obj_name]
                obj.empty_display_size = 1
                bpy.data.objects[obj.name]["Export"] = True
                bpy.data.objects[obj.name]["AssetId"] = str(data.get("_id"))
                bpy.data.collections[data.get("name")].objects.link(obj)
            else:
                with bpy.data.libraries.load(data.get("path"), link=True) as (data_from, data_to):
                    data_to.collections.append(data.get("name"))
                collection = bpy.data.collections.get(data.get("name"))
                collection.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable=True)
                bpy.ops.object.select_all(action='DESELECT')

        except Exception as error:
            util.message_log(error)

    def import_file(self, data=None):
        pass

    def thumbnail(self, path):
        try:
            if path:
                path = path.replace(".blend", ".png")
                path = os.path.normpath(path)
                if os.path.exists(path):
                    os.unlink(path)
            bpy.context.scene.render.filepath = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(path)), "thumb.png"))
            bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)
        except:
            pass

    def collect_meshs(self):
        _ctx = ctx.get_context()
        prj = ctx.get_project()
        settings = util.get_settings()
        template = util.get_template()
        template = template.get(prj.get("engine").get("type")).get("{}_alembic".format(_ctx.get("type")))
        data_field = {
            "asset": {
                "asset_type": _ctx.get("asset_type"),
                "asset": _ctx.get("name"),
                "name": "{}",
            },
            "shot": {
                "sequence": _ctx.get("sequence"),
                "shot": _ctx.get("name"),
                "name": "{}",
            },
        }

        path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), template.format(**data_field.get(_ctx.get("type"))))
        path = os.path.normpath(path)

        get_all_transforms = []
        for collection in bpy.context.scene.collection.children:
            for obj in collection.all_objects:
                if obj.type == "EMPTY":
                    try:
                        if bpy.data.objects[obj.name]["Export"]:
                            get_all_transforms.append({"name": obj.name, "path": path, "root": obj.name})
                    except:
                        pass

        return get_all_transforms

    def get_context(self):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    for region in area.regions:
                        if region.type == "WINDOW":
                            context_override = {
                                "window": window,
                                "screen": window.screen,
                                "area": area,
                                "region": region,
                                "scene": bpy.context.scene,
                            }
                        return context_override
        return None

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
