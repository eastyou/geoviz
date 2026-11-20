from __future__ import annotations

import unittest
from datetime import datetime

from geoviz.render import render_page
from geoviz.zones import GeoError, find_city


class RenderPageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.moment = datetime(2026, 11, 21, 12, 0)
        self.source = find_city("北京")

    def page(self, cities=None, title: str = "世界时区对照") -> str:
        if cities is None:
            cities = [find_city(name) for name in ("北京", "纽约", "檀香山", "东京")]
        return render_page(self.moment, self.source, cities, title=title)

    def test_card_count(self) -> None:
        page = self.page()
        self.assertEqual(page.count('<article class="card'), 4)

    def test_reference_marked_once(self) -> None:
        page = self.page()
        self.assertEqual(page.count('<em>参考</em>'), 1)
        self.assertIn('class="card reference"', page)

    def test_clock_and_marker(self) -> None:
        page = self.page()
        self.assertIn(">12:00<", page)
        self.assertIn(">23:00<", page)
        self.assertIn('style="left: 50.000%"', page)
        self.assertIn('style="left: 95.833%"', page)

    def test_cross_day(self) -> None:
        page = self.page()
        self.assertIn("前一天", page)
        self.assertIn("11-20", page)

    def test_dst_note(self) -> None:
        page = self.page()
        self.assertIn('class="dst"', page)
        self.assertIn("夏令时", page)

    def test_reference_header(self) -> None:
        page = self.page()
        self.assertIn("2026-11-21 12:00 周六", page)
        self.assertIn("2026-11-21 04:00 周六", page)

    def test_escape_title(self) -> None:
        page = self.page(title="<b>时区</b>")
        self.assertIn("&lt;b&gt;时区&lt;/b&gt;", page)
        self.assertNotIn("<b>时区</b>", page)

    def test_duplicate_cities_removed(self) -> None:
        beijing = find_city("北京")
        page = self.page([beijing, beijing, find_city("东京")])
        self.assertEqual(page.count('<article class="card'), 2)

    def test_empty_cities(self) -> None:
        with self.assertRaises(GeoError):
            self.page([])

    def test_blank_title(self) -> None:
        with self.assertRaises(GeoError):
            self.page(title="  ")

    def test_too_many_cities(self) -> None:
        cities = [find_city("北京")] * 41
        with self.assertRaises(GeoError):
            self.page(cities)

    def test_print_css_and_no_external_assets(self) -> None:
        page = self.page()
        self.assertIn("size: A4 portrait", page)
        self.assertNotIn("http://", page)
        self.assertNotIn("https://", page)


if __name__ == "__main__":
    unittest.main()
