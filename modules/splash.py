from utils import util
from PyQt5 import QtWidgets, QtCore, QtGui
from importlib import reload

reload(util)


class AppSplash(QtWidgets.QMainWindow):
    parent = None

    def __init__(self):
        super(AppSplash, self).__init__()
        try:
            self.setStyleSheet(util.get_style(name='style'))
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
            self.setSizePolicy(sizePolicy)
            self.resize(602, 382)
            self.setMinimumSize(QtCore.QSize(602, 382))

            self.ui = util.load_ui(target=self, name="splash")
            self.setCentralWidget(self.ui)
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        except Exception as error:
            util.message_log(error)


from utils import resources
