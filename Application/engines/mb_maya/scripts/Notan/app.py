import os.path
import sys
from glob import glob
from .utils import util
from maya import cmds, mel
from importlib import reload
from PySide2 import QtCore
from functools import partial
import datetime

reload(util)


def file_save():
    try:
        file_path = cmds.file(q=True, sn=True)
        context = util.get_context_from_path(path=file_path)
        file_save = os.path.join(context.get("path"), "{filename}.v{version}.{ext}".format(**context.get("info")))
        result = cmds.confirmDialog(title='Save file', message='Deseja salvar uma nova versão\n{}?'.format(os.path.basename(file_save)), button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if result == "Yes":
            cmds.file(rename=file_save)
            cmds.file(save=True, type='mayaAscii')
    except:
        pass


def blast():
    try:
        file_path = cmds.file(q=True, sn=True)
        context = util.get_context_from_path(path=file_path)
        project_root = cmds.workspace(q=True, rd=True)

        try:
            shot_name = context.get("info").get(context.get("type")).replace("SHOT_", "SH")
        except:
            shot_name = context.get("info").get(context.get("type"))

        context["info"]["filename"] = shot_name
        path_query = "movies/playblast/Review/{sequence}/{shot}/{filename}_blast.v{version}.avi".format(**context.get("info"))
        blast_path = os.path.join(project_root, path_query)
        blast_path = os.path.normpath(blast_path)

        blast_path = os.path.normpath(blast_path)
        blast_path_dir = os.path.dirname(blast_path)
        blast_path_dir = os.path.normpath(blast_path_dir)
        if not os.path.exists(blast_path_dir):
            os.makedirs(blast_path_dir)

        files = glob("{}/*.mp4".format(blast_path_dir))
        if len(files) >= 1:
            version = (len(files) + 1)
        else:
            version = 1

        fields = context.get("info")
        fields["version"] = "{:03d}".format(version)

        path_query = "movies/playblast/Review/{sequence}/{shot}/{filename}_blast.v{version}.avi".format(**context.get("info"))
        blast_path = os.path.join(project_root, path_query)
        blast_path = os.path.normpath(blast_path)

        result = cmds.confirmDialog(title='Gerar playblast', message='Deseja gerar uma nova versão do playblast\n{}?'.format(os.path.basename(blast_path)), button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if result == "Yes":
            width, height = (cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height"))
            frame_start, frame_end = (int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True)))

            cmds.playblast(
                format='avi',
                percent=100,
                quality=100,
                viewer=False,
                sound=get_sound(),
                sequenceTime=False,
                compression="none",
                combineSound=False,
                forceOverwrite=True,
                clearCache=True,
                startTime=int(frame_start),
                endTime=int(frame_end),
                offScreen=True,
                showOrnaments=True,
                filename=blast_path,
                widthHeight=[width, height],
                framePadding=4)
            cmds.confirmDialog(title='Gerar playblast', message='Playblast gerado com sucesso\n{}'.format(os.path.basename(blast_path)), button=['Ok'], defaultButton='Ok')
            QtCore.QTimer.singleShot(250, partial(create_layout, blast_path, context))
    except Exception as error:
        print(1, error)


def create_layout(path, context):
    try:

        libs = os.path.join(os.path.dirname(__file__), "libs")

        if not os.path.exists(libs):
            sys.path.append(libs)

        import ffmpeg

        logo_path = os.path.join(libs, "resources", "logo.png")
        font_path = os.path.join(libs, "resources", "font.ttf")
        ffmpeg_path = os.path.join(libs, "ffmpeg", "bin", "ffmpeg.exe")
        date = datetime.date.today().strftime("%d/%m/%Y")

        height_bar = 120
        space = (height_bar / 2)
        font_size = 18
        font_color = '#FFFFFF'
        border_color = '#3c3c3c00'
        border_width = 1
        line_spacing = -2

        base = ffmpeg.input(path)
        if get_sound():
            audio = base.audio
        else:
            audio = None

        settings = {
            "studio":
                {
                    "name": "Notan"
                }
        }
        step_shot = ""
        try:
            if "." in context.get("step"):
                step_shot = context.get("step").split(".")[1]
            elif "_" in context.get("step"):
                step_shot = context.get("step").split("_")[1]
        except:
            step_shot = context.get("step")

        base = ffmpeg.filter([base, ffmpeg.input(logo_path)], 'overlay', 'W-overlay_w-{}'.format(space), (space / 2))
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text=date, fontcolor=font_color, escape_text=True, x=space, y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='ANIMATOR: {}'.format(settings.get("studio").get("name")), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text="{}".format(step_shot), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='COUNT\: %{n}', start_number=1, fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='FRAMES\: {0}-{1}'.format(int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))), fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='{} {}'.format(context.get('sequence'), context.get('shot')), fontcolor=font_color, escape_text=True, x='{} * 5 + 100'.format(space), y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

        try:
            if get_sound():
                joined = ffmpeg.concat(base, audio, v=1, a=1).node
                cmd_blast = ffmpeg.output(joined[0], joined[1], path.replace(".avi", ".mp4"), loglevel="quiet")
            else:
                cmd_blast = ffmpeg.output(base, path.replace(".avi", ".mp4"), loglevel="quiet")
            try:
                cmd_blast.global_args('-y').run(cmd=ffmpeg_path)
                cmds.launch(mov=path.replace(".avi", ".mp4"))
            except Exception as error:
                print(2, error)
        except Exception as error:
            print(3, error)
    except Exception as error:
        print(4, error)


def get_sound():
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


def open_project():
    try:
        project_root = cmds.workspace(q=True, rd=True)
        if not os.path.exists(project_root):
            return
        os.startfile(project_root)
    except:
        pass
