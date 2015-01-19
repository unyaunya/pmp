#! python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from .util import s2dt, dt

class Task(object):
    """Taskクラス"""

    def __init__(self, name='(未定)', start=None, end=None, pv=0, ev=0):
        self._pv = 0
        self._ev = 0
        #------------------------
        self.name = name
        self.start = start
        self.end = end
        self.pv = pv
        self.ev = ev
        self.children = []
        self.expanded = True

    #@property
    #def uuid(self):
    #    return self._uuid

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
        newValue = max(0, value)
        if newValue == self._pv:
            return
        self._pv = newValue

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

    def minimumDate(self):
        if len(self.children) <= 0:
            return self.start
        val = datetime.max
        for task in self.children:
            d = task.minimumDate()
            if d < val:
                val = d
        return val

    def maximumDate(self):
        if len(self.children) <= 0:
            return self.end
        val = datetime.min
        for task in self.children:
            d = task.maximumDate()
            if d > val:
                val = d
        return val

    def adjustDate(self):
        self.start = self.minimumDate()
        self.end = self.maximumDate()

    @staticmethod
    def defaultTask():
        start=dt.today()
        end = start+timedelta(days=30)
        return Task(start=start, end=end)
