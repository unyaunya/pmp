#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QVariant
from .util import s2dt, dt2s
from .task import Task

class TaskModel(Task):
    def __init__(self, name="(未定)", start = None, end = None):
        super(TaskModel, self).__init__(name, start, end)
        self.dataModel = DataModel(self)
        self.ganttModel = GanttModel(self)

class _TaskTreeModel(object):
    def __init__(self, model):
        self.model = model
        self.children = model.children

    def treeItems(self, tasks = None):
        items = []
        if tasks is None:
            tasks = self.children
        for i in range(0, len(tasks)):
            task = tasks[i]
            item = QtGui.QTreeWidgetItem()
            self.setTreeWidgetItem(item, task)
            if task.children is not None and len(task.children) > 0:
                item.addChildren(self.treeItems(task.children))
            items.append(item)
        return items

    def setTreeWidgetItem(self, item, task):
        """派生クラスでオーバライド"""
        pass

    @property
    def start(self):
        return self.model.start

    @property
    def end(self):
        return self.model.end

class DataModel(_TaskTreeModel):
    def headerLabels(self):
        return ["項目名","開始日","終了日","担当者"]

    def setTreeWidgetItem(self, item, task):
        super(DataModel, self).setTreeWidgetItem(item, task)
        item.setText(0, task.name)
        item.setText(1, dt2s(task.start))
        item.setText(2, dt2s(task.end))

class GanttModel(_TaskTreeModel):
    def headerLabels(self):
        return ["hidden-name", ""]

    def setTreeWidgetItem(self, item, task):
        super(GanttModel, self).setTreeWidgetItem(item, task)
        item.setText(0, task.name)
        item.setData(1, Qt.UserRole, task)
