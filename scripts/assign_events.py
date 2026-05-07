"""
分組腳本 — 把學生分到 4 個事件並輸出投影名單與機器讀取用 JSON。

設計原則:
- 高出席風險生(高風險旗標)平均到不同事件,讓出席不確定性均攤
- 跨班混合,同班學生不集中在同事件
- 林廷澤 Mowna Iming 配到 truku(由教師決策,文化連結:族人後代讀族人故事)

輸出 (兩者皆含 PII,不上傳 GitHub,在 .gitignore 排除):
    data/class_roster.json                 — 機器讀取用,後續腳本可接
    outputs/event_assignment_board.html    — 投影用 (不顯示高風險旗標,避免課堂貼標籤)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── 事件中文與色碼 ─────────────────────────────────────────────────────
EVENTS = {
    "cepo":     {"name": "大港口", "year": "1877–1878", "ethnic": "阿美族 ‧ 海岸",  "color": "#C73E3A"},
    "dafen":    {"name": "大分",   "year": "1914–1933", "ethnic": "布農族 ‧ 深山",  "color": "#2C4A6E"},
    "cikasuan": {"name": "七腳川", "year": "1908",       "ethnic": "阿美族 ‧ 平原",  "color": "#D9A441"},
    "truku":    {"name": "太魯閣", "year": "1914",       "ethnic": "太魯閣族 ‧ 峽谷","color": "#8B2E2A"},
}

# ── 分配結果 (硬編碼,經教師確認) ──────────────────────────────────────
# 欄位: 班級, 座號, 姓名, 事件, 是否高出席風險, 備註
ROSTER = [
    # 大港口 cepo (5 人,含高風險 1)
    ("會二乙", "11", "周俞函",              "cepo",     True,  ""),
    ("商二乙", "30", "潘畇澕",              "cepo",     False, ""),
    ("商二乙", "24", "鍾育瑄",              "cepo",     False, ""),
    ("多二甲", "13", "蔡汶君",              "cepo",     False, ""),
    ("英二乙", "09", "余希璿",              "cepo",     False, ""),

    # 大分 dafen (5 人,含高風險 1)
    ("商二乙", "18", "吳姵瑤",              "dafen",    True,  ""),
    ("商二乙", "01", "李正揚",              "dafen",    False, ""),
    ("商二乙", "26", "梁翊芝",              "dafen",    False, ""),
    ("多二甲", "16", "杜安蕎",              "dafen",    False, ""),
    ("會二乙", "02", "江維哲",              "dafen",    False, ""),

    # 七腳川 cikasuan (4 人,無高風險)
    ("商二乙", "02", "邢越樺",              "cikasuan", False, ""),
    ("商二乙", "25", "張安茹",              "cikasuan", False, ""),
    ("多二甲", "05", "張育瑞",              "cikasuan", False, ""),
    ("商二甲", "03", "李昊諺",              "cikasuan", False, ""),

    # 太魯閣 truku (4 人,含高風險 1 + 文化連結 1)
    ("會二乙", "03", "林廷澤 Mowna Iming",  "truku",    True,  "族人後代,文化連結配對"),
    ("商二乙", "20", "林宜妏",              "truku",    False, ""),
    ("多二甲", "11", "王于庭",              "truku",    False, ""),
    ("商二甲", "11", "潘鴻宇",              "truku",    False, ""),
]


def write_roster_json() -> Path:
    """寫機器讀取用 JSON (含高風險旗標,僅本機保存)。"""
    data = {
        "meta": {
            "school": "花蓮高商",
            "course": "縱谷無言 ‧ 多元文化與文學",
            "term": "2026 春季",
            "total_students": len(ROSTER),
            "by_event": {ek: sum(1 for r in ROSTER if r[3] == ek) for ek in EVENTS},
            "high_risk_count": sum(1 for r in ROSTER if r[4]),
            "note": "本檔含學生姓名 (PII),僅本機保存,已在 .gitignore 排除",
        },
        "events": EVENTS,
        "students": [
            {
                "class": cls,
                "seat": seat,
                "name": name,
                "event": event,
                "high_risk": high_risk,
                "note": note,
            }
            for cls, seat, name, event, high_risk, note in ROSTER
        ],
    }
    path = ROOT / "data" / "class_roster.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_board_html() -> Path:
    """寫投影用 HTML (不顯示高風險旗標,避免課堂貼標籤)。"""
    by_class = sorted(ROSTER, key=lambda r: (r[0], r[1]))
    by_event: dict[str, list] = {ek: [] for ek in EVENTS}
    for r in ROSTER:
        by_event[r[3]].append(r)

    html = []
    html.append("""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>事件分配名單 ‧ 縱谷無言</title>
<style>
  :root {
    --cepo: #C73E3A; --dafen: #2C4A6E; --cikasuan: #D9A441; --truku: #8B2E2A;
    --bg: #F5F1EA; --ink: #2B2520; --muted: #6E665C;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 32px;
    background: var(--bg); color: var(--ink);
    font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
    font-size: 18px; line-height: 1.5;
  }
  h1 { font-size: 36px; margin: 0 0 4px; letter-spacing: 0.04em; }
  .sub { color: var(--muted); margin-bottom: 24px; font-size: 14px; letter-spacing: 0.15em; }
  h2 { font-size: 22px; margin: 32px 0 12px; letter-spacing: 0.04em; }
  .layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 32px; }
  table { width: 100%; border-collapse: collapse; background: rgba(255,251,242,0.85); }
  th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #DCD5C4; font-size: 18px; }
  th { background: rgba(43,37,32,0.06); font-weight: 600; letter-spacing: 0.1em; font-size: 14px; }
  .seat { font-family: 'Courier New', monospace; font-weight: 700; }
  .ev-tag {
    display: inline-block; padding: 4px 10px; border-radius: 14px;
    font-size: 14px; color: #fff; font-weight: 600; letter-spacing: 0.1em;
  }
  .ev-cepo     { background: var(--cepo); }
  .ev-dafen    { background: var(--dafen); }
  .ev-cikasuan { background: var(--cikasuan); color: #2B2520; }
  .ev-truku    { background: var(--truku); }
  .event-card {
    border-left: 6px solid; padding: 16px 20px; margin-bottom: 16px;
    background: rgba(255,251,242,0.85); border-radius: 4px;
  }
  .event-card.cepo     { border-color: var(--cepo); }
  .event-card.dafen    { border-color: var(--dafen); }
  .event-card.cikasuan { border-color: var(--cikasuan); }
  .event-card.truku    { border-color: var(--truku); }
  .event-card h3 { margin: 0 0 4px; font-size: 22px; letter-spacing: 0.04em; }
  .event-card .meta { color: var(--muted); font-size: 13px; letter-spacing: 0.15em; margin-bottom: 10px; }
  .event-card ul { margin: 0; padding-left: 20px; }
  .event-card li { padding: 4px 0; font-size: 17px; }
  .event-card li .cls { color: var(--muted); font-size: 14px; }
  .footer-note { margin-top: 40px; color: var(--muted); font-size: 12px; letter-spacing: 0.1em; text-align: center; }
  @media print { body { padding: 16px; } }
</style>
</head>
<body>
<h1>事件分配名單</h1>
<div class="sub">縱谷無言 ‧ 第三學期單元 ‧ 共 18 人</div>

<div class="layout">
""")

    # 左欄:按班級+座號排序 (學生找自己用)
    html.append('<div>')
    html.append('<h2>📋 找你自己 — 按班級 / 座號排</h2>')
    html.append('<table>')
    html.append('<thead><tr><th>班級</th><th>座號</th><th>姓名</th><th>你的事件</th></tr></thead>')
    html.append('<tbody>')
    for cls, seat, name, event, _hr, _note in by_class:
        ev = EVENTS[event]
        html.append(
            f'<tr><td>{cls}</td><td class="seat">{seat}</td>'
            f'<td>{name}</td>'
            f'<td><span class="ev-tag ev-{event}">{ev["name"]}</span></td></tr>'
        )
    html.append('</tbody></table>')
    html.append('</div>')

    # 右欄:按事件分組 (每事件有誰)
    html.append('<div>')
    html.append('<h2>🗂️ 各事件夥伴 — 找你的事件夥伴</h2>')
    for event_key, ev in EVENTS.items():
        members = by_event[event_key]
        html.append(f'<div class="event-card {event_key}">')
        html.append(f'<h3>{ev["name"]} <span style="color:var(--muted);font-size:14px;font-weight:400;">({len(members)} 人)</span></h3>')
        html.append(f'<div class="meta">{ev["year"]} ‧ {ev["ethnic"]}</div>')
        html.append('<ul>')
        for cls, seat, name, _ev, _hr, _note in sorted(members, key=lambda r: (r[0], r[1])):
            html.append(f'<li>{name} <span class="cls">— {cls} {seat}</span></li>')
        html.append('</ul>')
        html.append('</div>')
    html.append('</div>')

    html.append('</div>')  # /.layout
    html.append('<div class="footer-note">投影用 ‧ 同事件同學是「事件夥伴」 ‧ 可討論,但每人寫自己的句子</div>')
    html.append('</body></html>')

    path = ROOT / "outputs" / "event_assignment_board.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(html), encoding="utf-8")
    return path


def main():
    json_path = write_roster_json()
    html_path = write_board_html()

    print("分配結果:")
    for ek, ev in EVENTS.items():
        members = [r for r in ROSTER if r[3] == ek]
        hr = sum(1 for r in members if r[4])
        print(f"  {ev['name']:6s} ({ek:8s})  {len(members)} 人  高風險 {hr}")

    total = len(ROSTER)
    hr_total = sum(1 for r in ROSTER if r[4])
    print(f"\n  總計            {total} 人  高風險 {hr_total}")
    print(f"\n輸出:")
    print(f"  {json_path}")
    print(f"  {html_path}")
    print(f"\n  (兩檔皆含 PII,已在 .gitignore 排除)")


if __name__ == "__main__":
    main()
