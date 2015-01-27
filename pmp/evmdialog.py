#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui

class EvmDialog(QtGui.QDialog):
    def __init__(self, appName, parent):
        super(EvmDialog, self).__init__(parent)
        self.mainWindow = parent
        self.setWindowTitle(appName+":プロジェクト情報の設定")
        self.textEdit = self._createTextEdit()
        self.textEdit.setReadOnly(True)
        self.buttonOk = QtGui.QPushButton("buttonOk", self)
        self.buttonOk.setText(self.tr("&OK"))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        #1行目-----------------------------------------------------------------
        main_layout = QtGui.QGridLayout()
        main_layout.setSpacing(8)
        main_layout.setMargin(16)
        main_layout.addWidget(self.textEdit, 0, 0, 4, 2)

        #3行目
        main_layout.addWidget(self.buttonOk, 3, 0)
        self.setLayout(main_layout)
        #----------------------------------------------------------------------
        self.buttonOk.clicked.connect(self.accept)
        self.setFixedSize(300, 800)

    def _createTextEdit(self):
        textEdit = QtGui.QTextEdit(self)
        textEdit.setPlainText(self._getTextFromModel())
        textEdit.setReadOnly(True)
        return textEdit

    def _getTextFromModel(self):
        data = self.mainWindow.ganttWidget.ganttModel.getEvmData()
        accumulated = 0
        s = '日付, PV(当日), PV（累計)\n'
        for (aDate, pv, ev) in data:
            accumulated += pv
            s += "%s, %f, %f\n" % (aDate.strftime('%Y/%m/%d'), pv, accumulated)
        return s
