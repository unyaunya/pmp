#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from argparse import Namespace
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QRegion, QPrinter
from qtutil import PrintHandler
from .widget import GanttWidget
from .settings import ROW_HEIGHT, COLUMN_CHART, HEADER_HEIGHT, COLUMN_WIDTHS
from .settings import settings

class GanttPrintHandler(PrintHandler):
    def __init__(self, ganttWidget):
        super(GanttPrintHandler, self).__init__()
        self._printer = None
        self.ganttWidget = ganttWidget
        self._pri = Namespace()

    def printer(self):
        if self._printer is None:
            self._printer = QPrinter()
            self._printer.setOrientation(QtGui.QPrinter.Landscape)
            self._printer.setFullPage(True)
            #self._printer.setResolution(QPrinter.HighResolution)
            #self.translate(-15, -15)
        self._printer.setDocName(self.ganttWidget.ganttModel.name)
        return self._printer

    @property
    def horizontalPageCount(self):
        return settings.print.HORIZONTAL_PAGE_COUNT

    def pageCount(self):
        self.preparePrint(self.printer())
        return len(self._pageInfo)

    def preparePrint(self, printer):
        """印刷の前準備。派生クラスでオーバライド"""
        #印刷用のWidgetを用意する
        self._widget = GanttWidget()
        self._widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._widget.ganttModel = self.ganttWidget.ganttModel

        self._pri = self.getPrintRectInfo(printer)
        self._widget.setGeometry(QRect(0, 0,
            self._pri.log.headerWidth + self._pri.log.bodyWidth,
            self._pri.log.headerHeight + self._pri.log.bodyHeight))

        #各ページの表示範囲を算出する
        self._pageInfo = []
        bh = self._pri.log.bodyHeight
        top = 0
        while bh > 0:
            if bh < self._pri.log.bodyHeightPerPage:
                height = bh
            else:
                height = self._pri.log.bodyHeightPerPage
            #----
            bw = self._pri.log.bodyWidth
            left = 0
            while bw > 0:
                if bw < self._pri.log.bodyWidthPerPage:
                    width = bw
                else:
                    width = self._pri.log.bodyWidthPerPage
                self._pageInfo.append(QRect(left, top, width, height))
                left += width
                bw -= width
            #----
            top += height
            bh -= height
        print(self._pageInfo)

    def getPrintRectInfo(self, printer):
        bodyHeight = 0
        it = QtGui.QTreeWidgetItemIterator(self._widget,
                                    QtGui.QTreeWidgetItemIterator.NotHidden)
        while it.value():
            #rect = self.visualRect(self.indexFromItem(it.value()))
            #rowHeight = self.rowHeight(self.indexFromItem(it.value()))
            #print(rect, rowHeight)
            #visualRect, rowHeightで取得できる高さが実際の行高さよりも小さいので
            #定数値を足し込んでおくことにする
            bodyHeight += ROW_HEIGHT
            it += 1
        obj = Namespace()
        obj.dev = Namespace()
        obj.log = Namespace()
        obj.scl = Namespace()
        obj.log.headerWidth = sum(COLUMN_WIDTHS)
        obj.log.headerHeight = HEADER_HEIGHT
        obj.log.bodyWidth    = self._widget.preferableWidth()
        obj.log.bodyHeight   = bodyHeight
        obj.log.bodyWidthPerPage = obj.log.bodyWidth / self.horizontalPageCount
        obj.log.bodyHeightPerPage = ROW_HEIGHT * settings.print.ROWS_PER_PAGE
        obj.log.pageWidth = obj.log.headerWidth + obj.log.bodyWidthPerPage
        obj.log.pageHeight = obj.log.headerHeight + obj.log.bodyHeightPerPage
        pageRect = printer.pageRect()
        obj.dev.pageWidth = pageRect.width()
        obj.dev.pageHeight = pageRect.height()
        obj.dev.headerWidth = obj.dev.pageWidth * settings.print.HEADER_WIDTH_RATIO
        obj.dev.headerHeight = obj.dev.pageHeight * settings.print.HEADER_HEIGHT_RATIO
        obj.dev.bodyWidth    = obj.dev.pageWidth - obj.dev.headerWidth
        obj.dev.bodyHeight   = obj.dev.pageHeight - obj.dev.headerHeight
        obj.scl.headerWidth = obj.dev.headerWidth / obj.log.headerWidth
        obj.scl.headerHeight = obj.dev.headerHeight / obj.log.headerHeight
        obj.scl.bodyWidth = obj.dev.bodyWidth / obj.log.bodyWidthPerPage
        obj.scl.bodyHeight = obj.dev.bodyHeight / obj.log.bodyHeightPerPage
        #obj.header
        print(obj)
        return obj

    def printPage(self, painter, pageNo, pageCount):
        print(painter.device().pageRect(), painter.device().paperRect())
        painter.save()
        #-----------------------------------------------------------------------
        deviceRect = painter.device().pageRect()
        painter.translate(deviceRect.top(), deviceRect.left())
        #print(deviceRect)
        bodyRect = self._pageInfo[pageNo-1]
        #print(bodyRect)
        #データ部ヘッダ
        rect1 = self.renderDataHeader(painter, bodyRect)
        #データ部本体
        self.renderDataBody(painter, bodyRect)
        #チャート部ヘッダ
        self.renderChartHeader(painter, bodyRect)
        #チャート部本体
        self.renderChartBody(painter, bodyRect)
        #ページの枠線
        painter.setPen(self._widget.pen4chartBoundary)
        log = self._pri.dev
        painter.drawRect(0,0,log.headerWidth,log.headerHeight)
        painter.drawRect(log.headerWidth,0,log.bodyWidth,log.headerHeight)
        painter.drawRect(0,log.headerHeight,log.headerWidth,log.bodyHeight)
        painter.drawRect(
                log.headerWidth,log.headerHeight,log.bodyWidth,log.bodyHeight)
        #-----------------------------------------------------------------------
        painter.restore()

    def renderDataHeader(self, painter, bodyRect):
        """データ部ヘッダ"""
        painter.save()
        #painter.translate(0, 0)
        painter.scale(self._pri.scl.headerWidth, self._pri.scl.headerHeight)
        rect = QRect(0,0,self._pri.log.headerWidth, self._pri.log.headerHeight)
        self._widget.render(painter, sourceRegion=QRegion(rect))
        painter.restore()


    def renderDataBody(self, painter, bodyRect):
        """データ部本体"""
        painter.save()
        painter.translate(0, self._pri.dev.headerHeight)
        painter.scale(self._pri.scl.headerWidth, self._pri.scl.bodyHeight)
        self._widget.render(painter, sourceRegion=QtGui.QRegion(
            0, self._pri.log.headerHeight + bodyRect.top(),
            self._pri.log.headerWidth, bodyRect.height()))
        painter.restore()

    def renderChartHeader(self, painter, bodyRect):
        """チャート部ヘッダ"""
        painter.save()
        painter.translate(self._pri.dev.headerWidth, 0)
        painter.scale(self._pri.scl.bodyWidth, self._pri.scl.headerHeight)
        self._widget.render(painter, sourceRegion=QtGui.QRegion(
            self._pri.log.headerWidth + bodyRect.left(), 0,
            bodyRect.width(), self._pri.log.headerHeight))
        painter.restore()

    def renderChartBody(self, painter, bodyRect):
        """チャート部本体"""
        painter.save()
        painter.translate(self._pri.dev.headerWidth, self._pri.dev.headerHeight)
        painter.scale(self._pri.scl.bodyWidth, self._pri.scl.bodyHeight)
        self._widget.render(painter, sourceRegion=QtGui.QRegion(
            self._pri.log.headerWidth + bodyRect.left(),
            self._pri.log.headerHeight + bodyRect.top(),
            bodyRect.width(),
            bodyRect.height()))
        painter.restore()
