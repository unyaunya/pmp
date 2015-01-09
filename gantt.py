#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os, json
import sys
import configparser
from argparse import Namespace
from PyQt4 import QtGui
from PyQt4.QtGui import QAction, QWidget, QVBoxLayout, QMenuBar
from pygantt import TaskModel, Task, GanttWidget
from pygantt.config import config

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
        self.setWindowTitle("がんと")
        #-- GUI部品の作成
        self.ganttWidget = GanttWidget()
        self.main_frame = QWidget()
        #-- GUI部品のレイアウト
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ganttWidget)
        main_layout.addWidget(self.ganttWidget.getChartScrollBar())
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)
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

    def createMenus(self):
        menuBar = self.menuBar()
        if True:
            fileMenu = menuBar.addMenu("ファイル")
            fileMenu.addAction(self.actions.open)
            fileMenu.addAction(self.actions.save)
            fileMenu.addAction(self.actions.saveAs)
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

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def exit(self):
        sys.exit()


def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
