"""命令行入口：时区换算与对照页生成。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .render import render_page
from .timecalc import (
    convert,
    describe_difference,
    format_moment,
    format_table,
    parse_moment,
)
from .zones import (
    DEFAULT_CITIES,
    DEFAULT_TARGETS,
    City,
    GeoError,
    find_city,
)

_SPLIT_PATTERN = re.compile(r"[,，、;；\s]+")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geoviz",
        description="世界时区换算：命令行查时差，或生成一页时区对照图",
    )
    parser.add_argument("--version", action="version", version="geoviz 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser(
        "convert", help="把参考时间换算成多个城市的当地时间"
    )
    convert_parser.add_argument(
        "--at", required=True, help="参考时间，如 2026-11-21 12:00"
    )
    convert_parser.add_argument(
        "--from", dest="source", default="北京", help="参考城市，默认北京"
    )
    convert_parser.add_argument(
        "--to",
        default=",".join(DEFAULT_TARGETS),
        help="目标城市，逗号分隔，默认 %s" % "、".join(DEFAULT_TARGETS),
    )

    html_parser = subparsers.add_parser(
        "html", help="生成可打印的世界时区对照页"
    )
    html_parser.add_argument(
        "--at", required=True, help="参考时间，如 2026-11-21 12:00"
    )
    html_parser.add_argument(
        "--from", dest="source", default="北京", help="参考城市，默认北京"
    )
    html_parser.add_argument(
        "--cities",
        default=",".join(DEFAULT_CITIES),
        help="要展示的城市，逗号分隔",
    )
    html_parser.add_argument(
        "-o", "--output", default="timezones.html", help="输出 HTML 路径"
    )
    html_parser.add_argument(
        "--title", default="世界时区对照", help="页面标题"
    )
    return parser


def _split_names(text: str) -> List[str]:
    names = [part for part in _SPLIT_PATTERN.split(text.strip()) if part]
    if not names:
        raise GeoError("城市列表不能为空")
    return names


def _resolve(text: str) -> List[City]:
    return [find_city(name) for name in _split_names(text)]


def _run_convert(args: argparse.Namespace) -> int:
    moment = parse_moment(args.at)
    source = find_city(args.source)
    targets = _resolve(args.to)

    rows = []
    for city in targets:
        local = convert(moment, source, city)
        day_delta = (local.date() - moment.date()).days
        suffix = ""
        if day_delta > 0:
            suffix = "（次日）"
        elif day_delta < 0:
            suffix = "（前一天）"
        rows.append(
            [
                city.name,
                city.zone_label,
                city.offset_label,
                format_moment(local) + suffix,
                describe_difference(source, city),
            ]
        )

    print(
        "参考时间：%s（%s，%s）"
        % (format_moment(moment), source.name, source.offset_label)
    )
    print(
        format_table(
            rows,
            ["城市", "时区", "UTC 偏移", "当地时间", "时差"],
        )
    )
    return 0


def _run_html(args: argparse.Namespace) -> int:
    moment = parse_moment(args.at)
    source = find_city(args.source)
    cities = _resolve(args.cities)
    page = render_page(moment, source, cities, title=args.title)
    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1
    print(
        "已生成 %s：参考 %s %s，共 %d 个城市"
        % (args.output, source.name, format_moment(moment), len(cities))
    )
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "convert":
            return _run_convert(args)
        return _run_html(args)
    except GeoError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
