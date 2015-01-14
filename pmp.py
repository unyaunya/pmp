#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import QAction, QWidget, QVBoxLayout, QMenuBar, QLabel
from pmp import GanttWidget
from pmp.config import config
from pmp.settings import *
from qtutil import App, MainWindow, createAction, QDate2datetime, PrintHandler

class GanttPrintHandler(PrintHandler):
    def __init__(self, model):
        super(GanttPrintHandler, self).__init__()
        self._printer = None
        self.ganttModel = model

    def printer(self):
        if self._printer is None:
            self._printer = QtGui.QPrinter()
            self._printer.setOrientation(QtGui.QPrinter.Landscape)
        self._printer.setDocName(self.ganttModel.name)
        return self._printer

    def pageCount(self):
        return 5


class GanttMainWindow(MainWindow):
    def __init__(self, parent=None):
        super(GanttMainWindow, self).__init__(parent, APPLICATION_NAME)
        self._printHandler = None

    def setup_gui(self):
        super(GanttMainWindow, self).setup_gui()
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

    def createActions(self):
        super(GanttMainWindow, self).createActions()
        def dummy(action):
            print("Action(%s)" % action.text())
        gw = self.ganttWidget
        self.actions.open = createAction(gw.open, '開く', "Ctrl+O")
        self.actions.save = createAction(gw.save, '上書き保存', "Ctrl+S")
        self.actions.saveAs = createAction(gw.saveAs, '名前をつけて保存')
        self.actions.insert = createAction(gw.insert, 'タスクを挿入', "Ctrl+Insert")
        self.actions.remove = createAction(gw.remove, 'タスクを削除', "Ctrl+Delete")
        self.actions.levelUp = createAction(gw.levelUp, 'レベルを上げる', "Ctrl+Left")
        self.actions.levelDown = createAction(gw.levelDown, 'レベルを下げる', "Ctrl+Right")
        self.actions.up = createAction(gw.up, '一つ上に移動する', "Ctrl+Up")
        self.actions.down = createAction(gw.down, '一つ下に移動する', "Ctrl+Down")
        self.actions.setSelectModeRow = createAction(self.setSelectModeRow, '行選択', "Ctrl+1")
        self.actions.setSelectModeCell = createAction(self.setSelectModeCell, 'セル選択', "Ctrl+2")
        self.actions.copy = createAction(gw.copy, 'コピー', "Ctrl+C")
        self.actions.paste = createAction(gw.paste, '貼付け', "Ctrl+V")
        self.actions.day = createAction(gw.timescaleDay, '1日', "Ctrl+D")
        self.actions.week = createAction(gw.timescaleWeek, '1週間', "Ctrl+W")
        self.actions.month = createAction(gw.timescaleMonth, '1月', "Ctrl+M")
        self.actions.projectInfo = createAction(self.setProjectInfo, 'プロジェクト情報', "Alt+P")

    def createMenus(self):
        menuBar = self.menuBar()
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
        editMenu.addAction(self.actions.copy)
        editMenu.addAction(self.actions.paste)
        editMenu.addSeparator()
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
        selectionModeMenu = menuBar.addMenu("選択モード")
        selectionModeMenu.addAction(self.actions.setSelectModeRow)
        selectionModeMenu.addAction(self.actions.setSelectModeCell)
        configMenu = menuBar.addMenu("設定")
        configMenu.addAction(self.actions.projectInfo)
        miscMenu = menuBar.addMenu("その他")
        miscMenu.addAction(self.actions.aboutQt)
        miscMenu.addAction(self.actions.about)

    def printhandler(self):
        if self._printHandler is None:
            self._printHandler = GanttPrintHandler(self.ganttWidget.ganttModel)
        return self._printHandler

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def setProjectInfo(self):
        dialog = ProjectInfoDialog(self).exec_()

    def setSelectModeRow(self):
        self.ganttWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ganttWidget.refresh()

    def setSelectModeCell(self):
        self.ganttWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.ganttWidget.refresh()

class ProjectInfoDialog(QtGui.QDialog):
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

if __name__ == '__main__':
    App().exec(GanttMainWindow)
