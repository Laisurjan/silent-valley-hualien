"""
Build the 0604 professor-facing learning exhibit.

Inputs are the local NotebookLM exports and media files listed in
0604_成果網頁兩週工作清單.md. The script keeps the existing class_showcase.html
unchanged and writes a standalone exhibit page:

  outputs/ai_history_learning_exhibit.html
  data/0604_exhibit_data.json
  outputs/media/notebooklm/*
"""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = Path(r"C:\Users\godof\Downloads\0604\notebooklm_exports")
MEDIA_DIR = Path(r"C:\Users\godof\Downloads\0604\notebooklm_media")
OUTPUT_HTML = ROOT / "outputs" / "ai_history_learning_exhibit.html"
OUTPUT_JSON = ROOT / "data" / "0604_exhibit_data.json"
OUTPUT_MEDIA = ROOT / "outputs" / "media" / "notebooklm"


EVENTS = {
    "cepo": {
        "name": "大港口事件 / Cepo'",
        "years": "1877-1878",
        "ethnic": "阿美族・秀姑巒溪口部落",
        "place": "花蓮縣豐濱鄉靜浦、Makuta'ay 一帶",
        "image": "../assets/images/event_cepo.png",
        "color": "var(--color-cepo-dark)",
        "brief": "學生從清帝國治理、阿美族口述記憶與地名變遷切入，理解同一事件如何被寫成招撫、衝突、誘殺或族群創傷。",
        "focus": ["官方治理語言", "阿美族記憶", "遷徙與創傷", "地名與地景改寫"],
        "keywords": ["cepo", "makuta", "大港口", "阿美", "jingpu", "amis"],
    },
    "truku": {
        "name": "太魯閣戰役",
        "years": "1896-1914",
        "ethnic": "太魯閣族",
        "place": "立霧溪、木瓜溪上游與太魯閣口",
        "image": "../assets/images/event_truku.png",
        "color": "var(--color-truku-dark)",
        "brief": "展區呈現學生如何把 1914 年戰役放回更長的抵抗脈絡，看見 Gaya、山地治理、槍械收繳與主權衝突。",
        "focus": ["長期抵抗", "Gaya 與主權", "山地治理", "觀光地景背後的歷史"],
        "keywords": ["truku", "taroko", "太魯閣"],
    },
    "dafen": {
        "name": "大分事件 / 布農族抗爭",
        "years": "1914-1933",
        "ethnic": "布農族",
        "place": "花蓮縣卓溪鄉、大分與拉庫拉庫溪流域",
        "image": "../assets/images/event_dafen.png",
        "color": "var(--color-dafen-dark)",
        "brief": "學生整理大分事件時，將交易所、槍枝收押、生計壓力與拉荷・阿雷的長期抵抗放在同一條歷史線上。",
        "focus": ["收押槍枝", "交易所制度", "生計衝突", "1914-1933 長期抗爭"],
        "keywords": ["dafen", "dafa", "bunun", "大分", "布農", "yushan"],
    },
    "cikasuan": {
        "name": "七腳川事件 / Cikasuan",
        "years": "1908-1914",
        "ethnic": "阿美族・南勢阿美",
        "place": "花蓮縣吉安鄉七腳川溪流域",
        "image": "../assets/images/event_cikasuan.png",
        "color": "var(--color-cikasuan-dark)",
        "brief": "展區聚焦土地、勞役與殖民治理，並把學生的觀點比較整理成官方秩序與族群生存之間的差異。",
        "focus": ["土地剝奪", "勞役與治理", "族群遷徙", "阿美族韌性"],
        "keywords": ["cikasuan", "七腳川"],
    },
}

EVENT_ORDER = ["cepo", "truku", "dafen", "cikasuan"]

GLOBAL_REFERENCE_SOURCES = {
    "大港口事件 / Cepo'": [
        "原民會叢書-大港口事件1877-1878.pdf",
        "國教院補充教材-大港口事件.pdf",
        "140年前「大港口事件」阿美族遭清兵殺戮 - 公視新聞網 PNN",
        "靜浦考古遺址｜國家文化記憶庫",
        "大港口Cepo'事件口傳歷史寫生/聲及其對應之阿美族文化智慧調查與研究報告書",
        "南島近代史-清領時期【ZALAN見識南島】第三季逐字稿",
    ],
    "太魯閣戰役": [
        "原民會叢書-太魯閣事件1914.pdf",
        "國教院補充教材-太魯閣事件.pdf",
        "太魯閣戰爭百年回顧.pdf",
        "太魯閣事件-1914 Tnegjyalan Truku",
        "太魯閣-歷史背景 - 原住民族文化事業基金會",
        "太魯閣國家公園全球資訊網｜蘇花道今昔",
    ],
    "大分事件 / 布農族抗爭": [
        "原民會叢書-大分事件1914-1933.pdf",
        "國教院補充教材-大分事件.pdf",
        "1915年Dahu Ali（拉荷・阿雷）發動布農族大分抗日事件說之探討",
        "先祖「大分事件」抗日百年故事 - 國家文化記憶庫",
        "大分事件 - 國家文化記憶庫",
        "大分事件 - 臺灣原住民族事典",
        "大分事件一百周年紀念回顧 - 原住民族文獻",
    ],
    "七腳川事件 / Cikasuan": [
        "原民會叢書-七腳川事件1908-1914.pdf",
        "國教院補充教材-七腳川事件.pdf",
        "原住民族重大歷史事件：七腳川事件故事地圖系列",
        "The Cikasuan Incident 1908-1914 NotebookLM 來源資料",
    ],
}

MINDMAP_MANIFEST = [
    {
        "student": "余OO",
        "event": "unknown",
        "title": "學生上傳 PNG 心智圖 / 截圖 1",
        "file_name": "unnamed (1).png",
        "id": "1-SAv2DNcviPutduwYgvtJ-z1oySPP7Aw",
    },
    {
        "student": "余OO",
        "event": "unknown",
        "title": "學生上傳 PNG 心智圖 / 截圖 2",
        "file_name": "unnamed.png",
        "id": "1CA_y5gA6G9MSX_XrbPeVSMgeZk8C_GCT",
    },
    {
        "student": "杜OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1_gzIMmIjulLc_8OHckCn6GxcwHau1pMl",
    },
    {
        "student": "蔡OO",
        "event": "cepo",
        "title": "大港口事件 NotebookLM 心智圖",
        "file_name": "NotebookLM Mind Map (2).png",
        "id": "1JyEVL3idjt9-OA2fa1vai1sIEwNRO3MX",
    },
    {
        "student": "蔡OO",
        "event": "cepo",
        "title": "大港口事件 NotebookLM 輸出截圖",
        "file_name": "unnamed.png",
        "id": "1SIscvG9OGMDOpmtYBM_xQxgM1ONSi5rq",
    },
    {
        "student": "張OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "17xdEjz_mZZAQ03uWDEnRqPjlAIrrDYDK",
    },
    {
        "student": "潘OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1pjtgbuspq5LW-GPBawGNFR8Mtty_eUb7",
    },
    {
        "student": "梁OO",
        "event": "dafen",
        "title": "大分事件 NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1CIBkv6kyN3VXTC6eXBPGGvVcGi-qMiBM",
    },
    {
        "student": "張OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map (1).png",
        "id": "1mkJDFA2BvL63Lp3RODvl_51dwsWHhZT-",
    },
    {
        "student": "鍾OO",
        "event": "cepo",
        "title": "大港口事件心智圖",
        "file_name": "大港口事件-心智圖.png",
        "id": "1zvnaercNuEX32qNyRk-O9hQRRajQrQoE",
    },
    {
        "student": "林OO",
        "event": "unknown",
        "title": "學生上傳 PNG 心智圖 / 截圖",
        "file_name": "unnamed.png",
        "id": "1dVu0XbHZyxY5vlKM13qrqEXVfrmNR1hy",
    },
    {
        "student": "林OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1aDSdfdcfwF0YhJV4epuczPbzVa9YjIOD",
    },
    {
        "student": "吳OO",
        "event": "unknown",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map (1).png",
        "id": "1XD_iWOUzmjpiji30Acx5qQFzimmw9Hno",
    },
    {
        "student": "李OO",
        "event": "unknown",
        "title": "學生上傳 PNG 心智圖 / 截圖",
        "file_name": "unnamed.png",
        "id": "14HFghxXwt4j1yy_IdZzg_XPj_HD7BdbQ",
    },
]

MEDIA_MANIFEST = [
    {
        "event": "cepo",
        "kind": "video",
        "source": "1877-1878大港口事件解析.mp4",
        "target": "cepo-1877-1878-analysis.mp4",
        "title": "1877-1878 大港口事件解析",
        "note": "NotebookLM 影片生成成果，適合放在大港口展區作為事件導覽。",
    },
    {
        "event": "cepo",
        "kind": "video",
        "source": "1877大港口事件：帝國擴張與原民抗爭.mp4",
        "target": "cepo-empire-resistance.mp4",
        "title": "帝國擴張與原民抗爭",
        "note": "以帝國治理與原民抵抗為主軸，呈現學生用 AI 重組敘事的嘗試。",
    },
    {
        "event": "truku",
        "kind": "video",
        "source": "太魯閣事件：18年的抗日戰役.mp4",
        "target": "truku-18-year-war.mp4",
        "title": "太魯閣事件：18 年的抗日戰役",
        "note": "把太魯閣戰役放回長期抵抗脈絡，提醒觀眾不要只看單一年份。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "大港口事件的血腥真相.m4a",
        "target": "cepo-bloody-truth.m4a",
        "title": "大港口事件的血腥真相",
        "note": "NotebookLM 音訊成果，適合展示 AI 如何把史料轉成口語導覽。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "Take_your_story_back_from_narrative_theft.m4a",
        "target": "narrative-theft.m4a",
        "title": "Take your story back from narrative theft",
        "note": "英文音訊成果，可用來說明敘事權與歷史詮釋的課程主題。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/1877-1878大港口事件解析.mp3",
        "target": "cepo-1877-1878-analysis.mp3",
        "title": "1877-1878 大港口事件解析 MP3",
        "note": "測試轉檔版本，提供網頁播放器較穩定的音訊備用。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/1877大港口事件：帝國擴張與原民抗爭.mp3",
        "target": "cepo-empire-resistance.mp3",
        "title": "帝國擴張與原民抗爭 MP3",
        "note": "測試轉檔版本，提供網頁播放器較穩定的音訊備用。",
    },
    {
        "event": "truku",
        "kind": "audio",
        "source": "mp3/太魯閣事件：18年的抗日戰役.mp3",
        "target": "truku-18-year-war.mp3",
        "title": "太魯閣事件 18 年抗日戰役 MP3",
        "note": "影片轉音訊版本，手機展示時載入較快。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/大港口事件的血腥真相.mp3",
        "target": "cepo-bloody-truth.mp3",
        "title": "大港口事件的血腥真相 MP3",
        "note": "M4A 的測試轉檔版本，供瀏覽器相容性備用。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/Take_your_story_back_from_narrative_theft.mp3",
        "target": "narrative-theft.mp3",
        "title": "Narrative theft MP3",
        "note": "英文音訊的測試轉檔版本，供瀏覽器相容性備用。",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def classify_event(text: str) -> str:
    low = text.lower()
    for event_id, event in EVENTS.items():
        if any(keyword.lower() in low for keyword in event["keywords"]):
            return event_id
    return "cepo"


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_export_noise(text: str) -> str:
    skip_exact = {
        "group",
        "共用",
        "add",
        "建立筆記本",
        "settings",
        "設定",
        "來源",
        "全選",
        "對話",
        "more_vert",
        "copy_all",
        "thumb_up",
        "thumb_down",
        "工作室",
        "工作室輸出內容深入淺出，透過影像和音訊介紹筆記本的主題！",
        "play_arrow",
        "table_view",
        "flowchart",
        "stacked_bar_chart",
        "audio_magic_eraser",
        "subscriptions",
        "keyboard_arrow_right",
        "dock_to_left",
        "dock_to_right",
        "arrow_forward",
        "landscape_2",
        "auto_tab_group",
        "tablet",
        "🪦",
    }
    filtered = []
    for raw in clean_text(text).splitlines():
        line = raw.strip()
        if not line:
            filtered.append("")
            continue
        if re.match(r"^(Notebook|Notebook URL|Output|Detected title|Media output):", line):
            continue
        if line in skip_exact:
            continue
        if re.match(r"^\d+ 個來源|^\d{4}年\d+月\d+日|^·$|^Study Guide ·", line):
            continue
        has_sentence_mark = bool(re.search(r"[。！？；：，,.!?;:]", line))
        if len(line) <= 16 and not has_sentence_mark:
            continue
        filtered.append(line)
    return "\n".join(filtered)


def readable_paragraphs(text: str, limit: int = 2) -> list[str]:
    text = strip_export_noise(text)
    selected = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 70:
            continue
        if line.startswith("這個產出在 NotebookLM"):
            continue
        if "NotebookLM 中以影片/音訊播放器呈現" in line:
            continue
        if line.lower().count(".pdf") >= 2 or line.count("http") >= 1:
            continue
        if len(re.findall(r"｜|- 維基百科|公視|資訊網|基金會|逐字稿", line)) >= 3:
            continue
        if not re.search(r"[。！？.!?]", line):
            continue
        if len(line) > 260:
            line = line[:250].rstrip("，,；;。.") + "..."
        selected.append(line)
        if len(selected) >= limit:
            return selected

    chunks = re.split(r"\n\s*\n|(?<=。)\s*\n|(?<=\.)\s*\n", text)
    for chunk in chunks:
        chunk = re.sub(r"^[#*\-\d.、\s]+", "", chunk).strip()
        if len(chunk) < 70 or "Error" in chunk or "無法" in chunk or "Notebook URL" in chunk:
            continue
        if chunk.lower().count(".pdf") >= 2 or chunk.count("http") >= 1:
            continue
        if chunk.startswith("這個產出在 NotebookLM"):
            continue
        if not re.search(r"[。！？.!?]", chunk):
            continue
        if len(chunk) > 260:
            chunk = chunk[:250].rstrip("，,；;。.") + "..."
        selected.append(chunk)
        if len(selected) >= limit:
            break
    return selected


def collect_notebook_outputs() -> tuple[list[dict], dict[str, list[dict]]]:
    notebooks = []
    grouped = {event_id: [] for event_id in EVENTS}
    for folder in sorted(p for p in EXPORT_DIR.iterdir() if p.is_dir()):
        summary_path = folder / "_summary.json"
        txt_files = sorted(folder.glob("*.txt"))
        summary = {}
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        title = str(summary.get("notebook") or folder.name.split("_", 1)[-1])
        event_id = classify_event(folder.name + " " + title)
        samples = []
        output_titles = []
        for txt in txt_files:
            if txt.name.endswith("_ERROR.txt"):
                continue
            output_titles.append(txt.stem)
            for paragraph in readable_paragraphs(txt.read_text(encoding="utf-8", errors="ignore"), limit=1):
                samples.append({"title": txt.stem, "text": paragraph})
            if len(samples) >= 3:
                break

        item = {
            "folder": folder.name,
            "title": title,
            "event": event_id,
            "output_count": int(summary.get("outputCount") or len(txt_files)),
            "txt_count": len(txt_files),
            "json": summary_path.name if summary_path.exists() else "",
            "samples": samples[:3],
            "output_titles": output_titles[:5],
        }
        notebooks.append(item)
        grouped[event_id].append(item)
    return notebooks, grouped


def copy_media() -> list[dict]:
    OUTPUT_MEDIA.mkdir(parents=True, exist_ok=True)
    copied = []
    for item in MEDIA_MANIFEST:
        source = MEDIA_DIR / item["source"]
        target = OUTPUT_MEDIA / item["target"]
        status = "missing"
        size_mb = 0
        if source.exists():
            shutil.copy2(source, target)
            status = "copied"
            size_mb = round(target.stat().st_size / 1024 / 1024, 2)
        copied.append(
            {
                **item,
                "status": status,
                "size_mb": size_mb,
                "path": f"media/notebooklm/{item['target']}",
            }
        )
    return copied


def collect_mindmaps() -> list[dict]:
    mindmaps = []
    for item in MINDMAP_MANIFEST:
        file_id = item["id"]
        event_id = item["event"]
        mindmaps.append(
            {
                **item,
                "drive_url": f"https://drive.google.com/file/d/{file_id}/view",
                "preview_url": f"https://drive.google.com/file/d/{file_id}/preview",
            }
        )
    return mindmaps


def build_data() -> dict:
    notebooks, grouped = collect_notebook_outputs()
    media = copy_media()
    mindmaps = collect_mindmaps()
    by_event_media = {event_id: [] for event_id in EVENTS}
    for item in media:
        by_event_media[item["event"]].append(item)

    return {
        "meta": {
            "title": "AI 與原住民族歷史敘事學習展",
            "generated_at": "2026-06-04",
            "notebook_count": len(notebooks),
            "txt_count": sum(n["txt_count"] for n in notebooks),
            "json_count": len(list(EXPORT_DIR.rglob("*.json"))),
            "media_count": len([m for m in media if m["status"] == "copied"]),
            "mindmap_count": len(mindmaps),
            "source_exports": str(EXPORT_DIR),
            "source_media": str(MEDIA_DIR),
        },
        "events": [
            {
                "id": event_id,
                **{k: v for k, v in EVENTS[event_id].items() if k != "keywords"},
                "notebooks": grouped[event_id],
                "media": by_event_media[event_id],
            }
            for event_id in EVENT_ORDER
        ],
        "all_notebooks": notebooks,
        "mindmaps": mindmaps,
        "reference_sources": GLOBAL_REFERENCE_SOURCES,
    }


CSS = r"""
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg-main);color:var(--text-primary);font-family:var(--font-serif);line-height:1.75}.wrap{max-width:1180px;margin:0 auto;padding:0 24px}.hero{min-height:92vh;display:grid;align-content:end;background:linear-gradient(90deg,rgba(14,11,8,.82),rgba(14,11,8,.28)),url("../assets/images/hero_valley.png") center/cover no-repeat;border-bottom:1px solid var(--line-thin)}.hero-inner{max-width:1180px;margin:0 auto;width:100%;padding:44px 24px 52px}.eyebrow{font-family:var(--font-sans);font-size:12px;letter-spacing:.28em;color:var(--accent);text-transform:uppercase}.hero h1{font-size:52px;line-height:1.18;margin:12px 0 14px;color:#fff;letter-spacing:0}.hero p{max-width:760px;margin:0;color:rgba(245,241,234,.86);font-family:var(--font-sans);font-size:17px}.nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}.nav a{color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.28);padding:8px 12px;border-radius:8px;font-family:var(--font-sans);font-size:13px;background:rgba(0,0,0,.18)}.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:28px;max-width:920px}.stat{border:1px solid rgba(255,255,255,.22);border-radius:8px;padding:12px;background:rgba(14,11,8,.34)}.stat strong{display:block;color:#fff;font-size:28px;line-height:1.1}.stat span{font-family:var(--font-sans);font-size:12px;color:rgba(255,255,255,.72)}section{padding:56px 0;border-bottom:1px solid var(--line-thin)}h2{font-size:32px;color:var(--text-title);line-height:1.3;margin:0 0 10px;letter-spacing:0}.lead{max-width:820px;color:var(--text-second);font-family:var(--font-sans);margin:0 0 24px}.two-col{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);gap:26px;align-items:start}.event-head{display:grid;grid-template-columns:160px minmax(0,1fr);gap:18px;align-items:stretch}.event-head img{width:100%;height:100%;min-height:190px;object-fit:cover;border-radius:8px;border:1px solid var(--line-thin)}.event-title{border-left:5px solid var(--event-color);padding-left:16px}.event-title .years{font-family:var(--font-sans);font-size:13px;color:var(--event-color);letter-spacing:.18em}.event-title h3{font-size:30px;color:var(--text-title);margin:4px 0}.event-title p{margin:0;color:var(--text-second)}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.chip{border:1px solid var(--line-soft);border-radius:999px;padding:5px 9px;font-family:var(--font-sans);font-size:12px;color:var(--text-primary)}.panel{background:var(--bg-card);border:1px solid var(--line-soft);border-radius:8px;padding:18px}.panel h4{margin:0 0 10px;color:var(--text-title);font-size:18px}.notebook-list{display:grid;gap:12px}.notebook{border-left:3px solid var(--event-color);background:rgba(0,0,0,.12);padding:12px;border-radius:0 8px 8px 0}.notebook h5{margin:0 0 5px;color:var(--text-title);font-size:16px}.notebook .meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:8px}.quote{margin:8px 0 0;padding:10px;border:1px solid var(--line-thin);border-radius:8px}.quote b{display:block;font-family:var(--font-sans);font-size:12px;color:var(--event-color);margin-bottom:4px}.quote p{margin:0;font-size:14px;color:var(--text-primary)}.media-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.media-card{border:1px solid var(--line-soft);border-radius:8px;padding:14px;background:var(--bg-card)}.media-card h5{font-size:16px;margin:0 0 4px;color:var(--text-title)}.media-card p{font-family:var(--font-sans);font-size:13px;color:var(--text-second);margin:0 0 10px}.media-card audio,.media-card video{width:100%;display:block;border-radius:6px}.mindmap-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.mindmap-card{border:1px solid var(--line-soft);background:var(--bg-card);border-radius:8px;overflow:hidden}.mindmap-card figure{margin:0;background:#f5f1ea}.mindmap-card iframe{display:block;width:100%;aspect-ratio:16/10;border:0;background:#f5f1ea}.mindmap-body{padding:14px}.mindmap-body h4{font-size:18px;margin:0 0 4px;color:var(--text-title)}.mindmap-meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:10px}.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:16px}.ref-group{border:1px solid var(--line-soft);border-radius:8px;background:var(--bg-card);padding:16px}.ref-group h3{margin:0 0 8px;color:var(--text-title);font-size:18px}.ref-group ul{margin:0;padding-left:18px}.ref-group li{font-family:var(--font-sans);font-size:13px;color:var(--text-second);line-height:1.65}.source-link{display:inline-block;margin-top:10px;color:var(--accent);font-family:var(--font-sans);font-size:13px}.wall{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.work-card{border:1px solid var(--line-soft);background:var(--bg-card);border-radius:8px;padding:16px}.work-card h4{margin:0 0 8px;color:var(--text-title);font-size:19px}.work-card p{margin:0 0 10px;color:var(--text-second);font-family:var(--font-sans);font-size:14px}.checklist{display:grid;gap:8px;margin:0;padding:0;list-style:none}.checklist li{padding-left:22px;position:relative;font-family:var(--font-sans);font-size:14px}.checklist li:before{content:"";position:absolute;left:0;top:.65em;width:8px;height:8px;background:var(--accent);border-radius:50%}.notice{border:1px solid var(--line-soft);border-left:5px solid var(--accent);border-radius:8px;padding:16px;background:rgba(217,164,65,.08);font-family:var(--font-sans)}footer{padding:26px 24px;text-align:center;color:var(--text-muted);font-family:var(--font-sans);font-size:12px}@media(max-width:820px){.hero{min-height:88vh}.hero h1{font-size:38px}.stats,.two-col,.media-grid,.wall,.mindmap-grid,.refs{grid-template-columns:1fr}.event-head{grid-template-columns:1fr}.event-head img{height:220px}.wrap{padding:0 16px}section{padding:38px 0}}
"""


def render_media(item: dict) -> str:
    source = esc(item["path"])
    note = esc(item["note"])
    title = esc(item["title"])
    size = esc(item["size_mb"])
    if item["status"] != "copied":
        player = '<p>來源檔尚未複製，請確認 0604 影音資料夾。</p>'
    elif item["kind"] == "video":
        player = f'<video controls preload="metadata" src="{source}"></video>'
    else:
        player = f'<audio controls preload="metadata" src="{source}"></audio>'
    return f'<article class="media-card"><h5>{title}</h5><p>{note}｜{size} MB</p>{player}</article>'


def render_notebook(notebook: dict, color: str) -> str:
    samples = "".join(
        f'<div class="quote"><b>{esc(sample["title"])}</b><p>{esc(sample["text"])}</p></div>'
        for sample in notebook["samples"]
    )
    if not samples:
        samples = '<div class="quote"><p>此筆記本目前只有應用程式輸出或短格式內容，先列入盤點，不直接作長段展示。</p></div>'
    return f"""
<article class="notebook" style="--event-color:{color}">
  <h5>{esc(notebook["title"])}</h5>
  <div class="meta">{esc(notebook["output_count"])} 個輸出｜{esc(notebook["txt_count"])} 個 txt｜{esc(notebook["folder"])}</div>
  {samples}
</article>
"""


def render_mindmap(item: dict) -> str:
    event = EVENTS.get(item["event"])
    event_name = event["name"] if event else "事件待確認"
    return f"""
<article class="mindmap-card">
  <figure>
    <iframe src="{esc(item["preview_url"])}" title="{esc(item["title"])}" loading="lazy" allow="autoplay"></iframe>
  </figure>
  <div class="mindmap-body">
    <h4>{esc(item["title"])}</h4>
    <div class="mindmap-meta">{esc(item["student"])}｜{esc(event_name)}｜{esc(item["file_name"])}</div>
    <a class="source-link" href="{esc(item["drive_url"])}" target="_blank" rel="noopener">開啟原始 PNG</a>
  </div>
</article>
"""


def render_reference_sources(groups: dict) -> str:
    cards = []
    for title, refs in groups.items():
        items = "".join(f"<li>{esc(ref)}</li>" for ref in refs)
        cards.append(f'<article class="ref-group"><h3>{esc(title)}</h3><ul>{items}</ul></article>')
    return "".join(cards)


def build_html(data: dict) -> str:
    meta = data["meta"]
    nav = "".join(f'<a href="#{event["id"]}">{esc(event["name"])}</a>' for event in data["events"])
    mindmaps = "".join(render_mindmap(item) for item in data["mindmaps"])
    reference_sources = render_reference_sources(data["reference_sources"])
    events_html = []
    for event in data["events"]:
        color = event["color"]
        notebooks = "".join(render_notebook(n, color) for n in event["notebooks"]) or '<p class="lead">尚未對應到 NotebookLM 匯出。</p>'
        media = "".join(render_media(m) for m in event["media"] if m["status"] == "copied")
        if not media:
            media = '<p class="lead">目前沒有對應影音檔，先以文字與圖片成果展示。</p>'
        focus = "".join(f'<span class="chip">{esc(item)}</span>' for item in event["focus"])
        events_html.append(
            f"""
<section id="{esc(event["id"])}" style="--event-color:{color}">
  <div class="wrap two-col">
    <div>
      <div class="event-head">
        <img src="{esc(event["image"])}" alt="">
        <div class="event-title">
          <div class="years">{esc(event["years"])}｜{esc(event["ethnic"])}</div>
          <h3>{esc(event["name"])}</h3>
          <p>{esc(event["place"])}</p>
          <div class="chips">{focus}</div>
        </div>
      </div>
      <p class="lead" style="margin-top:18px">{esc(event["brief"])}</p>
      <div class="media-grid">{media}</div>
    </div>
    <aside class="panel">
      <h4>NotebookLM 輸出節錄</h4>
      <div class="notebook-list">{notebooks}</div>
    </aside>
  </div>
</section>
"""
        )

    return f"""<!DOCTYPE html>
<html lang="zh-Hant" class="theme-dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<link rel="stylesheet" href="../assets/styles/design_tokens.css">
<style>{CSS}</style>
</head>
<body class="theme-dark weave-pattern">
<header class="hero">
  <div class="hero-inner">
    <div class="event-color-bar"><div class="seg-cepo"></div><div class="seg-dafen"></div><div class="seg-cikasuan"></div><div class="seg-truku"></div></div>
    <div class="eyebrow">花蓮高商 多元文化與文學</div>
    <h1>{esc(meta["title"])}</h1>
    <p>展示學生如何用 NotebookLM 閱讀史料、整理事件、比較官方與族群觀點，並把 AI 生成內容轉化為可討論、可查證的歷史敘事。</p>
    <nav class="nav">{nav}<a href="#mindmaps">心智圖</a><a href="#process">學習歷程</a><a href="#wall">作品牆</a><a href="#references">參考資料</a></nav>
    <div class="stats">
      <div class="stat"><strong>{esc(meta["notebook_count"])}</strong><span>本 NotebookLM</span></div>
      <div class="stat"><strong>{esc(meta["txt_count"])}</strong><span>份文字輸出</span></div>
      <div class="stat"><strong>{esc(meta["json_count"])}</strong><span>份 JSON 摘要</span></div>
      <div class="stat"><strong>{esc(meta["media_count"])}</strong><span>組影音檔</span></div>
      <div class="stat"><strong>{esc(meta["mindmap_count"])}</strong><span>張 PNG 心智圖</span></div>
    </div>
  </div>
</header>
<main>
  <section id="overview">
    <div class="wrap two-col">
      <div>
        <h2>課程成果總覽</h2>
        <p class="lead">這不是單純讓學生交 AI 生成物，而是把 AI 放在史料閱讀、觀點比較與改寫練習中。網站刻意區分「NotebookLM 輸出節錄」與「教師整理說明」，避免把 AI 生成文字直接當作史實。</p>
      </div>
      <div class="notice">教授觀看時可先看統計與四個展區，再進入影音與作品牆。學生完成度不一，但班級整體已形成可展示的多媒體學習成果。</div>
    </div>
  </section>
  {''.join(events_html)}
  <section id="mindmaps">
    <div class="wrap">
      <h2>NotebookLM 心智圖與 PNG 截圖</h2>
      <p class="lead">以下 PNG 來自 Google Drive「2026作業」學生資料夾。能由檔名或同資料夾作品判讀事件者已先標註；其餘保留「事件待確認」，避免誤把未查證的 AI 生成圖歸入錯誤事件。預覽使用 Google Drive 原生 preview，若瀏覽器阻擋嵌入，可點「開啟原始 PNG」。</p>
      <div class="mindmap-grid">{mindmaps}</div>
    </div>
  </section>
  <section id="process">
    <div class="wrap two-col">
      <div>
        <h2>生成工具與學習歷程</h2>
        <p class="lead">學生用 NotebookLM 將 PDF、教材與事件資料轉為摘要、Study Guide、資料表、音訊與影片，再回到課堂任務：事實句、觀點差異句、省思句。</p>
      </div>
      <ul class="checklist">
        <li>先選事件並建立研究問題。</li>
        <li>用 NotebookLM 摘要史料，但保留人工判讀。</li>
        <li>比較官方歷史、族群記憶、地景與遷徙。</li>
        <li>把 AI 輸出改寫成自己的理解。</li>
        <li>補上來源，避免把生成錯誤當作史實。</li>
      </ul>
    </div>
  </section>
  <section id="wall">
    <div class="wrap">
      <h2>學生作品牆與補件格式</h2>
      <p class="lead">下一節課可以要求每位學生至少補齊一張成果卡；低完成度學生則以一張 NotebookLM 截圖、一段 80-120 字理解與一個來源作為最低展示內容。</p>
      <div class="wall">
        <article class="work-card"><h4>成果卡</h4><p>事件名稱、研究問題、事實句、觀點差異句、省思句、至少兩個來源。</p></article>
        <article class="work-card"><h4>代表素材</h4><p>大港口心智圖、太魯閣影音、大分 PDF/PPT、七腳川觀點比較。</p></article>
        <article class="work-card"><h4>檢查原則</h4><p>手機可讀、媒體可播、圖片清楚、姓名必要時匿名、AI 文字需人工判斷。</p></article>
      </div>
    </div>
  </section>
  <section id="references">
    <div class="wrap">
      <h2>NotebookLM 總參考資料來源</h2>
      <p class="lead">以下列出本次 12 本 NotebookLM 所使用或匯出紀錄中可辨識的主要來源。這裡是全站總參考資料，不對應單一學生作品。</p>
      <div class="refs">{reference_sources}</div>
    </div>
  </section>
</main>
<footer>資料來源：{esc(meta["source_exports"])}｜{esc(meta["source_media"])}｜產出日期：{esc(meta["generated_at"])}</footer>
</body>
</html>"""


def main() -> None:
    data = build_data()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(data), encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_HTML.relative_to(ROOT)}")
    print(f"copied media: {data['meta']['media_count']}")


if __name__ == "__main__":
    main()
