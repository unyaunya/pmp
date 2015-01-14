#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from datetime import datetime

def QDate2datetime(qdate):
    return datetime(qdate.year(), qdate.month(), qdate.day())

def tuple2color(aTuple):
    (r,g,b,alpha) = aTuple
    return QtGui.QColor(r,g,b,alpha)

def createAction(func, name, shortcut = None):
    """Actionオブジェクト作成用のユーティリティメソッド"""
    action = QtGui.QAction(name, None)
    if shortcut is not None:
        if isinstance(shortcut, str):
            action.setShortcut(QtGui.QKeySequence.fromString(shortcut))
        else:
            action.setShortcut(shortcut)
    action.triggered.connect(func)
    return action

