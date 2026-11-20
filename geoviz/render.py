"""生成世界时区对照页面。"""

from __future__ import annotations

import html
from datetime import datetime, timedelta
from typing import List, Sequence

from .timecalc import WEEKDAYS, convert, describe_difference, format_moment
from .zones import City, GeoError

MAX_CITIES = 40

PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 22px 24px 28px;
    background: #f8fafc;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
  }
  header { margin-bottom: 16px; }
  h1 { font-size: 23px; margin: 0 0 6px; letter-spacing: 0.5px; }
  .sub { color: #475569; font-size: 13px; line-height: 1.8; }
  .sub b { color: #0f172a; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(255px, 1fr));
    gap: 12px;
  }
  .card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px 10px;
    break-inside: avoid;
  }
  .card.reference { border-color: #0ea5e9; box-shadow: 0 0 0 1px #0ea5e9 inset; }
  .card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
  .name { font-size: 15px; font-weight: 700; }
  .name em {
    font-style: normal;
    font-size: 10px;
    color: #0369a1;
    background: #e0f2fe;
    border-radius: 999px;
    padding: 1px 7px;
    margin-left: 4px;
    vertical-align: 1px;
  }
  .dst { color: #b45309; font-size: 11px; }
  .zone { color: #64748b; font-size: 11px; }
  .clock-row { display: flex; align-items: baseline; gap: 8px; margin: 6px 0 8px; }
  .clock {
    font-family: "SF Mono", "Menlo", "Consolas", monospace;
    font-size: 30px;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .date { color: #475569; font-size: 12px; }
  .band {
    position: relative;
    height: 30px;
    border-radius: 6px;
    overflow: hidden;
    background: linear-gradient(
      to right,
      #0f172a 0%, #0f172a 25%,
      #fef9c3 25%, #fef9c3 75%,
      #0f172a 75%, #0f172a 100%
    );
  }
  .band .tick { position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(15, 23, 42, 0.18); }
  .band .marker {
    position: absolute;
    top: -2px;
    bottom: -2px;
    width: 4px;
    border-radius: 2px;
    transform: translateX(-50%);
    background: #f59e0b;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.22);
  }
  .band .marker.night { background: #38bdf8; box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25); }
  .scale {
    display: flex;
    justify-content: space-between;
    color: #94a3b8;
    font-size: 9px;
    margin-top: 2px;
  }
  .meta { margin-top: 7px; font-size: 11px; color: #475569; display: flex; flex-wrap: wrap; gap: 6px; }
  .diff { color: #0f172a; font-weight: 600; }
  .crossday {
    color: #b91c1c;
    background: #fef2f2;
    border-radius: 4px;
    padding: 0 5px;
  }
  .note {
    margin-top: 16px;
    color: #64748b;
    font-size: 12px;
    line-height: 1.8;
    border-top: 1px dashed #cbd5e1;
    padding-top: 10px;
  }
  @page { size: A4 portrait; margin: 10mm; }
  @media print {
    body { background: #fff; padding: 0; }
    .card { break-inside: avoid; }
    .note { margin-top: 10px; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
  @media (max-width: 560px) {
    body { padding: 14px; }
    .grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub">
    参考时间：<b>__REFERENCE__</b> · __CITY__（__ZONE__）<br>
    同一时刻的 UTC 时间：__UTC__
  </div>
</header>
<div class="grid">
__CARDS__
</div>
<div class="note">
  时区按各城市的标准时间计算，未计入夏令时。带 <span class="dst">*</span> 的城市实行夏令时，
  夏令时期间当地时间需要再加 1 小时。日界线两侧日期可能不同，卡片中已标出「前一天 / 次日」。
</div>
</body>
</html>
"""

_CARD_TEMPLATE = """<article class="card__REFERENCE_CLASS__">
  <div class="card-head">
    <div class="name">__NAME____REFERENCE_BADGE____DST__</div>
    <div class="zone">__ZONE__ · __OFFSET__</div>
  </div>
  <div class="clock-row">
    <div class="clock">__CLOCK__</div>
    <div class="date">__DATE__ __WEEKDAY____CROSSDAY__</div>
  </div>
  <div class="band">
    __TICKS__
    <span class="marker__MARKER_CLASS__" style="left: __POSITION__%"></span>
  </div>
  <div class="scale"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>
  <div class="meta"><span class="diff">__DIFF__</span><span>__DIFF_NOTE__</span></div>
</article>"""


def _card(
    city: City,
    reference: City,
    moment: datetime,
    local: datetime,
) -> str:
    hour = local.hour + local.minute / 60.0
    position = hour / 24.0 * 100.0
    is_night = local.hour < 6 or local.hour >= 18
    day_delta = (local.date() - moment.date()).days
    if day_delta > 0:
        crossday = " · 次日"
    elif day_delta < 0:
        crossday = " · 前一天"
    else:
        crossday = ""
    ticks = "".join(
        '<span class="tick" style="left:%.3f%%"></span>' % (index * 100.0 / 24)
        for index in range(1, 24)
    )
    card = _CARD_TEMPLATE
    replacements = {
        "__REFERENCE_CLASS__": " reference" if city == reference else "",
        "__NAME__": html.escape(city.name),
        "__REFERENCE_BADGE__": "<em>参考</em>" if city == reference else "",
        "__DST__": '<span class="dst" title="实行夏令时">*</span>' if city.dst else "",
        "__ZONE__": html.escape(city.zone_label),
        "__OFFSET__": html.escape(city.offset_label),
        "__CLOCK__": local.strftime("%H:%M"),
        "__DATE__": local.strftime("%m-%d"),
        "__WEEKDAY__": WEEKDAYS[local.weekday()],
        "__CROSSDAY__": crossday,
        "__TICKS__": ticks,
        "__MARKER_CLASS__": "night" if is_night else "",
        "__POSITION__": "%.3f" % position,
        "__DIFF__": html.escape(describe_difference(reference, city)),
        "__DIFF_NOTE__": "相对参考城市"
        if city != reference
        else "这是参考城市",
    }
    for key, value in replacements.items():
        card = card.replace(key, value)
    return card


def render_page(
    moment: datetime,
    source: City,
    cities: Sequence[City],
    title: str = "世界时区对照",
) -> str:
    """生成整页 HTML；参数不合法时抛 ``GeoError``。"""
    if not title.strip():
        raise GeoError("页面标题不能为空")
    if not cities:
        raise GeoError("至少需要一个城市")
    if len(cities) > MAX_CITIES:
        raise GeoError("城市过多，最多支持 %d 个" % MAX_CITIES)

    unique: List[City] = []
    seen = set()
    for city in cities:
        if city.name in seen:
            continue
        seen.add(city.name)
        unique.append(city)
    if not unique:
        raise GeoError("至少需要一个城市")

    cards = "".join(
        _card(city, source, moment, convert(moment, source, city))
        for city in unique
    )
    utc_moment = moment - timedelta(minutes=source.offset)

    page = PAGE_TEMPLATE
    replacements = {
        "__TITLE__": html.escape(title.strip()),
        "__REFERENCE__": html.escape(format_moment(moment)),
        "__CITY__": html.escape(source.name),
        "__ZONE__": html.escape(source.zone_label + " · " + source.offset_label),
        "__UTC__": html.escape(format_moment(utc_moment)),
        "__CARDS__": cards,
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page
