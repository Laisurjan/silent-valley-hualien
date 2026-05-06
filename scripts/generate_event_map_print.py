"""
產出 outputs/event_map_print.svg
讀 data/class_data.json，渲染淺色 A2 橫式印刷地圖。

設計：
  A2 橫式（594 × 420 mm，含 3 mm 出血 → 600 × 426 mm）
  花蓮輪廓 + 中央山脈陰影 + 太平洋
  四個事件位置點，旁邊浮出「亮點句框」（每事件 2 句學生省思摘錄）
  下方資訊條（課程、班級、日期、QR 提示）

使用：
  python scripts/generate_event_map_print.py
"""

import json
import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON  = ROOT / 'data' / 'class_data.json'
OUTPUT_SVG  = ROOT / 'outputs' / 'event_map_print.svg'
OUTPUT_PDF  = ROOT / 'outputs' / 'event_map_print.pdf'

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import with_masked_names

# ---------------------------------------------------------------------------
# 規格：A2 橫式，含出血
# ---------------------------------------------------------------------------
# 1 mm = 1 unit（在 SVG 內）
PAGE_W, PAGE_H = 594, 420       # A2 trim
BLEED = 3                        # 3mm 出血
CANVAS_W = PAGE_W + BLEED * 2    # 600
CANVAS_H = PAGE_H + BLEED * 2    # 426

# 設計用安全區（離 trim 邊 12mm）
SAFE_INSET = 12

# ---------------------------------------------------------------------------
# 顏色（淺色版 / CMYK 友善）
# ---------------------------------------------------------------------------

COLORS = {
    'bg':           '#F5F1EA',
    'paper':        '#FFFBF2',
    'ink':          '#2B2520',
    'text':         '#3A3530',
    'text_second':  '#5C5552',
    'text_muted':   '#8B7355',
    'line':         'rgba(43, 37, 32, 0.3)',
    'line_thin':    'rgba(43, 37, 32, 0.12)',
    'cepo':         '#C73E3A',   # 阿美紅
    'dafen':        '#2C4A6E',   # 布農藍
    'cikasuan':     '#D9A441',   # 阿美黃
    'truku':        '#8B2E2A',   # 太魯閣紅
    'mountain':     'rgba(91, 124, 168, 0.15)',
    'ocean':        'rgba(91, 124, 168, 0.06)',
}

# ---------------------------------------------------------------------------
# 地圖區域：在 A2 橫式上，地圖放左半邊縱長
# ---------------------------------------------------------------------------
# 地圖區（mm）：左 30, 上 50, 寬 220, 高 320
MAP_X = 30 + BLEED
MAP_Y = 50 + BLEED
MAP_W = 220
MAP_H = 320


# ---------------------------------------------------------------------------
# 花蓮縣輪廓：載入開放資料（g0v/twgeojson, CC0）已簡化版
# ---------------------------------------------------------------------------
GEO_FILE = ROOT / 'data' / 'geo' / 'hualien_outline.json'

def load_hualien_outline():
    if not GEO_FILE.exists():
        raise FileNotFoundError(
            f'找不到 {GEO_FILE}。請先執行：python scripts/_extract_hualien.py'
        )
    return json.loads(GEO_FILE.read_text(encoding='utf-8'))


# 事件位置（lng, lat）— 真實經緯度，與互動地圖共用
EVENTS = {
    'cepo': {
        'name':   '大港口事件',
        'eng':    "Cepo' 戰役",
        'year':   '1877',
        'ethnic': '阿美族 ‧ 秀姑巒阿美',
        'place':  '花蓮縣豐濱鄉靜浦村',
        'color':  COLORS['cepo'],
        'lat':    23.4720, 'lng': 121.5025,
    },
    'dafen': {
        'name':   '大分事件',
        'eng':    '布農抗日',
        'year':   '1915',
        'ethnic': '布農族 ‧ 巒社群、丹社群',
        'place':  '花蓮縣卓溪鄉（玉山國家公園）',
        'color':  COLORS['dafen'],
        'lat':    23.2780, 'lng': 121.0830,
    },
    'cikasuan': {
        'name':   '七腳川事件',
        'eng':    'Cikasuan',
        'year':   '1908',
        'ethnic': '阿美族 ‧ 南勢阿美',
        'place':  '花蓮縣吉安鄉（古名 Cikasuan）',
        'color':  COLORS['cikasuan'],
        'lat':    23.9700, 'lng': 121.5775,
    },
    'truku': {
        'name':   '太魯閣戰役',
        'eng':    'Truku 戰役',
        'year':   '1914',
        'ethnic': '太魯閣族（含部分賽德克族）',
        'place':  '主戰場立霧溪、木瓜溪上游山區',
        'color':  COLORS['truku'],
        'lat':    24.1572, 'lng': 121.6213,
    },
}

# 引線終點（亮點句框位置，mm）— 排在地圖右側
QUOTE_BOXES = {
    'truku':    {'x': 280, 'y': 60,   'w': 280},
    'cikasuan': {'x': 280, 'y': 145,  'w': 280},
    'cepo':     {'x': 280, 'y': 230,  'w': 280},
    'dafen':    {'x': 280, 'y': 315,  'w': 280},
}


# ---------------------------------------------------------------------------
# 投影：lng/lat → mm 印刷座標
# ---------------------------------------------------------------------------

class Projector:
    """等距投影（簡化版 Mercator-like）：
       將 (lng, lat) 線性映射到 (mm_x, mm_y)，等比例縮放並置中於 MAP 區。
    """
    def __init__(self, ring):
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        self.lng_min, self.lng_max = min(xs), max(xs)
        self.lat_min, self.lat_max = min(ys), max(ys)
        lng_span = self.lng_max - self.lng_min
        lat_span = self.lat_max - self.lat_min
        # 等比縮放（取較緊那邊）
        self.scale = min(MAP_W / lng_span, MAP_H / lat_span)
        actual_w = lng_span * self.scale
        actual_h = lat_span * self.scale
        self.offset_x = MAP_X + (MAP_W - actual_w) / 2
        self.offset_y = MAP_Y + (MAP_H - actual_h) / 2

    def __call__(self, lng, lat):
        x = self.offset_x + (lng - self.lng_min) * self.scale
        y = self.offset_y + (self.lat_max - lat) * self.scale  # 緯度越大越上
        return (x, y)


def esc(s):
    return html.escape(str(s) if s is not None else '')


def truncate(s, n=70):
    s = str(s or '')
    if len(s) <= n:
        return s
    return s[:n].rstrip() + '…'


# ---------------------------------------------------------------------------
# 取每個事件的「亮點句」（印刷版 2 句）
# ---------------------------------------------------------------------------

def collect_highlights(students, event_id, max_quotes=2):
    pool = [s for s in students if s.get('event') == event_id]
    quotes = []

    for st in pool:
        q3 = str(st.get('showcase_sentences', {}).get('reflection') or '').strip()
        if q3:
            quotes.append({
                'text':  q3,
                'name':  st.get('name', ''),
                'class_name': st.get('class_name', ''),
                'seat':  st.get('seat', ''),
            })
        if len(quotes) >= max_quotes:
            break

    if len(quotes) < max_quotes:
        for st in pool:
            q1 = str(st.get('showcase_sentences', {}).get('difference') or '').strip()
            if q1 and not any(q['text'] == q1 for q in quotes):
                quotes.append({
                    'text':  q1,
                    'name':  st.get('name', ''),
                    'class_name': st.get('class_name', ''),
                    'seat':  st.get('seat', ''),
                })
            if len(quotes) >= max_quotes:
                break

    return quotes[:max_quotes]


# ---------------------------------------------------------------------------
# 文字斷行（中文簡易版：依字符數）
# ---------------------------------------------------------------------------

def wrap_text(text, max_chars):
    text = str(text or '').strip()
    if not text:
        return []
    lines = []
    cur = ''
    for ch in text:
        cur += ch
        # 在標點處優先斷
        if len(cur) >= max_chars and ch in '，。、；：！？.,;:':
            lines.append(cur)
            cur = ''
        elif len(cur) >= max_chars + 4:
            lines.append(cur)
            cur = ''
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# 渲染：地圖
# ---------------------------------------------------------------------------

def ring_to_path(ring, project):
    """把 [(lng, lat), ...] 轉成 SVG path 字串（封閉）"""
    pts = [project(lng, lat) for lng, lat in ring]
    if not pts:
        return ''
    cmds = [f'M {pts[0][0]:.2f} {pts[0][1]:.2f}']
    for x, y in pts[1:]:
        cmds.append(f'L {x:.2f} {y:.2f}')
    cmds.append('Z')
    return ' '.join(cmds)


def render_map(students):
    outline = load_hualien_outline()
    project = Projector(outline['main'])
    main_path = ring_to_path(outline['main'], project)
    islet_paths = [ring_to_path(r, project) for r in outline.get('islets', [])]

    parts = []

    # 太平洋字（僅留低調文字標示，不再有藍底）
    parts.append(f'''
    <text x="{MAP_X + MAP_W - 4}" y="{MAP_Y + MAP_H * 0.55}"
          text-anchor="end" font-family="Songti TC, serif" font-size="7"
          letter-spacing="3" fill="{COLORS['text_muted']}" opacity="0.5">
      太　平　洋
    </text>
    ''')

    # 花蓮縣輪廓（來自 g0v/twgeojson 公開資料）
    parts.append(f'''
    <g>
      <path d="{main_path}"
            fill="{COLORS['paper']}" stroke="{COLORS['ink']}" stroke-width="0.6"
            stroke-linejoin="round"/>
    </g>
    ''')
    for ip in islet_paths:
        parts.append(f'''
        <path d="{ip}"
              fill="{COLORS['paper']}" stroke="{COLORS['ink']}" stroke-width="0.4"/>
        ''')

    # 中央山脈標籤（位置：花蓮縣中西部）
    mx, my = project(121.30, 23.65)
    parts.append(f'''
    <text x="{mx}" y="{my}" font-family="Songti TC, serif" font-size="6"
          letter-spacing="3" fill="rgba(91,124,168,0.65)"
          writing-mode="tb" text-anchor="middle">中央山脈</text>
    ''')

    # 北
    parts.append(f'''
    <g transform="translate({MAP_X + MAP_W / 2}, {MAP_Y - 8})">
      <text text-anchor="middle" font-family="Songti TC, serif" font-size="8"
            letter-spacing="2" fill="{COLORS['text_muted']}">北 ↑</text>
    </g>
    ''')

    # 比例尺：用真實經緯距推算
    # 1° latitude ≈ 110.94 km；取 20 km 對應的 mm 長度
    lat_per_km = 1 / 110.94
    sb_km = 20
    sb_mm = sb_km * lat_per_km * project.scale
    sx = MAP_X + 8
    sy = MAP_Y + MAP_H - 8
    parts.append(f'''
    <g>
      <line x1="{sx}" y1="{sy}" x2="{sx + sb_mm:.2f}" y2="{sy}"
            stroke="{COLORS['ink']}" stroke-width="0.6"/>
      <line x1="{sx}" y1="{sy - 1.5}" x2="{sx}" y2="{sy + 1.5}"
            stroke="{COLORS['ink']}" stroke-width="0.6"/>
      <line x1="{sx + sb_mm:.2f}" y1="{sy - 1.5}" x2="{sx + sb_mm:.2f}" y2="{sy + 1.5}"
            stroke="{COLORS['ink']}" stroke-width="0.6"/>
      <text x="{sx + sb_mm / 2:.2f}" y="{sy + 5}" text-anchor="middle"
            font-family="Songti TC, serif" font-size="5"
            fill="{COLORS['text_muted']}" letter-spacing="0.1em">
        {sb_km} km
      </text>
    </g>
    ''')

    # 事件標記（圓點 + 引線 + 標籤）
    for eid in ['truku', 'cikasuan', 'cepo', 'dafen']:
        ev = EVENTS[eid]
        box = QUOTE_BOXES[eid]
        mx, my = project(ev['lng'], ev['lat'])
        bx = box['x'] + BLEED          # 框左上 x
        by = box['y'] + BLEED          # 框左上 y

        # 引線：從圓點 → 框左中
        line_end_x = bx
        line_end_y = by + 22

        # 引線（折線：先水平延伸再到框）
        bend_x = mx + 24
        parts.append(f'''
        <polyline points="{mx},{my} {bend_x},{my} {line_end_x},{line_end_y}"
                  fill="none" stroke="{ev['color']}" stroke-width="0.5"
                  stroke-dasharray="2 2"/>
        ''')

        # 標記點：外環 + 圓點
        parts.append(f'''
        <g>
          <circle cx="{mx}" cy="{my}" r="4" fill="none"
                  stroke="{ev['color']}" stroke-width="0.6" opacity="0.5"/>
          <circle cx="{mx}" cy="{my}" r="2.4" fill="{ev['color']}"/>
          <circle cx="{mx}" cy="{my}" r="0.8" fill="{COLORS['paper']}"/>
        </g>
        ''')

        # 點旁標籤（事件名稱小字，避免遮輪廓）
        # 太魯閣 / 七腳川：標籤放下方左；大港口 / 大分：放下方右
        label_anchor = 'start'
        label_dx = 6
        label_dy = -2
        parts.append(f'''
        <text x="{mx + label_dx}" y="{my + label_dy}"
              text-anchor="{label_anchor}"
              font-family="Songti TC, serif" font-size="5"
              fill="{COLORS['text_muted']}" letter-spacing="0.15em">
          {esc(ev['place'].replace('花蓮縣', '').replace('（玉山國家公園）', '').replace('主戰場', ''))[:8]}
        </text>
        ''')

    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# 渲染：每個亮點句框
# ---------------------------------------------------------------------------

def render_quote_box(students, eid):
    ev = EVENTS[eid]
    box = QUOTE_BOXES[eid]
    bx = box['x'] + BLEED
    by = box['y'] + BLEED
    bw = box['w']
    bh = 75

    quotes = collect_highlights(students, eid, max_quotes=2)
    n_total = sum(1 for s in students if s.get('event') == eid)

    # 標題列
    parts = [f'''
    <g>
      <!-- 左側色條 -->
      <rect x="{bx}" y="{by}" width="2" height="{bh}" fill="{ev['color']}"/>

      <!-- 內容區 -->
      <g transform="translate({bx + 8}, {by})">

        <!-- 標題行：年份 + 事件名 + 族群 -->
        <text x="0" y="6" font-family="Inter, sans-serif" font-size="6"
              fill="{ev['color']}" font-weight="700" letter-spacing="0.2em">
          {esc(ev['year'])}
        </text>
        <text x="20" y="6" font-family="Songti TC, serif" font-size="11"
              fill="{COLORS['ink']}" font-weight="600" letter-spacing="0.04em">
          {esc(ev['name'])}
        </text>
        <text x="0" y="14" font-family="Songti TC, serif" font-size="5"
              fill="{COLORS['text_muted']}" letter-spacing="0.2em">
          {esc(ev['ethnic'])}　／　{esc(ev['place'])}
        </text>
    ''']

    # 引文（最多 2 句）
    qy = 22
    if not quotes:
        parts.append(f'''
        <text x="0" y="{qy}" font-family="Songti TC, serif" font-size="5.5"
              fill="{COLORS['text_muted']}" font-style="italic" letter-spacing="0.05em">
          ＿＿  尚無學生省思  ＿＿
        </text>
        ''')
    else:
        for q in quotes:
            text = truncate(q['text'], 56)
            lines = wrap_text(text, 28)
            for line in lines[:2]:
                parts.append(f'''
                <text x="0" y="{qy}" font-family="Songti TC, serif" font-size="5"
                      fill="{COLORS['text']}" letter-spacing="0.04em">
                  {esc(line)}
                </text>
                ''')
                qy += 6
            byline = f"— {q['class_name']} {q['seat']} {q['name']}"
            parts.append(f'''
            <text x="{bw - 16}" y="{qy}" text-anchor="end"
                  font-family="Inter, sans-serif" font-size="4.5"
                  fill="{ev['color']}" letter-spacing="0.2em">
              {esc(byline)}
            </text>
            ''')
            qy += 8

    parts.append(f'''
        <!-- 學生數 -->
        <text x="{bw - 16}" y="{bh - 4}" text-anchor="end"
              font-family="Inter, sans-serif" font-size="4.5"
              fill="{COLORS['text_muted']}" letter-spacing="0.25em">
          共 {n_total} 位學生
        </text>
      </g>
    </g>
    ''')

    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def render_header_block(meta):
    x = SAFE_INSET + BLEED
    y = SAFE_INSET + BLEED
    return f'''
    <g>
      <!-- 四色織紋條 -->
      <g>
        <rect x="{x}" y="{y}" width="35" height="2" fill="{COLORS['cepo']}"/>
        <rect x="{x + 35}" y="{y}" width="35" height="2" fill="{COLORS['dafen']}"/>
        <rect x="{x + 70}" y="{y}" width="35" height="2" fill="{COLORS['cikasuan']}"/>
        <rect x="{x + 105}" y="{y}" width="35" height="2" fill="{COLORS['truku']}"/>
      </g>

      <text x="{x}" y="{y + 12}" font-family="Inter, sans-serif" font-size="5"
            fill="{COLORS['text_muted']}" letter-spacing="0.4em">
        {esc(meta.get('school', ''))} ‧ {esc(meta.get('course', ''))}
      </text>

      <text x="{x}" y="{y + 28}" font-family="Songti TC, serif" font-size="22"
            fill="{COLORS['ink']}" font-weight="600" letter-spacing="0.04em">
        縱谷無言．我們的歷史
      </text>

      <text x="{x}" y="{y + 38}" font-family="Songti TC, serif" font-size="8"
            fill="{COLORS['text_second']}" letter-spacing="0.1em" font-style="italic">
        花蓮原住民族四場大事，與 {meta.get('student_count', 0)} 位高中生的省思
      </text>
    </g>
    '''


def render_footer(meta):
    fx = SAFE_INSET + BLEED
    fy = CANVAS_H - SAFE_INSET - 6
    return f'''
    <g>
      <line x1="{fx}" y1="{fy - 8}" x2="{CANVAS_W - SAFE_INSET - BLEED}" y2="{fy - 8}"
            stroke="{COLORS['ink']}" stroke-width="0.3" opacity="0.4"/>
      <text x="{fx}" y="{fy}" font-family="Inter, sans-serif" font-size="4"
            fill="{COLORS['text_muted']}" letter-spacing="0.3em">
        {esc(meta.get('unit', ''))}　‧　{esc(meta.get('generated_at', '')[:10])}
      </text>
      <text x="{CANVAS_W - SAFE_INSET - BLEED}" y="{fy}" text-anchor="end"
            font-family="Inter, sans-serif" font-size="4"
            fill="{COLORS['text_muted']}" letter-spacing="0.3em">
        印刷規格　A2 橫式 ‧ 出血 3mm　／　淺色版
      </text>
    </g>
    '''


def render_legend():
    """右下角小說明：四色 = 四個事件"""
    lx = CANVAS_W - SAFE_INSET - BLEED - 100
    ly = MAP_Y + MAP_H + 14
    items = [
        ('大港口事件', COLORS['cepo']),
        ('大分事件',   COLORS['dafen']),
        ('七腳川事件', COLORS['cikasuan']),
        ('太魯閣戰役', COLORS['truku']),
    ]
    parts = [f'''
    <text x="{lx}" y="{ly - 3}" font-family="Inter, sans-serif" font-size="4"
          fill="{COLORS['text_muted']}" letter-spacing="0.3em">
      四 色 ‧ 四 個 事 件
    </text>
    ''']
    for i, (name, color) in enumerate(items):
        col = i % 2
        row = i // 2
        ix = lx + col * 56
        iy = ly + 4 + row * 8
        parts.append(f'''
        <g>
          <circle cx="{ix + 2}" cy="{iy + 2}" r="2" fill="{color}"/>
          <text x="{ix + 8}" y="{iy + 4}" font-family="Songti TC, serif"
                font-size="6" fill="{COLORS['text']}" letter-spacing="0.05em">
            {esc(name)}
          </text>
        </g>
        ''')
    return '\n'.join(parts)


def render_corner_decorations():
    """淡墨等高線、山形與海岸線；純 path，避開地圖主體與標記。"""
    ink = COLORS['ink']
    return f'''
    <g id="corner-decorations" fill="none" stroke="{ink}" stroke-linecap="round" stroke-linejoin="round" opacity="0.20">
      <path d="M18 398 C44 384 68 387 92 374 C116 361 135 366 154 352" stroke-width="0.45"/>
      <path d="M22 407 C49 392 77 397 103 383 C128 370 145 375 166 363" stroke-width="0.35"/>
      <path d="M32 416 C58 404 86 406 112 394 C134 384 153 387 176 376" stroke-width="0.25"/>
      <path d="M30 362 L47 344 L61 356 L78 331 L101 363" stroke-width="0.55"/>
      <path d="M440 24 C465 16 489 17 516 28 C544 39 565 36 585 22" stroke-width="0.40"/>
      <path d="M447 36 C470 28 493 30 518 39 C546 49 566 46 590 32" stroke-width="0.30"/>
      <path d="M465 58 C487 44 508 49 527 32 L552 62" stroke-width="0.50"/>
      <path d="M28 24 C48 37 67 35 88 25 C111 14 132 17 154 32" stroke-width="0.38"/>
      <path d="M24 37 C46 49 68 48 91 37 C113 27 136 31 159 45" stroke-width="0.28"/>
      <path d="M502 388 C525 371 548 376 572 360 C586 351 595 349 604 350" stroke-width="0.45"/>
      <path d="M515 404 C537 389 558 392 581 378 C592 371 600 369 607 370" stroke-width="0.32"/>
      <path d="M472 414 L492 391 L508 405 L530 374 L558 416" stroke-width="0.55"/>
    </g>
    '''


def build_svg(data):
    data = with_masked_names(data)
    students = data['students']
    meta = data['meta']

    quote_blocks = '\n'.join(
        render_quote_box(students, eid) for eid in ['truku', 'cikasuan', 'cepo', 'dafen']
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
     width="{CANVAS_W}mm" height="{CANVAS_H}mm"
     viewBox="0 0 {CANVAS_W} {CANVAS_H}">

<!--
  縱谷無言．事件地圖（印刷版）
  規格：A2 橫式 594×420mm + 出血 3mm = 600×426mm
  色彩：CMYK 友善（深褐 #2B2520、阿美紅 #C73E3A、布農藍 #2C4A6E、阿美黃 #D9A441、太魯閣紅 #8B2E2A）
  字型：Songti TC / Noto Serif TC（中文）、Inter（英數）
  使用：放大 print，請保留 3mm 出血，trim 至 594×420mm。
-->

  <defs>
    <!-- 織紋 pattern：菱形格 -->
    <pattern id="weave" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="4" fill="{COLORS['bg']}"/>
      <path d="M0 2 L2 0 M2 4 L4 2" stroke="rgba(139,69,19,0.04)" stroke-width="0.4"/>
    </pattern>
  </defs>

  <!-- 整版織紋背景（含出血） -->
  <rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="url(#weave)"/>

  <!-- 出血標記（裁切時要移除）-->
  <g stroke="{COLORS['ink']}" stroke-width="0.2" opacity="0.5">
    <line x1="{BLEED}" y1="0" x2="{BLEED}" y2="3"/>
    <line x1="0" y1="{BLEED}" x2="3" y2="{BLEED}"/>
    <line x1="{CANVAS_W - BLEED}" y1="0" x2="{CANVAS_W - BLEED}" y2="3"/>
    <line x1="{CANVAS_W}" y1="{BLEED}" x2="{CANVAS_W - 3}" y2="{BLEED}"/>
    <line x1="{BLEED}" y1="{CANVAS_H}" x2="{BLEED}" y2="{CANVAS_H - 3}"/>
    <line x1="0" y1="{CANVAS_H - BLEED}" x2="3" y2="{CANVAS_H - BLEED}"/>
    <line x1="{CANVAS_W - BLEED}" y1="{CANVAS_H}" x2="{CANVAS_W - BLEED}" y2="{CANVAS_H - 3}"/>
    <line x1="{CANVAS_W}" y1="{CANVAS_H - BLEED}" x2="{CANVAS_W - 3}" y2="{CANVAS_H - BLEED}"/>
  </g>

  <!-- 淡墨等高線 + 山形 + 海岸線角飾，純 SVG path，避開地圖與標記 -->
  {render_corner_decorations()}

  <!-- 標題區 -->
  {render_header_block(meta)}

  <!-- 地圖 -->
  {render_map(students)}

  <!-- 圖例 -->
  {render_legend()}

  <!-- 四個亮點句框 -->
  {quote_blocks}

  <!-- 底部資訊 -->
  {render_footer(meta)}

</svg>
'''


def find_chrome():
    """找系統上的 Chrome / Edge headless 可執行檔。"""
    cands = [
        os.environ.get('CHROME_PATH'),
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    for c in cands:
        if c and Path(c).exists():
            return c
    for name in ('google-chrome', 'chromium', 'chrome', 'msedge'):
        p = shutil.which(name)
        if p:
            return p
    return None


def svg_to_pdf(svg_path: Path, pdf_path: Path):
    """用 Chrome / Edge headless 把 SVG 轉成 PDF（A2 橫式 + 3mm 出血）。"""
    chrome = find_chrome()
    if not chrome:
        return svg_to_pdf_cairosvg(svg_path, pdf_path)

    svg_text = svg_path.read_text(encoding='utf-8')
    wrapper = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: {CANVAS_W}mm {CANVAS_H}mm; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: white; }}
  svg {{ display: block; width: {CANVAS_W}mm; height: {CANVAS_H}mm; }}
</style>
</head>
<body>
{svg_text}
</body>
</html>
'''
    wrap_html = ROOT / 'outputs' / 'event_map_print_wrapper.html'
    wrap_html.write_text(wrapper, encoding='utf-8')

    cmd = [
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-crash-reporter',
        '--disable-crashpad',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_path}',
        wrap_html.as_uri(),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    if r.returncode != 0:
        print('  Chrome 失敗：', r.stderr.splitlines()[-1] if r.stderr else r.returncode)
        return svg_to_pdf_cairosvg(svg_path, pdf_path)
    return pdf_path.exists()


def svg_to_pdf_cairosvg(svg_path: Path, pdf_path: Path):
    try:
        import cairosvg
    except Exception:
        print('  跳過 PDF：找不到可用的 Chrome/Edge 或 cairosvg。')
        return False
    cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path), output_width=CANVAS_W * 96 / 25.4, output_height=CANVAS_H * 96 / 25.4)
    print('  PDF fallback：cairosvg')
    return pdf_path.exists()


def main():
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f'找不到資料檔：{INPUT_JSON}')

    with INPUT_JSON.open('r', encoding='utf-8') as f:
        data = json.load(f)

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    svg_doc = build_svg(data)
    OUTPUT_SVG.write_text(svg_doc, encoding='utf-8')

    size_kb = OUTPUT_SVG.stat().st_size // 1024
    print(f'已輸出：{OUTPUT_SVG.relative_to(ROOT)}')
    print(f'  尺寸：A2 橫式 {CANVAS_W} x {CANVAS_H} mm（含 3mm 出血）')
    print(f'  學生：{len(data["students"])} 位')
    print(f'  檔案：{size_kb} KB')

    # PDF 輸出（Chrome headless）
    if svg_to_pdf(OUTPUT_SVG, OUTPUT_PDF):
        pdf_kb = OUTPUT_PDF.stat().st_size // 1024
        print(f'已輸出：{OUTPUT_PDF.relative_to(ROOT)}')
        print(f'  檔案：{pdf_kb} KB')


if __name__ == '__main__':
    main()
