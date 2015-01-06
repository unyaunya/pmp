#! python3
# -*- coding: utf-8 -*-

import uuid
from .util import s2dt, dt


class Task(object):
    """Taskクラス"""

    def __init__(self, name='(未定)', start=None, end=None, pv=0, ev=0):
        self._uuid = uuid.uuid4()
        self.name = name
        self.start = start
        self.end = end
        self.pv = pv
        self.ev = ev
        self.children = []

    @staticmethod
    def to_json(obj):
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

    @staticmethod
    def from_json(json_object):
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
        return json_object

    @property
    def uuid(self):
        return self._uuid

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = s2dt(value)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = s2dt(value)

    @property
    def pv(self):
        return self._pv

    @pv.setter
    def pv(self, value):
        self._pv = max(0, value)

    @property
    def ev(self):
        return self._ev

    @ev.setter
    def ev(self, value):
        self._ev = min(self.pv, value)

    def add(self, child):
        self.children.append(child)
        return child

    def get(self, task):
        if index < 0 or index >= len(self.children):
            return None
        return self.children[index]
