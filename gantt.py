#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os, json
import sys
import configparser
from datetime import datetime
from argparse import Namespace
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QAction, QWidget, QVBoxLayout, QMenuBar, QLabel
from pygantt import TaskModel, Task, GanttWidget
from pygantt.config import config
from pygantt.settings import *
from pygantt.qtutil import QDate2datetime

def __SampleModel():
    model = TaskModel('サンプル工事', '2014/11/01', '2015/09/30')
    task = Task('たすく1', '2014/11/01', '2014/12/01', 1000, 600)
    task.add(Task('たすく1-1', '2014/12/01', '2015/03/01', 400, 200))
    task.add(Task('たすく1-2', '2014/12/10', '2014/12/31', 300, 100))
    task.add(Task('たすく1-3', '2015/01/01', '2015/01/18', 100, 80))
    model.add(task)
    task = Task('たすく2', '2014/11/01', '2014/12/01')
    task2_1 = task.add(Task('たすく2-1', '2014/11/01', '2014/12/01'))
    task2_1.add(Task('たすく2-1-1', '2014/11/01', '2014/11/10'))
    task2_1.add(Task('たすく2-1-2', '2014/11/05', '2014/11/20'))
    task2_1.add(Task('たすく2-1-3', '2014/11/18', '2014/12/01'))
    task.add(Task('たすく2-2', '2014/11/01', '2014/12/01'))
    task.add(Task('たすく2-3', '2014/11/01', '2014/12/01'))
    model.add(task)
    task = Task('たすく3', '2014/11/01', '2014/12/01')
    task.add(Task('たすく3-1', '2014/11/01', '2014/12/01'))
    task.add(Task('たすく3-2', '2014/11/01', '2014/12/01'))
    task.add(Task('たすく3-3', '2014/11/01', '2014/12/01'))
    model.add(task)
    print(TaskModel.dump(model, os.getcwd()+'\\hoge.json.txt'))
    return model

def SampleModel():
    path = os.getcwd()+'\\hoge.json.txt'
    model = TaskModel.load(path)
    TaskModel.dump(model, os.getcwd()+'\\hoge.json.txt.bak.txt')
    return model

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._setup_gui()

    def _setup_gui(self):
        self.setWindowTitle(APPLICATION_NAME)
        #-- GUI部品の作成
        self.ganttWidget = GanttWidget()
        self.main_frame = QWidget()
        #-- GUI部品のレイアウト
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ganttWidget)
        main_layout.addWidget(self.ganttWidget.getChartScrollBar())
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)
        self.statusBar().showMessage('Ready')
        #-- メニュー／アクションの作成
        self.createActions()
        self.createMenus()
        #-- その他(シグナル/スロットの接続とか)
        self.ganttWidget.currentFileChanged.connect(self._currentFileChanged)
        self.resize(1024, 768)
        if config.lastUsed() != '':
            self.ganttWidget.load(config.lastUsed())

    def _currentFileChanged(self, newFileName):
        self.setWindowTitle(newFileName)

    def _createAction(self, func, name, shortcut = None):
        action = QAction(name, self)
        if shortcut is not None:
            if isinstance(shortcut, str):
                action.setShortcut(QtGui.QKeySequence.fromString(shortcut))
            else:
                action.setShortcut(shortcut)
        action.triggered.connect(func)
        return action

    def createActions(self):
        def dummy(action):
            print("Action(%s)" % action.text())

        gw = self.ganttWidget
        self.actions = Namespace()
        self.actions.open = self._createAction(gw.open, '開く', "Ctrl+O")
        self.actions.save = self._createAction(gw.save, '上書き保存', "Ctrl+S")
        self.actions.saveAs = self._createAction(gw.saveAs, '名前をつけて保存')
        self.actions.exit = self._createAction(self.exit, '終了', "Alt+F4")
        self.actions.insert = self._createAction(gw.insert, 'タスクを挿入', "Ctrl+Insert")
        self.actions.remove = self._createAction(gw.remove, 'タスクを削除', "Ctrl+Delete")
        self.actions.levelUp = self._createAction(gw.levelUp, 'レベルを上げる', "Ctrl+Left")
        self.actions.levelDown = self._createAction(gw.levelDown, 'レベルを下げる', "Ctrl+Right")
        self.actions.up = self._createAction(gw.up, '一つ上に移動する', "Ctrl+Up")
        self.actions.down = self._createAction(gw.down, '一つ下に移動する', "Ctrl+Down")
        self.actions.day = self._createAction(gw.timescaleDay, '1日', "Ctrl+D")
        self.actions.week = self._createAction(gw.timescaleWeek, '1週間', "Ctrl+W")
        self.actions.month = self._createAction(gw.timescaleMonth, '1月', "Ctrl+M")
        self.actions.print = self._createAction(self.printAction, '印刷', "Ctrl+P")
        self.actions.preview = self._createAction(self.printPreview, '印刷プレビュー')
        self.actions.pageSettings = self._createAction(self.pageSettings, 'ページ設定')
        self.actions.projectInfo = self._createAction(self.setProjectInfo, 'プロジェクト情報', "Alt+P")
        self.actions.aboutQt = self._createAction(self.aboutQt, 'Qtについて')
        self.actions.about = self._createAction(self.about, 'バージョン情報', "Alt+A")

    def createMenus(self):
        menuBar = self.menuBar()
        if True:
            fileMenu = menuBar.addMenu("ファイル")
            fileMenu.addAction(self.actions.open)
            fileMenu.addAction(self.actions.save)
            fileMenu.addAction(self.actions.saveAs)
            fileMenu.addSeparator()
            fileMenu.addAction(self.actions.print)
            fileMenu.addAction(self.actions.preview)
            fileMenu.addAction(self.actions.pageSettings)
            fileMenu.addSeparator()
            fileMenu.addAction(self.actions.exit)
            editMenu = menuBar.addMenu("編集")
            editMenu.addAction(self.actions.insert)
            editMenu.addAction(self.actions.remove)
            editMenu.addSeparator()
            editMenu.addAction(self.actions.up)
            editMenu.addAction(self.actions.down)
            editMenu.addAction(self.actions.levelUp)
            editMenu.addAction(self.actions.levelDown)
            timescaleMenu = menuBar.addMenu("タイムスケール")
            timescaleMenu.addAction(self.actions.day)
            timescaleMenu.addAction(self.actions.week)
            timescaleMenu.addAction(self.actions.month)
            configMenu = menuBar.addMenu("設定")
            configMenu.addAction(self.actions.projectInfo)
            miscMenu = menuBar.addMenu("その他")
            miscMenu.addAction(self.actions.aboutQt)
            miscMenu.addAction(self.actions.about)

    def drawing(self, painter):
        painter.drawRect(-49,-49,98,98)
        painter.drawEllipse(QtCore.QPoint(0,0),49,49)

    def print(self, printer):
        painter = QtGui.QPainter(printer)
        rect = painter.viewport()
        side = min(rect.width(), rect.height())
        painter.setViewport((rect.width() - side) / 2, (rect.height() - side) / 2, side, side)
        painter.setWindow(-50, -50, 100, 100)
        for i in range(3):
            if i > 0:
                printer.newPage()
                self.drawing(painter)
        print(printer)

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def printAction(self):
        printer = QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer)
        if dialog.exec():
            self.print(printer)

    def printPreview(self):
        printer = QtGui.QPrinter()
        preview = QtGui.QPrintPreviewDialog(printer)
        preview.paintRequested.connect(self.print)
        preview.exec()

    def pageSettings(self):
        QtGui.QMessageBox.information(self, APPLICATION_NAME, "実装されていません")

    def setProjectInfo(self):
        dialog = ProjectInfoDialog(self)
        rslt = dialog.exec_()
        print(rslt)

    def about(self):
        QtGui.QMessageBox.about(self, APPLICATION_NAME, "分かりません")

    def aboutQt(self):
        QtGui.QMessageBox.aboutQt(self)

    def exit(self):
        sys.exit()

class ProjectInfoDialog(QtGui.QDialog):
    #def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags(0)):
    #    super(ProjectInfoDialog, self).__init__(parent, flags)
    def __init__(self, parent):
        super(ProjectInfoDialog, self).__init__(parent)
        self.mainWindow = parent
        self.setWindowTitle(APPLICATION_NAME+":プロジェクト情報の設定")
        self.buttonOk = QtGui.QPushButton("buttonOk", self)
        self.buttonOk.setText(self.tr("&OK"))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        self.buttonCancel = QtGui.QPushButton("buttonCancel", self)
        self.buttonCancel.setText(self.tr("&Cancel"))
        self.buttonCancel.setAutoDefault(1)
        self.buttonAdjustDate = QtGui.QPushButton("チャートから日付をセットする")
        model =self.mainWindow.ganttWidget.ganttModel
        self.projectName = QtGui.QLineEdit(model.name)
        self.startDate = QtGui.QDateEdit(model.start)
        self.endDate = QtGui.QDateEdit(model.end)
        #1行目-----------------------------------------------------------------
        main_layout = QtGui.QGridLayout()
        main_layout.setSpacing(8)
        main_layout.setMargin(16)
        main_layout.addWidget(QLabel("プロジェクト名"), 1, 0)
        main_layout.addWidget(self.projectName, 1, 1, 1, 3)
        #2行目
        main_layout.addWidget(QLabel("開始日"), 2, 0)
        main_layout.addWidget(self.startDate, 2, 1)
        main_layout.addWidget(QLabel("終了日"), 2, 2)
        main_layout.addWidget(self.endDate, 2, 3)
        #3行目
        main_layout.addWidget(self.buttonOk, 3, 0)
        main_layout.addWidget(self.buttonCancel, 3, 1)
        main_layout.addWidget(self.buttonAdjustDate, 3, 2, 1, 2)
        self.setLayout(main_layout)
        #----------------------------------------------------------------------
        self.buttonOk.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)
        self.buttonAdjustDate.clicked.connect(self.adjustDate)

    def _model(self):
        return self.mainWindow.ganttWidget.ganttModel

    def adjustDate(self):
        self.startDate.setDate(self._model().minimumDate())
        self.endDate.setDate(self._model().maximumDate())

    def accept(self):
        super(ProjectInfoDialog, self).accept()
        print(self.projectName.text(), self.startDate.date(), self.endDate.date())
        self._model().name = self.projectName.text()
        self._model().start = QDate2datetime(self.startDate.date())
        self._model().end = QDate2datetime(self.endDate.date())
        self.mainWindow.ganttWidget.ganttModel = self._model()


def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
