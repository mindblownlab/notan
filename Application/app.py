import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
python_root = os.path.join(os.path.dirname(root_path), "Python", "Lib", "site-packages")

PYTHONPATH = []

if root_path not in sys.path:
    sys.path.insert(0, root_path)
PYTHONPATH.append(root_path)

if python_root not in sys.path:
    sys.path.insert(0, python_root)
PYTHONPATH.append(python_root)

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
