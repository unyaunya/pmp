#! python3
# -*- coding: utf-8 -*-

import os, sys

from datetime import datetime as dt, timedelta
from uuid import UUID
from urllib.parse import urlparse
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QModelIndex, QPoint, QRect
from PyQt4.QtGui import QBrush, QPen, QColor, QFontMetrics, QFileDialog
from .util import s2dt, dt2s
from .settings import *
from .model import Task, TaskModel
from .config import config
from .treewidgetitem import TreeWidgetItem
from qtutil import tuple2color, tuple2brush, to_datetime

_ONEDAY = timedelta(days=1)

class CalendarDrawingInfo():
    def __init__(self):
        if False:
            self._dayWidth = TIMESCALE_DAY.WIDTH
            self.year = True
            self.month = True
            self.week = False
            self.day = True
            self.chart = CALENDAR.DAY
        self.setTimescale(TIMESCALE_MONTH)

    def setTimescale(self, timescale):
        self._dayWidth = timescale.WIDTH
        self.year = timescale.YEAR
        self.month = timescale.MONTH
        self.week = timescale.WEEK
        self.day = timescale.DAY
        self.chart = timescale.CHART

    def rowCount(self):
        n = 0
        if self.year: n += 1
        if self.month: n += 1
        if self.week: n += 1
        if self.day: n += 1
        return n

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

        rowCount = self.rowCount()
        dh = float(rect.height())/self.rowCount()
        self.ys = []
        for i in range(rowCount):
            self.ys.append(dh * i)
        self.ys.append(rect.bottom())
        #----
        xs_ = rect.left()
        xe_ = rect.right()
        #----
        date = start
        self.xs = [[rect.left()], [rect.left()], [rect.left()], [rect.left()]]
        self.ts = [[str(date.year)+"年"], [str(date.month)+"月"], [''], [str(date.day)]]
        self.bs = [ [boundingRect(self.ts[CALENDAR.YEAR][0])],
                    [boundingRect(self.ts[CALENDAR.MONTH][0])],
                    [boundingRect(self.ts[CALENDAR.DAY][0])],
                    [boundingRect(self.ts[CALENDAR.DAY][0])]]
        x = xs_
        pdate = date
        prev_week = date
        x += self.dayWidth
        #while date <= end:
        while x <= xe_:
            date += _ONEDAY
            #-----------------------
            if pdate.day != date.day:
                text = str(date.day)
                self.xs[CALENDAR.DAY].append(x)
                self.ts[CALENDAR.DAY].append(text)
                self.bs[CALENDAR.DAY].append(boundingRect(text))
            if date.weekday() == 0:
                text = str(date.day)
                self.xs[CALENDAR.WEEK].append(x)
                self.ts[CALENDAR.WEEK].append(text)
                self.bs[CALENDAR.WEEK].append(boundingRect(text))
            if pdate.month != date.month:
                text = str(date.month)+"月"
                self.xs[CALENDAR.MONTH].append(x)
                self.ts[CALENDAR.MONTH].append(text)
                self.bs[CALENDAR.MONTH].append(boundingRect(text))
            if pdate.year != date.year:
                text = str(date.year)+"年"
                self.xs[CALENDAR.YEAR].append(x)
                self.ts[CALENDAR.YEAR].append(text)
                self.bs[CALENDAR.YEAR].append(boundingRect(text))
            #-----------------------
            x += self.dayWidth
            pdate = date
        else:
            self.ys.append(dh * i)
            self.xs[CALENDAR.YEAR].append(x)
            self.xs[CALENDAR.MONTH].append(x)
            self.xs[CALENDAR.WEEK].append(x)
            self.xs[CALENDAR.DAY].append(x)

    @property
    def dayWidth(self):
        return self._dayWidth

    @dayWidth.setter
    def dayWidth(self, value):
        self._dayWidth = value

    def drawHeader(self, painter, rect, pen4line, pen4text):
        painter.setPen(pen4line)
        self.drawCalendarHorizontalLine_(painter, rect)
        row = 0
        if self.year:
            index = CALENDAR.YEAR
            self.drawCalendarVerticalLine_(painter, index, self.ys[row], self.ys[row+1]-1, pen4line, pen4text)
            row += 1
        if self.month:
            index = CALENDAR.MONTH
            self.drawCalendarVerticalLine_(painter, index, self.ys[row], self.ys[row+1]-1, pen4line, pen4text)
            row += 1
        if self.week:
            index = CALENDAR.WEEK
            self.drawCalendarVerticalLine_(painter, index, self.ys[row], self.ys[row+1]-1, pen4line, pen4text)
            row += 1
        if self.day:
            index = CALENDAR.DAY
            self.drawCalendarVerticalLine_(painter, index, self.ys[row], self.ys[row+1]-1, pen4line, pen4text)
            row += 1

    def drawCalendarHorizontalLine_(self, painter, rect):
        xs_ = rect.left()
        xe_ = rect.right()
        for i in range(1, self.rowCount()):
            painter.drawLine(xs_, self.ys[i], xe_, self.ys[i])

    def drawCalendarVerticalLine_(self, painter, i, top, bottom, pen4line, pen4text = None):
        yhigh = top
        ylow  = bottom
        ytext = ylow-CALENDAR_BOTTOM_MARGIN
        for j in range(len(self.ts[i])):
            xpos = self.xs[i][j]
            painter.setPen(pen4line)
            painter.drawLine(xpos, yhigh, xpos, ylow)
            #xpos += CALENDAR_LEFT_MARGIN
            xpos = (self.xs[i][j]+self.xs[i][j+1]-self.bs[i][j].width())/2
            if pen4text is not None:
                painter.setPen(pen4text)
                painter.drawText(xpos, ytext, self.ts[i][j])

    def drawItemBackground(self, painter, top, bottom, pen4line):
        self.drawCalendarVerticalLine_(painter, self.chart, top, bottom, pen4line)


class GanttHeaderView(QtGui.QHeaderView):
    def __init__(self, ganttWidget):
        super(GanttHeaderView, self).__init__ (Qt.Horizontal, ganttWidget)
        self.ganttWidget = ganttWidget
        color = QColor(Qt.lightGray)
        color.setAlpha(128)
        self.pen4line = QPen(color)
        self.pen4text = QPen(Qt.darkGray)
        self.sectionResized.connect(self._adjustSectionSize)
        self.cdi = CalendarDrawingInfo()

    def resizeEvent(self, event):
        super(GanttHeaderView, self).resizeEvent(event)
        self._adjustSectionSize()

    def _adjustSectionSize(self):
        self.ganttWidget.getChartScrollBar().adjustSectionSize()

    def sizeHint(self):
        sh = super(GanttHeaderView, self).sizeHint()
        sh.setHeight(HEADER_HEIGHT)
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
        self.cdi.prepare(painter, rect, self.ganttWidget.ganttModel.start, self.ganttWidget.ganttModel.end + _ONEDAY)
        self.cdi.drawHeader(painter, rect, self.pen4line, self.pen4text)
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
        value = self.ganttWidget.preferableWidth() - self.ganttWidget.header().sectionSize(COLUMN_CHART)
        self.setMaximum(max(0, value))
        #print("_adjustScrollBar(%d -> %d)" % (value, self.maximum()))

    def adjustScrollPosition(self):
        self.ganttWidget.header().headerDataChanged(Qt.Horizontal, COLUMN_CHART, COLUMN_CHART)
        self.ganttWidget.headerItem().emitDataChanged()


class Widget_(QtGui.QTreeWidget):
    def __init__(self, model = TaskModel()):
        super(Widget_, self).__init__()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._csb = ChartScrollBar(self)
        self.setHeader(GanttHeaderView(self))
        self.ganttModel = model
        self.cdi = CalendarDrawingInfo()
        self.setHeaderLabels(HEADER_LABELS)
        self._dateOfProgressLine = dt.today()
        settings.applyTo(self)
        self.header().sectionResized.connect(self._recordSectionSize)

    def _recordSectionSize(self, column, oldSize, newSize):
        obj = settings.getColumn(column)
        if oldSize > 0 and newSize == 0:
            obj.visible = False
        else:
            obj.visible = True
            obj.width = newSize

    @property
    def ganttModel(self):
        return self._ganttModel

    @ganttModel.setter
    def ganttModel(self, model):
        if model is None:
            return
        self._ganttModel = model
        self.clear()
        items = TreeWidgetItem.Items(model.children)
        self.addTopLevelItems(items)
        self._sync_expand_collapse(items)

    @property
    def dateOfProgressLine(self):
        return self._dateOfProgressLine

    @dateOfProgressLine.setter
    def dateOfProgressLine(self, value):
        if not isinstance(value, (date, datetime)):
            return
        self._dateOfProgressLine = to_datetime(value)
        self.refresh()

    def _sync_expand_collapse(self, items):
        for item in items:
            self._sync_expand_collapse(item.childItems())
            if item.task.expanded:
                self.expandItem(item)
            else:
                self.collapseItem(item)

    def preferableWidth(self):
        if self.ganttModel is None:
            return 0
        return self.xpos(self.ganttModel.end, _ONEDAY)

    def xpos(self, dt, offset=None):
        dt = to_datetime(dt)
        if offset is not None:
            dt += offset
        tdelta = dt - self.ganttModel.start
        return tdelta.days * self.cdi.dayWidth

    def paintEvent(self, e):
        rect = e.rect()
        #print("paintEvnt", rect)
        rect.setLeft(self.columnViewportPosition(COLUMN_CHART))
        rect.setRight(rect.right() + self.getChartScrollBar().value())
        self.cdi.prepare(None, rect, self.ganttModel.start, self.ganttModel.end + _ONEDAY)
        self.xposOfToday = self.xpos(self.dateOfProgressLine)
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
        #----
        item = self.itemFromIndex(index)
        self.drawChart(painter, item, self._chartRect(item, itemRect))
        #----
        self.drawProgressLine(painter, item, itemRect)
        #----
        painter.restore()

    def drawProgressLine(self, painter, item, itemRect):
        # x <-- イナズマ線のx座標
        x = self.columnViewportPosition(COLUMN_CHART) + self.xposOfToday
        progressRate = item.progressRate
        #xposOfItem <-- 当該アイテムの進捗を示すｘ座標
        xposOfItem = self._currentPosOfItem(item)

        #遅れていない未着手タスク
        if self.dateOfProgressLine < s2dt(item.start) and progressRate == 0.0:
            xposOfItem = x
        #過去の完了タスク
        elif self.dateOfProgressLine > s2dt(item.end) and progressRate == 1.0:
            xposOfItem = x

        painter.setPen(self.pen4progressLine)
        y1 = itemRect.top()
        y3 = itemRect.bottom()
        if x == xposOfItem:
            painter.drawLine(x, y1, x, y3)
        else:
            y2 = (y1+y3)/2
            painter.drawLine(x, y1, xposOfItem, y2)
            painter.drawLine(xposOfItem, y2, x, y3)

    def _chartRect(self, item, rect):
        """taskを描画する矩形の座標を算出する"""
        y = (rect.top()+rect.bottom())/2
        x0 = self.columnViewportPosition(COLUMN_CHART)
        x1 = x0 + self.xpos(item.start)
        x2 = x0 + self.xpos(item.end, _ONEDAY)
        #print(x1, x2)
        return QRect(x1, y-CHART_HEIGHT/2, x2-x1, CHART_HEIGHT)

    def _currentPosOfItem(self, item):
        """指定されたitemの進捗を示すx座標を算出する"""
        x0 = self.columnViewportPosition(COLUMN_CHART)
        x1 = self.xpos(item.start)
        x2 = self.xpos(item.end, _ONEDAY)
        pr = item.progressRate
        return x0 + x1 * (1-pr) + x2 * pr

    def drawChart(self, painter, item, chartRect):
        task = item.task
        if task is None:
            return
        painter.fillRect(chartRect,
            self.brush4aggregatedTask if item.isAggregated()
            else self.brush4chartFill)
        painter.setPen(self.pen4chartBoundary)
        painter.drawRect(chartRect)
        #--進捗率の表示--
        if item.pv > 0:
            progressRect = QRect(
                chartRect.left(),
                chartRect.top()+(chartRect.height()-PROGRESST_HEIGHT)/2,
                chartRect.width() * item.progressRate,
                PROGRESST_HEIGHT)
            painter.fillRect(progressRect, self.brush4chartFillProgress)
            painter.drawRect(progressRect)

    def drawItemBackground(self, painter, itemRect):
        #this methhod is called outside paintEvent in MacOS X
        if self.cdi is not None:
            self.cdi.drawItemBackground(painter,
                    itemRect.top(), itemRect.bottom(), self.pen4chartBoundary)

    def getChartScrollBar(self):
        """チャート部用のスクロールバーを取得する"""
        return self._csb

    def setDayWidth(self, value):
        if value < 0:
            return
        self.cdi.dayWidth = value
        self.header().cdi.dayWidth = value
        self.getChartScrollBar().adjustScrollPosition()

    def refresh(self):
        self.getChartScrollBar().adjustScrollPosition()


class GanttWidget(Widget_):
    #-----------------------------------------------------------------------
    # Qtシグナル
    #-----------------------------------------------------------------------
    currentFileChanged = QtCore.pyqtSignal(str)

    #-----------------------------------------------------------------------
    # コンストラクタ
    #-----------------------------------------------------------------------
    def __init__(self, model = None):
        super(GanttWidget, self).__init__()
        #-----------------------------------------------------------------------
        self.dateEditDelegate = DateEditDelegate(self)
        self.setItemDelegateForColumn(COLUMN_START, self.dateEditDelegate)
        self.setItemDelegateForColumn(COLUMN_END, self.dateEditDelegate)
        #-----------------------------------------------------------------------
        self._currentFileName = None
        self._path = None
        self._workingDirectory = None
        #-----------------------------------------------------------------------
        self.itemCollapsed.connect(self.taskCollapsed)
        self.itemExpanded.connect(self.taskExpanded)

    #-----------------------------------------------------------------------
    # その他
    #-----------------------------------------------------------------------
    @property
    def path(self):
        return self._path

    @property
    def workingDirectory(self):
        if self._path is None:
            self._path = os.getcwd()
        return self._path

    @property
    def currentFileName(self):
        return self._currentFileName

    def load(self, url):
        try:
            obj = urlparse(url)
            if obj.netloc == '':
                self._workingDirectory = os.path.dirname(obj.path)
            self.ganttModel = TaskModel.load(url)
            config.addLastUsed(url)
            self._currentFileName = url
            self.currentFileChanged.emit(self._currentFileName)
        except :
            print("Unexpected error:", sys.exc_info())
            QtGui.QMessageBox.warning(self,
                "がんと", "<%s>を開けませんでした" % url, "OK")
            if DEBUG:
                raise
                #pass

    def saveFile(self, url):
        try:
            print("save %s" % url)
            obj = urlparse(url)
            if obj.netloc == '':
                self._workingDirectory = os.path.dirname(obj.path)
            TaskModel.dump(self.ganttModel, url)
            self.load(url)
            #self._currentFileName = fileName
            #self.currentFileChanged.emit(self._currentFileName)
        except:
            if DEBUG:
                raise
            else:
                print("Unexpected error:", sys.exc_info())
                QtGui.QMessageBox.warning(self,
                    "がんと", "<%s>を開けませんでした" % url, "OK")

    def itemFromUuid(self, uuid):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            found = item.findFromUuid(uuid)
            if found is not None:
                return found
        return None

    def insertAfter(self, item, newItem):
        (ci, index, parent, parentTask) = self._get_item_info(item)
        if parentTask == self.ganttModel:
            parent.insertChild(index+1, newItem)
        else:
            parent.insertChild(index+1, newItem)
        parentTask.children.insert(index+1, newItem.task)

    #---------------------------------------------------------------------------
    #   アクション
    #---------------------------------------------------------------------------
    def insert(self, action):
        """カレントアイテムの次に新規タスクを挿入する"""
        self.insertAfter(None, TreeWidgetItem(Task.defaultTask()))

    def remove(self, action):
        """カレントアイテムを削除する"""
        (ci, index, parent, parentTask) = self._get_item_info()
        if ci is None:
            return
        parentTask.children.remove(ci.task)
        parent.removeChild(ci)

    def _get_item_info(self, ci = None):
        if ci is None:
            ci = self.currentItem()
        if ci is None:
            parent = self.invisibleRootItem()
            parentTask = self.ganttModel
            index = -1
        elif self._isToplevel(ci):
            parent = self.invisibleRootItem()
            parentTask = self.ganttModel
            index = parent.indexOfChild(ci)
        else:
            parent = ci.parent()
            parentTask = parent.task
            index = parent.indexOfChild(ci)
        return (ci, index, parent, parentTask)

    def _isToplevel(self, item):
        if item.parent() is None:
            return True
        if self.indexFromItem(item.parent(), 0).isValid():
            return False
        return True

    def levelUp(self, action):
        (ci, index, parent, parentTask) = self._get_item_info()
        if ci is None:
            return
        if self._isToplevel(ci):
            #トップレベルにいるなら、レベルを上げようがない
            return
        #親アイテムから離脱する
        parentTask.children.remove(ci.task)
        parent.removeChild(ci)
        #親アイテムの直近の弟になる。
        (parent, parent_index, granpa, granpaTask) = self._get_item_info(parent)
        granpa.insertChild(parent_index+1, ci)
        granpaTask.children.insert(parent_index+1, ci.task)
        self._sync_expand_collapse([ci])
        #対象タスクをカレントタスクにする
        self.setCurrentItem(ci)

    def levelDown(self, action):
        (ci, index, parent, parentTask) = self._get_item_info()
        if ci is None:
            return
        modelIndex = self.indexFromItem(ci, 0)
        if modelIndex.row() <= 0:
            #兄アイテムがいない場合は処理を行わない
            return
        #年の近い兄アイテムを探しておく
        sibling = self.itemFromIndex(modelIndex.sibling(modelIndex.row()-1, 0))
        #親アイテムから離脱する
        parentTask.children.remove(ci.task)
        parent.removeChild(ci)
        #年の近い兄アイテムの末子になる
        sibling.addChild(ci)
        sibling.task.children.append(ci.task)
        self._sync_expand_collapse([ci])
        #対象タスクをカレントタスクにする
        self.setCurrentItem(ci)

    def up(self, action):
        """同一レベル内で一つ上に移動する"""
        (ci, index, parent, parentTask) = self._get_item_info()
        if ci is None:
            return
        newIndex = index - 1
        if newIndex < 0:
            #すでに一番上にいるなら処理を行わない
            return
        #一つ上の位置に挿入する
        self._move(ci, newIndex, parent, parentTask)

    def down(self, action):
        """同一レベル内で一つ下に移動する"""
        (ci, index, parent, parentTask) = self._get_item_info()
        if ci is None:
            return
        newIndex = index + 1
        if parent.childCount() <= newIndex:
            #すでに一番下にいるなら処理を行わない
            return
        #一つ下の位置に挿入する
        self._move(ci, newIndex, parent, parentTask)

    def _move(self, ci, newIndex, parent, parentTask):
        #一旦、親アイテムから離脱する
        parentTask.children.remove(ci.task)
        parent.removeChild(ci)
        #新しい位置に挿入する
        parent.insertChild(newIndex, ci)
        parentTask.children.insert(newIndex, ci.task)
        self._sync_expand_collapse([ci])
        #対象タスクをカレントタスクにする
        self.setCurrentItem(ci)

    def open(self, action):
        """ファイルを開く"""
        fileName = QFileDialog.getOpenFileName(self,
                        'ファイルを開く', self.workingDirectory)
        print("load %s" % fileName)
        if len(fileName) <= 0:
            return
        self.load(fileName)

    def openServer(self, action):
        """ファイルを開く"""
        print(settings.misc.server_url)
        self.load(settings.misc.server_url)

    def save(self, action):
        """ファイルを保存する"""
        if self._currentFileName is None:
            self.saveAs(action)
        else:
            self.saveFile(self._currentFileName)

    def saveAs(self, action):
        """ファイル名を指定して保存する"""
        fileName = QFileDialog.getSaveFileName(self,
                        'ファイルを保存する', self.workingDirectory)
        print(fileName)
        if len(fileName) <= 0:
            return
        self.saveFile(fileName)

    def timescaleDay(self, action):
        self._timescale(TIMESCALE_DAY)

    def timescaleWeek(self, action):
        self._timescale(TIMESCALE_WEEK)

    def timescaleMonth(self, action):
        self._timescale(TIMESCALE_MONTH)

    def _timescale(self, timescale):
        self.setDayWidth(timescale.WIDTH)
        self.header().cdi.year = timescale.YEAR
        self.header().cdi.month = timescale.MONTH
        self.header().cdi.week = timescale.WEEK
        self.header().cdi.day = timescale.DAY
        self.cdi.chart = timescale.CHART
        self.getChartScrollBar()._adjustScrollBar()
        self.getChartScrollBar().adjustScrollPosition()

    def copy(self):
        clipboard = QtGui.QApplication.clipboard()
        ci = self.currentItem()
        if ci is None:
            return
        clipboard.setText(str(ci.uuid))

    def cut(self):
        """未実装"""
        pass

    def paste(self):
        ci = self.currentItem()
        if ci is None:
            return
        clipboard = QtGui.QApplication.clipboard()
        uuid = clipboard.text()
        item = self.itemFromUuid(UUID(uuid))
        if item is None:
            return
        self.insertAfter(ci, item.clone())

    #---------------------------------------------------------------------------
    def taskExpanded(self, item):
        item.task.expanded = True

    def taskCollapsed(self, item):
        item.task.expanded = False

class DateEditDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        self.treeWidget = parent
        super(DateEditDelegate, self).__init__(parent)

    def _createEditor(self, aDate, parent):
        editor = QtGui.QDateEdit(aDate, parent)
        editor.setCalendarPopup(True)
        return editor

    def createEditor(self, parent, option, modelIndex):
        column = modelIndex.column()
        item = self.treeWidget.itemFromIndex(modelIndex)
        if column == COLUMN_START:
            print('COLUMN_START', item.task.start)
            return self._createEditor(item.task.start, parent)
        elif column == COLUMN_END:
            print('COLUMN_END', item.task.end)
            return self._createEditor(item.task.end, parent)
        else:
            return super(DateEditDelegate, self).createEditor(parent, option, modelIndex)

