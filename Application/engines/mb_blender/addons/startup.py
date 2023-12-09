from pathlib import Path

import bpy
from PySide2 import QtWidgets
from bpy.app.handlers import persistent
from bpy.props import StringProperty

from engines.mb_blender import engine
from utils import context as ctx

bl_info = {
    "name": "BossMind",
    "author": "Mindblownlab",
    "version": (2, 0, 0),
    "blender": (3, 6, 2),
    "location": "Development > MBLab",
    "description": "Gestao de pipeline integrada",
    "category": "Development",
}

app = QtWidgets.QApplication.instance()
if app == None:
    app = QtWidgets.QApplication(['blender'])
else:
    app.beep()
app_blender = engine.BlenderEngine()


# CONTEXT ------------------------------------------------------------------------------------------------------------

class MB_MT_context(bpy.types.Menu):
    data_project = ctx.get_project()
    data_context = dict(ctx.get_context())
    if data_context.get("type") is None:
        bl_label = data_project.get("name")
    else:
        if data_context.get("type") == "asset":
            bl_label = "{}, {} {}".format(data_context.get("step"), data_context.get("type").capitalize(), data_context.get("name"))
        else:
            try:
                bl_label = "{}, {} {}".format(data_context.get("step").split("_")[1], data_context.get("type").capitalize(), data_context.get("name"))
            except:
                bl_label = "{}, {} {}".format(data_context.get("step"), data_context.get("type").capitalize(), data_context.get("name"))

    def draw(self, context):
        data_context = dict(ctx.get_context())
        layout = self.layout
        if data_context.get("type") is None:
            layout.operator('mb.mb_mt_open_project_folder', icon="FILE_FOLDER")
            layout.separator()
        else:
            layout.operator('mb.mb_mt_open_project_folder', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_open_context_folder', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_settings_scene', icon="TOOL_SETTINGS")


class MB_MT_context_open_project_folder(bpy.types.Operator):
    bl_label = "Open project folder"
    bl_idname = "mb.mb_mt_open_project_folder"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_project.open_folder()
        return {'FINISHED'}


class MB_MT_context_open_context_folder(bpy.types.Operator):
    data_context = dict(ctx.get_context())
    if data_context.get("type") is not None:
        bl_label = "Open {} {} folder".format(data_context.get("type").capitalize(), data_context.get("step"))
    else:
        bl_label = "Open folder"
    bl_idname = "mb.mb_mt_open_context_folder"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_project.open_folder_context()
        return {'FINISHED'}


class MB_MT_context_settings_scene(bpy.types.Operator):
    bl_label = "Set and Check Scene settings"
    bl_idname = "mb.mb_mt_settings_scene"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


# OPEN, SAVE, PUBLISH ------------------------------------------------------------------------------------------------------------

class MB_MT_open(bpy.types.Operator):
    bl_label = "Open File"
    bl_idname = "mb.mb_mt_open"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_workfile.open()
        return {'FINISHED'}


class MB_MT_save(bpy.types.Operator):
    bl_label = "File Save"
    bl_idname = "mb.mb_mt_save"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_workfile.open_save()
        return {'FINISHED'}


class MB_MT_publish(bpy.types.Operator):
    bl_label = "Publish"
    bl_idname = "mb.mb_mt_publish"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_publish.open()
        return {'FINISHED'}


# MANAGER ------------------------------------------------------------------------------------------------------------

class MB_MT_manager(bpy.types.Operator):
    bl_label = "Manager"
    bl_idname = "mb.mb_mt_manager"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_manager.open()
        return {'FINISHED'}


# LOAD FILE ------------------------------------------------------------------------------------------------------------

class MB_MT_load_file(bpy.types.Operator):
    bl_label = "Load File"
    bl_idname = "mb.mb_mt_load_file"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        app_blender.app_loader.open()
        return {'FINISHED'}


# RELOAD  ------------------------------------------------------------------------------------------------------------

class MB_MT_reload(bpy.types.Operator):
    bl_label = "Reload"
    bl_idname = "mb.mb_mt_reload"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        bpy.ops.script.reload()
        return {'FINISHED'}


# ROOT MENU ------------------------------------------------------------------------------------------------------------

class MB_MT_root_menu(bpy.types.Menu):
    data_context = dict(ctx.get_context())
    bl_label = "MBLab"
    if data_context.get("type") is None:
        bl_icon = "COLLECTION_NEW"
    else:
        if data_context.get("type") == "asset":
            bl_icon = "MESH_CUBE"
        else:
            bl_icon = "RENDER_ANIMATION"

    mblab = None
    targetWorkspace: StringProperty(name=None, default=None)

    def draw(self, context):
        data_context = dict(ctx.get_context())
        layout = self.layout
        if data_context.get("type") is None:
            layout.menu('MB_MT_context', icon=MB_MT_root_menu.bl_icon)
            layout.separator()
            layout.operator('mb.mb_mt_open', icon="FILE_FOLDER")
            layout.separator()
        else:
            layout.menu('MB_MT_context', icon=MB_MT_root_menu.bl_icon)
            layout.separator()
            layout.operator('mb.mb_mt_open', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_save', icon="FILE_TICK")
            layout.operator('mb.mb_mt_publish', icon="EXPORT")
            layout.operator('mb.mb_mt_manager', icon="ASSET_MANAGER")
            layout.separator()
            layout.operator('mb.mb_mt_load_file', icon="IMPORT")
        layout.separator()
        layout.operator('mb.mb_mt_reload')

    def menu_draw(self, context):
        self.layout.menu("MB_MT_root_menu")

    def execute(self, context):
        if self.targetWorkspace in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces[self.targetWorkspace]
            return {'FINISHED'}

        success = bpy.ops.workspace.append_activate(idname=self.targetWorkspace, filepath=bpy.utils.user_resource('CONFIG', 'startup.blend'))
        if success == {'FINISHED'}:
            return success

        for p in Path(next(bpy.utils.app_template_paths())).rglob("startup.blend"):
            success = bpy.ops.workspace.append_activate(idname=self.targetWorkspace, filepath=str(p))
            if success == {'FINISHED'}:
                return success
        else:
            print('Workspace Swapper: Could not find the requested workspace "{}"'.format(self.targetWorkspace))
        return {'CANCELLED'}


CLASSES = [
    MB_MT_root_menu,

    MB_MT_context,
    MB_MT_context_open_project_folder,
    MB_MT_context_open_context_folder,
    MB_MT_context_settings_scene,

    MB_MT_open,
    MB_MT_save,
    MB_MT_publish,

    MB_MT_manager,
    MB_MT_load_file,

    MB_MT_reload,
]


@persistent
def load_handler(dummy, context):
    if ctx.get_context():
        _context = ctx.get_context()

        if _context.get("step") == "Model":
            bpy.context.window.workspace = bpy.data.workspaces["Modeling"]

        if _context.get("step") == "LookDev":
            bpy.context.window.workspace = bpy.data.workspaces["Shading"]

        if _context.get("step") == "Animation":
            bpy.context.window.workspace = bpy.data.workspaces["Animation"]

        if _context.get("step") == "Assembly":
            bpy.context.window.workspace = bpy.data.workspaces["Layout"]

        if _context.get("step") == "Light":
            bpy.context.window.workspace = bpy.data.workspaces["Rendering"]


@persistent
def save_handler(path):
    pass
    # if path:
    #     path = os.path.normpath(path)
    #     path = path.replace(".blend", ".png")
    #     path = path.replace("\\", "/")
    #     if os.path.exists(path):
    #         os.unlink(path)
    # bpy.context.scene.render.filepath = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(path)), "thumb.png"))
    # bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(MB_MT_root_menu.menu_draw)
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.save_post.append(save_handler)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(MB_MT_root_menu.menu_draw)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
