import copy
from utils.api import Api
from utils import util
import os


class EnginesModel(Api):
    collection = 'engines'

    def all(self):
        settings = util.storage(path=os.path.join(util.get_root_path(), 'config', 'settings.yml'))
        engines = settings.get("engines")
        for e in range(len(engines)):
            eng = engines[e]
            thumb_path = os.path.join(util.get_root_path(), "storage", "engines", "{}.png".format(eng.get("type")))
            data_engine = copy.deepcopy(eng)
            if os.path.exists(thumb_path):
                data_engine["icon"] = thumb_path
            engines[e] = {**data_engine}
        return engines
