import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON = ROOT / "data" / "class_data.json"
OUTPUT_HTML = ROOT / "outputs" / "class_showcase.html"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import with_masked_names

EVENTS = {
    "cepo": {"name": "大港口事件", "color": "--color-cepo-dark", "image": "event_cepo.png"},
    "dafen": {"name": "大分事件", "color": "--color-dafen-dark", "image": "event_dafen.png"},
    "cikasuan": {"name": "七腳川事件", "color": "--color-cikasuan-dark", "image": "event_cikasuan.png"},
    "truku": {"name": "太魯閣戰役", "color": "--color-truku-dark", "image": "event_truku.png"},
}
EVENT_ORDER = ["cepo", "dafen", "cikasuan", "truku"]
STANCE_WORDS = ["平定", "征討", "叛亂", "討伐", "歸順"]


def esc(value):
    return html.escape(str(value or ""))


def sentence(student, key):
    show = student.get("showcase_sentences", {})
    if show.get(key):
        return show[key]
    legacy = student.get("legacy_supplement") or {}
    if key == "reflection":
        return (legacy.get("reflections") or {}).get("q3", "")
    if key == "difference":
        return (student.get("perspectives") or {}).get("difference") or (student.get("perspectives") or {}).get("differences", "")
    return (student.get("facts") or {}).get("time", "")


def mark_original(text):
    out = esc(text)
    for word in STANCE_WORDS:
        out = out.replace(esc(word), f"<s>{esc(word)}</s>")
    return out


def score_box(grading):
    labels = [("basic", "基本事實"), ("ai_use", "AI 使用"), ("perspective", "立場比較"), ("showcase", "展示句")]
    rows = []
    for key, label in labels:
        value = grading.get(key)
        rows.append(f"<div><span>{label}</span><strong>{'' if value is None else esc(value)} / 2</strong></div>")
    return "\n".join(rows)


def source_list(sources):
    if not sources:
        return "<li>未填寫</li>"
    items = []
    for src in sources:
        page = f"｜{esc(src.get('pdf_page'))}" if src.get("pdf_page") else ""
        url = f"<div class=\"url\">{esc(src.get('url'))}</div>" if src.get("url") else ""
        items.append(f"<li><strong>{esc(src.get('title'))}</strong>{page}{url}</li>")
    return "\n".join(items)


def render_card(student):
    ev = EVENTS.get(student.get("event"), EVENTS["cikasuan"])
    ai = student.get("ai_process", {})
    per = student.get("perspectives", {})
    grading = student.get("grading", {})
    return f"""
<article class="card" style="--event-color:var({ev['color']})">
  <div class="strip"></div>
  <div class="card-main">
    <header>
      <div class="meta">{esc(student.get('class_name'))}　{esc(student.get('seat'))}　{esc(student.get('name'))}</div>
      <h2>{esc(ev['name'])}</h2>
    </header>
    <section class="sentences">
      <p><span>事實句</span><strong>{esc(sentence(student, 'fact'))}</strong></p>
      <p><span>差異句</span><strong>{esc(sentence(student, 'difference'))}</strong></p>
      <p><span>省思句</span><strong>{esc(sentence(student, 'reflection'))}</strong></p>
    </section>
    <details>
      <summary>AI process / 改寫 / 來源</summary>
      <div class="details-grid">
        <section>
          <h3>AI 使用過程</h3>
          <p><b>問題：</b>{esc(ai.get('question'))}</p>
          <p><b>重點：</b>{esc('；'.join(ai.get('ai_points', [])))}</p>
          <p><b>關鍵詞：</b>{esc('、'.join(ai.get('keywords', [])))}</p>
          <p><b>查證紀錄：</b>{esc(ai.get('process_log') or ai.get('verify_log'))}</p>
        </section>
        <section>
          <h3>AI 原句 → 改寫</h3>
          <p class="rewrite"><span>{mark_original(ai.get('original_ai_sentence'))}</span><b>{esc(ai.get('revised_sentence'))}</b></p>
          <p>{esc(ai.get('revision_reason'))}</p>
        </section>
        <section>
          <h3>立場比較</h3>
          <p><b>官方：</b>{esc(per.get('official'))}</p>
          <p><b>部落／族人：</b>{esc(per.get('tribal'))}</p>
          <p><b>差異：</b>{esc(per.get('difference') or per.get('differences'))}</p>
        </section>
        <section>
          <h3>資料來源</h3>
          <ul>{source_list(student.get('sources', []))}</ul>
        </section>
      </div>
    </details>
  </div>
  <aside class="score">{score_box(grading)}</aside>
</article>
"""


CSS = r"""
*{box-sizing:border-box} body{margin:0;background:var(--bg-page);color:var(--text-primary);font-family:var(--font-serif)}
.wrap{max-width:1180px;margin:0 auto;padding:28px}.hero{min-height:360px;padding:28px 28px 22px;display:grid;align-content:end;background:linear-gradient(90deg,rgba(0,0,0,.48),rgba(0,0,0,.08)),url("../assets/images/hero_valley.png") center/cover no-repeat;border-radius:8px;overflow:hidden}.hero h1{margin:0;color:#fff;font-size:42px;letter-spacing:0;text-shadow:0 2px 16px rgba(0,0,0,.32)}.hero p{color:rgba(255,255,255,.86);font-family:var(--font-sans)}
.nav{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 22px}.nav a{font-family:var(--font-sans);font-size:12px;color:var(--text-primary);border:1px solid var(--line-soft);padding:7px 10px;text-decoration:none;border-radius:999px}
.hero .nav a{color:#fff;border-color:rgba(255,255,255,.42);background:rgba(0,0,0,.12)}.event{margin:26px 0}.event h2{font-size:28px;color:var(--text-title);letter-spacing:0}.event-image{width:100%;height:230px;object-fit:cover;border-radius:8px;margin:0 0 14px;opacity:.82}.grid{display:grid;gap:16px}
.empty{margin:0;padding:18px;border:1px dashed var(--line-soft);border-radius:8px;color:var(--text-muted);font-family:var(--font-sans)}
.card{display:grid;grid-template-columns:6px minmax(0,1fr) 170px;background:var(--bg-card);border:1px solid var(--line-soft);border-radius:8px;overflow:hidden}
.strip{background:var(--event-color)}.card-main{padding:18px}.meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);letter-spacing:.12em}.card h2{margin:3px 0 12px;font-size:24px;color:var(--text-title)}
.sentences{display:grid;gap:10px}.sentences p{margin:0;border-left:4px solid var(--event-color);padding:9px 12px;background:rgba(0,0,0,.035)}.sentences span{display:block;font-family:var(--font-sans);font-size:12px;color:var(--text-muted)}.sentences strong{display:block;font-size:22px;line-height:1.55;color:var(--text-title)}
details{margin-top:14px;border-top:1px solid var(--line-thin);padding-top:10px}summary{cursor:pointer;font-family:var(--font-sans);color:var(--text-second)}.details-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:10px}.details-grid section{border:1px solid var(--line-thin);padding:10px;border-radius:6px}.details-grid h3{margin:0 0 6px;color:var(--text-title);font-size:16px}.details-grid p,.details-grid li{font-size:14px;line-height:1.7}.url{font-family:monospace;font-size:11px;word-break:break-all;color:var(--text-muted)}
.rewrite{display:grid;gap:8px}.rewrite span{border:1px dashed var(--line-soft);padding:8px}.rewrite b{background:rgba(217,164,65,.28);padding:8px;color:var(--text-title)}s{color:#b84741;text-decoration-thickness:2px}
.score{border-left:1px solid var(--line-thin);padding:14px;background:rgba(0,0,0,.035);display:grid;align-content:start;gap:8px}.score div{display:flex;justify-content:space-between;gap:8px;font-family:var(--font-sans);font-size:12px}.score strong{color:var(--event-color)}
@media(max-width:760px){.card{grid-template-columns:5px 1fr}.score{grid-column:2;border-left:0;border-top:1px solid var(--line-thin)}.details-grid{grid-template-columns:1fr}.sentences strong{font-size:18px}}
"""


def build_html(data):
    data = with_masked_names(data)
    students = data.get("students", [])
    sections = []
    for eid in EVENT_ORDER:
        group = [s for s in students if s.get("event") == eid]
        ev = EVENTS[eid]
        cards = "\n".join(render_card(s) for s in group) or "<p class=\"empty\">尚無學生卡片。</p>"
        sections.append(f"<section class=\"event\" id=\"{eid}\"><h2>{esc(ev['name'])}</h2><img class=\"event-image\" src=\"../assets/images/{esc(ev['image'])}\" alt=\"\" loading=\"lazy\"><div class=\"grid\">{cards}</div></section>")
    nav = "".join(f"<a href=\"#{eid}\">{esc(EVENTS[eid]['name'])}</a>" for eid in EVENT_ORDER)
    inline = json.dumps(data, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant" class="theme-dark"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>事件理解卡成果展示</title><link rel="stylesheet" href="../assets/styles/design_tokens.css"><style>{CSS}</style></head>
<body class="theme-dark weave-pattern"><main class="wrap"><header class="hero"><div class="event-color-bar"><div class="seg-cepo"></div><div class="seg-dafen"></div><div class="seg-cikasuan"></div><div class="seg-truku"></div></div><h1>事件理解卡成果展示</h1><p>姓名已屏蔽；資料由 data/class_data.json 產生。</p><nav class="nav">{nav}</nav></header>{''.join(sections)}</main><script id="class-data" type="application/json">{inline}</script></body></html>"""


def main():
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(build_html(data), encoding="utf-8")
    print(f"wrote {OUTPUT_HTML.relative_to(ROOT)} ({OUTPUT_HTML.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
