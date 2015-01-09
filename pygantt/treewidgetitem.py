#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QModelIndex
from .util import s2dt, dt2s
from .settings import *

class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, task=None):
        super(TreeWidgetItem, self).__init__()
        if task is not None:
            self.taskToItem(task)

    def taskToItem(self, task):
        self.name = task.name
        self.start = dt2s(task.start)
        self.end = dt2s(task.end)
        self.setText(3, "unknown")
        self.task = task
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        if task.children is not None and len(task.children) > 0:
            self.addChildren(TreeWidgetItem.Items(task.children))

    def childItems(self):
        items = []
        for i in range(self.childCount()):
            items.append(self.child(i))
        return items

    @property
    def task(self):
        return self.data(COLUMN_CHART, Qt.UserRole)

    @task.setter
    def task(self, value):
        self.setData(COLUMN_CHART, Qt.UserRole, value)

    @property
    def name(self):
        return self.data(0, Qt.DisplayRole)

    @name.setter
    def name(self, value):
        self.setData(0, Qt.DisplayRole, value)

    @property
    def start(self):
        return self.data(1, Qt.DisplayRole)

    @start.setter
    def start(self, value):
        self.setData(1, Qt.DisplayRole, value)

    @property
    def end(self):
        return self.data(2, Qt.DisplayRole)

    @end.setter
    def end(self, value):
        self.setData(2, Qt.DisplayRole, value)

    @staticmethod
    def Items(tasks):
        return [TreeWidgetItem(tasks[i]) for i in range(0, len(tasks))]