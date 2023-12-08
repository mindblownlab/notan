from utils import util, context


class AppScene:
    ui = None
    parent = None
    project = None
    context = None

    def __init__(self, parent=None):
        self.parent = parent
        self.project = context.get_project()
        self.context = context.get_context()