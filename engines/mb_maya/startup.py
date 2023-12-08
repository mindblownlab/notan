from PySide2 import QtWidgets
from utils import util
from utils import context as ctx
from engines.mb_maya import engine
from maya import cmds, mel
from importlib import reload

reload(engine)
app = QtWidgets.QApplication.instance()
if app == None:
    app = QtWidgets.QApplication()
else:
    app.beep()
app_maya = engine.MayaEngine()

context = ctx.get_context()
project = ctx.get_project()

root_menu = "mind_menu"
menu_label = "MBLab"

try:
    if cmds.menu(root_menu, exists=1):
        cmds.deleteUI(root_menu, menu=1)

    gMainWindow = mel.eval("global string $gMainWindow;$temp = $gMainWindow")
    cmds.menu(root_menu, label=menu_label, parent=gMainWindow, tearOff=1, allowOptionBoxes=1)

    if context.get("type") is None:
        menu_project = cmds.menuItem(label="Project {}".format(project.get("name")), image="project.png", parent=root_menu, subMenu=True)
        cmds.menuItem(label="Open project folder", image="proj_folder.png", parent=menu_project, command=lambda x=None: app_maya.app_project.open_folder())
        cmds.menuItem(divider=True, parent=root_menu)
        cmds.menuItem(label="File Open", image="folder.png", parent=root_menu, command=lambda x=None: app_maya.app_workfile.open())

    else:
        step_name = ""
        if context.get("type") == "asset":
            menu_project = cmds.menuItem(label="{}, {} {}".format(context.get("step"), context.get("type").capitalize(), context.get("name")), image="project.png", parent=root_menu, subMenu=True)
        else:
            try:
                step_name = context.get("step").split("_")[1]
            except:
                step_name = context.get("step")
            menu_project = cmds.menuItem(label="{}, {} {}".format(step_name, context.get("type").capitalize(), context.get("name")), image="project.png", parent=root_menu, subMenu=True)

        cmds.menuItem(divider=True, parent=root_menu)
        cmds.menuItem(label="File Open", parent=root_menu, image="folder.png", command=lambda x=None: app_maya.app_workfile.open())
        cmds.menuItem(label="Open Project folder", parent=menu_project, image="proj_folder.png", command=lambda x=None: app_maya.app_project.open_folder())
        cmds.menuItem(label="Open {} {} folder".format(context.get("type").capitalize(), step_name), image="proj_folder.png", parent=menu_project, command=lambda x=None: app_maya.app_project.open_folder_context())

        cmds.menuItem(label="File Save", image="saving.png", parent=root_menu, command=lambda x=None: app_maya.app_workfile.open_save())
        cmds.menuItem(label="Publish", image="publish.png", parent=root_menu, command=lambda x=None: app_maya.app_publish.open())
        cmds.menuItem(label="Manager", image="manager.png", parent=root_menu, command=lambda x=None: app_maya.app_manager.open())
        cmds.menuItem(divider=True, parent=root_menu)
        if context.get("type") == "asset":
            cmds.menuItem(label="Asset group", image="cog.png", parent=root_menu, command=lambda x=None: app_maya.create_asset_group())
            cmds.menuItem(divider=True, parent=root_menu)
        if context.get("type") == "shot":
            cmds.menuItem(label="Shot groups", image="cog.png", parent=root_menu, command=lambda x=None: app_maya.create_shot_group())
            cmds.menuItem(label="Shot settings", image="cog.png", parent=root_menu, command=lambda x=None: app_maya.app_project.setter_config())
            cmds.menuItem(divider=True, parent=root_menu)
            cmds.menuItem(label="Playblast", image="anim_blast.png", parent=root_menu, command=lambda x=None: app_maya.app_blast.open())
        cmds.menuItem(label="Load File", image="load.png", parent=root_menu, command=lambda x=None: app_maya.app_loader.open())

    cmds.menuItem(divider=True, parent=root_menu)
    cmds.menuItem(label="Reload", image="refresh.png", parent=root_menu, command=lambda x=None: app_maya.refresh())
except Exception as error:
    util.message_log(error)