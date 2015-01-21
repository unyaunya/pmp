#! python3
# -*- coding: utf-8 -*-

class Namespace(dict):
    """辞書の派生クラス。項目を属性としてアクセスできるようにした。

    次のように使用できる。

    >>> a = Namespace()
    >>> a.b = 1
    >>> a['b']
    1

    >>> a.c.d = 1
    >>> a['c']['d']
    1
    >>> type(a.c)
    <class 'namespace.Namespace'>

    次の使い方はエラーになる。

    >>> a.d = 1
    >>> a.d.e = 2
    Traceback (most recent call last):
        ...
    AttributeError: 'int' object has no attribute 'e'

    基本的に__getattr__ の再定義をしているだけなので、ホントの
    属性があれば、そちらへのアクセスが優先され、辞書に登録した
    項目は隠蔽されるので注意が必要。
    """
    def __init__(self, aDict=None):
        super(Namespace, self).__init__()
        if aDict is None:
            return
        for (key, value) in aDict.items():
            if isinstance(value, dict):
                self[key] = Namespace(value)
            else:
                self[key] = value

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

    def merge(self, ns):
        """ns(dictインスタンス)をマージする"""
        if not isinstance(ns, Namespace):
            ns = Namespace(ns)
        for (key, value) in ns.getItems():
            self.setData(key, value)