import os
import sys
import yaml
import math
import os.path, time
import logging
from glob import glob
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
except:
    from PySide2.QtWidgets import *

try:
    from PyQt5 import uic, QtCore, QtGui, QtWidgets
except:

    from PySide2 import QtCore, QtWidgets
    from PySide2.QtUiTools import QUiLoader

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
logger = logging.getLogger(__name__)

resolutions = {
    "HD 1080": {
        "width": 1920,
        "height": 1080
    },
    "HD 720": {
        "width": 1280,
        "height": 720
    },
    "HD 540": {
        "width": 960,
        "height": 540
    },
}


def get_root_path():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__))))


def storage(data=None, path=None, replace=False):
    try:
        if data:
            if replace:
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)

            if not os.path.exists(path):
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)
            else:
                return None
        else:
            if os.path.exists(path):
                with open(path) as fl:
                    return yaml.safe_load(fl)
            else:
                return None
    except Exception as error:
        message_log(error)


def context_storage(item=None, file=None):
    try:
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        if not os.path.exists(file):
            with open(file, 'w') as outfile:
                yaml.dump(None, outfile, default_flow_style=False)

        with open(file) as fl:
            data = yaml.safe_load(fl) or []

        try:
            index = next((index for (index, d) in enumerate(data) if d["_id"] == item.get("_id") and d["step"] == item.get("step") and d["engine"] == item.get("engine")), None)
            data[index] = item
        except:
            if isinstance(item, list):
                data = item
            else:
                data.append(item)

        with open(file, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    except Exception as error:
        message_log(error)


def get_size_file(path=None):
    file_stats = os.stat(path)
    return {
        "size": file_stats.st_size,
        "bytes": convert_size(file_stats.st_size)
    }


def get_data_file(path):
    return {
        "created": time.ctime(os.path.getctime(path)),
        "last_modified": time.ctime(os.path.getmtime(path)),
    }


def convert_size(size):
    if size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%s %s" % (s, size_name[i])


def no_accents(value=""):
    # return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # return normalize('NFKD', value).encode('ASCII', 'ignore').decode('ASCII')
    return value


def get_settings():
    return storage(path=os.path.join(get_root_path(), 'config', 'settings.yml'))


def get_project_template():
    return storage(path=os.path.join(get_root_path(), 'config', 'structure.yml'))


def set_storage(data, file):
    file = file.replace('\\', '/')
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, 'w') as seq_file:
        yaml.dump(data, seq_file, default_flow_style=False)


def get_style(name='style'):
    path = os.path.join(get_root_path(), 'ui', '{}.qss'.format(name))
    with open(path, 'r') as fh:
        return fh.read()


def current_date():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def get_ui(name='desktop'):
    return os.path.join(get_root_path(), 'ui', '{}.ui'.format(name))


def load_ui(name='desktop', target=None):
    try:
        from PyQt5 import uic, QtCore, QtGui, QtWidgets
        if target is None:
            return uic.loadUi(get_ui(name))
        else:
            return uic.loadUi(get_ui(name), target)
    except Exception as error:
        message_log(error)


def load_ui_engine(name='desktop', target=None):
    try:
        from PySide2 import QtCore
        from PySide2.QtUiTools import QUiLoader
        loader = QUiLoader()
        if target is None:
            return loader.load(get_ui(name))
        else:
            return loader.load(get_ui(name), target)
    except Exception as error:
        message_log(error)


def get_ffmpeg():
    try:
        return os.path.normpath(os.path.join(get_root_path(), "library", "ffmpeg", "bin", "ffmpeg.exe"))
    except:
        return "ffmpeg path error"


def get_database(name="templates"):
    path = os.path.join(get_root_path(), "database", "{}.yml".format(name))
    path = os.path.normpath(path)
    return storage(path=path)


def Base64ToBytes(path):
    from PyQt5 import QtCore
    image = QtGui.QImage(path)
    ba = QtCore.QByteArray()
    buff = QtCore.QBuffer(ba)
    image.save(buff, "PNG")
    return ba.toBase64().data()


def load_icon_ext(name="", ext="ico"):
    return os.path.join(get_root_path(), "resources", "{}.{}".format(name, ext))


def load_icon(name=""):
    return os.path.join(get_root_path(), "resources", "{}.png".format(name))


def get_files(project=None, context=None, path=None):
    try:
        file_path_root = os.path.join(os.path.dirname(path), "*.{}".format(project.get("engine").get("ext")))
        files = glob(file_path_root)
        files = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, files))
        files = list(map(lambda sec: os.path.normpath(sec), files))
        files = sorted(files, key=lambda file: os.path.getctime(file))
        files.reverse()
        list_all = []
        for file_path in files:
            filename = os.path.basename(file_path)
            version = int(filename.split(".")[1].replace("v", ""))
            file_data = {
                "filename": filename,
                "version": version,
                "path": file_path,
                "date": get_data_file(file_path),
                "size": get_size_file(file_path),
            }
            list_all.append(file_data)
        return list_all
    except Exception as error:
        message_log(error)


def message_log(error):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.warning("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))


def get_template():
    return storage(path=os.path.join(get_root_path(), 'config', 'templates.yml'))


def get_last_version(ctx, prj):
    try:
        settings = get_settings()
        if ctx.get("type") == "asset":
            data_path = {
                "asset_type": ctx.get("asset_type"),
                "asset": ctx.get("name"),
                "step": ctx.get("step"),
                "version": 1,
                "filename": ctx.get("name"),
                "ext": prj.get("engine").get("ext")
            }
            template_name = "asset_work"
        else:
            template_name = "shot_work"
            data_path = {
                "sequence": ctx.get("sequence"),
                "shot": ctx.get("name"),
                "step": ctx.get("step"),
                "step_shot": ctx.get("step").split("_")[1][:4],
                "version": 1,
                "filename": ctx.get("name"),
                "ext": prj.get("engine").get("ext")
            }
        path = os.path.join(prj.get("path"), settings.get("folder_production"), prj.get("engine").get("work"), get_template().get(prj.get("engine").get("type")).get(template_name).format(**data_path))
        path = os.path.dirname(os.path.normpath(path))
        files = glob("{}/*.{}".format(path, prj.get("engine").get("ext")))
        if len(files) >= 1:
            return (len(files) + 1)
        else:
            return 1
    except:
        return 1


def get_info_context(ctx, prj, local="work"):
    try:
        version = get_last_version(ctx, prj)
        settings = get_settings()
        convert_version = "{:03d}".format(version)

        if ctx.get("type") == "asset":
            data_info = {
                "asset_type": ctx.get("asset_type"),
                "asset": ctx.get("name"),
                "step": ctx.get("step"),
                "version": convert_version,
                "filename": ctx.get("name"),
                "ext": prj.get("engine").get("ext")
            }
            template_name = "asset_{}".format(local)
        else:
            try:
                shot_name = ctx.get("name").replace("SHOT_", "SH")
            except:
                shot_name = ctx.get("name")

            step_shot = ""
            try:
                if "." in ctx.get("step"):
                    step_shot = ctx.get("step").split(".")[1]
                elif "_" in ctx.get("step"):
                    step_shot = ctx.get("step").split("_")[1]
            except:
                step_shot = ctx.get("step")

            data_info = {
                "sequence": ctx.get("sequence"),
                "shot": ctx.get("name"),
                "step": step_shot,
                "step_shot": step_shot,
                "version": convert_version,
                "filename": shot_name,
                "ext": prj.get("engine").get("ext")
            }
            template_name = "shot_{}".format(local)

        if local == "work":
            folder = prj.get("engine").get("work")
        else:
            folder = prj.get("engine").get("publish")

        path = os.path.join(prj.get("path"), settings.get("folder_production"), folder, get_template().get(prj.get("engine").get("type")).get(template_name).format(**data_info))
        path = os.path.normpath(path)

        return {
            "path": path,
            "info": data_info,
            "version": version
        }
    except Exception as error:
        message_log(error)


def thumbnail(path=None):
    pass


def message(type="Warning", title=None, message=None, parent=None, callback=None):
    msg = QMessageBox(parent)
    if type == "Question":
        msg.setIcon(QMessageBox.Question)
    if type == "Warning":
        msg.setIcon(QMessageBox.Warning)
    if type == "Information":
        msg.setIcon(QMessageBox.Critical)

    if title:
        msg.setWindowTitle(title)

    if message:
        msg.setText(message)

    if type == "Warning":
        msg.setStandardButtons(QMessageBox.Ok)
    else:
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.buttonClicked.connect(lambda call: callback)
    msg.exec_()
    return msg


def fix_duplicate_name(data, field="filename"):
    duplicates = []
    for cache in data:
        duplicates.append(cache[field])
    total_per_item = {i: duplicates.count(i) for i in duplicates}
    for item in total_per_item:
        y = 0
        for o in range(len(data)):
            opt = data[o]
            if item == opt[field]:
                if y > 0:
                    data[o][field] = "{name}{indice}".format(name=opt[field], indice=y)
                y += 1
    return data


def get_relation(name=None):
    settings = get_settings()
    return settings.get("relations").get(name) or ""


def get_context_from_path(path):
    path = os.path.normpath(path)
    root_path = os.path.dirname(path)
    file_name, file_extension = os.path.splitext(path)
    filename = os.path.basename(file_name).split(".")[0]
    context = root_path.split("\\")
    context = context[-4:]
    version = get_last_version(path)

    type = context[0]
    convert_version = "{:03d}".format(version)
    convert_type = {
        "assets": "asset",
        "scenes": "shot"
    }

    if convert_type.get(type) == "asset":
        data_info = {
            "asset_type": context[1],
            "asset": context[2],
            "step": context[3],
            "version": convert_version,
            "filename": filename,
            "ext": file_extension.replace(".", "")
        }
    else:
        try:
            shot_name = context[2].replace("SHOT_", "SH")
        except:
            shot_name = context[2]

        data_info = {
            "sequence": context[1],
            "shot": context[2],
            "step": context[3],
            "step_shot": context[3],
            "version": convert_version,
            "filename": "{}{}".format(shot_name, context[3]),
            "ext": file_extension.replace(".", "")
        }

    return {
        "path": root_path,
        "info": data_info,
        "version": version
    }
