import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
libraries = ["", "env\Lib\site-packages"]
PYTHONPATH = []

for lib in libraries:
    path = os.path.normpath(os.path.join(root_path, lib))
    if path not in sys.path:
        sys.path.insert(0, path)
    PYTHONPATH.append(path)

os.environ['PYTHONPATH'] = ";".join(PYTHONPATH)

from importlib import reload
from PyQt5 import QtWidgets
from utils import util
from modules import desktop

reload(util)
reload(desktop)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mb_main = desktop.AppDesktop()
    app.exec_()
