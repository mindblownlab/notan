import os
import sys
from utils import util, context
import shutil

class Startup:

    def __init__(self, data=None):
        try:
            root_path = os.path.join(util.get_root_path())
            settings = util.get_settings()
            project = context.get_project()
            engine_root = os.path.join(root_path, "engines", "mb_maya")
            environment_path = os.path.join(os.environ['APPDATA'], settings.get("studio").get("name"))

            PYTHONPATH = []

            PYTHONPATH.insert(0, root_path)

            lib_path = os.path.join(root_path, "env", "Lib", "site-packages-lite")
            if lib_path not in PYTHONPATH:
                sys.path.append(lib_path)
                PYTHONPATH.append(lib_path)

            if engine_root not in PYTHONPATH:
                sys.path.append(engine_root)
                PYTHONPATH.append(engine_root)

            os.environ['PYTHONPATH'] = ";".join(PYTHONPATH)

            module = r"""+ {studio} {version} {root}
MAYA_PLUG_IN_PATH += {root}\plug-in
MAYA_SHELF_PATH += {root}\shelves
MAYA_SCRIPT_PATH += {root}\scripts
""".format(root=engine_root, studio=settings.get("studio").get("name"), version=settings.get("developer").get("version"))

            modules_path = os.path.join(environment_path, str(data.get("version")), 'modules', '{}.mod'.format(settings.get("studio").get("name")))
            if not os.path.exists(os.path.dirname(modules_path)):
                os.makedirs(os.path.dirname(modules_path))

            with open(modules_path, 'w') as f:
                f.write(module)

            project_path = os.path.join(settings.get("project_root"), project.get("name"), settings.get("folder_production"), data.get("work"))
            project_path = os.path.normpath(project_path)

            os.environ['MAYA_APP_DIR'] = environment_path
            os.environ['MB_PROJECT_PATH'] = project_path
            os.environ['MB_ROOT'] = root_path

            version_path = os.path.join(environment_path, str(data.get("version")), 'prefs', 'icons')
            if not os.path.exists(version_path):
                os.makedirs(version_path)

            version_path = os.path.join(environment_path, str(data.get("version")), 'prefs', 'icons')
            if not os.path.exists(version_path):
                os.makedirs(version_path)

            splash_ori = os.path.join(project_path, 'splash.png')
            if os.path.exists(splash_ori):
                splash_ori = splash_ori.replace("\\", "/")
                splash_dst = os.path.join(version_path, 'MayaStartupImage.png')
                splash_dst = splash_dst.replace("\\", "/")
                shutil.copy2(splash_ori, splash_dst)

        except Exception as error:
            util.message_log(error)
