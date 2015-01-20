#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt
from .misc import QDate2datetime
from .namespace import Namespace


class ItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

    def createEditor(self, parent, option, modelIndex):
        return None

class PropertyTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(PropertyTreeWidget, self).__init__(parent)
        self.setHeaderLabels(['項目名', '値'])
        self.header().resizeSection(0, 200)
        self.header().resizeSection(1, 200)
        self.setItemDelegateForColumn(0, ItemDelegate(self))

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
    def __init__(self, title, parent):
        super(PropertyDialog, self).__init__(parent)
        self.mainWindow = parent
        self.setWindowTitle(title)
        self.buttonOk = QtGui.QPushButton("buttonOk", self)
        self.buttonOk.setText(self.tr("&OK"))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        self.buttonCancel = QtGui.QPushButton("buttonCancel", self)
        self.buttonCancel.setText(self.tr("&Cancel"))
        self.buttonCancel.setAutoDefault(1)

        self.propertyTreeWidget = PropertyTreeWidget(self)
        self.setFixedSize(450, 600)
        #1行目-----------------------------------------------------------------
        main_layout = QtGui.QGridLayout()
        main_layout.setSpacing(8)
        main_layout.setMargin(16)
        main_layout.addWidget(self.propertyTreeWidget, 1, 0, 2, 2)

        #2行目
        #main_layout.addWidget(QLabel("開始日"), 2, 0)
        #main_layout.addWidget(self.startDate, 2, 1)
        #main_layout.addWidget(QLabel("終了日"), 2, 2)
        #main_layout.addWidget(self.endDate, 2, 3)
        #3行目
        main_layout.addWidget(self.buttonOk, 3, 0)
        main_layout.addWidget(self.buttonCancel, 3, 1)
        self.setLayout(main_layout)
        #----------------------------------------------------------------------
        self.buttonOk.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)

    def setProperties(self, dlgSpecs, settings):
        self.dlgSpecs = dlgSpecs
        widget = self.propertyTreeWidget
        rootItem = widget.invisibleRootItem()
        parent = rootItem
        elems = self.dlgSpecs
        for e in elems:
            item = TreeWidgetItem(e, settings)
            parent.addChild(item)
            widget._expand([item])

    def accept(self):
        super(PropertyDialog, self).accept()


class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, data=None, settings=None):
        super(TreeWidgetItem, self).__init__()
        self.settings = settings
        #self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
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
                if self.option.key is None:
                    return None
                return self.settings.getData(self.option.key, self.option.defaultValue)
        super(TreeWidgetItem, self).data(column, role)

    def setData(self, column, role, value):
        if role == Qt.EditRole:
            print(column, role, value, self.option.key)
            if column == 1:
                self.settings.setData(self.option.key, self.option.typeName(value))
                print(self.settings)

    @staticmethod
    def Items(options, settings):
        return [TreeWidgetItem(x, settings) for x in options]
