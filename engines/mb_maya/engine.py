import json
import os
from PySide2 import QtWidgets, QtGui, QtCore
from utils import util, context
from modules import workfiles, project, loader, publish, manager, scene, blast
from importlib import reload
from maya import cmds, mel
from functools import partial
import ffmpeg
import datetime

reload(workfiles)
reload(project)
reload(loader)
reload(publish)
reload(manager)
reload(scene)
reload(blast)


class MayaEngine(QtWidgets.QMainWindow):
    ui = None
    settings = None
    app_workfile = None
    app_project = None
    app_loader = None
    app_publish = None
    app_manager = None
    app_blsat = None

    def __init__(self, parent=None):
        self.parent = parent
        super(MayaEngine, self).__init__(parent)
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
        self.app_scene = scene.AppScene(self)
        self.app_blast = blast.AppBlast(self)

    def open_scene(self, ctx=None):
        try:
            cmds.file(ctx.get("path"), force=True, open=True, prompt=False, loadAllReferences=True)
            self.refresh()
        except Exception as error:
            util.message_log(error)

    def save_scene(self, file=None):
        try:
            cmds.file(rename=file)
            cmds.file(save=True, type='mayaAscii')
            self.refresh()
        except Exception as error:
            util.message_log(error)

    def publish_scene(self, file=None, ctx=None, prj=None):
        try:
            if ctx.get("step") == util.get_relation("lookdev"):
                try:
                    if cmds.objExists("{}_master_grp".format(ctx.get("name"))):
                        cmds.select("{}_master_grp".format(ctx.get("name")), r=True)
                    cmds.file(file, force=True, options="v=0;", typ="mayaAscii", es=True, preserveReferences=False, constraints=False)
                except:
                    if cmds.objExists("*:{}_master_grp".format(ctx.get("name"))):
                        cmds.select("*:{}_master_grp".format(ctx.get("name")), r=True)
                    cmds.file(file, force=True, options="v=0;", typ="mayaAscii", es=True, preserveReferences=False, constraints=False)
            else:
                if ctx.get("step") == util.get_relation("model"):
                    transforms = cmds.ls(type="transform")
                    transforms = list(filter(lambda node: node not in ["persp", "top", "front", "side"] and "cam" not in node, transforms))
                    cmds.select(transforms)
                    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=False, pn=True)
                    cmds.select(clear=True)

                    template = util.get_template()
                    template = template.get(prj.get("engine").get("type")).get("{}_alembic".format(ctx.get("type")))
                    settings = util.get_settings()
                    args = ["uvWrite", "stripNamespaces", "worldSpace", "writeVisibility"]
                    alembicArgs = " -".join(args)
                    fields = {
                        "asset_type": ctx.get("asset_type"),
                        "asset": ctx.get("name"),
                        "name": ctx.get("name"),
                        "ext": "abc",
                    }

                    abc_path = os.path.join(util.get_root_path(), settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), template.format(**fields))
                    root = cmds.ls("{}_master_grp".format(ctx.get("name")), long=True)[0]
                    abc_path = os.path.normpath(abc_path)
                    abc_path = abc_path.replace("\\", "/")
                    abc_path_dir = os.path.dirname(abc_path)
                    if not os.path.exists(abc_path_dir):
                        os.makedirs(abc_path_dir)
                    abc_export_cmd = "-frameRange 1 1 -{args} -dataFormat ogawa -root {root} -file '{file}'".format(args=alembicArgs, root=root, file=abc_path)
                    cmds.AbcExport(jobArg=abc_export_cmd)

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

                    util.context_storage(
                        item=data_publish,
                        file=os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), settings.get("database"), "published.yml")
                    )

                cmds.file(file, force=True, options="v=0;", type="mayaAscii", pr=True, ea=True)

            cmds.file(save=True)
            self.refresh()

            pass
        except Exception as error:
            util.message_log(error)

    def create_new_file(self, ctx=None, prj=None):
        cmds.file(f=True, new=True)
        assetName = "{}_master_grp".format(ctx.get("name"))
        settings = util.get_settings()

        if ctx.get("type") == "asset" and ctx.get("step") == util.get_relation("model"):
            if not cmds.objExists(assetName):
                cmds.group(name=assetName, em=True)

            if not cmds.objExists("{}.Export".format(assetName)):
                cmds.addAttr("{}".format(assetName), ln='Export', at='bool')
                cmds.setAttr("{}.Export".format(assetName), 1, e=True, keyable=True)
                cmds.setAttr("{}.Export".format(assetName), lock=True)
                cmds.setAttr("{}.Export".format(assetName), lock=True)
            if not cmds.objExists("{}.AssetId".format(assetName)):
                cmds.addAttr("{}".format(assetName), ln="AssetId", dt="string")
                cmds.setAttr("{}.AssetId".format(assetName), ctx.get("_id"), type="string")
                cmds.setAttr("{}.AssetId".format(assetName), lock=True)
                cmds.setAttr("{}.AssetId".format(assetName), lock=True)

        if ctx.get("type") == "asset" and ctx.get("step") == util.get_relation("lookdev"):
            try:
                light_path = os.path.join(os.environ['MB_ROOT'], "studio_light", "maya", "scene_{}.ma".format(cmds.about(version=True)))
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

                cmds.progressWindow(title=ctx.get('name'), progress=0, status='Wait...', isInterruptable=True)
                cmds.pause(seconds=3)

                if os.path.exists(light_path):
                    cmds.progressWindow(edit=True, progress=25, status="Setup Light", isInterruptable=True)
                    cmds.file(light_path, r=True, type="mayaAscii", gr=True, ignoreVersion=True, mergeNamespacesOnClash=True, namespace="STUDIO_LIGHT", options="v=0")
                    cmds.setAttr("STUDIO_LIGHT:environment_light.fileTextureName", "{}\\studio_light\\maya\\light.hdr".format(os.environ["MB_ROOT"]), type="string")
                    cmds.setAttr("STUDIO_LIGHT:aces_color.fileTextureName", "{}\\studio_light\\maya\\check.jpg".format(os.environ["MB_ROOT"]), type="string")
                    cmds.pause(seconds=3)

                model_path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), context_path.format(**data_field))
                model_path = os.path.normpath(model_path)
                if os.path.exists(model_path):
                    cmds.progressWindow(edit=True, progress=50, status="Reference model", isInterruptable=True)
                    cmds.file(model_path, r=True, type="mayaAscii", gr=False, ignoreVersion=True, mergeNamespacesOnClash=False, namespace=":", options="v=0")
                    cmds.pause(seconds=3)

                cmds.progressWindow(edit=True, progress=75, status="Set camera", isInterruptable=True)
                cameraName = "STUDIO_LIGHT:turn_cam"
                modelEditor = cmds.getPanel(withFocus=True)
                if modelEditor != 'modelPanel4':
                    modelEditor = 'modelPanel4'
                cmds.modelEditor(modelEditor, e=True, camera=cameraName, grid=False)
                cmds.pause(seconds=3)

                cmds.progressWindow(edit=True, progress=100, status="Finishing...", isInterruptable=True)
                cmds.progressWindow(endProgress=1)
            except Exception as error:
                util.message_log(error)

        if ctx.get("type") == "shot" and ctx.get("step") == util.get_relation("assembly"):
            try:
                data_step = settings.get("setup_animation")
                for g in data_step.keys():
                    group = data_step.get(g)
                    group_name = "{}_grp".format(group.get("group"))
                    cmds.group(empty=True, name=group_name)
                    cmds.setAttr("{}.useOutlinerColor".format(group_name), True)
                    cmds.setAttr("{}.outlinerColor".format(group_name), group.get("color")[0], group.get("color")[1], group.get("color")[2])
                    cmds.setAttr("{}.overrideEnabled".format(group_name), 1)
                    cmds.setAttr("{}.overrideDisplayType".format(group_name), 2)

                    if "children" in group.keys():
                        for s in group.get("children"):
                            sub_group = group.get("children").get(s)
                            sub_group_name = "{}_grp".format(sub_group.get("group"))
                            cmds.group(empty=True, name=sub_group_name, parent="{}_grp".format(group.get("group")))
                            cmds.setAttr("{}.useOutlinerColor".format(sub_group_name), True)
                            cmds.setAttr("{}.outlinerColor".format(sub_group_name), sub_group.get("color")[0], sub_group.get("color")[1], sub_group.get("color")[2])
                            cmds.setAttr("{}.overrideEnabled".format(sub_group_name), 1)
                            cmds.setAttr("{}.overrideDisplayType".format(sub_group_name), 2)

            except RuntimeError as error:
                util.message_log(error)

        if ctx.get("type") == "shot" and ctx.get("step") == util.get_relation("animation"):
            cmds.group(name="ASSEMBLY", em=True)

        cmds.select(clear=True)
        self.refresh()

    def reference_file(self, data=None, ctx=None, index=0):
        try:
            path = data.get("path").replace("\\", "/")
            group_name = os.path.basename(path)
            group_name = group_name.replace(".", "_")
            if data.get("type") == "sound":
                if os.path.exists(path):
                    cmds.file(path, i=True, type='audio', options='o=0')
                    cmds.rename("audio1", "{}_SND".format(data.get("name")))
            else:
                cmds.file(path, reference=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=group_name, groupReference=True)
                if index == 0:
                    if cmds.objExists("CHAR_grp"):
                        cmds.select(["{}RNgroup".format(group_name), "CHAR_grp"], add=True)
                        cmds.parent()
                        cmds.select(clear=True)

                    if cmds.objExists("CAM_grp"):
                        if "cam" in path.lower():
                            cmds.select(["{}RNgroup".format(group_name), "CAM_grp"], add=True)
                            cmds.parent()
                            cmds.select(clear=True)
                else:
                    if cmds.objExists("CHAR_grp"):
                        cmds.select("{}RN{}group".format(group_name, index), "CHAR_grp", add=True)
                        cmds.parent()
                        cmds.select(clear=True)

        except Exception as error:
            util.message_log(error)

    def import_file(self, data=None, ctx=None):
        try:
            path = data.get("path").replace("\\", "/")
            if data.get("type") == "sound":
                if os.path.exists(path):
                    cmds.file(path, i=True, type='audio', options='o=0')
                    cmds.rename("audio1", "{}_SND".format(data.get("name")))
            else:
                cmds.file(path, i=True, renameAll=True, gr=False, namespace=":", preserveReferences=False)
        except Exception as error:
            util.message_log(error)

    def create_shot_group(self):
        ctx = context.get_context()
        if ctx.get("type") == "shot":
            cmds.group(name="CAM", em=True)
            cmds.group(name="CHAR", em=True)
            cmds.group(name="PROXY", em=True)
            cmds.group(name="Env_prx", em=True, parent="PROXY")
            cmds.group(name="Char_prx", em=True, parent="PROXY")

        if ctx.get("type") == "shot" and ctx.get("step") == util.get_relation("animation"):
            cmds.group(name="ASSEMBLY", em=True)

        cmds.select(clear=True)

    def create_asset_group(self):
        ctx = context.get_context()
        if ctx.get("type") == "asset":
            selected = cmds.ls(selection=True)
            if selected:
                assetName = selected[0]
                if not cmds.objExists("{}.Export".format(assetName)):
                    cmds.addAttr("{}".format(assetName), ln='Export', at='bool')
                    cmds.setAttr("{}.Export".format(assetName), 1, e=True, keyable=True)
                    cmds.setAttr("{}.Export".format(assetName), lock=True)
                    cmds.setAttr("{}.Export".format(assetName), lock=True)
                if not cmds.objExists("{}.AssetId".format(assetName)):
                    cmds.addAttr("{}".format(assetName), ln="AssetId", dt="string")
                    cmds.setAttr("{}.AssetId".format(assetName), ctx.get("_id"), type="string")
                    cmds.setAttr("{}.AssetId".format(assetName), lock=True)
                    cmds.setAttr("{}.AssetId".format(assetName), lock=True)
            else:
                assetName = "{}_master_grp".format(ctx.get("name"))
                if not cmds.objExists(assetName):
                    cmds.group(name=assetName, em=True)
                if not cmds.objExists("{}.Export".format(assetName)):
                    cmds.addAttr("{}".format(assetName), ln='Export', at='bool')
                    cmds.setAttr("{}.Export".format(assetName), 1, e=True, keyable=True)
                    cmds.setAttr("{}.Export".format(assetName), lock=True)
                    cmds.setAttr("{}.Export".format(assetName), lock=True)
                if not cmds.objExists("{}.AssetId".format(assetName)):
                    cmds.addAttr("{}".format(assetName), ln="AssetId", dt="string")
                    cmds.setAttr("{}.AssetId".format(assetName), ctx.get("_id"), type="string")
                    cmds.setAttr("{}.AssetId".format(assetName), lock=True)
                    cmds.setAttr("{}.AssetId".format(assetName), lock=True)

    def thumbnail(self, path):
        try:
            if path:
                path = path.replace(".blend", ".png")
                path = os.path.normpath(path)
                if os.path.exists(path):
                    os.unlink(path)
        except:
            pass

    def refresh(self):
        from importlib import reload
        import startup
        reload(startup)
        cmds.select(clear=True)

    def collect_meshs(self):
        get_all_transforms = cmds.ls(transforms=True)
        ctx = context.get_context()
        prj = context.get_project()
        settings = util.get_settings()
        template = util.get_template()
        template = template.get(prj.get("engine").get("type")).get("{}_alembic".format(ctx.get("type")))
        data_field = {
            "asset": {
                "asset_type": ctx.get("asset_type"),
                "asset": ctx.get("name"),
                "name": "{}",
            },
            "shot": {
                "sequence": ctx.get("sequence"),
                "shot": ctx.get("name"),
                "name": "{}",
                "type": "publish",
            },
        }

        path = os.path.join(settings.get("project_root"), prj.get("name"), settings.get("folder_production"), prj.get("engine").get("publish"), template.format(**data_field.get(ctx.get("type"))))
        path = os.path.normpath(path)

        get_all_transforms = list(filter(lambda g: cmds.objExists(g + '.Export') and cmds.getAttr(g + '.Export'), get_all_transforms))
        try:
            get_all_transforms = list(map(lambda asset: {"name": asset.split(":")[1], "path": path, "root": cmds.ls(asset, long=True)[0]}, get_all_transforms))
        except:
            get_all_transforms = list(map(lambda asset: {"name": asset, "path": path, "root": cmds.ls(asset, long=True)[0]}, get_all_transforms))

        return get_all_transforms

    def setter_config(self, ctx=None, prj=None):
        width, height = prj.get('resolution')
        frame_start, frame_end = ctx.get("frames")

        cmds.currentUnit(time='film')
        cmds.setAttr("defaultResolution.width", int(width))
        cmds.setAttr("defaultResolution.height", int(height))

        cmds.playbackOptions(minTime=int(frame_start), maxTime=int(frame_end), animationStartTime=int(frame_start), animationEndTime=int(frame_end))
        cmds.setAttr("defaultRenderGlobals.startFrame", int(frame_start))
        cmds.setAttr("defaultRenderGlobals.endFrame", int(frame_end))
        cmds.setAttr("defaultResolution.pa", int(prj.get("aspect")))

    # PLAYBLAST

    def play_pause(self, state=None):
        cmds.play(state=state)

    def get_all_cameras(self):
        try:
            all_cameras = cmds.listCameras(p=True)
            all_cameras = list(filter(lambda cam: cam not in ["persp", "front", "left", "right", "bottom"], all_cameras))
            all_cameras.sort()
            return list(map(lambda cam: {"name": cam.upper(), "cam": cam}, all_cameras))
        except Exception as error:
            util.message_log(error)

    def get_sound(self):
        try:
            aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
            try:
                audio = cmds.timeControl(aPlayBackSliderPython, q=True, sound=True, displaySound=True)
                if audio:
                    return audio
                else:
                    cmds.warning('No sound node.')
                    return ""
            except:
                cmds.timeControl(aPlayBackSliderPython, e=True, sound="", displaySound=False)
        except:
            return ""

    def playblast(self, path=None, ctx=None, prj=None, ui=None):
        self.prepare_viewport(active=True)
        resolution = ui.resolution.currentText()
        width, height = list(util.resolutions[resolution].values())
        QtCore.QCoreApplication.processEvents()
        ui.progress_bar.setFormat("Create playblast")
        ui.progress_bar.setProperty("value", 33)
        frame_start, frame_end = (int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True)))

        QtCore.QCoreApplication.processEvents()
        cmds.playblast(
            format='avi',
            percent=100,
            quality=100,
            viewer=False,
            sound=self.get_sound(),
            sequenceTime=False,
            compression="none",
            combineSound=False,
            forceOverwrite=True,
            clearCache=True,
            startTime=int(frame_start),
            endTime=int(frame_end),
            offScreen=True,
            showOrnaments=True,
            filename=path,
            widthHeight=[width, height],
            framePadding=4)
        QtCore.QTimer.singleShot(250, partial(self.create_layout, ui, path))

    def create_layout(self, ui, path):
        try:
            logo_path = os.path.join(util.get_root_path(), "resources", "logo.png")
            font_path = os.path.join(util.get_root_path(), "resources", "font.ttf")
            ffmpeg_path = os.path.join(os.path.dirname(ffmpeg.__file__), "bin", "ffmpeg.exe")
            date = datetime.date.today().strftime("%d/%m/%Y")
            QtCore.QCoreApplication.processEvents()

            height_bar = 120
            space = (height_bar / 2)
            font_size = 18
            font_color = '#FFFFFF'
            border_color = '#3c3c3c00'
            border_width = 1
            line_spacing = -2

            try:
                cmds.camera(ui.cameras.currentText(), e=True, displayResolution=False)
            except:
                pass

            base = ffmpeg.input(path)
            if self.get_sound():
                audio = base.audio
            else:
                audio = None

            ctx = context.get_context()
            settings = util.get_settings()
            step_shot = ""
            try:
                if "." in ctx.get("step"):
                    step_shot = ctx.get("step").split(".")[1]
                elif "_" in ctx.get("step"):
                    step_shot = ctx.get("step").split("_")[1]
            except:
                step_shot = ctx.get("step")

            base = ffmpeg.filter([base, ffmpeg.input(logo_path)], 'overlay', 'W-overlay_w-{}'.format(space), (space / 2))
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text=date, fontcolor=font_color, escape_text=True, x=space, y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='ANIMATOR: {}'.format(ui.animator.text() or settings.get("studio").get("name")), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text="{}".format(step_shot), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='COUNT\: %{n}', start_number=1, fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='FRAMES\: {0}-{1}'.format(int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))), fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='{} {}'.format(ctx.get('sequence'), ctx.get('shot')), fontcolor=font_color, escape_text=True, x='{} * 5 + 100'.format(space), y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

            try:
                ui.progress_bar.setFormat("Convert and create layout")
                ui.progress_bar.setProperty("value", 66)
                if self.get_sound():
                    joined = ffmpeg.concat(base, audio, v=1, a=1).node
                    cmd_blast = ffmpeg.output(joined[0], joined[1], path.replace(".avi", ".mp4"), loglevel="quiet")
                else:
                    cmd_blast = ffmpeg.output(base, path.replace(".avi", ".mp4"), loglevel="quiet")
                try:
                    cmd_blast.global_args('-y').run(cmd=ffmpeg_path)
                    cmds.launch(mov=path.replace(".avi", ".mp4"))
                except Exception as error:
                    util.message_log(error)
            except Exception as error:
                util.message_log(error)

            QtCore.QCoreApplication.processEvents()
            ui.progress_bar.setVisible(False)
            self.setDisabled(False)
            ui.progress_bar.setFormat("Playnlast complete create")
            ui.progress_bar.setProperty("value", 99)
            self.prepare_viewport(active=False)
            os.unlink(path)
        except Exception as error:
            util.message_log(error)

    def prepare_viewport(self, active=True):
        viewport = cmds.getPanel(withFocus=True)
        if viewport != "modelPanel4":
            viewport = "modelPanel4"
        if active:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)

            cmds.modelEditor(viewport, e=True,
                             allObjects=False,
                             polymeshes=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            mel.eval('generateAllUvTilePreviews;')
            cmds.modelEditor(viewport, e=True, grid=False)
        else:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(viewport, e=True,
                             allObjects=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            cmds.modelEditor(viewport, e=True, grid=True)

    def closeEvent(self, event):
        try:
            self.prepare_viewport(active=False)
            if self.ui.main_layout.count() > 0:
                for i in range(self.ui.main_layout.count()):
                    item = self.ui.main_layout.takeAt(i)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
        except Exception as error:
            util.message_log(error)
