#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt4 import QtGui
from PyQt4.QtGui import QAction, QWidget, QVBoxLayout, QMenuBar, QLabel
from qtutil import App, MainWindow, createAction
from pmp import GanttWidget, GanttPrintHandler
from pmp import config
from pmp.settings import APPLICATION_NAME, Settings, settings, dlgSpecs
from pmp.projectinfodialog import ProjectInfoDialog
from pmp.evmdialog import EvmDialog
from pmp.optiondialog import OptionDialog

class GanttMainWindow(MainWindow):
    def __init__(self, parent=None):
        path = "settings.ini"
        self._printHandler = None
        try:
            _settings = Settings.load(path)
        except Exception as e:
            logging.warning("couldn't load '%s'" % path)
            logging.debug(e)
            _settings = None
        if _settings is not None:
            settings.merge(_settings)
        super(GanttMainWindow, self).__init__(parent, APPLICATION_NAME)
        if _settings is None:
            self.information("%sが読めない(;_;)" % path)

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
            logging.debug("Action(%s)" % action.text())
        gw = self.ganttWidget
        self.actions.open = createAction(gw.open, '開く', "Ctrl+O")
        self.actions.openServer = createAction(gw.openServer, 'サーバから開く', "Ctrl+A")
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
        self.actions.setOptions = createAction(self.setOptions, "オプション", "Alt+O")
        self.actions.evm = createAction(self.showEVM, "EVMデータ")

    def createMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("ファイル")
        fileMenu.addAction(self.actions.open)
        fileMenu.addAction(self.actions.openServer)
        fileMenu.addAction(self.actions.save)
        fileMenu.addAction(self.actions.saveAs)
        fileMenu.addSeparator()
        fileMenu.addAction(self.actions.print)
        fileMenu.addAction(self.actions.preview)
        fileMenu.addAction(self.actions.pageSettings)
        fileMenu.addSeparator()
        fileMenu.addAction(self.actions.quit)
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
        configMenu.addAction(self.actions.setOptions)
        miscMenu = menuBar.addMenu("その他")
        miscMenu.addAction(self.actions.evm)
        miscMenu.addAction(self.actions.aboutQt)
        miscMenu.addAction(self.actions.about)

    def printhandler(self):
        if self._printHandler is None:
            self._printHandler = GanttPrintHandler(self.ganttWidget)
        return self._printHandler

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def setProjectInfo(self):
        ProjectInfoDialog(APPLICATION_NAME, self).exec_()

    def setOptions(self):
        OptionDialog.createModal(self.ganttWidget, self).exec_()

    def setSelectModeRow(self):
        self.ganttWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ganttWidget.refresh()

    def setSelectModeCell(self):
        self.ganttWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.ganttWidget.refresh()

    def showEVM(self):
        EvmDialog(APPLICATION_NAME, self).exec_()

def exec():
    logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M:%S',
                filename='~pmp.log',
                )
    logging.info('START')
    app = App()
    app.exec(GanttMainWindow)
    Settings.dump(settings, "settings.ini")
    logging.info('END')
    logging.shutdown()

if __name__ == '__main__':
    exec()
