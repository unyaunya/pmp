#! python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt, timedelta
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QModelIndex, QPoint, QRect
from PyQt4.QtGui import QBrush, QPen, QColor, QFontMetrics
from .util import s2dt
from .settings import Settings

DAY_WIDTH = 16
COLUMN_NAME  = 0
COLUMN_CHART = 4
CALENDAR_BOTTOM_MARGIN = 3
CALENDAR_LEFT_MARGIN = 3
CHART_HEIGHT = 12
PROGRESST_HEIGHT = 8

CALENDAR_TOP    = 0
CALENDAR_YEAR   = 0
CALENDAR_MONTH  = 1
CALENDAR_DAY    = 2
CALENDAR_BOTTOM = 3

_ONEDAY = timedelta(days=1)

class CalendarDrawingInfo():
    def __init__(self):
        pass

    def prepare(self, painter, rect, start, end):
        if painter is None:
            zeroRect = QRect()
            def boundingRect(s):
                """指定された文字列の描画サイズを取得する"""
                return zeroRect
        else:
            fm = QFontMetrics(painter.font())
            def boundingRect(s):
                """指定された文字列の描画サイズを取得する"""
                return fm.boundingRect(s)

        self.ys = [0,0,0,0]
        self.ys[CALENDAR_TOP] = rect.top()
        dh = (rect.bottom() - self.ys[CALENDAR_TOP])/CALENDAR_BOTTOM
        self.ys[CALENDAR_MONTH] = self.ys[CALENDAR_YEAR] + dh
        self.ys[CALENDAR_DAY] = self.ys[CALENDAR_MONTH] + dh
        self.ys[CALENDAR_BOTTOM] = rect.bottom()
        #----
        xs_ = rect.left()
        xe_ = rect.right()
        #----
        date = start
        self.xs = [[rect.left()], [rect.left()], [rect.left()]]
        self.ts = [[str(date.year)], [str(date.month)], [str(date.day)]]
        self.bs = [[boundingRect(self.ts[0][0])], [boundingRect(self.ts[1][0])], [boundingRect(self.ts[2][0])]]
        x = xs_
        pdate = date
        x += DAY_WIDTH
        while date <= end:
            date += _ONEDAY
            #-----------------------
            if pdate.day != date.day:
                y = self.ys[2]
                text = str(date.day)
                self.xs[2].append(x)
                self.ts[2].append(text)
                self.bs[2].append(boundingRect(text))
            if pdate.month != date.month:
                y = self.ys[1]
                text = str(date.month)
                self.xs[1].append(x)
                self.ts[1].append(text)
                self.bs[1].append(boundingRect(text))
            if pdate.year != date.year:
                y = self.ys[0]
                text = str(date.year)
                self.xs[0].append(x)
                self.ts[0].append(text)
                self.bs[0].append(boundingRect(text))
            #-----------------------
            x += DAY_WIDTH
            pdate = date
        else:
            self.xs[0].append(x)
            self.xs[1].append(x)
            self.xs[2].append(x)

    def drawHeader(self, painter, rect, pen4line, pen4text):
        painter.setPen(pen4line)
        self.drawCalendarHorizontalLine_(painter, rect)
        for i in range(3):
            self.drawCalendarVerticalLine_(painter, i, self.ys[i], self.ys[i+1]-1, pen4text)

    def drawCalendarHorizontalLine_(self, painter, rect):
        xs_ = rect.left()
        xe_ = rect.right()
        painter.drawLine(xs_, self.ys[1], xe_, self.ys[1])
        painter.drawLine(xs_, self.ys[2], xe_, self.ys[2])

    def drawCalendarVerticalLine_(self, painter, i, top, bottom, pen4text = None):
        yhigh = top
        ylow  = bottom
        ytext = ylow-CALENDAR_BOTTOM_MARGIN
        for j in range(len(self.ts[i])):
            xpos = self.xs[i][j]
            painter.drawLine(xpos, yhigh, xpos, ylow)
            #xpos += CALENDAR_LEFT_MARGIN
            xpos = (self.xs[i][j]+self.xs[i][j+1]-self.bs[i][j].width())/2
            if pen4text is not None:
                painter.setPen(pen4text)
                painter.drawText(xpos, ytext, self.ts[i][j])

    def drawItemBackground(self, painter, top, bottom, pen4line):
        painter.setPen(pen4line)
        self.drawCalendarVerticalLine_(painter, CALENDAR_DAY, top, bottom)


class GanttHeaderView(QtGui.QHeaderView):
    def __init__(self, ganttWidget):
        super(GanttHeaderView, self).__init__ (Qt.Horizontal, ganttWidget)
        self.ganttWidget = ganttWidget
        color = QColor(Qt.lightGray)
        color.setAlpha(128)
        self.pen4line = QPen(color)
        self.pen4text = QPen(Qt.darkGray)
        self.sectionResized.connect(self._adjustSectionSize)

    def resizeEvent(self, event):
        super(GanttHeaderView, self).resizeEvent(event)
        self._adjustSectionSize()

    def _adjustSectionSize(self):
        self.ganttWidget.getChartScrollBar().adjustSectionSize()

    def sizeHint(self):
        sh = super(GanttHeaderView, self).sizeHint()
        sh.setHeight(sh.height()*2.4)
        return sh

    def paintSection(self, painter, rect, logicalIndex):
        super(GanttHeaderView, self).paintSection(painter, rect, logicalIndex)
        if logicalIndex != COLUMN_CHART:
            return
        painter.save()
        #print("paintSection", rect, logicalIndex)
        painter.setClipRect(rect)
        sv = self.ganttWidget.getChartScrollBar().value()
        painter.translate(-sv, 0)
        rect.setRight(rect.right() + sv)
        cdi = CalendarDrawingInfo()
        cdi.prepare(painter, rect, self.ganttWidget.ganttModel.start, self.ganttWidget.ganttModel.end + _ONEDAY)
        cdi.drawHeader(painter, rect, self.pen4line, self.pen4text)
        painter.restore()

class ChartScrollBar(QtGui.QScrollBar):
    """チャート部用のスクロールバーを作成する"""

    def __init__(self, ganttWidget):
        super(ChartScrollBar, self).__init__(Qt.Horizontal, ganttWidget)
        self.ganttWidget = ganttWidget
        self.valueChanged.connect(self.adjustScrollPosition)

    def adjustSectionSize(self):
        """チャート部を、Widgetの端まで広げる"""
        header = self.ganttWidget.header()
        if header is None:
            return
        width = header.width()
        for i in range(header.count()):
            if i != COLUMN_CHART:
                width -= header.sectionSize(i)
        if width >= 0:
            header.resizeSection(COLUMN_CHART, width)
        self._adjustScrollBar()

    def _adjustScrollBar(self):
        """スクロールバーの最大値を設定、必要あれば現在値も修正する"""
        self.setMaximum(self.ganttWidget.preferableWidth() - self.ganttWidget.header().sectionSize(COLUMN_CHART))

    def adjustScrollPosition(self, value):
        #print("adjustScrollPosition", value, self.updatesEnabled())
        #self.ganttWidget.paintEvent(QtGui.QPaintEvent(QRect(0,0,1004,639)))
        self.ganttWidget.header().headerDataChanged(Qt.Horizontal, COLUMN_CHART, COLUMN_CHART)
        self.ganttWidget.headerItem().emitDataChanged()



class Widget_(QtGui.QTreeWidget):
    def __init__(self, settings = Settings(), model = None):
        super(Widget_, self).__init__()
        self.settings = settings
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._csb = ChartScrollBar(self)
        self.setHeader(GanttHeaderView(self))
        self.ganttModel = model
        self.pen4chartBoundary = QPen(QColor(128,128,128,128))
        self.brush4chartFill = QBrush(QColor(0,64,64,128))
        self.brush4chartFillProgress = QBrush(QColor(255,0,0,128))
        self.cdi = None
        self.setHeaderLabels(["項目名","開始日","終了日","担当者", ""])

    @property
    def ganttModel(self):
        return self._ganttModel

    @ganttModel.setter
    def ganttModel(self, model):
        self._ganttModel = model
        if model is None:
            return
        self.addTopLevelItems(model.treeItems())
        #
        for i in range(self.topLevelItemCount()):
            self.expandItem(self.topLevelItem(i))

    def preferableWidth(self):
        if self.ganttModel is None:
            return 0
        return self.xpos(self.ganttModel.end+_ONEDAY)

    def xpos(self, dt):
        tdelta = dt - self.ganttModel.start
        return tdelta.days * DAY_WIDTH

    def paintEvent(self, e):
        rect = e.rect()
        #print("paintEvnt", rect)
        rect.setLeft(self.columnViewportPosition(COLUMN_CHART))
        self.cdi = CalendarDrawingInfo()
        self.cdi.prepare(None, rect, self.ganttModel.start, self.ganttModel.end + _ONEDAY)
        super(Widget_, self).paintEvent(e)

    def drawRow(self, painter, options, index):
        """ガントチャート1行を描画する"""
        super(Widget_, self).drawRow(painter, options, index)
        painter.save()
        #print(self.visualRect(index))
        itemRect = self.visualRect(index.sibling(index.row(), COLUMN_CHART))
        #itemRect = self.visualItemRect(item)
        #print("\tdrawRow:", itemRect)
        painter.setClipRect(itemRect)
        painter.translate(-self.getChartScrollBar().value(), 0)
        #----
        self.drawItemBackground(painter, itemRect)
        task = self.itemFromIndex(index).data(COLUMN_CHART, Qt.UserRole)
        if task is not None:
            self.drawChart(painter, task, self._chartRect(task, itemRect))
        #----
        painter.restore()

    def _chartRect(self, task, rect):
        """taskを描画する矩形の座標を算出する"""
        y = (rect.top()+rect.bottom())/2
        x0 = self.columnViewportPosition(COLUMN_CHART)
        x1 = x0 + self.xpos(task.start)
        x2 = x0 + self.xpos(task.end+_ONEDAY)
        #print(x1, x2)
        return QRect(x1, y-CHART_HEIGHT/2, x2-x1, CHART_HEIGHT)

    def drawChart(self, painter, task, chartRect):
        #painter.drawLine(x1, y, x2, y)
        painter.fillRect(chartRect, self.brush4chartFill)
        painter.setPen(self.pen4chartBoundary)
        painter.drawRect(chartRect)
        #--進捗率の表示--
        if task.pv > 0:
            progressRect = QRect(
                chartRect.left(),
                chartRect.top()+(chartRect.height()-PROGRESST_HEIGHT)/2,
                chartRect.width() * task.ev/task.pv,
                PROGRESST_HEIGHT)
            painter.fillRect(progressRect, self.brush4chartFillProgress)
            painter.drawRect(progressRect)

    def drawItemBackground(self, painter, itemRect):
        #this methhod is called outside paintEvent in MacOS X
        if self.cdi is not None:
            self.cdi.drawItemBackground(painter, itemRect.top(), itemRect.bottom(), self.pen4chartBoundary)

    def getChartScrollBar(self):
        """チャート部用のスクロールバーを取得する"""
        return self._csb

class GanttWidget(Widget_):
    def __init__(self, settings = Settings(), model = None):
        super(GanttWidget, self).__init__(settings)

    def insertAction(self):
        print("insert", self.currentItem())
        ci = self.currentItem()
        if ci is None:
            parent = self.invisibleRootItem()
            parent.addChild(QtGui.QTreeWidgetItem())
        else:
            parent = ci.parent()
            if parent is None:
                parent = self.invisibleRootItem()
            index = parent.indexOfChild(ci)
            parent.insertChild(index, self._createDefaultItem())

    def removeAction(self):
        print("remove", self.currentItem())
        ci = self.currentItem()
        parent = ci.parent()
        if parent is None:
            parent = self.invisibleRootItem()
        parent.removeChild(ci)

    def _createDefaultItem(self):
        ni = QtGui.QTreeWidgetItem()
        ni.setText(0, '(未定義)')
        ni.setText(1, '2014/12/01')
        ni.setText(2, '2014/12/31)')
        return ni
