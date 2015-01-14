#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from argparse import Namespace
from .misc import createAction

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

    def createActions(self):
        """Actionオブジェクトを作成する。派生クラスでオーバライド"""
        self.actions = Namespace()
        self.actions.exit = createAction(self.exit, '終了', "Alt+F4")
        self.actions.print = createAction(self.printAction, '印刷', "Ctrl+P")
        self.actions.preview = createAction(self.printPreview, '印刷プレビュー')
        self.actions.pageSettings = createAction(self.pageSettings, 'ページ設定')
        self.actions.aboutQt = createAction(self.aboutQt, 'Qtについて')
        self.actions.about = createAction(self.about, 'バージョン情報', "Alt+A")

    #def drawing(self, painter):
    #    painter.drawRect(-49,-49,98,98)
    #    painter.drawEllipse(QtCore.QPoint(0,0),49,49)

    def print(self, printer):
        """印刷用の描画処理。派生クラスでオーバライド"""
        painter = QtGui.QPainter(printer)
        rect = painter.viewport()
        side = min(rect.width(), rect.height())
        painter.setViewport((rect.width() - side) / 2, (rect.height() - side) / 2, side, side)
        painter.setWindow(-50, -50, 100, 100)
        for i in range(3):
            if i > 0:
                printer.newPage()
                #self.drawing(painter)
                painter.drawRect(-49,-49,98,98)
                painter.drawEllipse(QtCore.QPoint(0,0),49,49)
        print(printer)

    def not_implemented(self):
        QtGui.QMessageBox.information(self, self.applicationName, "実装されていません")


    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def printAction(self):
        printer = self.printer()
        dialog = QtGui.QPrintDialog(printer)
        if dialog.exec():
            self.print(printer)

    def printPreview(self):
        printer = self.printer()
        preview = QtGui.QPrintPreviewDialog(printer)
        preview.paintRequested.connect(self.print)
        preview.exec()

    def pageSettings(self):
        self.not_implemented()

    def about(self):
        QtGui.QMessageBox.about(self, self.applicationName, "分かりません")

    def aboutQt(self):
        QtGui.QApplication.aboutQt()

    def exit(self):
        QtGui.QApplication.exit()

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
