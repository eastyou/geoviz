"""时间解析、时区换算与表格对齐。"""

from __future__ import annotations

import unicodedata
from datetime import datetime, timedelta
from typing import List

from .zones import City, GeoError

WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")

_FORMATS = (
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d",
)


def parse_moment(text: str) -> datetime:
    """解析「2026-11-21 12:00」这类本地时间，不带时区信息。"""
    value = text.strip().replace("：", ":")
    if not value:
        raise GeoError("时间不能为空（示例：2026-11-21 12:00）")
    for fmt in _FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise GeoError(
        "时间格式不正确: %s（示例：2026-11-21 12:00 或 2026-11-21）" % text.strip()
    )


def convert(moment: datetime, source: City, target: City) -> datetime:
    """把 source 的本地时间换算成 target 的本地时间。"""
    utc = moment - timedelta(minutes=source.offset)
    return utc + timedelta(minutes=target.offset)


def format_moment(moment: datetime) -> str:
    """格式化成「2026-11-21 20:00 周六」。"""
    return "%s %s" % (
        moment.strftime("%Y-%m-%d %H:%M"),
        WEEKDAYS[moment.weekday()],
    )


def format_date(moment: datetime) -> str:
    return moment.strftime("%m-%d")


def describe_difference(source: City, target: City) -> str:
    """描述目标城市相对参考城市的时差。"""
    difference = target.offset - source.offset
    if difference == 0:
        return "同时"
    sign = "快" if difference > 0 else "慢"
    absolute = abs(difference)
    hours = absolute // 60
    minutes = absolute % 60
    if minutes:
        return "%s %d 小时 %d 分" % (sign, hours, minutes)
    return "%s %d 小时" % (sign, hours)


def display_width(text: str) -> int:
    """按终端显示宽度计数，中文算 2 列。"""
    width = 0
    for char in text:
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def pad_display(text: str, width: int) -> str:
    """按显示宽度右侧补空格，超宽时原样返回。"""
    padding = width - display_width(text)
    if padding <= 0:
        return text
    return text + " " * padding


def format_table(rows: List[List[str]], headers: List[str]) -> str:
    """把二维文本按显示宽度对齐成表格。"""
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], display_width(cell))
    lines = ["  ".join(pad_display(header, widths[index]) for index, header in enumerate(headers))]
    lines.append("  ".join("-" * width for width in widths))
    for row in rows:
        lines.append(
            "  ".join(pad_display(cell, widths[index]) for index, cell in enumerate(row))
        )
    return "\n".join(lines)
