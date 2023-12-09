from utils.api import Api
import os
from utils import util


class ShotsModel(Api):
    collection = 'shots'

    def all(self):
        try:
            path = os.path.join(self.get_settings().get("project_root"), self.get_project().get("name"), self.get_settings().get("folder_production"), self.get_settings().get("database"), "{}.yml".format(self.collection))
            path = os.path.normpath(path)
            data = util.storage(path=path)
            return data or []
        except Exception as error:
            util.message_log(error)
