import json

from utils.api import Api
import os
from utils import util
from glob import glob


class ProjectsModel(Api):
    collection = 'projects'

    def all(self):
        try:
            settings = util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))
            project_root = settings.get("project_root")
            projects = glob(os.path.join(project_root, "*")) or []

            if len(projects) > 0:
                projects = list(filter(lambda prj: ".ini" not in prj, projects))
                projects = list(map(lambda prj: {
                    "name": os.path.basename(prj),
                    "path": os.path.normpath(prj),
                    "resolution": [1920, 1080],
                    "fps": 24,
                    "aspect": 1,
                    "status": "active",
                    "thumb": os.path.join(util.get_root_path(), "storage", "default", "thumb.png")
                }, projects))

                for p in range(len(projects)):
                    prj = projects[p]
                    prj.update({"name": prj.get("name").replace(" ", "_")})
                    data_file = os.path.join(prj.get("path"), settings.get("folder_production"), self.get_settings().get("database"), "project.yml")
                    if os.path.exists(data_file):
                        data_project = util.storage(path=data_file) or dict()
                        thumb_path = os.path.join(prj.get("path"), settings.get("folder_production"), "_database_", "thumb.png")
                        data_project["thumb"] = prj.get("thumb")
                        if os.path.exists(thumb_path):
                            data_project["thumb"] = thumb_path
                        projects[p] = {**data_project}
            return projects
        except Exception as error:
            util.message_log(error)
