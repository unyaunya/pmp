#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt
from .misc import to_date
from .namespace import Namespace
from datetime import date, datetime

class NoEditItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(NoEditItemDelegate, self).__init__(parent)

    def createEditor(self, parent, option, modelIndex):
        return None

class ItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        self.treeWidget = parent

    #def paint(self, painter, option, modelIndex):
    #    item = self.treeWidget.itemFromIndex(modelIndex)
    #    typeName = item.option.typeName
    #    if typeName == date:
    #        super(ItemDelegate, self).paint(painter, option, modelIndex)
    #    else:
    #        super(ItemDelegate, self).paint(painter, option, modelIndex)

    def createEditor(self, parent, option, modelIndex):
        item = self.treeWidget.itemFromIndex(modelIndex)
        typeName = item.option.typeName
        if typeName == date:
            widget = QtGui.QDateEdit(
                item.settings.getData(item.option.key, item.option.defaultValue),
                parent)
            widget.setCalendarPopup(True)
            return widget
        else:
            return super(ItemDelegate, self).createEditor(parent, option, modelIndex)

class PropertyTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(PropertyTreeWidget, self).__init__(parent)
        self.setHeaderLabels(['項目名', '値'])
        self.header().resizeSection(0, 200)
        self.header().resizeSection(1, 200)
        self.setItemDelegateForColumn(0, NoEditItemDelegate(self))
        self.setItemDelegateForColumn(1, ItemDelegate(self))

    def _expand(self, items):
        for item in items:
            self._expand(item.childItems())
            self.expandItem(item)


class Property(object):
    def __init__(self, displayName, typeName=None, key=None, defaultValue=None):
        self.displayName = displayName
        self.typeName = typeName
        self.key = key
        self.defaultValue = defaultValue

class PropertyDialog(QtGui.QDialog):
    def __init__(self, title, parent = None):
        super(PropertyDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.buttonOk = QtGui.QPushButton("buttonOk", self)
        self.buttonOk.setText(self.tr("&OK"))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)

        self.propertyTreeWidget = PropertyTreeWidget(self)
        self.setFixedSize(450, 600)
        #1行目-----------------------------------------------------------------
        main_layout = QtGui.QGridLayout()
        main_layout.setSpacing(8)
        main_layout.setMargin(16)
        main_layout.addWidget(self.propertyTreeWidget, 0, 0, 1, 3)
        #2行目
        main_layout.addWidget(self.buttonOk, 1, 2)
        self.setLayout(main_layout)
        #----------------------------------------------------------------------

    def setProperties(self, dlgSpecs, settings):
        self.dlgSpecs = dlgSpecs
        self.settings = Namespace(settings)
        widget = self.propertyTreeWidget
        rootItem = widget.invisibleRootItem()
        parent = rootItem
        elems = self.dlgSpecs
        for e in elems:
            item = TreeWidgetItem(e, self.settings)
            parent.addChild(item)
            widget._expand([item])

class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, data=None, settings=None):
        super(TreeWidgetItem, self).__init__()
        self.settings = settings
        if isinstance(data, str):
            self.option = Property(data)
            children = None
        elif isinstance(data, list):
            self.option = Property(data[0])
            children = TreeWidgetItem.Items(data[1:], settings)
        elif isinstance(data, Property):
            self.option = data
            self.setFlags(self.flags() | Qt.ItemIsEditable)
            children = None
        else:
            raise Error
        if children is not None:
            self.addChildren(children)

    def childItems(self):
        items = []
        for i in range(self.childCount()):
            items.append(self.child(i))
        return items

    def data(self, column, role):
        if role == Qt.DisplayRole:
            if column == 0:
                return self.option.displayName
            if column == 1:
                print(self.option.key)
                if self.option.key is None:
                    return None
                value = self.settings.getData(self.option.key, self.option.defaultValue)
                if self.option.typeName == date:
                    value = value.strftime("%Y/%m/%d")
                return value
        super(TreeWidgetItem, self).data(column, role)

    def setData(self, column, role, value):
        print(column, role, value, self.option.key)
        if role == Qt.EditRole:
            if column == 1:
                if self.option.typeName == date:
                    value = to_date(value.date())
                else:
                    value = self.option.typeName(value)
                self.settings.setData(self.option.key, value)
                print(self.settings)

    @staticmethod
    def Items(options, settings):
        return [TreeWidgetItem(x, settings) for x in options]
