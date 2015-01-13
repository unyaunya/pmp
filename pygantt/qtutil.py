#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from datetime import datetime

def QDate2datetime(qdate):
    return datetime(qdate.year(), qdate.month(), qdate.day())

def tuple2color(aTuple):
    (r,g,b,alpha) = aTuple
    return QtGui.QColor(r,g,b,alpha)