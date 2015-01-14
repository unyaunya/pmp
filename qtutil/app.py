#! python3
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui

class App(object):
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)

    def exec(self, mainWindowClass):
        self.mainWindow = mainWindowClass()
        self.mainWindow.show()
        self.app.exec_()

