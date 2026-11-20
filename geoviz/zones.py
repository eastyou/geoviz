"""城市与固定时区偏移。

初中地理讲时区时用的是「标准时间」，不涉及时区数据库和夏令时。
这里刻意只维护固定偏移，保证任何平台、任何年份的结果都一致。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


class GeoError(ValueError):
    """城市、时间或参数不合法。"""


_CHINESE_NUMBERS = (
    "零",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "十一",
    "十二",
    "十三",
    "十四",
)


@dataclass(frozen=True)
class City:
    """一个城市及其标准时区偏移（分钟）。"""

    name: str
    offset: int
    aliases: Tuple[str, ...] = ()
    dst: bool = False

    @property
    def offset_label(self) -> str:
        return format_offset(self.offset)

    @property
    def zone_label(self) -> str:
        if self.offset % 60 == 0:
            hours = self.offset // 60
            if hours == 0:
                return "零时区"
            number = (
                _CHINESE_NUMBERS[abs(hours)]
                if abs(hours) < len(_CHINESE_NUMBERS)
                else str(abs(hours))
            )
            if hours > 0:
                return "东%s区" % number
            return "西%s区" % number
        return self.offset_label


CITIES: Tuple[City, ...] = (
    City("北京", 480, ("beijing", "pek", "中国")),
    City("上海", 480, ("shanghai",)),
    City("东京", 540, ("tokyo", "日本")),
    City("首尔", 540, ("seoul", "韩国")),
    City("新加坡", 480, ("singapore",)),
    City("曼谷", 420, ("bangkok",)),
    City("新德里", 330, ("newdelhi", "delhi", "印度")),
    City("迪拜", 240, ("dubai",)),
    City("莫斯科", 180, ("moscow", "俄罗斯")),
    City("开罗", 120, ("cairo",), dst=True),
    City("雅典", 120, ("athens",), dst=True),
    City("巴黎", 60, ("paris", "法国"), dst=True),
    City("伦敦", 0, ("london", "英国", "uk"), dst=True),
    City("里约热内卢", -180, ("rio", "riodejaneiro", "里约"), dst=False),
    City("圣保罗", -180, ("saopaulo",)),
    City("纽约", -300, ("newyork", "ny", "nyc", "美国"), dst=True),
    City("芝加哥", -360, ("chicago",), dst=True),
    City("丹佛", -420, ("denver",), dst=True),
    City("洛杉矶", -480, ("losangeles", "la"), dst=True),
    City("安克雷奇", -540, ("anchorage",), dst=True),
    City("檀香山", -600, ("honolulu", "夏威夷")),
    City("帕果帕果", -660, ("pagopago", "美属萨摩亚")),
    City("奥克兰", 720, ("auckland", "新西兰"), dst=True),
    City("悉尼", 600, ("sydney", "澳大利亚"), dst=True),
    City("基里巴斯", 840, ("kiribati", "莱恩群岛")),
)

DEFAULT_TARGETS: Tuple[str, ...] = (
    "伦敦",
    "纽约",
    "洛杉矶",
    "东京",
    "悉尼",
    "奥克兰",
)

DEFAULT_CITIES: Tuple[str, ...] = (
    "北京",
    "东京",
    "悉尼",
    "奥克兰",
    "新德里",
    "迪拜",
    "莫斯科",
    "巴黎",
    "伦敦",
    "纽约",
    "洛杉矶",
    "檀香山",
)


def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def _build_index() -> Dict[str, City]:
    index: Dict[str, City] = {}
    for city in CITIES:
        for alias in (city.name,) + city.aliases:
            index[_normalize(alias)] = city
    return index


_INDEX: Dict[str, City] = _build_index()

_KNOWN_NAMES = "、".join(city.name for city in CITIES)


def find_city(name: str) -> City:
    """按中文名、英文名或别名查找城市。"""
    key = _normalize(name)
    if not key:
        raise GeoError("城市名不能为空（可用：%s）" % _KNOWN_NAMES)
    city: Optional[City] = _INDEX.get(key)
    if city is None:
        raise GeoError("不认识的城市: %s（可用：%s）" % (name.strip(), _KNOWN_NAMES))
    return city


def format_offset(minutes: int) -> str:
    """把分钟偏移格式化成 ``UTC+08:00``。"""
    sign = "+" if minutes >= 0 else "-"
    absolute = abs(minutes)
    return "UTC%s%02d:%02d" % (sign, absolute // 60, absolute % 60)


__all__ = [
    "CITIES",
    "DEFAULT_CITIES",
    "DEFAULT_TARGETS",
    "City",
    "GeoError",
    "find_city",
    "format_offset",
]
