#! python3
# -*- coding: utf-8 -*-

import os
import configparser

MAX_LASTUSED = 5

class Config(object):
    def __init__(self):
        self.inifile = configparser.SafeConfigParser()
        self.inifile.read(self._filename())
        self._lastUsed = []
        try:
            n = max(MAX_LASTUSED,
                    min(0, int(self.inifile.get("lastUsed", "count"))))
        except (ValueError, configparser.NoSectionError):
            n = MAX_LASTUSED
        for i in range(n):
            try:
                self._lastUsed.append(self.inifile.get("lastUsed", "file%d" % (i+1)))
            except:
                pass
        self._lastUsed = [x for x in self._lastUsed if x != '']

    def _filename(self):
        return "./config.ini"
        #return os.path.join(os.environ['HOME'], '.pygantt.ini'

    def lastUsedCount(self):
        return len(self._lastUsed)

    def lastUsed(self, index = 0):
        if index < 0 or index >= len(self._lastUsed):
            return ''
        return self._lastUsed[index]

    def addlastUsed(self, file):
        try:
            n = self._lastUsed.index(file)
        except:
            self._lastUsed.insert(0, file)
            if len(self._lastUsed) > MAX_LASTUSED:
                self._lastUsed = self._lastUsed[0:MAX_LASTUSED]
        self.save()

    def save(self):
        config = configparser.ConfigParser()
        config['lastUsed'] = {}
        config['lastUsed']['count'] = str(len(self._lastUsed))
        for i in range(len(self._lastUsed)):
            config['lastUsed']['file%d' % (i+1)] = self._lastUsed[i]
        with open(self._filename(), 'w') as f:
            config.write(f)

config = Config()