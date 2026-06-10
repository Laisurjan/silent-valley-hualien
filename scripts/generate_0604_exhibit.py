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
from datetime import date
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

# 依資料夾編號明確指定事件，避免關鍵字誤判（例如 11 號筆記本含 "Amis" 被誤歸大港口）。
# "general" = 跨事件綜論，不放進單一事件展區。
FOLDER_EVENT_OVERRIDES = {
    "01": "truku",
    "02": "truku",
    "03": "dafen",
    "04": "cepo",
    "05": "cepo",
    "06": "general",
    "07": "dafen",
    "08": "truku",
    "09": "dafen",
    "10": "cikasuan",
    "11": "cikasuan",
    "12": "cepo",
}

# 給觀展者看的中文標題；原始 NotebookLM 英文標題保留在卡片小字。
NOTEBOOK_TITLE_OVERRIDES = {
    "01": "太魯閣戰役百年與文化韌性",
    "02": "太魯閣戰爭百年回顧",
    "03": "大分事件與布農族抗爭 1914-1933",
    "04": "靜浦考古遺址：阿美族的傳承",
    "05": "Cepo' 戰役：1877 阿美族的抵抗",
    "06": "臺灣原住民族歷史與抵抗（跨事件綜論）",
    "07": "玉山之子：布農族抗爭 1914-1933",
    "08": "太魯閣戰役：百年抗爭與主權",
    "09": "大分事件：布農族抵抗與殖民政策",
    "10": "七腳川事件 1908-1914",
    "11": "七腳川事件：阿美族的流離與韌性",
    "12": "大港口事件：阿美族抗清與文化衝擊",
}

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

# 每個內容只保留一個版本：影片用 MP4、音訊用 MP3（檔案較小、瀏覽器相容性最好）。
MEDIA_MANIFEST = [
    {
        "event": "cepo",
        "kind": "video",
        "source": "1877-1878大港口事件解析.mp4",
        "target": "cepo-1877-1878-analysis.mp4",
        "title": "1877-1878 大港口事件解析",
        "note": "NotebookLM 影片導覽：事件起因、經過與對阿美族社會的影響。",
    },
    {
        "event": "cepo",
        "kind": "video",
        "source": "1877大港口事件：帝國擴張與原民抗爭.mp4",
        "target": "cepo-empire-resistance.mp4",
        "title": "帝國擴張與原民抗爭",
        "note": "以清帝國治理與阿美族抵抗為雙主軸，重組事件敘事。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/大港口事件的血腥真相.mp3",
        "target": "cepo-bloody-truth.mp3",
        "title": "大港口事件的血腥真相",
        "note": "AI 口述導覽（Audio Overview）：把史料轉成口語敘事的範例。",
    },
    {
        "event": "cepo",
        "kind": "audio",
        "source": "mp3/Take_your_story_back_from_narrative_theft.mp3",
        "target": "narrative-theft.mp3",
        "title": "Take Your Story Back from Narrative Theft",
        "note": "英文 Audio Overview：把故事從「敘事掠奪」中拿回來，呼應課程的敘事權主題。",
    },
    {
        "event": "truku",
        "kind": "video",
        "source": "太魯閣事件：18年的抗日戰役.mp4",
        "target": "truku-18-year-war.mp4",
        "title": "太魯閣事件：18 年的抗日戰役",
        "note": "把 1914 年戰役放回 1896 年起的長期抵抗脈絡，不只看單一年份。",
    },
    {
        "event": "truku",
        "kind": "audio",
        "source": "mp3/太魯閣事件：18年的抗日戰役.mp3",
        "target": "truku-18-year-war.mp3",
        "title": "太魯閣戰役（音訊版）",
        "note": "影片的音訊版本，適合行動裝置快速聆聽。",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def classify_event(text: str) -> str:
    low = text.lower()
    # 先比對專名度高的事件，最後才比對含泛用詞（amis）的大港口，無法判定歸入綜論。
    for event_id in ["cikasuan", "truku", "dafen", "cepo"]:
        if any(keyword.lower() in low for keyword in EVENTS[event_id]["keywords"]):
            return event_id
    return "general"


def folder_prefix(folder_name: str) -> str:
    match = re.match(r"^(\d+)_", folder_name)
    return match.group(1) if match else ""


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


def clip_sentence(text: str, limit: int = 260) -> str:
    """超過長度時在完整句子的句號處截斷，避免「並...」這種半句結尾。"""
    if len(text) <= limit:
        return text
    cut = text[: limit - 10]
    pos = max(cut.rfind("。"), cut.rfind("！"), cut.rfind("？"))
    if pos >= 80:
        return cut[: pos + 1]
    return cut.rstrip("，,；;。.") + "……"


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
        selected.append(clip_sentence(line))
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
        selected.append(clip_sentence(chunk))
        if len(selected) >= limit:
            break
    return selected


def pretty_sample_label(stem: str) -> str:
    label = re.sub(r"^\d+_", "", stem)
    if label == "content_copy":
        return "內容節錄"
    if label == "資料表":
        return "資料表"
    if label.lower().startswith("study guide"):
        return "Study Guide"
    return "AI 摘要"


def collect_notebook_outputs() -> tuple[list[dict], dict[str, list[dict]]]:
    notebooks = []
    grouped = {event_id: [] for event_id in [*EVENTS, "general"]}
    seen_texts: set[str] = set()  # NotebookLM 匯出常重複同段摘要，跨筆記本全域去重
    for folder in sorted(p for p in EXPORT_DIR.iterdir() if p.is_dir()):
        summary_path = folder / "_summary.json"
        txt_files = sorted(folder.glob("*.txt"))
        summary = {}
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        original_title = str(summary.get("notebook") or folder.name.split("_", 1)[-1])
        prefix = folder_prefix(folder.name)
        title = NOTEBOOK_TITLE_OVERRIDES.get(prefix, original_title)
        event_id = FOLDER_EVENT_OVERRIDES.get(prefix) or classify_event(folder.name + " " + original_title)
        samples = []
        output_titles = []
        for txt in txt_files:
            if txt.name.endswith("_ERROR.txt"):
                continue
            output_titles.append(txt.stem)
            for paragraph in readable_paragraphs(txt.read_text(encoding="utf-8", errors="ignore"), limit=1):
                fingerprint = re.sub(r"\s+", "", paragraph)[:80]
                if fingerprint in seen_texts:
                    continue
                seen_texts.add(fingerprint)
                samples.append({"title": pretty_sample_label(txt.stem), "text": paragraph})
            if len(samples) >= 2:
                break

        item = {
            "folder": folder.name,
            "title": title,
            "original_title": original_title,
            "event": event_id,
            "output_count": int(summary.get("outputCount") or len(txt_files)),
            "txt_count": len(txt_files),
            "json": summary_path.name if summary_path.exists() else "",
            "samples": samples[:2],
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
        elif target.exists():
            # 原始下載資料夾被清掉時，沿用先前已複製到 outputs 的檔案
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
        mindmaps.append(
            {
                **item,
                "drive_url": f"https://drive.google.com/file/d/{file_id}/view",
                "preview_url": f"https://drive.google.com/file/d/{file_id}/preview",
            }
        )
    # 已確認事件的排前面（依展區順序），待學生審查歸類的排後面
    order = {event_id: idx for idx, event_id in enumerate(EVENT_ORDER)}
    mindmaps.sort(key=lambda m: order.get(m["event"], len(order)))
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
            "generated_at": date.today().isoformat(),
            "notebook_count": len(notebooks),
            "txt_count": sum(n["txt_count"] for n in notebooks),
            "media_count": len([m for m in media if m["status"] == "copied"]),
            "mindmap_count": len(mindmaps),
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
        "general_notebooks": grouped["general"],
        "all_notebooks": notebooks,
        "mindmaps": mindmaps,
        "reference_sources": GLOBAL_REFERENCE_SOURCES,
    }


CSS = r"""
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg-main);color:var(--text-primary);font-family:var(--font-serif);line-height:1.75}.wrap{max-width:1180px;margin:0 auto;padding:0 24px}.hero{min-height:92vh;display:grid;align-content:end;background:linear-gradient(90deg,rgba(14,11,8,.82),rgba(14,11,8,.28)),url("../assets/images/hero_valley.png") center/cover no-repeat;border-bottom:1px solid var(--line-thin)}.hero-inner{max-width:1180px;margin:0 auto;width:100%;padding:44px 24px 52px}.eyebrow{font-family:var(--font-sans);font-size:12px;letter-spacing:.28em;color:var(--accent);text-transform:uppercase}.hero h1{font-size:52px;line-height:1.18;margin:12px 0 14px;color:#fff;letter-spacing:0}.hero p{max-width:760px;margin:0;color:rgba(245,241,234,.86);font-family:var(--font-sans);font-size:17px}.nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}.nav a{color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.28);padding:8px 12px;border-radius:8px;font-family:var(--font-sans);font-size:13px;background:rgba(0,0,0,.18)}.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:28px;max-width:920px}.stat{border:1px solid rgba(255,255,255,.22);border-radius:8px;padding:12px;background:rgba(14,11,8,.34)}.stat strong{display:block;color:#fff;font-size:28px;line-height:1.1}.stat span{font-family:var(--font-sans);font-size:12px;color:rgba(255,255,255,.72)}section{padding:56px 0;border-bottom:1px solid var(--line-thin)}h2{font-size:32px;color:var(--text-title);line-height:1.3;margin:0 0 10px;letter-spacing:0}.lead{max-width:820px;color:var(--text-second);font-family:var(--font-sans);margin:0 0 24px}.two-col{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);gap:26px;align-items:start}.event-head{display:grid;grid-template-columns:160px minmax(0,1fr);gap:18px;align-items:stretch}.event-head img{width:100%;height:100%;min-height:190px;object-fit:cover;border-radius:8px;border:1px solid var(--line-thin)}.event-title{border-left:5px solid var(--event-color);padding-left:16px}.event-title .years{font-family:var(--font-sans);font-size:13px;color:var(--event-color);letter-spacing:.18em}.event-title h3{font-size:30px;color:var(--text-title);margin:4px 0}.event-title p{margin:0;color:var(--text-second)}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.chip{border:1px solid var(--line-soft);border-radius:999px;padding:5px 9px;font-family:var(--font-sans);font-size:12px;color:var(--text-primary)}.panel{background:var(--bg-card);border:1px solid var(--line-soft);border-radius:8px;padding:18px}.panel h4{margin:0 0 10px;color:var(--text-title);font-size:18px}.notebook-list{display:grid;gap:12px}.notebook{border-left:3px solid var(--event-color);background:rgba(0,0,0,.12);padding:12px;border-radius:0 8px 8px 0}.notebook h5{margin:0 0 5px;color:var(--text-title);font-size:16px}.notebook .meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:8px}.quote{margin:8px 0 0;padding:10px;border:1px solid var(--line-thin);border-radius:8px}.quote b{display:block;font-family:var(--font-sans);font-size:12px;color:var(--event-color);margin-bottom:4px}.quote p{margin:0;font-size:14px;color:var(--text-primary)}.media-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.media-card{border:1px solid var(--line-soft);border-radius:8px;padding:14px;background:var(--bg-card)}.media-card h5{font-size:16px;margin:0 0 4px;color:var(--text-title)}.media-card p{font-family:var(--font-sans);font-size:13px;color:var(--text-second);margin:0 0 10px}.media-card audio,.media-card video{width:100%;display:block;border-radius:6px}.mindmap-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.mindmap-card{border:1px solid var(--line-soft);background:var(--bg-card);border-radius:8px;overflow:hidden}.mindmap-card figure{margin:0;background:#f5f1ea}.mindmap-card iframe{display:block;width:100%;aspect-ratio:16/10;border:0;background:#f5f1ea}.mindmap-body{padding:14px}.mindmap-body h4{font-size:18px;margin:0 0 4px;color:var(--text-title)}.mindmap-meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:10px}.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:16px}.ref-group{border:1px solid var(--line-soft);border-radius:8px;background:var(--bg-card);padding:16px}.ref-group h3{margin:0 0 8px;color:var(--text-title);font-size:18px}.ref-group ul{margin:0;padding-left:18px}.ref-group li{font-family:var(--font-sans);font-size:13px;color:var(--text-second);line-height:1.65}.source-link{display:inline-block;margin-top:10px;color:var(--accent);font-family:var(--font-sans);font-size:13px}.wall{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.work-card{border:1px solid var(--line-soft);background:var(--bg-card);border-radius:8px;padding:16px}.work-card h4{margin:0 0 8px;color:var(--text-title);font-size:19px}.work-card p{margin:0 0 10px;color:var(--text-second);font-family:var(--font-sans);font-size:14px}.checklist{display:grid;gap:8px;margin:0;padding:0;list-style:none}.checklist li{padding-left:22px;position:relative;font-family:var(--font-sans);font-size:14px}.checklist li:before{content:"";position:absolute;left:0;top:.65em;width:8px;height:8px;background:var(--accent);border-radius:50%}.notice{border:1px solid var(--line-soft);border-left:5px solid var(--accent);border-radius:8px;padding:16px;background:rgba(217,164,65,.08);font-family:var(--font-sans)}footer{padding:26px 24px;text-align:center;color:var(--text-muted);font-family:var(--font-sans);font-size:12px}.badge{display:inline-block;font-family:var(--font-sans);font-size:11px;letter-spacing:.06em;padding:3px 9px;border-radius:999px;border:1px solid var(--line-soft);white-space:nowrap}.badge-event{color:var(--event-color);border-color:var(--event-color)}.badge-pending{color:var(--accent);border-color:var(--accent);background:rgba(217,164,65,.1)}.mindmap-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.wall-step{font-family:var(--font-sans);font-size:12px;letter-spacing:.18em;color:var(--accent);margin-bottom:6px}@media(max-width:820px){.hero{min-height:88vh}.hero h1{font-size:38px}.stats,.two-col,.media-grid,.wall,.mindmap-grid,.refs{grid-template-columns:1fr}.event-head{grid-template-columns:1fr}.event-head img{height:220px}.wrap{padding:0 16px}section{padding:38px 0}}
"""


def render_media(item: dict) -> str:
    source = esc(item["path"])
    note = esc(item["note"])
    title = esc(item["title"])
    if item["status"] != "copied":
        player = '<p>來源檔尚未複製，請確認 0604 影音資料夾。</p>'
    elif item["kind"] == "video":
        player = f'<video controls preload="metadata" src="{source}"></video>'
    else:
        player = f'<audio controls preload="metadata" src="{source}"></audio>'
    return f'<article class="media-card"><h5>{title}</h5><p>{note}</p>{player}</article>'


def render_notebook(notebook: dict, color: str) -> str:
    samples = "".join(
        f'<div class="quote"><b>AI 生成｜{esc(sample["title"])}</b><p>{esc(sample["text"])}</p></div>'
        for sample in notebook["samples"]
    )
    if not samples:
        samples = '<div class="quote"><p>此筆記本以心智圖、資料表等短格式輸出為主，文字節錄詳見各展區。</p></div>'
    original = notebook.get("original_title", "")
    original_line = (
        f'<div class="meta">{esc(notebook["output_count"])} 個 AI 輸出｜NotebookLM：{esc(original)}</div>'
        if original and original != notebook["title"]
        else f'<div class="meta">{esc(notebook["output_count"])} 個 AI 輸出</div>'
    )
    return f"""
<article class="notebook" style="--event-color:{color}">
  <h5>{esc(notebook["title"])}</h5>
  {original_line}
  {samples}
</article>
"""


def render_mindmap(item: dict) -> str:
    event = EVENTS.get(item["event"])
    if event:
        badge = f'<span class="badge badge-event" style="--event-color:{event["color"]}">{esc(event["name"])}</span>'
        title = item["title"]
    else:
        badge = '<span class="badge badge-pending">審查中｜待學生歸類</span>'
        title = "NotebookLM 心智圖"
    return f"""
<article class="mindmap-card">
  <figure>
    <iframe src="{esc(item["preview_url"])}" title="{esc(title)}" loading="lazy" allow="autoplay"></iframe>
  </figure>
  <div class="mindmap-body">
    <h4>{esc(title)}</h4>
    <div class="mindmap-meta">{badge}<span>{esc(item["student"])}</span></div>
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
    general_html = ""
    if data.get("general_notebooks"):
        general_cards = "".join(
            render_notebook(n, "var(--accent)") for n in data["general_notebooks"]
        )
        general_html = f"""
  <section id="general">
    <div class="wrap">
      <h2>跨事件綜論</h2>
      <p class="lead">部分筆記本同時涵蓋多個歷史事件（含霧社事件等對照閱讀），不歸入單一展區，列於此處供整體脈絡參考。</p>
      <div class="notebook-list" style="max-width:820px">{general_cards}</div>
    </div>
  </section>
"""
    events_html = []
    for event in data["events"]:
        color = event["color"]
        notebooks = "".join(render_notebook(n, color) for n in event["notebooks"]) or '<p class="lead">尚未對應到 NotebookLM 匯出。</p>'
        media = "".join(render_media(m) for m in event["media"] if m["status"] == "copied")
        if not media:
            media = '<p class="lead">本展區以 NotebookLM 文字輸出與學生心智圖呈現。</p>'
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
    <p>學生以 NotebookLM 閱讀史料、比較官方文獻與族群記憶；AI 生成的素材經學生審查、歸類與改寫後才上牆。這裡展示的不是 AI 能生成什麼，而是學生如何判斷。</p>
    <nav class="nav">{nav}<a href="#mindmaps">心智圖</a><a href="#process">學習歷程</a><a href="#wall">學生策展</a><a href="#references">參考資料</a></nav>
    <div class="stats">
      <div class="stat"><strong>4</strong><span>大歷史事件</span></div>
      <div class="stat"><strong>{esc(meta["notebook_count"])}</strong><span>本 NotebookLM 筆記本</span></div>
      <div class="stat"><strong>{esc(meta["txt_count"])}</strong><span>份 AI 文字輸出</span></div>
      <div class="stat"><strong>{esc(meta["media_count"])}</strong><span>組影音成果</span></div>
      <div class="stat"><strong>{esc(meta["mindmap_count"])}</strong><span>張學生心智圖</span></div>
    </div>
  </div>
</header>
<main>
  <section id="overview">
    <div class="wrap two-col">
      <div>
        <h2>課程成果總覽</h2>
        <p class="lead">這不是讓學生交 AI 生成物，而是把 AI 放進史料閱讀、觀點比較與改寫練習中。本站刻意區分「NotebookLM 輸出節錄」與「教師整理說明」，AI 生成文字一律標示，不直接視為史實。</p>
      </div>
      <div class="notice">本頁所有標示「AI 生成」的內容，定位都是學生審查與改寫的素材；標示「審查中」者，代表已排入學生審查會進行歸類與判讀。觀展動線建議：四大事件展區 → 心智圖 → 學生策展。</div>
    </div>
  </section>
  {''.join(events_html)}
  {general_html}
  <section id="mindmaps">
    <div class="wrap">
      <h2>學生心智圖</h2>
      <p class="lead">以下心智圖來自學生作業資料夾。已能確認事件者以事件色標示；標示「審查中」者，將由學生在審查會中判讀歸類——判斷一張 AI 心智圖屬於哪個事件、依據是哪些關鍵詞，正是本課程要練的 AI 素養。若瀏覽器阻擋嵌入預覽，可點「開啟原始 PNG」。</p>
      <div class="mindmap-grid">{mindmaps}</div>
    </div>
  </section>
  <section id="process">
    <div class="wrap two-col">
      <div>
        <h2>生成工具與學習歷程</h2>
        <p class="lead">學生用 NotebookLM 將權威史料 PDF 轉為摘要、Study Guide、資料表、音訊與影片，再回到課堂的三句寫作：事實句、差異句、省思句。</p>
      </div>
      <ul class="checklist">
        <li>選定事件，建立自己的研究問題。</li>
        <li>用 NotebookLM 摘要史料，保留人工判讀。</li>
        <li>審查 AI 輸出：歸類心智圖、辨認有立場的用詞。</li>
        <li>比較官方說法與族群記憶，寫出差異。</li>
        <li>把 AI 輸出改寫成自己的話，並補上來源。</li>
      </ul>
    </div>
  </section>
  <section id="wall">
    <div class="wrap">
      <h2>學生策展：AI 素材的三道審查</h2>
      <p class="lead">AI 生成的素材要登上這面牆，必須先通過全班的三道審查程序。</p>
      <div class="wall">
        <article class="work-card"><div class="wall-step">第一道</div><h4>歸類</h4><p>判讀心智圖與摘要屬於哪個事件，說出判斷依據的關鍵詞。</p></article>
        <article class="work-card"><div class="wall-step">第二道</div><h4>挑錯與票選</h4><p>找出 AI 錯置的內容與有立場的用詞（招撫、平亂、歸順、理蕃……），票選最值得上牆的段落。</p></article>
        <article class="work-card"><div class="wall-step">第三道</div><h4>三句展示</h4><p>事實句、差異句、省思句——用自己的話寫下一句可上牆的理解。</p></article>
      </div>
      <p class="lead" style="margin-top:18px">審查會後，本區將更新全班票選結果與入選的學生句子。</p>
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
<footer>花蓮高商「多元文化與文學」縱谷無言單元｜素材：NotebookLM 匯出與學生課堂作業｜頁面更新：{esc(meta["generated_at"])}</footer>
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
