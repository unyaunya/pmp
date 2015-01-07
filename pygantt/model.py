#! python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QVariant
from .util import s2dt, dt2s, dt
from .task import Task
import json, codecs

class TaskModel(Task):
    #def __init__(self, name="(未定)", start = None, end = None, pv=0, ev=0):
    #    super(TaskModel, self).__init__(name, start, end, pv, ev)

    def treeItems(self, tasks = None):
        items = []
        if tasks is None:
            tasks = self.children
        for i in range(0, len(tasks)):
            task = tasks[i]
            item = QtGui.QTreeWidgetItem()
            self._setTreeWidgetItem(item, task)
            if task.children is not None and len(task.children) > 0:
                item.addChildren(self.treeItems(task.children))
            items.append(item)
        return items

    @staticmethod
    def _setTreeWidgetItem(item, task):
        item.setText(0, task.name)
        item.setText(1, dt2s(task.start))
        item.setText(2, dt2s(task.end))
        item.setText(3, "unknown")
        item.setData(4, Qt.UserRole, task)

    @staticmethod
    def dump(obj, path):
        with codecs.open(path, 'w', 'utf8') as f:
            json.dump(obj, f, indent=2, default=_to_json, ensure_ascii=False)

    @staticmethod
    def load(path):
        with open(path, mode='r', encoding='utf-8') as f:
            model = json.load(f, object_hook=_from_json)
            #taskModel = TaskModel(model.name, model.start, model.end)
            #taskModel.children = model
            #return taskModel
            return model

def _to_json(obj):
    if isinstance(obj, TaskModel):
        return {'__class__': 'pygantt.TaskModel',
                'name': obj.name,
                'start': obj.start,
                'end': obj.end,
                'pv': obj.pv,
                'ev': obj.ev,
                'children': obj.children,
                }
    if isinstance(obj, Task):
        return {'__class__': 'pygantt.Task',
                'name': obj.name,
                'start': obj.start,
                'end': obj.end,
                'pv': obj.pv,
                'ev': obj.ev,
                'children': obj.children,
                }
    if isinstance(obj, dt):
        return {'__class__': 'datetime.datetime',
                 '__value__': obj.isoformat()}
    raise TypeError(repr(obj) + ' is not JSON serializable')

def _from_json(json_object):
    if '__class__' in json_object:
        if json_object['__class__'] == 'datetime.datetime':
            return dt.strptime(json_object['__value__'], '%Y-%m-%dT%H:%M:%S')
        if json_object['__class__'] == 'pygantt.Task':
            model = Task(
                    name = json_object['name'],
                    start = json_object['start'],
                    end = json_object['end'],
                    pv = json_object['pv'],
                    ev = json_object['ev'],
                    )
            model.children = json_object['children']
            return model
        if json_object['__class__'] == 'pygantt.TaskModel':
            model = TaskModel(
                    name = json_object['name'],
                    start = json_object['start'],
                    end = json_object['end'],
                    pv = json_object['pv'],
                    ev = json_object['ev'],
                    )
            #model.pv = json_object['pv'],
            #model.ev = json_object['ev'],
            model.children = json_object['children']
            return model
    return json_object
