# geoviz

[![CI](https://github.com/eastyou/geoviz/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/geoviz/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

世界时区换算与可视化：在终端查「北京中午 12 点，纽约几点」，或者生成一页 24 小时带对照图，直接投屏或打印。

适合地理课讲时区和日界线，也适合跨国团队对会议时间。零依赖、不联网、结果稳定。

## 特性

- **25 个城市**：覆盖 UTC-11 到 UTC+14，包含新德里（+5:30）这样的半小时时区
- **命令行换算**：一次查询多个城市，自动标注「前一天 / 次日」
- **24 小时带**：每个城市一条昼夜色带，指针显示当地时间，白天夜晚一眼区分
- **中文时区名**：东八区、西五区、零时区，地理课直接用
- **参考时间高亮**：生成页面时标出参考城市和对应的 UTC 时间
- **固定标准时间**：不用 tzdata，不依赖系统时区库，Windows / Linux / macOS 结果一致
- **47 个单元测试**：城市解析、跨日换算、表格对齐与 HTML 渲染

## 安装

```bash
pip install "git+https://github.com/eastyou/geoviz.git"
```

或者不安装直接运行：

```bash
git clone https://github.com/eastyou/geoviz.git
cd geoviz
python3 -m geoviz convert --at "2026-11-21 12:00" --from 北京 --to 纽约,伦敦,东京
```

## 快速开始

查时差：

```console
$ geoviz convert --at "2026-11-21 12:00" --from 北京 --to 纽约,伦敦,东京,新德里
参考时间：2026-11-21 12:00 周六（北京，UTC+08:00）
城市    时区       UTC 偏移   当地时间                         时差
------  ---------  ---------  -------------------------------  ---------------
纽约    西五区     UTC-05:00  2026-11-20 23:00 周五（前一天）  慢 13 小时
伦敦    零时区     UTC+00:00  2026-11-21 04:00 周六            慢 8 小时
东京    东九区     UTC+09:00  2026-11-21 13:00 周六            快 1 小时
新德里  UTC+05:30  UTC+05:30  2026-11-21 09:30 周六            慢 2 小时 30 分
```

生成对照页：

```console
$ geoviz html --at "2026-11-21 12:00" --from 北京 -o 时区对照.html
已生成 时区对照.html：参考 北京 2026-11-21 12:00 周六，共 12 个城市
```

用浏览器打开后可直接投屏；打印时选择 A4 纵向。

## 参数

### `geoviz convert`

| 参数 | 说明 |
| --- | --- |
| `--at` | 参考时间，必填，如 `2026-11-21 12:00` |
| `--from` | 参考城市，默认 `北京` |
| `--to` | 目标城市，逗号分隔，默认 伦敦、纽约、洛杉矶、东京、悉尼、奥克兰 |

### `geoviz html`

| 参数 | 说明 |
| --- | --- |
| `--at` | 参考时间，必填 |
| `--from` | 参考城市，默认 `北京` |
| `--cities` | 展示城市，逗号分隔，默认 12 个城市 |
| `-o, --output` | 输出 HTML，默认 `timezones.html` |
| `--title` | 页面标题，默认「世界时区对照」 |

### 城市名

中文名、英文名和常用别名都可以，大小写与空格不敏感：

```text
北京 / Beijing / 中国      纽约 / New York / NYC / 美国
伦敦 / London / UK          洛杉矶 / LA / Los Angeles
东京 / Tokyo                里约 / Rio / Rio de Janeiro
```

完整城市列表见 [zones.py](geoviz/zones.py)。

### 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 写入文件失败 |
| `2` | 城市、时间或参数不合法 |

## 关于夏令时

本项目按**标准时间**换算，故意不引入时区数据库：

- 中国、日本、印度等不实行夏令时的国家，结果始终准确
- 伦敦、巴黎、纽约、洛杉矶、悉尼等城市在夏令时期间实际时间要 **+1 小时**
- 页面和表格中带 `*` 的城市会实行夏令时，请自行修正

这样做的好处是零依赖、跨平台一致，也更贴近初中地理「标准时区」的教学口径。如果需要精确到某一天的夏令时规则，请使用 Python 3.9+ 的 `zoneinfo`。

## 使用建议

- 地理课讲日界线时，用 `--to 基里巴斯,帕果帕果` 对照 UTC+14 与 UTC-11
- 讲半小时时区时，用 `--to 新德里`
- 开国际会议时，先用 `convert` 找到双方都在 9:00~18:00 的时间段
- 把 `html` 的输出拷到教室电脑，断网也能投屏

## 开发与测试

```bash
python3 -m unittest discover -s tests -v
```

CI 覆盖 Python 3.9 ~ 3.13 与 Linux / macOS / Windows，并会实际执行一次换算和页面生成做冒烟测试。

## License

[MIT](LICENSE) © 2026 eastyou
