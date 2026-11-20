from __future__ import annotations

import unittest

from geoviz.zones import (
    CITIES,
    DEFAULT_CITIES,
    DEFAULT_TARGETS,
    GeoError,
    find_city,
    format_offset,
)


class FindCityTest(unittest.TestCase):
    def test_chinese_name(self) -> None:
        self.assertEqual(find_city("北京").name, "北京")
        self.assertEqual(find_city("纽约").offset, -300)

    def test_english_and_aliases(self) -> None:
        self.assertEqual(find_city("Beijing").name, "北京")
        self.assertEqual(find_city("new york").name, "纽约")
        self.assertEqual(find_city("NYC").name, "纽约")
        self.assertEqual(find_city("la").name, "洛杉矶")
        self.assertEqual(find_city("里约").name, "里约热内卢")

    def test_unknown(self) -> None:
        with self.assertRaises(GeoError) as context:
            find_city("火星")
        self.assertIn("不认识的城市", str(context.exception))

    def test_empty(self) -> None:
        with self.assertRaises(GeoError):
            find_city("  ")


class OffsetTest(unittest.TestCase):
    def test_format_offset(self) -> None:
        self.assertEqual(format_offset(480), "UTC+08:00")
        self.assertEqual(format_offset(0), "UTC+00:00")
        self.assertEqual(format_offset(330), "UTC+05:30")
        self.assertEqual(format_offset(-300), "UTC-05:00")
        self.assertEqual(format_offset(-660), "UTC-11:00")
        self.assertEqual(format_offset(840), "UTC+14:00")

    def test_zone_label(self) -> None:
        self.assertEqual(find_city("北京").zone_label, "东八区")
        self.assertEqual(find_city("伦敦").zone_label, "零时区")
        self.assertEqual(find_city("纽约").zone_label, "西五区")
        self.assertEqual(find_city("新德里").zone_label, "UTC+05:30")
        self.assertEqual(find_city("基里巴斯").zone_label, "东十四区")

    def test_dst_flags(self) -> None:
        self.assertTrue(find_city("伦敦").dst)
        self.assertTrue(find_city("悉尼").dst)
        self.assertFalse(find_city("莫斯科").dst)
        self.assertFalse(find_city("北京").dst)


class CityListTest(unittest.TestCase):
    def test_unique_names(self) -> None:
        names = [city.name for city in CITIES]
        self.assertEqual(len(names), len(set(names)))

    def test_every_alias_resolves(self) -> None:
        for city in CITIES:
            for alias in city.aliases:
                self.assertEqual(find_city(alias).name, city.name)

    def test_default_lists_resolve(self) -> None:
        for name in DEFAULT_CITIES + DEFAULT_TARGETS:
            self.assertEqual(find_city(name).name, name)

    def test_offsets_in_range(self) -> None:
        for city in CITIES:
            self.assertGreaterEqual(city.offset, -12 * 60)
            self.assertLessEqual(city.offset, 14 * 60)


if __name__ == "__main__":
    unittest.main()
