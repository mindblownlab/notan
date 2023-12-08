from utils.api import Api
from utils import util
import os

class StepsModel(Api):
    collection = 'steps'

    def all(self, type="asset"):
        try:
            settings = self.get_settings()
            return list(map(lambda ast: {
                "name": ast,
                "type": ast
            }, settings.get("steps").get(type)))
        except Exception as error:
            util.message_log(error)
