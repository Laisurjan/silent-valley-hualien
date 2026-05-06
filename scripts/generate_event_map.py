"""
產出 outputs/event_map_interactive.html
讀 data/class_data.json，渲染深色花蓮事件地圖。

設計：
  使用 Leaflet + OpenStreetMap（CartoDB Dark Matter tiles，開放資料、免 API key）
  四個事件以 lat/lng 標記在真實位置上；點擊 → 右側面板顯示亮點句
  桌機：左地圖 / 右面板；手機：上地圖 / 下面板

姓名屏蔽：
  學生姓名顯示為「首+O+尾」形式（資料檔不動）。

使用：
  python scripts/generate_event_map.py
"""

import json
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON  = ROOT / 'data' / 'class_data.json'
OUTPUT_HTML = ROOT / 'outputs' / 'event_map_interactive.html'

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import with_masked_names

# ---------------------------------------------------------------------------
# 事件元資訊（含真實 lat/lng）
# ---------------------------------------------------------------------------
# 經緯度來源：OpenStreetMap / Google Maps 公開資料
#   靜浦村（大港口）   23.4720, 121.5025（村中心，避開海岸線外）
#   大分山屋          23.2780, 121.0830（玉山國家公園境內）
#   吉安鄉中心        23.9700, 121.5775
#   太魯閣口          24.1572, 121.6213

EVENTS = {
    'cepo': {
        'name':    '大港口事件',
        'eng':     "Cepo' 戰役",
        'year':    '1877',
        'ethnic':  '阿美族 ‧ 秀姑巒阿美',
        'place':   '花蓮縣豐濱鄉靜浦村',
        'color':   '--color-cepo-dark',
        'lat':     23.4720,
        'lng':     121.5025,
        'tagline': '清軍以「招撫」之名誘殺阿美青年。事後於屠殺地建靜浦國小、靜浦營，地名也被「靜浦」取代。',
    },
    'dafen': {
        'name':    '大分事件',
        'eng':     '布農抗日',
        'year':    '1915',
        'ethnic':  '布農族 ‧ 巒社群、丹社群',
        'place':   '花蓮縣卓溪鄉（玉山國家公園）',
        'color':   '--color-dafen-dark',
        'lat':     23.2780,
        'lng':     121.0830,
        'tagline': '拉荷．阿雷與族人從 1915 抵抗到 1933，整整 18 年；1933 才以「歸順」名義落幕。',
    },
    'cikasuan': {
        'name':    '七腳川事件',
        'eng':     'Cikasuan',
        'year':    '1908',
        'ethnic':  '阿美族 ‧ 南勢阿美',
        'place':   '花蓮縣吉安鄉（古名 Cikasuan）',
        'color':   '--color-cikasuan-dark',
        'lat':     23.9700,
        'lng':     121.5775,
        'tagline': '一個社被滅，地名換了兩次：Cikasuan → 吉野村 → 吉安。',
    },
    'truku': {
        'name':    '太魯閣戰役',
        'eng':     'Truku 戰役',
        'year':    '1914',
        'ethnic':  '太魯閣族（含部分賽德克族）',
        'place':   '主戰場立霧溪、木瓜溪上游山區',
        'color':   '--color-truku-dark',
        'lat':     24.1572,
        'lng':     121.6213,
        'tagline': '兩萬軍警對三千族人。佐久間死了，族人退下山。今天那裡叫太魯閣國家公園。',
    },
}

EVENT_ORDER = ['truku', 'cikasuan', 'cepo', 'dafen']  # 由北到南

# CSS 變數對應的實際色碼（給 Leaflet marker 用）
EVENT_COLORS_HEX = {
    'cepo':     '#E85A52',
    'dafen':    '#5B7CA8',
    'cikasuan': '#E8C56B',
    'truku':    '#B84741',
}


def esc(s):
    return html.escape(str(s) if s is not None else '')


def truncate(s, n=78):
    s = str(s or '')
    if len(s) <= n:
        return s
    return s[:n].rstrip() + '…'


def collect_highlights(students, event_id, max_quotes=3):
    pool = [s for s in students if s.get('event') == event_id]
    quotes = []

    for st in pool:
        q3 = str(st.get('showcase_sentences', {}).get('reflection') or '').strip()
        if q3:
            quotes.append({
                'text': q3,
                'name': st.get('name', ''),
                'class_name': st.get('class_name', ''),
                'seat': st.get('seat', ''),
                'prompt': '省思句',
            })
        if len(quotes) >= max_quotes:
            break

    if len(quotes) < max_quotes:
        for st in pool:
            q1 = str(st.get('showcase_sentences', {}).get('difference') or '').strip()
            if q1 and not any(q['text'] == q1 for q in quotes):
                quotes.append({
                    'text': q1,
                    'name': st.get('name', ''),
                    'class_name': st.get('class_name', ''),
                    'seat': st.get('seat', ''),
                    'prompt': '差異句',
                })
            if len(quotes) >= max_quotes:
                break

    return quotes[:max_quotes]


def count_students(students, event_id):
    return sum(1 for s in students if s.get('event') == event_id)


def render_panel_data(students):
    data = {}
    for eid in EVENT_ORDER:
        ev = EVENTS[eid]
        quotes = collect_highlights(students, eid)
        data[eid] = {
            'name':     ev['name'],
            'eng':      ev['eng'],
            'year':     ev['year'],
            'ethnic':   ev['ethnic'],
            'place':    ev['place'],
            'tagline':  ev['tagline'],
            'lat':      ev['lat'],
            'lng':      ev['lng'],
            'color':    EVENT_COLORS_HEX[eid],
            'count':    count_students(students, eid),
            'quotes':   quotes,
            'image':    f'../assets/images/event_{eid}.png',
        }
    return data


def render_default_panel_html(n):
    return f'''
    <div class="panel-empty">
      <img class="panel-hero-img" src="../assets/images/hero_valley.png" alt="">
      <div class="panel-eyebrow">縱谷無言．事件地圖</div>
      <h2 class="panel-empty-title">縱谷把痛苦悄悄埋起來。<br/>地圖把它們指出來。</h2>
      <p class="panel-empty-body">
        花蓮的山與海之間，發生過四場讓族人失語的大事。
        我們用 {n} 位學生的省思亮點，重新說一次。
      </p>
      <p class="panel-empty-hint">
        <span class="hint-arrow">←</span> 點地圖上任一個事件
      </p>
      <div class="event-color-bar" style="margin-top: 2rem;">
        <div class="seg-cepo"></div>
        <div class="seg-dafen"></div>
        <div class="seg-cikasuan"></div>
        <div class="seg-truku"></div>
      </div>
      <p class="panel-empty-foot">
        地圖底圖：OpenStreetMap 貢獻者　／　CARTO Dark Matter
      </p>
    </div>
    '''


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = r'''
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; }
body {
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: var(--font-serif);
  line-height: var(--lh-body);
  overflow-x: hidden;
}

/* ---------- 頂部 ---------- */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.2rem 2rem;
  border-top: 3px solid var(--accent);
  border-bottom: 0.5px solid var(--line-thin);
  background: var(--bg-page);
}
.topbar-eyebrow {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.4em;
  color: var(--text-muted);
}
.topbar-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-title);
  letter-spacing: 0.1em;
  margin: 0.2rem 0 0;
}
.topbar-back {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.3em;
  color: var(--text-muted);
  border: 0.5px solid var(--line-soft);
  padding: 8px 14px;
  transition: color 0.2s, border-color 0.2s;
  text-decoration: none;
}
.topbar-back:hover {
  color: var(--accent);
  border-color: var(--accent);
}

/* ---------- 主版面 ---------- */
.map-stage {
  display: grid;
  grid-template-columns: 1fr 460px;
  height: calc(100vh - 90px);
  min-height: 540px;
}
@media (max-width: 880px) {
  .map-stage {
    grid-template-columns: 1fr;
    height: auto;
  }
}

/* ---------- 左：地圖 ---------- */
.map-pane {
  position: relative;
  background: var(--bg-main);
}
@media (max-width: 880px) {
  .map-pane { height: 60vh; min-height: 380px; border-bottom: 0.5px solid var(--line-thin); }
}
#leaflet-map {
  width: 100%;
  height: 100%;
  background: #0E0B08;
}

/* Leaflet：與我們深色版的視覺對齊 */
.leaflet-container {
  font-family: var(--font-sans);
  background: #0E0B08;
}
.leaflet-control-zoom {
  border: 0.5px solid var(--line-soft) !important;
  box-shadow: none !important;
}
.leaflet-control-zoom a {
  background: rgba(43, 37, 32, 0.85) !important;
  color: var(--text-title) !important;
  border-color: var(--line-thin) !important;
}
.leaflet-control-zoom a:hover {
  background: rgba(43, 37, 32, 1) !important;
  color: var(--accent) !important;
}
.leaflet-control-attribution {
  background: rgba(14, 11, 8, 0.7) !important;
  color: var(--text-muted) !important;
  font-size: 10px !important;
  letter-spacing: 0.1em;
}
.leaflet-control-attribution a {
  color: var(--text-second) !important;
}

/* 自製 marker：圓點 + pulse 環 */
.event-marker {
  position: relative;
  width: 22px; height: 22px;
}
.event-marker .dot {
  position: absolute; inset: 6px;
  border-radius: 50%;
  background: var(--m-color);
  border: 1.5px solid #F5F1EA;
  box-shadow: 0 0 0 2px rgba(14, 11, 8, 0.6);
  cursor: pointer;
  transition: transform 0.2s;
}
.event-marker .pulse {
  position: absolute; inset: 0;
  border-radius: 50%;
  border: 1px solid var(--m-color);
  opacity: 0;
  animation: m-pulse 2.4s ease-out infinite;
  pointer-events: none;
}
.event-marker.is-active .dot {
  transform: scale(1.3);
}
@keyframes m-pulse {
  0%   { transform: scale(0.5); opacity: 0.7; }
  80%  { transform: scale(1.5); opacity: 0; }
  100% { transform: scale(1.5); opacity: 0; }
}

/* 標籤 tooltip */
.event-marker-tooltip {
  background: rgba(43, 37, 32, 0.92) !important;
  border: 0.5px solid var(--line-soft) !important;
  color: var(--text-title) !important;
  font-family: var(--font-serif) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.05em !important;
  padding: 4px 10px !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}
.event-marker-tooltip::before { display: none !important; }
.leaflet-tooltip-right.event-marker-tooltip { margin-left: 12px; }
.leaflet-tooltip-left.event-marker-tooltip  { margin-right: 12px; }

.tt-year {
  display: block;
  font-family: var(--font-sans);
  font-size: 10px;
  letter-spacing: 0.25em;
  font-weight: 400;
  color: var(--text-muted);
  margin-top: 2px;
}

/* ---------- 右：資訊面板 ---------- */
.info-pane {
  padding: 2.4rem 2rem;
  background: var(--bg-page);
  position: relative;
  overflow-y: auto;
  border-left: 0.5px solid var(--line-thin);
}
@media (max-width: 880px) {
  .info-pane { border-left: none; }
}
.panel-eyebrow {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.4em;
  color: var(--text-muted);
  margin-bottom: 1.4rem;
}
.panel-hero-img {
  display: block;
  width: 100%;
  height: 180px;
  object-fit: cover;
  object-position: center;
  border-radius: 8px;
  margin-bottom: 1.6rem;
  opacity: 0.88;
  border: 0.5px solid var(--line-thin);
}

/* 預設面板 */
.panel-empty-title {
  font-size: clamp(22px, 2.6vw, 30px);
  font-weight: 600;
  color: var(--text-title);
  margin: 0 0 1.4rem;
  letter-spacing: 0.04em;
  line-height: 1.4;
}
.panel-empty-body {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-second);
  max-width: 380px;
}
.panel-empty-hint {
  font-family: var(--font-sans);
  font-size: 12px;
  letter-spacing: 0.3em;
  color: var(--accent);
  margin-top: 2.4rem;
}
.panel-empty-foot {
  font-family: var(--font-sans);
  font-size: 10px;
  letter-spacing: 0.25em;
  color: var(--text-muted);
  margin-top: 2rem;
}
.hint-arrow { display: inline-block; margin-right: 8px; }
@media (max-width: 880px) {
  .hint-arrow { display: none; }
}

/* 已選事件面板 */
.panel-event-meta {
  display: flex; gap: 1rem; align-items: baseline;
  margin-bottom: 0.6rem;
}
.panel-event-year {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.2em;
}
.panel-event-eng {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.3em;
  color: var(--text-muted);
}
.panel-event-name {
  font-size: clamp(26px, 3vw, 36px);
  font-weight: 600;
  color: var(--text-title);
  margin: 0 0 0.4rem;
  letter-spacing: 0.04em;
}
.panel-event-place {
  font-family: var(--font-sans);
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--text-second);
  margin: 0 0 1.2rem;
}
.panel-event-tagline {
  font-size: 15px;
  color: var(--text-second);
  font-style: italic;
  line-height: 1.85;
  border-left: 2px solid;
  padding-left: 1rem;
  margin: 0 0 2rem;
  max-width: 380px;
}
.panel-event-count {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.3em;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
}

/* 引文卡 */
.quote-list { display: flex; flex-direction: column; gap: 1.2rem; }
.quote-card {
  background: var(--bg-card);
  padding: 1.4rem 1.4rem 1.2rem;
  border-left: 3px solid;
  position: relative;
}
.quote-prompt {
  font-family: var(--font-sans);
  font-size: 10px;
  letter-spacing: 0.3em;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
}
.quote-text {
  font-family: var(--font-serif);
  font-size: 15px;
  line-height: 1.85;
  color: var(--text-primary);
  margin: 0 0 0.8rem;
}
.quote-byline {
  font-family: var(--font-sans);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  text-align: right;
}
.quote-empty {
  font-family: var(--font-sans);
  font-size: 13px;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  padding: 1.2rem;
  text-align: center;
  border: 0.5px dashed var(--line-soft);
}

.panel-close {
  position: absolute;
  top: 1.2rem; right: 1.2rem;
  background: none;
  border: 0.5px solid var(--line-soft);
  color: var(--text-muted);
  width: 32px; height: 32px;
  cursor: pointer;
  font-size: 16px;
  font-family: var(--font-sans);
  line-height: 1;
  transition: color 0.2s, border-color 0.2s;
}
.panel-close:hover { color: var(--accent); border-color: var(--accent); }

/* 底部 */
.map-foot {
  text-align: center;
  padding: 1.2rem 2rem 1.8rem;
  font-family: var(--font-sans);
  font-size: 10px;
  letter-spacing: 0.3em;
  color: var(--text-muted);
  border-top: 0.5px solid var(--line-thin);
}
'''


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def build_html(class_data):
    class_data = with_masked_names(class_data)
    students = class_data['students']
    meta = class_data['meta']

    panel_data = render_panel_data(students)
    panel_data_json = json.dumps(panel_data, ensure_ascii=False)

    default_panel = render_default_panel_html(len(students))
    default_panel_json = json.dumps(default_panel, ensure_ascii=False)

    html_doc = f'''<!DOCTYPE html>
<html lang="zh-Hant" class="theme-dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>縱谷無言．事件地圖｜{esc(meta.get('school', ''))}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin=""/>
<link rel="stylesheet" href="../assets/styles/design_tokens.css">
<style>{CSS}</style>
</head>
<body>

<header class="topbar">
  <div>
    <div class="topbar-eyebrow">{esc(meta.get('school', ''))}　‧　{esc(meta.get('course', ''))}</div>
    <h1 class="topbar-title">縱谷無言．事件地圖</h1>
  </div>
  <a href="class_showcase.html" class="topbar-back">← 班級成果</a>
</header>

<main class="map-stage">

  <section class="map-pane">
    <div id="leaflet-map" role="region" aria-label="花蓮縣事件地圖"></div>
  </section>

  <aside class="info-pane" id="info-pane">
    {default_panel}
  </aside>

</main>

<footer class="map-foot">
  花蓮高商．多元文化與文學．原住民族單元　‧　共 {len(students)} 位學生　‧　地圖底圖：© OpenStreetMap、© CARTO
</footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
<script>
  const PANEL_DATA = {panel_data_json};
  const DEFAULT_HTML = {default_panel_json};

  const pane = document.getElementById('info-pane');
  let activeId = null;
  const markers = {{}};

  // ---------- 地圖 ----------
  const map = L.map('leaflet-map', {{
    center: [23.75, 121.40],
    zoom: 9,
    minZoom: 8,
    maxZoom: 14,
    zoomControl: true,
    attributionControl: true,
    scrollWheelZoom: true,
  }});

  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }}).addTo(map);

  // ---------- Marker：自製 div icon ----------
  function makeIcon(color) {{
    return L.divIcon({{
      className: '',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
      html: `<div class="event-marker" style="--m-color: ${{color}};">
               <div class="pulse"></div>
               <div class="dot"></div>
             </div>`
    }});
  }}

  Object.keys(PANEL_DATA).forEach(eid => {{
    const ev = PANEL_DATA[eid];
    const m = L.marker([ev.lat, ev.lng], {{
      icon: makeIcon(ev.color),
      keyboard: true,
      title: ev.name + ' ' + ev.year,
    }}).addTo(map);

    m.bindTooltip(`${{ev.name}}<span class="tt-year">${{ev.year}}　${{ev.count}} 位學生</span>`, {{
      permanent: true,
      direction: 'right',
      offset: [12, 0],
      className: 'event-marker-tooltip',
      interactive: false,
    }});

    m.on('click', () => selectEvent(eid));
    markers[eid] = m;
  }});

  // 自動 fit 到四個事件範圍
  const bounds = L.latLngBounds(Object.values(PANEL_DATA).map(e => [e.lat, e.lng]));
  map.fitBounds(bounds, {{ padding: [60, 80] }});

  // ---------- Panel ----------
  function escapeHtml(s) {{
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }}

  function selectEvent(eid) {{
    const ev = PANEL_DATA[eid];
    if (!ev) return;
    activeId = eid;

    // marker 視覺
    Object.entries(markers).forEach(([id, m]) => {{
      const el = m.getElement && m.getElement();
      if (el) {{
        const inner = el.querySelector('.event-marker');
        if (inner) inner.classList.toggle('is-active', id === eid);
      }}
    }});

    // 平移到該點
    map.panTo([ev.lat, ev.lng], {{ animate: true, duration: 0.5 }});

    let quotesHtml = '';
    if (ev.quotes.length === 0) {{
      quotesHtml = '<div class="quote-empty">這個事件還沒有學生作品</div>';
    }} else {{
      quotesHtml = ev.quotes.map(q => `
        <article class="quote-card" style="border-left-color: ${{ev.color}};">
          <div class="quote-prompt" style="color: ${{ev.color}};">${{escapeHtml(q.prompt)}}</div>
          <p class="quote-text">${{escapeHtml(q.text)}}</p>
          <div class="quote-byline">— ${{escapeHtml(q.class_name)}}　${{escapeHtml(q.seat)}}　${{escapeHtml(q.name)}}</div>
        </article>
      `).join('');
    }}

    pane.innerHTML = `
      <button class="panel-close" id="panel-close" aria-label="返回">×</button>
      <img class="panel-hero-img" src="${{ev.image}}" alt="">
      <div class="panel-eyebrow" style="color: ${{ev.color}};">${{escapeHtml(ev.ethnic)}}</div>
      <div class="panel-event-meta">
        <span class="panel-event-year" style="color: ${{ev.color}};">${{escapeHtml(ev.year)}}</span>
        <span class="panel-event-eng">${{escapeHtml(ev.eng)}}</span>
      </div>
      <h2 class="panel-event-name">${{escapeHtml(ev.name)}}</h2>
      <p class="panel-event-place">${{escapeHtml(ev.place)}}</p>
      <p class="panel-event-tagline" style="border-left-color: ${{ev.color}};">${{escapeHtml(ev.tagline)}}</p>
      <div class="panel-event-count">學生省思亮點　‧　共 ${{ev.count}} 位學生</div>
      <div class="quote-list">${{quotesHtml}}</div>
    `;
    document.getElementById('panel-close').addEventListener('click', resetPane);

    if (window.innerWidth < 880) {{
      pane.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
  }}

  function resetPane() {{
    activeId = null;
    Object.values(markers).forEach(m => {{
      const el = m.getElement && m.getElement();
      if (el) {{
        const inner = el.querySelector('.event-marker');
        if (inner) inner.classList.remove('is-active');
      }}
    }});
    pane.innerHTML = DEFAULT_HTML;
    map.fitBounds(bounds, {{ padding: [60, 80] }});
  }}

  document.addEventListener('keydown', e => {{
    if (e.key === 'Escape' && activeId) resetPane();
  }});
</script>

</body>
</html>
'''
    return html_doc


def main():
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f'找不到資料檔：{INPUT_JSON}')

    data = json.loads(INPUT_JSON.read_text(encoding='utf-8'))
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    html_doc = build_html(data)
    OUTPUT_HTML.write_text(html_doc, encoding='utf-8')

    size_kb = OUTPUT_HTML.stat().st_size // 1024
    print(f'已輸出：{OUTPUT_HTML.relative_to(ROOT)}')
    print(f'  學生：{len(data["students"])} 位')
    print(f'  地圖：Leaflet + OpenStreetMap (CARTO Dark Matter)')
    print(f'  檔案：{size_kb} KB')


if __name__ == '__main__':
    main()
