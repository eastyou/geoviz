from __future__ import annotations

import unittest
from datetime import datetime

from geoviz.timecalc import (
    convert,
    describe_difference,
    display_width,
    format_moment,
    format_table,
    pad_display,
    parse_moment,
)
from geoviz.zones import GeoError, find_city


class ParseMomentTest(unittest.TestCase):
    def test_formats(self) -> None:
        expected = datetime(2026, 11, 21, 12, 0)
        for text in (
            "2026-11-21 12:00",
            "2026-11-21T12:00",
            "2026-11-21 12:00:00",
            "2026/11/21 12:00",
        ):
            self.assertEqual(parse_moment(text), expected)

    def test_date_only(self) -> None:
        self.assertEqual(parse_moment("2026-11-21"), datetime(2026, 11, 21, 0, 0))

    def test_full_width_colon(self) -> None:
        self.assertEqual(
            parse_moment("2026-11-21 12：30"), datetime(2026, 11, 21, 12, 30)
        )

    def test_invalid(self) -> None:
        for text in ("", "12:00", "2026-13-01 10:00", "2026-11-21 25:00"):
            with self.assertRaises(GeoError):
                parse_moment(text)


class ConvertTest(unittest.TestCase):
    def setUp(self) -> None:
        self.moment = datetime(2026, 11, 21, 12, 0)
        self.beijing = find_city("北京")

    def convert_to(self, name: str) -> datetime:
        return convert(self.moment, self.beijing, find_city(name))

    def test_same_timezone(self) -> None:
        self.assertEqual(self.convert_to("上海"), self.moment)

    def test_london(self) -> None:
        self.assertEqual(self.convert_to("伦敦"), datetime(2026, 11, 21, 4, 0))

    def test_new_york_previous_day(self) -> None:
        self.assertEqual(self.convert_to("纽约"), datetime(2026, 11, 20, 23, 0))

    def test_honolulu(self) -> None:
        self.assertEqual(self.convert_to("檀香山"), datetime(2026, 11, 20, 18, 0))

    def test_kiribati(self) -> None:
        self.assertEqual(self.convert_to("基里巴斯"), datetime(2026, 11, 21, 18, 0))

    def test_kiribati_next_day(self) -> None:
        evening = datetime(2026, 11, 21, 20, 0)
        local = convert(evening, self.beijing, find_city("基里巴斯"))
        self.assertEqual(local, datetime(2026, 11, 22, 2, 0))

    def test_pago_pago(self) -> None:
        self.assertEqual(self.convert_to("帕果帕果"), datetime(2026, 11, 20, 17, 0))

    def test_half_hour_offset(self) -> None:
        self.assertEqual(self.convert_to("新德里"), datetime(2026, 11, 21, 9, 30))

    def test_round_trip(self) -> None:
        target = find_city("纽约")
        local = convert(self.moment, self.beijing, target)
        self.assertEqual(convert(local, target, self.beijing), self.moment)


class FormatTest(unittest.TestCase):
    def test_format_moment(self) -> None:
        self.assertEqual(
            format_moment(datetime(2026, 11, 21, 12, 0)),
            "2026-11-21 12:00 周六",
        )

    def test_difference(self) -> None:
        beijing = find_city("北京")
        self.assertEqual(describe_difference(beijing, find_city("纽约")), "慢 13 小时")
        self.assertEqual(describe_difference(beijing, find_city("伦敦")), "慢 8 小时")
        self.assertEqual(describe_difference(beijing, find_city("东京")), "快 1 小时")
        self.assertEqual(
            describe_difference(beijing, find_city("新德里")), "慢 2 小时 30 分"
        )
        self.assertEqual(describe_difference(beijing, beijing), "同时")

    def test_display_width(self) -> None:
        self.assertEqual(display_width("北京"), 4)
        self.assertEqual(display_width("abc"), 3)
        self.assertEqual(display_width("A中"), 3)

    def test_pad_display(self) -> None:
        self.assertEqual(pad_display("北京", 6), "北京  ")
        self.assertEqual(pad_display("abcdef", 4), "abcdef")

    def test_format_table_alignment(self) -> None:
        table = format_table(
            [["北京", "东八区"], ["纽约", "西五区"]],
            ["城市", "时区"],
        )
        lines = table.splitlines()
        self.assertEqual(len(lines), 4)
        widths = {display_width(line) for line in lines[:3]}
        self.assertEqual(len(widths), 1)


if __name__ == "__main__":
    unittest.main()
