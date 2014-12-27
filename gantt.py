#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QVBoxLayout
from pygantt import TaskModel, Task, GanttFrame

def SampleModel():
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
    return model

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._setup_gui()

    def _setup_gui(self):
        self.setWindowTitle("がんと")
        #-- GUI部品の作成
        hello_button = QtGui.QPushButton("波浪わーるど")
        check_box = QtGui.QCheckBox("Check Box")
        #-- GUI部品のレイアウト
        main_layout = QVBoxLayout()
        main_layout.addWidget(GanttFrame(model = SampleModel()))
        main_layout.addWidget(hello_button)
        main_layout.addWidget(check_box)
        self.main_frame = QWidget()
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)
        #-- シグナル/スロットの接続
        hello_button.clicked.connect(self.on_click)
        check_box.stateChanged.connect(self.print_state)
        #
        self.resize(1024, 768)

    def on_click(self):
        print("Hello World")

    def print_state(self, state):
        if state == 0:
            print("Unchecked")
        else:
            print("Checked")

def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
