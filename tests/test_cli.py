from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from geoviz.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def run_cli(self, *args: str) -> tuple:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_convert(self) -> None:
        code, stdout, stderr = self.run_cli(
            "convert",
            "--at",
            "2026-11-21 12:00",
            "--from",
            "北京",
            "--to",
            "纽约,伦敦,东京",
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("参考时间", stdout)
        self.assertIn("纽约", stdout)
        self.assertIn("慢 13 小时", stdout)
        self.assertIn("2026-11-20 23:00", stdout)

    def test_convert_unknown_city(self) -> None:
        code, _, stderr = self.run_cli(
            "convert", "--at", "2026-11-21 12:00", "--to", "火星"
        )
        self.assertEqual(code, 2)
        self.assertIn("不认识的城市", stderr)

    def test_convert_bad_time(self) -> None:
        code, _, stderr = self.run_cli(
            "convert", "--at", "昨天中午", "--to", "东京"
        )
        self.assertEqual(code, 2)
        self.assertIn("时间格式", stderr)

    def test_convert_empty_targets(self) -> None:
        code, _, stderr = self.run_cli(
            "convert", "--at", "2026-11-21 12:00", "--to", "  "
        )
        self.assertEqual(code, 2)
        self.assertIn("城市列表", stderr)

    def test_html(self) -> None:
        output = self.root / "zones.html"
        code, stdout, stderr = self.run_cli(
            "html",
            "--at",
            "2026-11-21 12:00",
            "--from",
            "北京",
            "--cities",
            "北京,纽约,悉尼",
            "-o",
            str(output),
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("已生成", stdout)
        text = output.read_text(encoding="utf-8")
        self.assertIn('<article class="card', text)
        self.assertIn("纽约", text)

    def test_html_write_failure(self) -> None:
        code, _, stderr = self.run_cli(
            "html",
            "--at",
            "2026-11-21 12:00",
            "-o",
            str(self.root),
        )
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", stderr)


if __name__ == "__main__":
    unittest.main()
