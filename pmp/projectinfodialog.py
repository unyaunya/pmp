#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import QLabel
from qtutil import QDate2datetime

class ProjectInfoDialog(QtGui.QDialog):
    def __init__(self, appName, parent):
        super(ProjectInfoDialog, self).__init__(parent)
        self.mainWindow = parent
        self.setWindowTitle(appName+":プロジェクト情報の設定")
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
