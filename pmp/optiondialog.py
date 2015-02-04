#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from qtutil import PropertyDialog
from pmp.settings import APPLICATION_NAME, Settings, settings, dlgSpecs

class OptionDialog(PropertyDialog):
    def __init__(self, ganttWidget=None, parent = None):
        self.ganttWidget = ganttWidget
        super(OptionDialog, self).__init__(APPLICATION_NAME+":オプション設定", parent)
        self.setProperties(dlgSpecs, settings)

    def save(self):
        settings.merge(self.settings)
        Settings.dump(settings, "settings.ini")
        settings.applyTo(self.ganttWidget)

    def saveAndAccept(self):
        self.save()
        super(OptionDialog, self).accept()

    @staticmethod
    def createModal(ganttWidget, parent):
        dialog = OptionDialog(ganttWidget, parent)
        dialog.buttonOk.clicked.connect(dialog.saveAndAccept)
        return dialog

    @staticmethod
    def createModeless(ganttWidget, parent):
        dialog = OptionDialog(ganttWidget, parent)
        return dialog
