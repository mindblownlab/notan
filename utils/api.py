import json
import os
from utils import util, context


class Api(object):
    collection = ''

    def get_settings(self):
        return util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))

    def get_project(self):
        data = context.get_project()
        settings = self.get_settings()
        if data.get("path") is None:
            data.update({"path": os.path.join(settings.get("project_root"), data.get("name"))})
            os.environ['MB_PROJECT'] = json.dumps(data)
        return data

    def get_context(self):
        return context.get_project()

    def get_template(self):
        return util.storage(path=os.path.join(util.get_root_path(), 'config', 'templates.yml'))
