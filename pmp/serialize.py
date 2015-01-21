#! python3
# -*- coding: utf-8 -*-

import json, codecs
from datetime import date
from .util import s2dt, dt2s
from .task import Task
from .model import TaskModel

def to_json(obj):
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
    if isinstance(obj, date):
        return {'__class__': 'datetime.date',
                'value': dt2s(obj)
                }
    raise TypeError(repr(obj) + ' is not JSON serializable')

def from_json(json_object):
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
        if json_object['__class__'] == 'datetime.date':
            value = s2dt(json_object['value'])
            return date(value.year, value.month, value.day)
    return json_object
