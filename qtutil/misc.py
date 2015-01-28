#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from datetime import date, datetime

def toQDate(value, formatString='yyyy/MM/dd'):
    if isinstance(value, QtCore.QDate):
        return value
    if isinstance(value, QtCore.QDateTime):
        return value.date()
    if isinstance(value, (date, datetime)):
        return QtCore.QDate(value.year, value.month, value.day)
    if isinstance(value, str):
        return QtCore.QDate.fromString(value, formatString)
    else:
        raise ValueError('toQDate:invalid type <%s>' % str(type(value)))

def to_datetime(value, formatString='%Y/%M/%d'):
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, (QtCore.QDate, QtCore.QDateTime)):
        return datetime(value.year(), value.month(), value.day())
    if isinstance(value, str):
        return datetime.strptime(obj, formatString)
    else:
        raise ValueError('to_datetime:invalid type <%s>' % str(type(value)))

def to_date(value, formatString='%Y/%M/%d'):
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return date(value.year, value.month, value.day)
    if isinstance(value, (QtCore.QDate, QtCore.QDateTime)):
        return date(value.year(), value.month(), value.day())
    if isinstance(value, str):
        return date.strptime(obj, formatString)
    else:
        raise ValueError('to_date:invalid type <%s>' % str(type(value)))

def tuple2color(aTuple):
    (r,g,b,alpha) = aTuple
    return QtGui.QColor(r,g,b,alpha)

def tuple2brush(aTuple):
    return QtGui.QBrush(tuple2color(aTuple))

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

