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

    def getItems(self):
        """(keystr, value)のリストを取得する"""
        values = []
        for i in self.items():
            if isinstance(i[1], Namespace):
                values.extend([
                    (("%s.%s") % (i[0], x[0]), x[1])
                    for x in i[1].getItems()])
            else:
                values.append(i)
        return values

    def dump(self, f):
        for i in self.getItems():
            print("%s = %s" % (i[0], i[1]), file=f)

    def load(self, f):
        for line in f.readlines():
            words = [word.trim() in line.split('=')]
            self.setData(word[0], word[1])
