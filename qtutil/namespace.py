#! python3
# -*- coding: utf-8 -*-

class Namespace(dict):
    def __getattr__(self, key):
        if not key in self:
            self[key] = Namespace()
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def setData(self, keystr, value):
        keys = keystr.split('.')
        obj = self
        for key in keys[:-1]:
            if not key in obj:
                obj[key] = Namespace()
            obj = obj[key]
        obj[keys[len(keys)-1]] = value

    def getData(self, keystr, defaultValue):
        keys = keystr.split('.')
        obj = self
        for key in keys[:-1]:
            if not key in obj:
                obj[key] = Namespace()
            obj = obj[key]
        lastKey = keys[len(keys)-1]
        if lastKey in obj:
            return obj[lastKey]
        else:
            return defaultValue
