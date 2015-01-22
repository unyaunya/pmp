#! python3
# -*- coding: utf-8 -*-

from .util import s2dt, dt2s, dt
from .task import Task
from datetime import timedelta
import json, codecs

class TaskModel(Task):
    def __init__(self, name='未設定', start=dt.today(), end=None, pv=0, ev=0):
        if end is None:
            end = start+timedelta(days=100)
        super(TaskModel, self).__init__(name, start, end, pv, ev)

    def getEvmData(self):
        _ONEDAY = timedelta(days=1)
        data = []
        d = self.start
        while d <= self.end:
            data.append((d, self.pvFromDate(d), 0))
            d += _ONEDAY
        return data

    @staticmethod
    def dump(obj, path):
        with codecs.open(path, 'w', 'utf8') as f:
            json.dump(obj, f, indent=2, default=_to_json, ensure_ascii=False)

    @staticmethod
    def load(path):
        with open(path, mode='r', encoding='utf-8') as f:
            return json.load(f, object_hook=_from_json)

def _to_json(obj):
    if isinstance(obj, TaskModel):
        return {'__class__': 'pygantt.TaskModel',
                'name': obj.name,
                'start': dt2s(obj.start),
                'end': dt2s(obj.end),
                'pv': obj.pv,
                'ev': obj.ev,
                'children': obj.children,
                'expanded': obj.expanded,
                }
    if isinstance(obj, Task):
        return {'__class__': 'pygantt.Task',
                'name': obj.name,
                'start': dt2s(obj.start),
                'end': dt2s(obj.end),
                'pv': obj.pv,
                'ev': obj.ev,
                'children': obj.children,
                'expanded': obj.expanded,
                }
    raise TypeError(repr(obj) + ' is not JSON serializable')

def _from_json(json_object):
    if '__class__' in json_object:
        if json_object['__class__'] == 'pygantt.Task':
            model = Task(
                    name = json_object['name'],
                    start = s2dt(json_object['start']),
                    end = s2dt(json_object['end']),
                    pv = json_object['pv'],
                    ev = json_object['ev'],
                    )
            model.children = json_object['children']
            model.expanded = True
            try:
                model.expanded = json_object['expanded']
            except:
                pass
            return model
        if json_object['__class__'] == 'pygantt.TaskModel':
            model = TaskModel(
                    name = json_object['name'],
                    start = s2dt(json_object['start']),
                    end = s2dt(json_object['end']),
                    pv = json_object['pv'],
                    ev = json_object['ev'],
                    )
            model.children = json_object['children']
            return model
    return json_object
