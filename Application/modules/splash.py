from importlib import reload
from utils import util
from PyQt5 import QtWidgets, QtCore, QtGui

reload(util)


class AppSplash(QtWidgets.QMainWindow):
    ui = None
    settings = None

    def __init__(self, parent=None):
        super(AppSplash, self).__init__()
        self.parent = parent
        self.setStyleSheet(util.get_style(name='style'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setSizePolicy(sizePolicy)

        self.ui = util.load_ui(target=self, name="splash")
        pixmap = QtGui.QPixmap(util.load_icon(name="splash"))
        self.ui.image.setPixmap(pixmap)
        self.show()

        QtCore.QTimer.singleShot(2500, self.startup)

    def startup(self):
        self.close()
        self.parent.show()
