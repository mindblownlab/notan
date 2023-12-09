from utils.api import Api
from utils import util
import os
from glob import glob


class TypesModel(Api):
    collection = 'types'

    def all(self):
        try:
            settings = self.get_settings()
            return list(map(lambda typ: {
                "name": typ,
                "type": typ
            }, settings.get("types_assets")))
        except Exception as error:
            util.message_log(error)