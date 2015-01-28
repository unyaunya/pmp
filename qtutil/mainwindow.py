#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from argparse import Namespace
from .misc import createAction
from .print import PrintHandler

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, applicationName="MyApp"):
        super(MainWindow, self).__init__(parent)
        self.applicationName = applicationName
        self.setup_gui()

    def setup_gui(self):
        """GUI部品のセットアップ。派生クラスでオーバライド"""
        self.setWindowTitle(self.applicationName)

    def printer(self):
        """printerオブジェクトを取得する。派生クラスでオーバライド"""
        return QtGui.QPrinter()

    def printhandler(self):
        """PrintHandlerオブジェクトを取得する。派生クラスでオーバライド"""
        return PrintHandler()

    def createActions(self):
        """Actionオブジェクトを作成する。派生クラスでオーバライド"""
        self.actions = Namespace()
        self.actions.quit = createAction(self.quit, '終了', "Alt+F4")
        self.actions.print = createAction(self.printAction, '印刷', "Ctrl+P")
        self.actions.preview = createAction(self.printPreview, '印刷プレビュー')
        self.actions.pageSettings = createAction(self.pageSettings, 'ページ設定')
        self.actions.aboutQt = createAction(self.aboutQt, 'Qtについて')
        self.actions.about = createAction(self.about, 'バージョン情報', "Alt+A")

    def print(self, printer):
        """印刷用の描画処理。派生クラスでオーバライド"""
        self.printhandler().print(printer)

    def not_implemented(self):
        self.information("実装されていません")

    def information(self, s):
        QtGui.QMessageBox.information(self, self.applicationName, s)

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def printAction(self):
        self.printhandler().printAction()

    def printPreview(self):
        self.printhandler().printPreview()

    def pageSettings(self):
        self.printhandler().pageSetting()

    def about(self):
        QtGui.QMessageBox.about(self, self.applicationName, "分かりません")

    def aboutQt(self):
        QtGui.QApplication.aboutQt()

    def quit(self):
        QtGui.QApplication.quit()

    #---------------------------------------------------------------------------
    #   staticmethod
    #---------------------------------------------------------------------------
    @staticmethod
    def createAction(func, name, shortcut = None):
        """Actionオブジェクト作成用のユーティリティメソッド"""
        action = QAction(name, self)
        if shortcut is not None:
            if isinstance(shortcut, str):
                action.setShortcut(QtGui.QKeySequence.fromString(shortcut))
            else:
                action.setShortcut(shortcut)
        action.triggered.connect(func)
        return action
