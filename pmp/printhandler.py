#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from .widget import GanttWidget
from qtutil import PrintHandler

class GanttPrintHandler(PrintHandler):
    def __init__(self, ganttWidget):
        super(GanttPrintHandler, self).__init__()
        self._printer = None
        self.ganttWidget = ganttWidget

    def printer(self):
        if self._printer is None:
            self._printer = QtGui.QPrinter()
            self._printer.setOrientation(QtGui.QPrinter.Landscape)
        self._printer.setDocName(self.ganttWidget.ganttModel.name)
        return self._printer

    def pageCount(self):
        return 1

    def printPage(self, painter, pageNo, pageCount):
        painter.save()
        deviceRect = painter.device().pageRect()
        painter.translate(deviceRect.top(), deviceRect.left())
        widget = GanttWidget()
        widget.ganttModel = self.ganttWidget.ganttModel
        logicalRect = widget.paintRect()
        widget.setGeometry(logicalRect)
        print(deviceRect, logicalRect)
        ratio = 0.9 * (deviceRect.width()/logicalRect.width())
        logicalRect = QtCore.QRect(0,0,logicalRect.width(),ratio*deviceRect.height())
        painter.scale(ratio, ratio)
        #widget.render(painter, sourceRegion=QtGui.QRegion(widget.paintRect()))

        pri = widget.printRectInfo()

        #データ部ヘッダ
        x_org = 0
        y_org = 0
        widget.renderDataHeader(pri, painter)

        #データ部本体
        y_org = pri['headerHeight']+100
        painter.translate(0, y_org)
        widget.renderDataBody(pri, painter)

        #チャート部ヘッダ
        x_org = pri['headerWidth']+100
        painter.translate(x_org, -y_org)
        y_org = 0
        widget.renderChartHeader(pri, painter)

        #チャート部本体
        y_org = pri['headerHeight']+100
        painter.translate(0, y_org)
        widget.renderChartBody(pri, painter)

        painter.restore()
