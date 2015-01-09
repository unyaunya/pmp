#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from datetime import datetime

def QDate2datetime(qdate):
    return datetime(qdate.year(), qdate.month(), qdate.day())