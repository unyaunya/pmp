#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from argparse import Namespace
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QRegion, QPrinter
from qtutil import PrintHandler
from .widget import GanttWidget
from .settings import ROW_HEIGHT, COLUMN_CHART, HEADER_HEIGHT
from .settings import settings
from .optiondialog import OptionDialog

class MyPrintPreviewDialog(QtGui.QPrintPreviewDialog):
    def __init__(self, ganttWidget, printer, parent = None, flags = Qt.WindowFlags()):
        super(MyPrintPreviewDialog, self).__init__(printer, parent, flags)
        self._prepareToolBar()
        self.pageSettingDialog = self._optionDialog(ganttWidget)

    def _optionDialog(self, ganttWidget):
        dialog = OptionDialog.createModeless(ganttWidget, self)
        def _ok():
            dialog.save()
            self._refresh()
        dialog.buttonOk.clicked.connect(_ok)
        def _optionClosed():
            self.actOption.setChecked(False)
        dialog.finished.connect(_optionClosed)
        return dialog

    def _prepareToolBar(self):
        tbs = self.findChildren(QtGui.QToolBar)
        if len(tbs) <= 0:
            self.toolbar = None
            return
        self.toolbar = tbs[0]
        self.toolbar.addSeparator()
        self.wgtRowsPerPage = self._createRowsPerPage()
        self.toolbar.addWidget(self.wgtRowsPerPage)
        self.actOption = self._createPageSettingAction()
        self.toolbar.addAction(self.actOption)

    def _createRowsPerPage(self):
        MINIMUM = 10
        def _rowsPerPageChanged(index):
            settings.print.ROWS_PER_PAGE = index+MINIMUM
            self._refresh()
        widget = QtGui.QComboBox(self)
        for i in range(MINIMUM,100):
            widget.addItem('1ページあたり%d行' % i)
        widget.setCurrentIndex(settings.print.ROWS_PER_PAGE - MINIMUM)
        widget.currentIndexChanged.connect(_rowsPerPageChanged)
        return widget

    def _createOptionutton(self):
        widget = QtGui.QButton('オプション')
        return widget

    def _createPageSettingAction(self):
        #action = QtGui.QAction(QtGui.QIcon(), self.tr("settings"), self)
        action = QtGui.QAction("オプション", self)
        action.setCheckable(True)
        action.setToolTip("オプション設定")
        action.toggled.connect(self._togglePageSettingDialog)
        return action

    def _togglePageSettingDialog(self, value):
        print(value)
        if value == True:
            self.pageSettingDialog.show()
        else:
            self.pageSettingDialog.hide()

    def _refresh(self):
        widget = self.findChild(QtGui.QPrintPreviewWidget)
        widget.updatePreview()

class GanttPrintHandler(PrintHandler):
    def __init__(self, ganttWidget):
        super(GanttPrintHandler, self).__init__()
        self._printer = None
        self.ganttWidget = ganttWidget
        self._pri = Namespace()

    def printer(self):
        if self._printer is None:
            self._printer = QPrinter(QPrinter.HighResolution)
            self._printer.setOrientation(QtGui.QPrinter.Landscape)
            self._printer.setFullPage(True)
            #self.translate(-15, -15)
        self._printer.setDocName(self.ganttWidget.ganttModel.name)
        return self._printer

    def createPreviewDialog(self, printer):
        return MyPrintPreviewDialog(self.ganttWidget, printer)

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
        print("self._pageInfo:", self._pageInfo)

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
        print("settings.columnWidth", settings.columnWidth)
        obj.log.headerWidth = settings.getHeaderWidth()
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
        print("paintRect:", painter.device().pageRect(), painter.device().paperRect())
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
