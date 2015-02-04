#! python3
# -*- coding: utf-8 -*-

import uuid
import copy

import numbers
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QModelIndex
from .settings import *
from qtutil import toQDate, to_datetime, tuple2brush

_aggregatedTaskBrush = tuple2brush(AGGREGATED_TASK_COLOR)

class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, task=None):
        super(TreeWidgetItem, self).__init__()
        self._uuid = uuid.uuid4()
        if task is not None:
            self.taskToItem(task)

    def taskToItem(self, task):
        self.name = task.name
        self.start = toQDate(task.start)
        self.end = toQDate(task.end)
        self.pv = task.pv
        self.ev = task.ev
        self.pic = task.pic
        self.task = task
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        if task.children is not None and len(task.children) > 0:
            self.addChildren(TreeWidgetItem.Items(task.children))

    def _dataChanged(self, column):
        task = self.task
        if self.task is None:
            return
        if column == COLUMN_NAME:
            task.name = self.name
        elif column == COLUMN_START:
            task.start = to_datetime(self.start)
        elif column == COLUMN_END:
            task.end = to_datetime(self.end)
        elif column == COLUMN_PV:
            task.pv = self.pv
        elif column == COLUMN_EV:
            task.ev = self.ev
        elif column == COLUMN_PIC:
            task.pic = self.pic

    def isAggregated(self):
        return self.childCount() > 0

    def data(self, column, role):
        if self.isAggregated():
            #集約タスクの属性は、子タスクの値から算出して表示する
            if role == Qt.DisplayRole:
                if column == COLUMN_PV:
                    return sum(item.pv for item in self.childItems())
                elif column == COLUMN_EV:
                    return sum(item.ev for item in self.childItems())
                elif column == COLUMN_START:
                    return toQDate(self.task.minimumDate())
                elif column == COLUMN_END:
                    return toQDate(self.task.maximumDate())
            elif role == Qt.ForegroundRole:
                return _aggregatedTaskBrush
        value = super(TreeWidgetItem, self).data(column, role)
        if column == COLUMN_PIC:
            if role == Qt.DisplayRole:
                if value is None:
                    value = "(未定)"
        return value

    def setData(self, column, role, value):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            if column == COLUMN_START or column == COLUMN_END:
                value = toQDate(value)
        super(TreeWidgetItem, self).setData(column, role, value)
        self._dataChanged(column)

    def childItems(self):
        items = []
        for i in range(self.childCount()):
            items.append(self.child(i))
        return items

    def findFromUuid(self, uuid):
        if self.uuid == uuid:
            return self
        for child in self.childItems():
            item = child.findFromUuid(uuid)
            if item is not None:
                return item
        return None

    @property
    def uuid(self):
        return self._uuid

    @property
    def task(self):
        return self.data(COLUMN_CHART, Qt.UserRole)

    @task.setter
    def task(self, value):
        self.setData(COLUMN_CHART, Qt.UserRole, value)

    @property
    def name(self):
        return self.data(COLUMN_NAME, Qt.DisplayRole)

    @name.setter
    def name(self, value):
        self.setData(COLUMN_NAME, Qt.DisplayRole, value)

    @property
    def start(self):
        return self.data(COLUMN_START, Qt.DisplayRole)

    @property
    def progressRate(self):
        if self.pv <= 0:
            return 0.0
        return min(1.0, self.ev / self.pv)

    @start.setter
    def start(self, value):
        self.setData(COLUMN_START, Qt.DisplayRole, value)

    @property
    def end(self):
        return self.data(COLUMN_END, Qt.DisplayRole)

    @end.setter
    def end(self, value):
        self.setData(COLUMN_END, Qt.DisplayRole, value)

    @property
    def pv(self):
        return self.data(COLUMN_PV, Qt.DisplayRole)

    @pv.setter
    def pv(self, value):
        if not isinstance(value, numbers.Real):
            return
        self.setData(COLUMN_PV, Qt.DisplayRole, value)

    @property
    def ev(self):
        return self.data(COLUMN_EV, Qt.DisplayRole)

    @ev.setter
    def ev(self, value):
        if not isinstance(value, numbers.Real):
            return
        self.setData(COLUMN_EV, Qt.DisplayRole, value)

    @property
    def pic(self):
        return self.data(COLUMN_PIC, Qt.DisplayRole)

    @pic.setter
    def pic(self, value):
        self.setData(COLUMN_PIC, Qt.DisplayRole, value)

    def clone(self):
        return TreeWidgetItem(copy.deepcopy(self.task))

    @staticmethod
    def Items(tasks):
        return [TreeWidgetItem(tasks[i]) for i in range(0, len(tasks))]
