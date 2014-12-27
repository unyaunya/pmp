#! python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt

DATE_FORMART = '%Y/%m/%d'

def s2dt(obj):
    """objをdatetime型に変換する"""
    if obj is None:
        return None
    if isinstance(obj, str):
        return dt.strptime(obj, DATE_FORMART)
    else:
        return obj


def dt2s(obj):
    """datetime型を文字列に変換する"""
    if obj is None:
        return ''
    if isinstance(obj, str):
        return obj
    else:
        return obj.strftime(DATE_FORMART)

