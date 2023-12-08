import json
import os
from utils import util, context
from models import shots


class AppProject:
    parent = None

    def __init__(self, parent=None):
        self.parent = parent

    def open_folder(self):
        try:
            data_project = context.get_project()
            settings = util.get_settings()
            path = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), data_project.get("engine").get("work"))
            if not os.path.exists(path):
                return
            os.startfile(path)
        except Exception as error:
            util.message_log(error)

    def open_folder_context(self):
        try:
            data_context = context.get_context()
            data_project = context.get_project()
            settings = util.get_settings()
            template = util.get_template()
            context_path = template.get(data_project.get("engine").get("type")).get("{}_{}".format(data_context.get("type"), "work"))

            data_field = {
                "asset": {
                    "asset_type": data_context.get("asset_type"),
                    "asset": data_context.get("name"),
                    "filename": data_context.get("name"),
                    "step": data_context.get("step"),
                    "version": "{:03d}".format(1),
                    "ext": data_project.get("engine").get("ext")
                },
                "shot": {
                    "sequencia": data_context.get("sequencia"),
                    "shot": data_context.get("name"),
                    "step": data_context.get("step"),
                    "filename": data_context.get("name"),
                    "version": "{:03d}".format(1),
                    "ext": data_project.get("engine").get("ext")
                }
            }
            path = os.path.join(settings.get("project_root"), data_project.get("name"), settings.get("folder_production"), data_project.get("engine").get("work"), context_path.format(**data_field.get(data_context.get("type"))))
            path = os.path.normpath(path)
            path = os.path.dirname(path)
            if os.path.isdir(path):
                os.startfile(path)
        except Exception as error:
            util.message_log(error)

    def setter_config(self):
        ctx = context.get_context()
        prj = context.get_project()
        all_shots = shots.ShotsModel()
        get_shot = list(filter(lambda sht: sht.get("_id") == ctx.get("_id"), all_shots.all()))
        
        # print(json.dumps(get_shot, indent=2))
        # print(json.dumps(ctx, indent=2))

        self.parent.setter_config(ctx=ctx, prj=prj)
