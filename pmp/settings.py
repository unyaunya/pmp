#! python3
# -*- coding: utf-8 -*-

import json, codecs
from datetime import date, datetime
from qtutil import Namespace, Property
from .serialize import to_json, from_json

class Settings(Namespace):
    KEY2IDX = ['name', 'start', 'end', 'pic', 'pv', 'ev', 'chart']

    def applyTo(self, ganttWidget):
        ganttWidget.dateOfProgressLine = self.misc.DATE_OF_PROGRESS_LINE
        print("settings.column.start.visible", settings.column.start.visible)
        self._columnResize(ganttWidget, COLUMN_START)
        self._columnResize(ganttWidget, COLUMN_END)
        self._columnResize(ganttWidget, COLUMN_PIC)
        self._columnResize(ganttWidget, COLUMN_PV)
        self._columnResize(ganttWidget, COLUMN_EV)

    def _columnIndexFromKey(self, key):
        for i in len(self.KEY2IDX):
            if key == self.KEY2IDX[i]:
                return i
        return -1

    def _keyFromColumnIndex(self, columnIndex):
        return self.KEY2IDX[columnIndex]

    def _columnResize(self, ganttWidget, columnIndex):
        obj = settings.column[self.KEY2IDX[columnIndex]]
        ganttWidget.header().resizeSection(columnIndex, obj.width)
        ganttWidget.setColumnHidden(columnIndex, not obj.visible)

    @staticmethod
    def dump(obj, path):
        with codecs.open(path, 'w', 'utf8') as f:
            return
            json.dump(obj, f, indent=2, default=to_json, ensure_ascii=False)

    @staticmethod
    def load(path):
        with open(path, mode='r', encoding='utf-8') as f:
            return json.load(f, object_hook=from_json)


settings = Settings()

#-------------------------------------------------------------------------------
#全般／共通項目
#-------------------------------------------------------------------------------
DEBUG=True
APPLICATION_NAME = "PMP(Poor Man's ms-Projcect)"

#-------------------------------------------------------------------------------
#データ部(画面左側)の表示諸元
#-------------------------------------------------------------------------------
HEADER_LABELS = ["項目名","開始日","終了日","担当者", "PV", "EV", ""]

COLUMN_NAME     = 0
COLUMN_START    = 1
COLUMN_END      = 2
COLUMN_PIC      = 3
COLUMN_PV       = 4
COLUMN_EV       = 5
COLUMN_CHART    = 6


#-------------------------------------------------------------------------------
#ヘッダ部(画面右上、カレンダ)の表示諸元
#-------------------------------------------------------------------------------

HEADER_HEIGHT   = 60

#カレンダ部のY座標を示す添字
CALENDAR = Namespace()
CALENDAR.YEAR   = 0
CALENDAR.MONTH  = 1
CALENDAR.WEEK   = 2
CALENDAR.DAY    = 3
CALENDAR.BOTTOM = 4

#1日の表示幅
TIMESCALE_DAY = Namespace()
TIMESCALE_DAY.WIDTH = 24.0
TIMESCALE_DAY.YEAR = True
TIMESCALE_DAY.MONTH = True
TIMESCALE_DAY.WEEK = False
TIMESCALE_DAY.DAY = True
TIMESCALE_DAY.CHART = CALENDAR.DAY

TIMESCALE_WEEK = Namespace()
TIMESCALE_WEEK.WIDTH = 8.0
TIMESCALE_WEEK.YEAR = True
TIMESCALE_WEEK.MONTH = True
TIMESCALE_WEEK.WEEK = True
TIMESCALE_WEEK.DAY = False
TIMESCALE_WEEK.CHART = CALENDAR.WEEK

TIMESCALE_MONTH = Namespace()
TIMESCALE_MONTH.WIDTH = 3.0
TIMESCALE_MONTH.YEAR = True
TIMESCALE_MONTH.MONTH = True
TIMESCALE_MONTH.WEEK = True
TIMESCALE_MONTH.DAY = False
TIMESCALE_MONTH.CHART = CALENDAR.WEEK

#ヘッダ部のテキスト描画の際のマージン
CALENDAR_BOTTOM_MARGIN = 3
CALENDAR_LEFT_MARGIN = 0 #未使用。一律センタリング


#-------------------------------------------------------------------------------
#チャート部(画面右下)の表示諸元
#-------------------------------------------------------------------------------

#ガントチャートの行高さ
ROW_HEIGHT = 20

#ガントチャートの線1本の高さ(行高さではない)
CHART_HEIGHT = 10

#ガントチャート内の進捗率の線1本の高さ
PROGRESST_HEIGHT = 6

CHART_BOUNDARY_COLOR    = (128,128,128,128) #チャート枠線色
CHART_COLOR             = ( 64,128,128,255) #チャート塗潰し色
PROGRESS_COLOR          = (160, 64, 64,255) #チャート内の進捗率塗潰し色
AGGREGATED_TASK_COLOR   = ( 64,128,255,255) #チャート塗潰し色
PROGRESS_LINE_COLOR     = (255,  0,  0,255) #イナズマ線色

#-------------------------------------------------------------------------------
#列幅
#-------------------------------------------------------------------------------
settings.columnWidth     = [360, 80, 80, 0, 40, 40, 600]

#-------------------------------------------------------------------------------
#列:幅、表示/非表示
#-------------------------------------------------------------------------------
settings.column.start.visible   = True
settings.column.start.width     = 80
settings.column.end.visible     = True
settings.column.end.width       = 80
settings.column.pic.visible     = True
settings.column.pic.width       = 80
settings.column.pv.visible      = True
settings.column.pv.width        = 40
settings.column.ev.visible      = True
settings.column.ev.width        = 40

#-------------------------------------------------------------------------------
#印刷諸元
#-------------------------------------------------------------------------------
settings.print.HORIZONTAL_PAGE_COUNT    = 1     #横のページ数
settings.print.ROWS_PER_PAGE            = 70    #1ページあたりの行数
settings.print.HEADER_HEIGHT_RATIO      = 0.10  #ヘッダ高さの割合(=ヘッダ高さ/ページ高さ)
settings.print.HEADER_WIDTH_RATIO       = 0.25  #ヘッダ幅の割合(=ヘッダ幅/ページ高さ)

#-------------------------------------------------------------------------------
#その他の諸元
#-------------------------------------------------------------------------------

dlgSpecs = [
    #'だみよ',
    #Property('1ページあたりの行数', int, 'print.ROWS_PER_PAGE', 63),
    ['印刷',
        Property('ヘッダ幅の割合', float, 'print.HEADER_WIDTH_RATIO', 0.25),
        Property('ヘッダ高さの割合', float, 'print.HEADER_HEIGHT_RATIO', 0.10),
        Property('1ページあたりの行数', int, 'print.ROWS_PER_PAGE', 70),
        Property('横のページ数', int, 'print.HORIZONTAL_PAGE_COUNT', 1),
    ],
    ['列表示/非表示',
        #"開始日","終了日","担当者", "PV", "EV"
        Property('開始日', bool, 'column.start.visible',True),
        Property('終了日', bool, 'column.end.visible',  True),
        Property('担当者', bool, 'column.pic.visible',  True),
        Property('PV',     bool, 'column.pv.visible',   True),
        Property('EV',     bool, 'column.ev.visible',   True),
    ],
    #['列幅',
    #    #"項目名","開始日","終了日","担当者", "PV", "EV"
    #    Property('項目名', int, 'width.NAME', 200),
    #    Property('開始日', int, 'width.START',80),
    #    Property('終了日', int, 'width.END',  80),
    #    Property('担当者', int, 'width.PIC',  0),
    #    Property('PV',     int, 'width.PV',   40),
    #    Property('EV',     int, 'width.EV',   40),
    #],
    ['その他',
        Property('イナズマ線の日付', date, 'misc.DATE_OF_PROGRESS_LINE', date.today()),
    ]
]
