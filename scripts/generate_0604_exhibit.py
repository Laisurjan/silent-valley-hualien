"""
Build the 0604 professor-facing learning exhibit.

Inputs are the local NotebookLM exports and media files listed in
0604_成果網頁兩週工作清單.md. The script writes standalone exhibit pages:

  outputs/ai_history_learning_exhibit.html         日常版（無開場動畫）
  outputs/ai_history_learning_exhibit_cinema.html  展示版（片頭墨色顯影＋Ken Burns＋晨霧）
  data/0604_exhibit_data.json
  outputs/media/notebooklm/*
"""

from __future__ import annotations

import html
import json
import math
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = Path(r"C:\Users\godof\Downloads\0604\notebooklm_exports")
MEDIA_DIR = Path(r"C:\Users\godof\Downloads\0604\notebooklm_media")
OUTPUT_HTML = ROOT / "outputs" / "ai_history_learning_exhibit.html"
OUTPUT_HTML_CINEMA = ROOT / "outputs" / "ai_history_learning_exhibit_cinema.html"
OUTPUT_JSON = ROOT / "data" / "0604_exhibit_data.json"
OUTPUT_MEDIA = ROOT / "outputs" / "media" / "notebooklm"


# 依學生審查會決議（2026-06-11，14:0）：事件名稱全站採「漢語名／族語名」雙名並列。
# 族語名只用有出處者，不杜撰：
#   cepo     O lalood i Cepo'──原民會叢書與口傳調查報告；2022 年部落正名「Cepo' 戰役」。
#   truku    Tnegjyalan Truku──原住民族文化事業基金會《太魯閣事件-1914 Tnegjyalan Truku》。
#   cikasuan Cikasuan──七腳川即阿美語 Cikasuan 音譯（柴薪很多之地），日治沒收後設吉野村，今吉安。
#   dafen    「大分」為布農語地名音譯（拉庫拉庫溪流域），尚無通行之族語事件名，故不並列、僅註明。
EVENTS = {
    "cepo": {
        "name": "大港口事件 / Cepo'",
        "name_dual": "大港口事件 ／ O lalood i Cepo'",
        "name_note": "「大港口」是漢人地名；O lalood i Cepo' 意為「Cepo' 的戰爭」，是阿美族人自己的命名。2022 年部落正名「Cepo' 戰役」。",
        "years": "1877-1878",
        "ethnic": "阿美族・秀姑巒溪口部落",
        "place": "花蓮縣豐濱鄉靜浦、Makuta'ay 一帶",
        "image": "../assets/images/event_cepo.png",
        "color": "var(--c-cepo)",
        "brief": "學生從清帝國治理、阿美族口述記憶與地名變遷切入，理解同一事件如何被寫成招撫、衝突、誘殺或族群創傷。",
        "focus": ["官方治理語言", "阿美族記憶", "遷徙與創傷", "地名與地景改寫"],
        "keywords": ["cepo", "makuta", "大港口", "阿美", "jingpu", "amis"],
    },
    "truku": {
        "name": "太魯閣戰役",
        "name_dual": "太魯閣戰役 ／ Tnegjyalan Truku",
        "name_note": "日方文獻稱「太魯閣蕃討伐」，這個稱呼本身就帶著立場；Tnegjyalan Truku 是太魯閣族語的命名。",
        "years": "1896-1914",
        "ethnic": "太魯閣族",
        "place": "立霧溪、木瓜溪上游與太魯閣口",
        "image": "../assets/images/event_truku.png",
        "color": "var(--c-truku)",
        "brief": "展區呈現學生如何把 1914 年戰役放回更長的抵抗脈絡，看見 Gaya、山地治理、槍械收繳與主權衝突。",
        "focus": ["長期抵抗", "Gaya 與主權", "山地治理", "觀光地景背後的歷史"],
        "keywords": ["truku", "taroko", "太魯閣"],
    },
    "dafen": {
        "name": "大分事件 / 布農族抗爭",
        "name_dual": "大分事件（布農族郡社群抗日 1914-1933）",
        "name_note": "「大分」是布農語地名的音譯（拉庫拉庫溪流域）。族人記憶中，1933 年的儀式不是「歸順」，而是有條件的和解。",
        "years": "1914-1933",
        "ethnic": "布農族",
        "place": "花蓮縣卓溪鄉、大分與拉庫拉庫溪流域",
        "image": "../assets/images/event_dafen.png",
        "color": "var(--c-dafen)",
        "brief": "學生整理大分事件時，將交易所、槍枝收押、生計壓力與拉荷・阿雷的長期抵抗放在同一條歷史線上。",
        "focus": ["收押槍枝", "交易所制度", "生計衝突", "1914-1933 長期抗爭"],
        "keywords": ["dafen", "dafa", "bunun", "大分", "布農", "yushan"],
    },
    "cikasuan": {
        "name": "七腳川事件 / Cikasuan",
        "name_dual": "七腳川事件 ／ Cikasuan",
        "name_note": "七腳川即阿美語 Cikasuan（柴薪很多的地方）。事件後土地被沒收，設「吉野」移民村，也就是今天的吉安。",
        "years": "1908-1914",
        "ethnic": "阿美族・南勢阿美",
        "place": "花蓮縣吉安鄉七腳川溪流域",
        "image": "../assets/images/event_cikasuan.png",
        "color": "var(--c-cikasuan)",
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

# 參考資料：每筆標明來源層級。史實數字一律以【政府出版品】為準（原民會
# 「原住民族重大歷史事件系列叢書」、國史館臺灣文獻館、國家教育研究院）。
GLOBAL_REFERENCE_SOURCES = {
    "大港口事件 / Cepo'": [
        "【政府出版品】原住民族委員會《原住民族重大歷史事件系列叢書：大港口事件 1877-1878》",
        "【政府出版品】國家教育研究院 原住民族重大歷史事件補充教材：大港口事件",
        "【政府委託研究】《大港口 Cepo' 事件口傳歷史寫生／聲及其對應之阿美族文化智慧調查與研究報告書》",
        "【官方資料庫】靜浦考古遺址｜文化部 國家文化記憶庫",
        "【公廣媒體】140 年前「大港口事件」阿美族遭清兵殺戮｜公視新聞網 PNN",
        "【公廣媒體】南島近代史．清領時期｜原住民族電視台【ZALAN 見識南島】第三季",
    ],
    "太魯閣戰役": [
        "【政府出版品】原住民族委員會《原住民族重大歷史事件系列叢書：太魯閣事件 1914》",
        "【政府出版品】國家教育研究院 原住民族重大歷史事件補充教材：太魯閣事件",
        "【學術研討】《太魯閣戰爭百年回顧》研討會論文集",
        "【官方影音】《太魯閣事件-1914 Tnegjyalan Truku》｜原住民族文化事業基金會",
        "【官方網站】太魯閣．歷史背景｜原住民族文化事業基金會",
        "【官方網站】蘇花道今昔｜太魯閣國家公園全球資訊網",
    ],
    "大分事件 / 布農族抗爭": [
        "【政府出版品】原住民族委員會《原住民族重大歷史事件系列叢書：大分事件 1914-1933》",
        "【政府出版品】國家教育研究院 原住民族重大歷史事件補充教材：大分事件",
        "【官方期刊】大分事件一百周年紀念回顧｜原住民族委員會《原住民族文獻》",
        "【官方資料庫】大分事件、先祖「大分事件」抗日百年故事｜文化部 國家文化記憶庫",
        "【官方辭書】大分事件｜臺灣原住民族事典",
        "【學術論文】〈1915 年 Dahu Ali（拉荷・阿雷）發動布農族大分抗日事件說之探討〉",
    ],
    "七腳川事件 / Cikasuan": [
        "【政府出版品】原住民族委員會《原住民族重大歷史事件系列叢書：七腳川事件 1908-1914》",
        "【政府出版品】國家教育研究院 原住民族重大歷史事件補充教材：七腳川事件",
        "【官方資料庫】原住民族重大歷史事件：七腳川事件故事地圖系列（原民會委託製作）",
        "【課程素材】The Cikasuan Incident 1908-1914｜NotebookLM 筆記本來源紀錄",
    ],
}

# 2026-06 盤點後依「作者研究的事件」歸檔（老師核可的預填）：
# 標 archived_by="author_event" 者頁面註記「依作者研究事件歸檔」；
# 原本就確認的（蔡/鍾/梁）不加註。
MINDMAP_MANIFEST = [
    {
        "student": "英二乙 09・余O璿",
        "event": "cepo",
        "archived_by": "author_event",
        "title": "學生上傳 PNG 心智圖 / 截圖 1",
        "file_name": "unnamed (1).png",
        "id": "1-SAv2DNcviPutduwYgvtJ-z1oySPP7Aw",
    },
    {
        "student": "英二乙 09・余O璿",
        "event": "cepo",
        "archived_by": "author_event",
        "title": "學生上傳 PNG 心智圖 / 截圖 2",
        "file_name": "unnamed.png",
        "id": "1CA_y5gA6G9MSX_XrbPeVSMgeZk8C_GCT",
    },
    {
        "student": "多二甲 16・杜O蕎",
        "event": "dafen",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1_gzIMmIjulLc_8OHckCn6GxcwHau1pMl",
    },
    {
        "student": "多二甲 13・蔡O君",
        "event": "cepo",
        "title": "大港口事件 NotebookLM 心智圖",
        "file_name": "NotebookLM Mind Map (2).png",
        "id": "1JyEVL3idjt9-OA2fa1vai1sIEwNRO3MX",
    },
    {
        "student": "多二甲 13・蔡O君",
        "event": "cepo",
        "title": "大港口事件 NotebookLM 輸出截圖",
        "file_name": "unnamed.png",
        "id": "1SIscvG9OGMDOpmtYBM_xQxgM1ONSi5rq",
    },
    {
        "student": "多二甲 05・張O瑞",
        "event": "cikasuan",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "17xdEjz_mZZAQ03uWDEnRqPjlAIrrDYDK",
    },
    {
        "student": "商二乙 30・潘O澕",
        "event": "cepo",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1pjtgbuspq5LW-GPBawGNFR8Mtty_eUb7",
    },
    {
        "student": "商二乙 19・梁O芝",
        "event": "dafen",
        "title": "大分事件 NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1CIBkv6kyN3VXTC6eXBPGGvVcGi-qMiBM",
    },
    {
        "student": "多二甲 05・張O瑞",
        "event": "cikasuan",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map (1).png",
        "id": "1mkJDFA2BvL63Lp3RODvl_51dwsWHhZT-",
    },
    {
        "student": "商二乙 24・鍾O瑄",
        "event": "cepo",
        "title": "大港口事件心智圖",
        "file_name": "大港口事件-心智圖.png",
        "id": "1zvnaercNuEX32qNyRk-O9hQRRajQrQoE",
    },
    {
        "student": "商二乙 20・林O妏",
        "event": "truku",
        "archived_by": "author_event",
        "title": "學生上傳 PNG 心智圖 / 截圖",
        "file_name": "unnamed.png",
        "id": "1dVu0XbHZyxY5vlKM13qrqEXVfrmNR1hy",
    },
    {
        "student": "商二乙 20・林O妏",
        "event": "truku",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map.png",
        "id": "1aDSdfdcfwF0YhJV4epuczPbzVa9YjIOD",
    },
    {
        "student": "商二乙 18・吳O瑤",
        "event": "dafen",
        "archived_by": "author_event",
        "title": "NotebookLM Mind Map",
        "file_name": "NotebookLM Mind Map (1).png",
        "id": "1XD_iWOUzmjpiji30Acx5qQFzimmw9Hno",
    },
    {
        "student": "商二乙 03・李O諺",
        "event": "cikasuan",
        "archived_by": "author_event",
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


# ============================================================================
# 開展前審查會成果（2026-06-11，14 位學生審稿人）
# 姓名一律屏蔽（王O庭式）＋班級座號代號；引文出自問卷與事件理解卡，
# 僅做錯字校正與斷句整理，不改學生原意。AI 文句一律標示 AI 生成。
# ============================================================================

PRIOR_KNOWLEDGE = [
    {"label": "完全沒聽過這些事件", "count": 3},
    {"label": "聽過，但不是在課堂上", "count": 7},
    {"label": "在課堂學過", "count": 4},
]

# 第一幕：AI 初稿翻頁書。引文皆為課程實際使用的 AI 生成文句（NotebookLM 匯出
# 或課堂示範原句），立場詞以 <i> 預埋紅線。每頁自帶「AI 初稿」浮水印。
FLIPBOOK_PAGES = [
    {
        "kind": "cover",
        "title": "縱谷無言",
        "subtitle": "AI 生成初稿・未經審查",
        "body": "這份初稿由 AI 整理史料而成。<br>它讀起來很順，可是它不是族人，它會說錯話。<br><br><b>請翻頁，看看它怎麼寫。</b>",
        "note": "本冊所有文句皆為 AI 生成，僅供學生審查教學使用，不得視為史實。",
    },
    {
        "kind": "page",
        "event": "truku",
        "title": "太魯閣（AI 初稿）",
        "quotes": [
            "日方為徹底征服「<i>兇蕃</i>」以開鑿橫斷道路並掌控山地資源（樟腦、礦產），發動海陸東西夾擊。",
            "太魯閣族 3,000 戰士憑天險與傳統戰術抵抗，但在強大火力與資源封鎖下，<i>各社相繼歸順</i>。",
        ],
        "note": "出自學生班上 NotebookLM 匯出檔。",
    },
    {
        "kind": "page",
        "event": "cepo",
        "title": "大港口（AI 初稿）",
        "quotes": [
            "受國際局勢影響，晚清政府推行「<i>開山撫番</i>」政策以強化對東臺灣的主權，卻因強徵勞力、侵佔土地及軍紀敗壞，引發阿美族人的強烈抵抗。",
            "清兵透過誘騙手段，在現今靜浦國小附近，對 165 名阿美族青年進行閉門屠殺。",
        ],
        "note": "出自學生班上 NotebookLM 匯出檔。整段都以朝廷當主詞，阿美族人成了「被引發」的受詞。",
    },
    {
        "kind": "page",
        "event": "cikasuan",
        "title": "七腳川（AI 初稿）",
        "quotes": [
            "日本政府<i>平定</i>了七腳川社的<i>叛亂</i>。",
        ],
        "note": "課堂示範用 AI 原句。一個「平定」、一個「叛亂」，整場滅社只剩九個字。",
    },
    {
        "kind": "page",
        "event": "dafen",
        "title": "大分（AI 初稿）",
        "quotes": [
            "該行動自 1915 年爆發後持續約十八年，最終於 1933 年<i>達成歸順與和解</i>。",
        ],
        "note": "出自學生班上 NotebookLM 匯出檔。AI 把事件寫成「結束了」。可是被遷走的部落，後來回去了嗎？",
    },
    {
        "kind": "back",
        "title": "初稿到此為止。",
        "subtitle": "它尚未經過審查。",
        "body": "14 位學生審稿人讀過這份稿。<br>接下來，是他們的決定。",
        "note": "",
    },
]

# 第二幕：審稿桌（三項表決）
REVIEW_VOTES = [
    {
        "question": "「兇蕃」這兩個字，要不要上牆？",
        "options": [
            {"label": "照用，歷史文件就是這樣寫的", "count": 0},
            {"label": "照用，但旁邊加註：這是日方對抵抗者的稱呼", "count": 5},
            {"label": "改成「太魯閣族人」，並註明原文用語", "count": 8, "win": True},
            {"label": "整段不要上牆", "count": 1},
        ],
        "verdict": "本展全站依最高票執行：改寫並註明原文。14 位審稿人裡，沒有一票願意照貼原文。",
    },
    {
        "question": "「各社相繼歸順」，由族人的後代來寫會是哪一句？",
        "options": [
            {"label": "各社相繼歸順（照原文）", "count": 0},
            {"label": "各社在火砲與封鎖下，為了讓族人活下去，停止了武裝抵抗", "count": 14, "win": True},
            {"label": "各社終於接受了現代化的治理", "count": 0},
            {"label": "各社全部被消滅了", "count": 0},
        ],
        "verdict": "14:0 全數通過。這一句同時保留了「被迫」，也保留了族人的選擇與尊嚴。",
    },
    {
        "question": "展覽標題，用誰的名字說故事？",
        "options": [
            {"label": "大港口事件（觀眾比較看得懂）", "count": 0},
            {"label": "O lalood i Cepo'（族人的名字）", "count": 0},
            {"label": "兩個並列，並說明兩個名字的來歷", "count": 14, "win": True},
            {"label": "都可以，名字不重要", "count": 0},
        ],
        "verdict": "14:0 全數通過。本展四個事件的標題已全部依此決議改為雙名並列。",
    },
]

# 第二幕：紅筆對照，AI 原句對學生改寫（出自事件理解卡）
REWRITE_PAIRS = [
    {
        "student": "多二甲 13・蔡O君",
        "event": "cepo",
        "ai": "這是一場為了維護國家主權與推行法治的「平定叛亂」行動。",
        "rewrite": "這是一場為自身利益殘害無辜的惡劣行為。",
        "reason": "有種把自己做的壞事合理化的感覺。",
    },
    {
        "student": "英二乙 09・余O璿",
        "event": "cepo",
        "ai": "清政府將此事件定義為阿美族「兇番」抗拒「開山撫番」政策的叛亂行為，主張必須透過「勦撫兼施」的軍事手段，達成對後山領土的實際佔有。",
        "rewrite": "清軍認為開發此地必須清掃、驅趕原住民，把開墾土地造成的迫害合理化。",
        "reason": "政府描述的角度和族人的觀點不同。",
    },
    {
        "student": "商二乙 20・林O妏",
        "event": "truku",
        "ai": "日軍官兵因「行為不檢」且「潛通蕃婦」，未能尊重地方之習慣。",
        "rewrite": "日方記成官兵「行為不檢」；族人記得的是日軍蹂躪族中女性，嚴重觸犯祖訓。",
        "reason": "我想同時寫出兩方的看法：同一件事，兩種記法。",
    },
]

# 第三幕收尾兩區：
# (1) 完整三句：走完「事實 → 差異（對官方／AI 立場的比對）→ 省思」整條弧的同學，獨立成區、三句並列。
#     句子出自事件理解卡，僅輕修明顯錯字與冗詞、不改原意（修改處見 commit 說明）。
# (2) 佳句：未完成三句、但留下一句值得上牆的同學。
THREE_SENTENCE_STUDENTS = [
    {
        "student": "多二甲 13・蔡O君",
        "event": "cepo",
        "fact": "我以為平靜的這片土地，曾經發生過許多想不到的非人對待。",
        "difference": "官方說「事件」，但族人記得的是「戰爭」。",
        "reflection": "我原本以為開山撫番只是原住民的屈服，現在發現那是頻繁抵抗後的無奈。",
    },
    {
        "student": "多二甲 16・杜O蕎",
        "event": "dafen",
        "fact": "我今天才知道，在簡單一句記載後，是血與淚寫成的。",
        "difference": "官方說是理蕃政策的「完全勝利」，但族人記得的是為了生存的「平等和解」。",
        "reflection": "我原本以為官方記載是正確的，現在發現記載也會有誤差。",
    },
    {
        "student": "多二甲 11・王O庭",
        "event": "truku",
        "fact": "太魯閣族和日本人的戰爭，比我想像中還要嚴重。",
        "difference": "官方說「招撫」，但族人記得的是強迫歸順。",
        "reflection": "我原本以為戰爭與我們無關，現在才發現它只是被名為時間的河流淹沒了。",
    },
    {
        "student": "商二乙 30・潘O澕",
        "event": "cepo",
        "fact": "我今天才知道，有這麼多是我原本不知道的事。",
        "difference": "官方說大港口事件是平亂行動，但族人記得的是保衛家園與土地的抗爭。",
        "reflection": "以後我經過大港口部落，會想起族人守護家園的故事。",
    },
    {
        "student": "英二乙 09・余O璿",
        "event": "cepo",
        "fact": "我今天才知道，可以自己搜尋、查找一段歷史背後的真相。",
        "difference": "官方說是「撫平當地居民」，但族人記得的是大規模的迫害。",
        "reflection": "這個地名看起來很平常，但背後其實是被掩蓋的歷史。",
    },
    {
        "student": "商二乙 01・李O揚",
        "event": "dafen",
        "fact": "我今天才知道，原來日本人跟原住民爆發過這麼多次衝突。",
        "difference": "官方說 1933 年的儀式是「最後未歸順蕃」的謝罪投降，但族人記得的是地位對等、官方先道歉後達成的「平等和解」。",
        "reflection": "風景優美的「多美麗」（Tomiri），背後其實是日方監控布農族人的駐在所，一段一點也不美麗的「十三里」壓迫史。",
    },
]

LAUREL_QUOTES = [
    {
        "student": "商二乙 20・林O妏",
        "event": "truku",
        "text": "官方寫的是強勢文化的統治史觀；族人記得的是對抗侵略、捍衛主權的正當性。",
    },
    {
        "student": "商二乙 25・張O茹",
        "event": "cikasuan",
        "text": "這種從受害者手中「奪走故事」的權力鬥爭，比戰爭本身更令我震撼。",
    },
    {
        "student": "多二甲 05・張O瑞",
        "event": "cikasuan",
        "text": "滅社後的七腳川平原被改建為吉野移民村，如今成了觀光勝地；這麼悲痛的事件，卻被遺忘成人們休閒娛樂的地方。",
    },
    {
        "student": "商二乙 24・鍾O瑄",
        "event": "cepo",
        "text": "以前從來沒聽說過的故事，因為上了這堂課才有所了解；這些事全部都該知道，畢竟發生在台灣這塊土地上。",
    },
    {
        "student": "商二乙 18・吳O瑤",
        "event": "dafen",
        "text": "過去在這片土地上的祖先們遇到的事，才有現在的我們。",
    },
]

# 學習歷程：學生的實作心得（問卷第 4 題，含批判 AI 限制與使用經驗）
AI_LITERACY_QUOTES = [
    {"student": "商二乙 18・吳O瑤", "text": "不能百分之百交給 AI，它只能達到輔助的作用，幫忙整理資料、圈出重點。"},
    {"student": "多二甲 11・王O庭", "text": "很方便，但用深度思考時會參雜一些類似但無關的事件。"},
    {"student": "多二甲 16・杜O蕎", "text": "記載與事實往往有偏差，研究時要收集不同立場的資料，以免減少客觀性。"},
    {"student": "多二甲 05・張O瑞", "text": "能快速統整出重點，在學習的同時，也另外得到了處理資料的能力。"},
    {"student": "多二甲 13・蔡O君", "text": "最近準備報告時也跟組員提到能用這個軟體，壓力小了也更方便了，未來會繼續用它協助作業和報告。"},
    {"student": "商二乙 25・張O茹", "text": "我更了解七腳川事件的經過，也知道歷史不能只從單一角度看待。"},
    {"student": "商二乙 24・鍾O瑄", "text": "覺得好特別，以前從來沒聽說過的故事，因為上了這堂課才有所了解。"},
    {"student": "商二乙 03・李O諺", "text": "不僅讓我知道原住民的歷史，也讓我更會用 NotebookLM 和 AI 去做作業。"},
    {"student": "英二乙 09・余O璿", "text": "非常實用的工具，整理、製成報告、學習卡都很有用。"},
    {"student": "商二乙 19・梁O芝", "text": "比我一個一個找還要快，能夠快速提升學習、整理資料。"},
]

# 尾聲：出口牆「臺灣所有人民應該知道的事」（問卷原句）
EXIT_WALL = [
    {"student": "多二甲 11・王O庭", "text": "我們不該忘記原住民祖先們的英勇對抗。"},
    {"student": "多二甲 16・杜O蕎", "text": "該知道的是完整歷史的事實，而非偏向某方的歷史。"},
    {"student": "英二乙 09・余O璿", "text": "不論族群，生長在台灣這片土地的我們，都該記得原住民族受過的、無法挽回的迫害。"},
    {"student": "商二乙 19・梁O芝", "text": "應該要知道許多歷史，而不是讓它被忘記。"},
    {"student": "多二甲 05・張O瑞", "text": "對於發生的憾事必須重視，也必須對族群給予尊重與理解，讓台灣固有的人文得以永續。"},
    {"student": "商二乙 30・潘O澕", "text": "不要打仗。"},
]

EXIT_WALL_CLOSER = {"student": "多二甲 13・蔡O君", "text": "這片土地並非一片祥和，請將歷史銘記在心。"}

# 各事件的學生產出對照（依事件理解卡的 Studio 選擇＋實際上傳的心智圖判定）。
# 用班級＋座號＋屏蔽名，座號唯一可追蹤；兩位完全空白未產出者（潘鴻宇、邢越樺）不列。
STUDENT_OUTPUTS = {
    "cepo": [
        {"student": "商二乙 30・潘O澕", "output": "心智圖"},
        {"student": "多二甲 13・蔡O君", "output": "心智圖"},
        {"student": "英二乙 09・余O璿", "output": "心智圖"},
        {"student": "商二乙 24・鍾O瑄", "output": "簡報"},
    ],
    "truku": [
        {"student": "多二甲 11・王O庭", "output": "心智圖"},
        {"student": "商二乙 20・林O妏", "output": "簡報"},
    ],
    "dafen": [
        {"student": "多二甲 16・杜O蕎", "output": "心智圖"},
        {"student": "商二乙 01・李O揚", "output": "心智圖"},
        {"student": "商二乙 19・梁O芝", "output": "心智圖"},
        {"student": "商二乙 18・吳O瑤", "output": "心智圖"},
    ],
    "cikasuan": [
        {"student": "多二甲 05・張O瑞", "output": "心智圖"},
        {"student": "商二乙 25・張O茹", "output": "音訊摘要"},
        {"student": "商二乙 03・李O諺", "output": "心智圖"},
    ],
}

# AI 節錄中的立場詞自動加註（學生審查決議的全站執行）
STANCE_TERMS = ["兇蕃", "兇番", "歸順", "理蕃", "理番", "招撫", "撫番", "平定", "平亂", "討伐", "滅社", "叛亂"]
STANCE_PATTERN = re.compile("(" + "|".join(STANCE_TERMS) + ")")


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def mark_stance(escaped_text: str) -> str:
    """在已轉義的 AI 節錄中標記立場詞（學生審查決議：殖民用語須註明為日方／官方視角）。"""
    return STANCE_PATTERN.sub(
        r'<mark class="stance" title="日方／官方文獻用語。學生審查會決議：照錄時須註明立場。">\1</mark>',
        escaped_text,
    )


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
            "title": "原住民十大歷史事件敘事展覽",
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
        "review_board": {
            "date": "2026-06-11",
            "reviewers": 14,
            "prior_knowledge": PRIOR_KNOWLEDGE,
            "votes": REVIEW_VOTES,
            "rewrite_pairs": REWRITE_PAIRS,
            "full_three_students": THREE_SENTENCE_STUDENTS,
            "laurel_quotes": LAUREL_QUOTES,
            "ai_literacy": AI_LITERACY_QUOTES,
            "exit_wall": [*EXIT_WALL, EXIT_WALL_CLOSER],
        },
        "student_outputs": STUDENT_OUTPUTS,
    }


CSS = r"""
/* ---- 主題別名：事件色與金色在淺色版自動換成出版用色 ---- */
.theme-dark{--c-cepo:var(--color-cepo-dark);--c-dafen:var(--color-dafen-dark);--c-cikasuan:var(--color-cikasuan-dark);--c-truku:var(--color-truku-dark);--ink-red:#E85A52;--paper:#F3ECDD;--paper-ink:#2B2520}
.theme-light{--c-cepo:var(--color-cepo);--c-dafen:var(--color-dafen);--c-cikasuan:var(--color-cikasuan);--c-truku:var(--color-truku);--accent:#8B5E1F;--ink-red:#C73E3A;--paper:#FFFBF2;--paper-ink:#2B2520}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg-main);color:var(--text-primary);font-family:var(--font-serif);line-height:1.8;overflow-x:hidden}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
/* ---- 主題切換鈕 ---- */
.theme-toggle{position:fixed;top:14px;right:14px;z-index:90;border:1px solid var(--line-soft);background:var(--bg-card);color:var(--text-title);font-family:var(--font-sans);font-size:13px;padding:8px 14px;border-radius:999px;cursor:pointer;backdrop-filter:blur(4px)}
.theme-toggle:hover{border-color:var(--accent);color:var(--accent)}
/* ---- 幕標 ---- */
.act-label{font-family:var(--font-sans);font-size:13px;letter-spacing:.4em;color:var(--accent);text-transform:uppercase;margin-bottom:10px}
.act-label::before{content:'';display:inline-block;width:26px;height:1px;background:var(--accent);vertical-align:middle;margin-right:12px}
/* ---- Hero（背景獨立圖層，展示版做 Ken Burns 與晨霧） ---- */
.hero{position:relative;min-height:92vh;display:grid;align-content:end;overflow:hidden;border-bottom:1px solid var(--line-thin);background:var(--bg-page)}
.hero-bg{position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,11,8,.85),rgba(14,11,8,.3)),url("../assets/images/hero_valley.png") center/cover no-repeat;will-change:transform}
.hero-mist{display:none}
.hero-veil{display:none}
.hero-inner{position:relative;z-index:2;max-width:1180px;margin:0 auto;width:100%;padding:44px 24px 56px}
.eyebrow{font-family:var(--font-sans);font-size:12px;letter-spacing:.28em;color:#D9A441;text-transform:uppercase}
.hero h1{font-size:56px;line-height:1.16;margin:12px 0 6px;color:#fff;letter-spacing:.02em}
.hero .sub{font-family:var(--font-sans);font-size:18px;color:#D9A441;letter-spacing:.14em;margin:0 0 14px}
.hero p.intro{max-width:780px;margin:0;color:rgba(245,241,234,.88);font-family:var(--font-sans);font-size:17px}
.nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}
.nav a{color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.28);padding:8px 13px;border-radius:8px;font-family:var(--font-sans);font-size:13px;background:rgba(0,0,0,.2)}
.nav a:hover{border-color:#D9A441;color:#D9A441}
.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:28px;max-width:960px}
.stat{border:1px solid rgba(255,255,255,.22);border-radius:8px;padding:12px;background:rgba(14,11,8,.4)}
.stat strong{display:block;color:#fff;font-size:30px;line-height:1.1}
.stat span{font-family:var(--font-sans);font-size:12px;color:rgba(255,255,255,.72)}
section{padding:64px 0;border-bottom:1px solid var(--line-thin)}
h2{font-size:36px;color:var(--text-title);line-height:1.3;margin:0 0 10px;letter-spacing:.01em}
.lead{max-width:840px;color:var(--text-second);font-family:var(--font-sans);font-size:16px;margin:0 0 24px}
.two-col{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);gap:26px;align-items:start}
/* ---- 第一幕：AI 初稿翻頁書 ---- */
#draft{background:radial-gradient(ellipse at 50% 20%,rgba(217,164,65,.06),transparent 60%)}
.book-stage{display:grid;justify-items:center;gap:18px;padding:18px 0 6px}
/* 攤頁式書本：書脊在容器正中，紙頁佔右半，翻過去正好落在左半，不會超出版面 */
/* 單頁置中：每一頁都是完整一張紙，繞中軸翻走露出下一頁，不超出版面、無空白半邊 */
.book{position:relative;width:min(660px,92vw);height:min(700px,80vh);min-height:460px;margin:0 auto;perspective:2400px}
.sheet{position:absolute;inset:0;transform-origin:center center;transform-style:preserve-3d;transition:transform .85s cubic-bezier(.3,.7,.3,1);cursor:pointer}
.sheet.flipped{transform:rotateY(-180deg)}
/* 古意紙頁：宋體、米黃紙、雙線內框、首行縮排、兩端對齊 */
.face{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:var(--paper);background-image:radial-gradient(rgba(120,90,50,.05) 1px,transparent 1px);background-size:7px 7px;color:var(--paper-ink);border:1px solid rgba(43,37,32,.25);border-radius:8px;padding:42px 40px 56px;overflow:hidden;font-family:var(--font-serif);box-shadow:inset 11px 0 22px -16px rgba(43,37,32,.32),0 18px 38px -20px rgba(0,0,0,.6)}
.face::after{content:'';position:absolute;inset:13px;border:1px solid rgba(43,37,32,.22);box-shadow:inset 0 0 0 3px var(--paper),inset 0 0 0 4px rgba(43,37,32,.12);border-radius:3px;pointer-events:none}
.face.cover-face::after{border-color:rgba(217,164,65,.4);box-shadow:inset 0 0 0 3px transparent,inset 0 0 0 4px rgba(217,164,65,.22)}
.face .wm{position:absolute;left:-12%;top:42%;width:124%;text-align:center;transform:rotate(-14deg);font-family:var(--font-serif);font-weight:700;font-size:30px;letter-spacing:.34em;color:rgba(199,62,58,.16);border-top:2px dashed rgba(199,62,58,.22);border-bottom:2px dashed rgba(199,62,58,.22);padding:8px 0;pointer-events:none;user-select:none;z-index:2}
.face .stamp{position:absolute;right:20px;bottom:16px;font-family:var(--font-serif);font-size:12px;letter-spacing:.14em;color:rgba(199,62,58,.8);border:1.5px solid rgba(199,62,58,.55);border-radius:3px;padding:4px 9px;transform:rotate(-4deg);z-index:2}
.face h3{font-family:var(--font-serif);font-size:17px;letter-spacing:.34em;text-indent:.34em;color:rgba(43,37,32,.62);margin:0 0 20px;text-align:center;padding-bottom:12px;position:relative}
.face h3::after{content:'';position:absolute;left:50%;bottom:0;width:48px;height:1px;margin-left:-24px;background:rgba(43,37,32,.3)}
.face blockquote{margin:0 0 18px;font-size:19.5px;line-height:2.15;color:var(--paper-ink);text-indent:2em;letter-spacing:.06em;text-align:justify;text-justify:inter-character}
.face blockquote i{font-style:normal;font-weight:700;background-image:linear-gradient(rgba(199,62,58,.6),rgba(199,62,58,.6));background-repeat:no-repeat;background-position:left bottom;padding-bottom:2px;animation:lineDraw .9s ease .4s both}
@keyframes lineDraw{from{background-size:0% 3px}to{background-size:100% 3px}}
.face .src{font-family:var(--font-serif);font-size:13px;line-height:1.8;color:rgba(43,37,32,.62);border-left:3px solid rgba(199,62,58,.4);padding-left:11px;letter-spacing:.03em}
.face.cover-face{display:grid;align-content:center;text-align:center;background:linear-gradient(160deg,#3A2F24,#241C13);color:#EFE6D2;border:1px solid rgba(217,164,65,.4);background-image:none}
.face.cover-face h3{color:#D9A441;letter-spacing:.55em;text-indent:.55em;font-size:14px;margin-bottom:10px}
.face.cover-face h3::after{background:rgba(217,164,65,.4)}
.face.cover-face .cov-title{font-size:46px;color:#F5F1EA;margin:0 0 6px;letter-spacing:.18em;text-indent:.18em}
.face.cover-face .cov-sub{font-family:var(--font-serif);color:#D98B6A;letter-spacing:.26em;text-indent:.26em;font-size:15px;margin:0 0 24px}
.face.cover-face p{font-family:var(--font-serif);font-size:16px;line-height:2.1;letter-spacing:.04em;color:rgba(239,230,210,.86);margin:0}
.face.cover-face .wm{color:rgba(217,138,106,.2);border-color:rgba(217,138,106,.25)}
.book-controls{display:flex;gap:14px;align-items:center;font-family:var(--font-sans);font-size:13.5px;color:var(--text-second)}
.book-controls button{border:1px solid var(--line-soft);background:var(--bg-card);color:var(--text-title);font-family:var(--font-sans);font-size:14px;padding:8px 16px;border-radius:999px;cursor:pointer}
.book-controls button:hover{border-color:var(--accent);color:var(--accent)}
/* ---- 過場提問 ---- */
.pause{padding:80px 0;text-align:center;background:linear-gradient(180deg,transparent,rgba(0,0,0,.18),transparent)}
.theme-light .pause{background:linear-gradient(180deg,transparent,rgba(43,37,32,.06),transparent)}
.pause .q-small{font-family:var(--font-sans);letter-spacing:.3em;font-size:13px;color:var(--accent);margin-bottom:14px}
.pause h2{font-size:42px;margin-bottom:8px}
.pause p{color:var(--text-second);font-family:var(--font-sans);margin:0 0 28px}
.reveal-btn{font-family:var(--font-sans);font-size:17px;letter-spacing:.08em;color:#1A1612;background:var(--accent);border:0;border-radius:999px;padding:14px 34px;cursor:pointer}
.reveal-btn:hover{filter:brightness(1.08)}
/* ---- 第二幕：審稿桌 ---- */
.vote-grid{display:grid;gap:18px;margin-top:10px}
.vote-card{border:1px solid var(--line-soft);border-radius:10px;background:var(--bg-card);padding:22px 24px}
.vote-card h3{margin:0 0 16px;font-size:22px;color:var(--text-title)}
.vote-row{display:grid;grid-template-columns:minmax(0,1fr) 110px 44px;gap:12px;align-items:center;padding:7px 0;font-family:var(--font-sans);font-size:14.5px}
.vote-row .opt{color:var(--text-second)}
.vote-row.win .opt{color:var(--text-title);font-weight:700}
.vote-row .bar{height:12px;border-radius:999px;background:rgba(127,127,127,.16);overflow:hidden}
.vote-row .bar i{display:block;height:100%;width:0;border-radius:999px;background:var(--text-muted);transition:width 1.1s cubic-bezier(.2,.7,.3,1)}
.vote-row.win .bar i{background:var(--accent)}
.revealed .vote-row .bar i{width:var(--w)}
.vote-row .n{text-align:right;font-variant-numeric:tabular-nums;color:var(--text-title);font-weight:700}
.verdict{margin-top:14px;border-top:1px dashed var(--line-soft);padding-top:12px;font-family:var(--font-sans);font-size:14.5px;color:var(--accent)}
/* ---- 紅筆對照 ---- */
.pairs{display:grid;gap:16px;margin-top:26px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line-soft);border-radius:10px;overflow:hidden}
.pair .side{padding:20px 22px}
.pair .ai-side{background:var(--paper);color:var(--paper-ink)}
.pair .ai-side b{display:block;font-family:var(--font-sans);font-size:12px;letter-spacing:.14em;color:rgba(199,62,58,.85);margin-bottom:10px}
.pair .ai-side p{margin:0;font-size:16.5px;line-height:1.95;text-decoration:line-through;text-decoration-color:rgba(199,62,58,.65);text-decoration-thickness:2px}
.pair .st-side{background:var(--bg-card);border-left:4px solid var(--accent)}
.pair .st-side b{display:block;font-family:var(--font-sans);font-size:12px;letter-spacing:.14em;color:var(--accent);margin-bottom:10px}
.pair .st-side p{margin:0 0 10px;font-size:17.5px;line-height:1.95;color:var(--text-title)}
.pair .st-side .why{font-family:var(--font-sans);font-size:13.5px;color:var(--text-second);margin:0}
.pair .st-side .who{font-family:var(--font-sans);font-size:12.5px;color:var(--text-muted);margin-top:10px;display:block}
/* ---- 事件展區 ---- */
.event-head{display:grid;grid-template-columns:160px minmax(0,1fr);gap:18px;align-items:stretch}
.event-head img{width:100%;height:100%;min-height:190px;object-fit:cover;border-radius:8px;border:1px solid var(--line-thin)}
.event-title{border-left:5px solid var(--event-color);padding-left:16px}
.event-title .years{font-family:var(--font-sans);font-size:13px;color:var(--event-color);letter-spacing:.18em}
.event-title h3{font-size:29px;color:var(--text-title);margin:4px 0;line-height:1.35}
.event-title p{margin:0;color:var(--text-second)}
.name-note{font-family:var(--font-sans);font-size:13px;color:var(--text-second);background:rgba(127,127,127,.08);border-left:3px solid var(--event-color);padding:8px 12px;border-radius:0 6px 6px 0;margin-top:10px}
.decision-chip{display:inline-block;font-family:var(--font-sans);font-size:11.5px;letter-spacing:.06em;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:3px 10px;margin-top:10px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{border:1px solid var(--line-soft);border-radius:999px;padding:5px 9px;font-family:var(--font-sans);font-size:12px;color:var(--text-primary)}
.panel{background:var(--bg-card);border:1px solid var(--line-soft);border-radius:8px;padding:18px}
.panel h4{margin:0 0 10px;color:var(--text-title);font-size:18px}
.contrib{margin-top:16px;padding-top:14px;border-top:1px solid var(--line-soft)}
.contrib h4{margin:0 0 10px;color:var(--text-title);font-size:16px}
.contrib-list{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.contrib-list li{display:flex;justify-content:space-between;align-items:center;gap:10px;font-family:var(--font-sans);font-size:13.5px;border-left:3px solid var(--event-color);background:rgba(127,127,127,.06);padding:6px 10px;border-radius:0 6px 6px 0}
.contrib-list .who{color:var(--text-primary)}
.contrib-list .out{color:var(--event-color);font-size:12px;border:1px solid var(--event-color);border-radius:999px;padding:2px 9px;white-space:nowrap}
.contrib-note{margin:10px 0 0;font-family:var(--font-sans);font-size:11.5px;color:var(--text-muted);line-height:1.6}
.notebook-list{display:grid;gap:12px}
.notebook{border-left:3px solid var(--event-color);background:rgba(0,0,0,.12);padding:12px;border-radius:0 8px 8px 0}
.theme-light .notebook{background:rgba(43,37,32,.05)}
.notebook h5{margin:0 0 5px;color:var(--text-title);font-size:16px}
.notebook .meta{font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:8px}
.quote{margin:8px 0 0;padding:10px;border:1px solid var(--line-thin);border-radius:8px}
.quote b{display:block;font-family:var(--font-sans);font-size:12px;color:var(--event-color);margin-bottom:4px}
.quote p{margin:0;font-size:14px;color:var(--text-primary)}
/* 立場詞紅線：以背景漸層當底線，進場時由左而右畫出（D-1 紅線顯影） */
mark.stance{color:inherit;cursor:help;background-image:linear-gradient(var(--ink-red),var(--ink-red));background-repeat:no-repeat;background-position:left bottom;background-size:100% 2px;background-color:transparent;padding-bottom:2px}
html.js .rv mark.stance{background-size:0% 2px}
html.js .rv.on mark.stance{background-size:100% 2px;transition:background-size .8s ease .45s}
.media-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.media-card{border:1px solid var(--line-soft);border-radius:8px;padding:14px;background:var(--bg-card)}
.media-card h5{font-size:16px;margin:0 0 4px;color:var(--text-title)}
.media-card p{font-family:var(--font-sans);font-size:13px;color:var(--text-second);margin:0 0 10px}
.media-card audio,.media-card video{width:100%;display:block;border-radius:6px}
/* 每事件縱谷位置小圖（內嵌 SVG，不捲動） */
.locator{text-align:center}
.locator h4{margin:0 0 8px;color:var(--text-title);font-size:16px}
.locator-map{background:rgba(127,127,127,.06);border:1px solid var(--line-soft);border-radius:8px;padding:8px}
.locator-map svg{display:block;width:auto;max-width:100%;height:auto;max-height:300px;margin:0 auto;color:var(--text-muted)}
.locator-map text{font-family:var(--font-sans)}
.locator-map .loc-on{fill:var(--event-color);font-size:13px;font-weight:700}
.locator-map .loc-off{fill:var(--text-muted);font-size:11px}
.locator-map .loc-compass{fill:var(--text-muted);font-size:10px;letter-spacing:.1em}
.locator-link{display:inline-block;margin-top:8px;color:var(--accent);font-family:var(--font-sans);font-size:13px}
/* ---- 心智圖 ---- */
.mindmap-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.mindmap-card{border:1px solid var(--line-soft);background:var(--bg-card);border-radius:8px;overflow:hidden}
.mindmap-card figure{margin:0;background:#f5f1ea}
.mindmap-card iframe{display:block;width:100%;aspect-ratio:16/10;border:0;background:#f5f1ea}
.mindmap-body{padding:14px}
.mindmap-body h4{font-size:18px;margin:0 0 4px;color:var(--text-title)}
.mindmap-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-family:var(--font-sans);font-size:12px;color:var(--text-muted);margin-bottom:10px}
.badge{display:inline-block;font-family:var(--font-sans);font-size:11px;letter-spacing:.06em;padding:3px 9px;border-radius:999px;border:1px solid var(--line-soft);white-space:nowrap}
.badge-event{color:var(--event-color);border-color:var(--event-color)}
.badge-pending{color:var(--accent);border-color:var(--accent);background:rgba(217,164,65,.1)}
.badge-archived{color:var(--text-muted);border-color:var(--line-soft);font-size:10.5px}
/* ---- 桂冠句子牆（桂冠預設收起，點卡片才頒出） ---- */
#laurels{background:radial-gradient(ellipse at 50% 0%,rgba(217,164,65,.07),transparent 55%)}
/* 完整三句卡片 */
#fullthree{background:radial-gradient(ellipse at 50% 0%,rgba(217,164,65,.08),transparent 55%)}
.ft-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:26px 0 4px}
.ft-card{position:relative;border:1px solid var(--line-soft);border-radius:12px;background:var(--bg-card);padding:24px 26px 16px;text-align:center;cursor:pointer;transition:border-color .3s}
.ft-card:hover{border-color:var(--accent)}
.ft-rows{display:grid;gap:12px;text-align:left;margin:4px 0 14px}
.ft-row{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start}
.ft-tag{font-family:var(--font-sans);font-size:13px;font-weight:700;color:var(--event-color);border:1px solid var(--event-color);border-radius:6px;padding:2px 8px;white-space:nowrap;margin-top:4px}
.ft-row p{margin:0;font-size:18px;line-height:1.8;color:var(--text-title)}
.ft-card .meta-line{font-family:var(--font-sans);font-size:14px;color:var(--text-muted)}
.ft-card .meta-line b{color:var(--event-color);font-weight:500}
@media(max-width:880px){.ft-grid{grid-template-columns:1fr}.ft-row p{font-size:16px}}
.laurel-featured{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:26px 0 12px}
.laurel-card{position:relative;border:1px solid var(--line-soft);border-radius:12px;background:var(--bg-card);padding:26px 28px 18px;text-align:center;cursor:pointer;transition:border-color .3s}
.laurel-card:hover{border-color:var(--accent)}
.laurel-card p.sent{font-size:23px;line-height:1.85;color:var(--text-title);margin:0 0 16px;text-wrap:balance}
.laurel-card .meta-line{font-family:var(--font-sans);font-size:13px;color:var(--text-muted)}
.laurel-card .meta-line b{color:var(--event-color);font-weight:500}
.laurel-quotes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}
.quote-card{border:1px solid var(--line-soft);border-radius:10px;background:var(--bg-card);padding:18px 20px 14px;position:relative;text-align:center;cursor:pointer;transition:border-color .3s}
.quote-card:hover{border-color:var(--accent)}
.quote-card p{font-size:16px;line-height:1.9;color:var(--text-primary);margin:0 0 12px}
.quote-card .meta-line{font-family:var(--font-sans);font-size:12.5px;color:var(--text-muted)}
.quote-card .meta-line b{color:var(--event-color);font-weight:500}
.medal{position:relative;width:200px;margin:0 auto;max-height:0;opacity:0;transform:translateY(-10px) scale(.65);transition:max-height .45s ease,opacity .45s ease,transform .55s cubic-bezier(.2,.9,.3,1.25);pointer-events:none}
.awarded .medal{max-height:160px;opacity:1;transform:none;margin-bottom:10px}
.medal svg{display:block;width:100%;height:auto;color:var(--accent)}
.medal .medal-text{position:absolute;inset:0 0 14% 0;display:grid;place-content:center;text-align:center}
.medal .medal-text b{font-family:var(--font-serif);font-size:25px;letter-spacing:.28em;text-indent:.28em;color:var(--accent);font-weight:700}
.medal .medal-text span{font-family:var(--font-sans);font-size:11px;letter-spacing:.22em;text-indent:.22em;color:var(--accent);margin-top:3px}
.quote-card .medal{width:150px}
.quote-card .medal .medal-text b{font-size:19px}
.quote-card .medal .medal-text span{font-size:10px}
.award-hint{font-family:var(--font-sans);font-size:11.5px;letter-spacing:.2em;color:var(--text-muted);margin-top:12px;user-select:none}
.laurel-card:hover .award-hint,.quote-card:hover .award-hint{color:var(--accent)}
.awarded .award-hint{display:none}
/* ---- 學習歷程 ---- */
.literacy-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:8px}
.literacy-card{border:1px solid var(--line-soft);border-left:4px solid var(--accent);border-radius:8px;background:var(--bg-card);padding:16px 18px}
.literacy-card p{margin:0 0 8px;font-size:15.5px;color:var(--text-primary)}
.literacy-card span{font-family:var(--font-sans);font-size:12px;color:var(--text-muted)}
.prior{margin-top:26px;border:1px solid var(--line-soft);border-radius:10px;background:var(--bg-card);padding:20px 22px;max-width:640px}
.prior h4{margin:0 0 4px;color:var(--text-title);font-size:18px}
.prior .pk-note{font-family:var(--font-sans);font-size:13px;color:var(--text-second);margin:0 0 14px}
.pk-row{display:grid;grid-template-columns:minmax(0,1fr) 130px 36px;gap:12px;align-items:center;padding:5px 0;font-family:var(--font-sans);font-size:14px;color:var(--text-second)}
.pk-row .bar{height:10px;border-radius:999px;background:rgba(127,127,127,.16);overflow:hidden}
.pk-row .bar i{display:block;height:100%;background:var(--accent);border-radius:999px}
.pk-row .n{text-align:right;color:var(--text-title);font-weight:700;font-variant-numeric:tabular-nums}
.checklist{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.checklist li{padding-left:22px;position:relative;font-family:var(--font-sans);font-size:14px}
.checklist li:before{content:"";position:absolute;left:0;top:.65em;width:8px;height:8px;background:var(--accent);border-radius:50%}
.notice{border:1px solid var(--line-soft);border-left:5px solid var(--accent);border-radius:8px;padding:16px;background:rgba(217,164,65,.08);font-family:var(--font-sans)}
/* ---- 出口牆 ---- */
#exit{text-align:center;background:linear-gradient(180deg,transparent,rgba(0,0,0,.22))}
.theme-light #exit{background:linear-gradient(180deg,transparent,rgba(43,37,32,.07))}
.exit-list{max-width:760px;margin:30px auto 0;display:grid;gap:18px}
.exit-list p{margin:0;font-size:19px;line-height:1.9;color:var(--text-primary)}
.exit-list span{display:block;font-family:var(--font-sans);font-size:12.5px;color:var(--text-muted);margin-top:4px}
.exit-closer{max-width:820px;margin:48px auto 0;padding-top:36px;border-top:1px solid var(--line-soft)}
.exit-closer p{font-size:33px;line-height:1.7;color:var(--text-title);margin:0 0 10px;text-wrap:balance}
.exit-closer span{font-family:var(--font-sans);font-size:13.5px;color:var(--accent)}
/* ---- 參考資料 ---- */
.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:16px}
.ref-group{border:1px solid var(--line-soft);border-radius:8px;background:var(--bg-card);padding:16px}
.ref-group h3{margin:0 0 8px;color:var(--text-title);font-size:18px}
.ref-group ul{margin:0;padding-left:18px}
.ref-group li{font-family:var(--font-sans);font-size:13px;color:var(--text-second);line-height:1.7}
.source-link{display:inline-block;margin-top:10px;color:var(--accent);font-family:var(--font-sans);font-size:13px}
footer{padding:26px 24px;text-align:center;color:var(--text-muted);font-family:var(--font-sans);font-size:12px}
@media(max-width:880px){
.hero{min-height:88vh}.hero h1{font-size:38px}
.stats,.two-col,.media-grid,.mindmap-grid,.refs,.laurel-featured,.laurel-quotes,.literacy-grid{grid-template-columns:1fr}
.event-head{grid-template-columns:1fr}.event-head img{height:220px}
.wrap{padding:0 16px}section{padding:40px 0}
.book{width:94vw;height:min(470px,66vh);min-height:330px}
.face{padding:18px 16px 42px}.face blockquote{font-size:15px;line-height:1.85}.face h3{font-size:13px;margin-bottom:12px}
.face.cover-face .cov-title{font-size:26px}.face .wm{font-size:17px}.face .src{font-size:11.5px}
.pair{grid-template-columns:1fr}.pair .st-side{border-left:0;border-top:4px solid var(--accent)}
.pause h2{font-size:30px}.laurel-card p.sent{font-size:19px}.exit-closer p{font-size:24px}
.vote-row{grid-template-columns:minmax(0,1fr) 70px 36px}
}
/* ============ 影片放大：閱讀文字全面加大（約 +40%，後置覆寫優先） ============ */
h2{font-size:46px}
.act-label{font-size:16px}
.lead{font-size:21px;max-width:920px}
.hero h1{font-size:64px}
.hero .sub{font-size:23px}
.hero p.intro{font-size:23px;max-width:880px}
.nav a{font-size:16px}
.stat strong{font-size:40px}
.stat span{font-size:15px}
.theme-toggle{font-size:16px;padding:10px 18px}
.face blockquote{font-size:21px;line-height:1.95}
.face h3{font-size:19px}
.face .src{font-size:14.5px;line-height:1.8}
.face .wm{font-size:34px}
.face .stamp{font-size:15px}
.face.cover-face .cov-title{font-size:54px}
.face.cover-face .cov-sub{font-size:19px}
.face.cover-face p{font-size:20px}
.pause h2{font-size:54px}
.pause .q-small{font-size:16px}
.pause p{font-size:21px}
.reveal-btn{font-size:22px;padding:16px 40px}
.book-controls{font-size:16.5px}
.book-controls button{font-size:17px;padding:10px 20px}
.vote-card h3{font-size:28px}
.vote-row{font-size:19px}
.verdict{font-size:18.5px}
.pair .ai-side p{font-size:22px}
.pair .st-side p{font-size:23px}
.pair .st-side .why{font-size:16.5px}
.pair .st-side .who{font-size:15px}
.pair .ai-side b,.pair .st-side b{font-size:15px}
.event-title h3{font-size:37px}
.event-title .years{font-size:16px}
.event-title p{font-size:19px}
.name-note{font-size:16.5px}
.decision-chip{font-size:14px}
.chip{font-size:15px}
.panel h4{font-size:23px}
.notebook h5{font-size:20px}
.notebook .meta{font-size:15px}
.quote b{font-size:15px}
.quote p{font-size:18px}
.contrib h4{font-size:20px}
.contrib-list li{font-size:17px}
.contrib-list .out{font-size:14.5px}
.contrib-note{font-size:14px}
.media-card h5{font-size:20px}
.media-card p{font-size:16.5px}
.mindmap-body h4{font-size:23px}
.mindmap-meta{font-size:15px}
.badge{font-size:14px}
.badge-archived{font-size:13px}
.laurel-card p.sent{font-size:31px}
.laurel-card .meta-line{font-size:16.5px}
.quote-card p{font-size:21px}
.quote-card .meta-line{font-size:15.5px}
.medal .medal-text b{font-size:30px}
.medal .medal-text span{font-size:14px}
.quote-card .medal .medal-text b{font-size:23px}
.quote-card .medal .medal-text span{font-size:12.5px}
.award-hint{font-size:14.5px}
.literacy-card p{font-size:20px}
.literacy-card span{font-size:15px}
.prior h4{font-size:23px}
.prior .pk-note{font-size:16px}
.pk-row{font-size:18px}
.exit-list p{font-size:25px}
.exit-list span{font-size:15.5px}
.exit-closer p{font-size:42px}
.exit-closer span{font-size:17px}
.ref-group h3{font-size:22px}
.ref-group li{font-size:16.5px}
.source-link{font-size:16px}
footer{font-size:14.5px}
@media(max-width:880px){
.hero h1{font-size:42px}.hero p.intro{font-size:18px}
h2{font-size:34px}.lead{font-size:18px}
.face blockquote{font-size:19px;line-height:1.9}.face h3{font-size:16px}
.face.cover-face .cov-title{font-size:32px}.face .wm{font-size:20px}.face .src{font-size:13.5px}
.pause h2{font-size:32px}.laurel-card p.sent{font-size:23px}.exit-closer p{font-size:27px}
.vote-card h3{font-size:22px}.vote-row{font-size:16px}.pair .ai-side p,.pair .st-side p{font-size:18px}
.event-title h3{font-size:28px}.quote-card p{font-size:18px}.exit-list p{font-size:20px}
}
/* ============ 墨色顯影（A-2 捲動浮現／只演一次） ============ */
html.js .rv{opacity:0;transform:translateY(16px);filter:blur(6px)}
html.js .rv.on{opacity:1;transform:none;filter:none;transition:opacity .9s ease-out,transform .9s cubic-bezier(.2,.7,.3,1),filter .9s ease-out}
html.js #exit .rv.on{transition-duration:1.4s}
/* 含 3D／iframe 的元素不上模糊，避免破壞翻頁立體與預覽載入 */
html.js .book-stage.rv,html.js .mindmap-card.rv{filter:none}
/* ============ 電影顆粒（B-10） ============ */
.grain{position:fixed;inset:0;z-index:70;pointer-events:none;opacity:.05;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E")}
.theme-light .grain{opacity:.035}
/* ============ 四色閱讀進度線（D-3） ============ */
.progress{position:fixed;top:0;left:0;height:3px;width:0;z-index:95;background:linear-gradient(90deg,var(--c-cepo),var(--c-truku),var(--c-dafen),var(--c-cikasuan));background-attachment:fixed;background-size:100vw 100%}
/* ============ 展示版片頭（A-1，只在 .cinema）：黑幕亮起→山谷推近→霧起→片名顯影 ============ */
@keyframes inkIn{from{opacity:0;filter:blur(8px);transform:translateY(14px)}to{opacity:1;filter:none;transform:none}}
@keyframes titleIn{from{opacity:0;filter:blur(12px);letter-spacing:.3em;transform:translateY(18px)}to{opacity:1;filter:none;letter-spacing:.02em;transform:none}}
@keyframes veilUp{to{opacity:0}}
@keyframes kenburns{from{transform:scale(1.14) translateY(-1.5%)}to{transform:scale(1) translateY(0)}}
@keyframes mistA{from{transform:translateX(-14%) translateY(1%)}to{transform:translateX(12%) translateY(-1%)}}
@keyframes mistB{from{transform:translateX(10%)}to{transform:translateX(-12%)}}
@keyframes barScan{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.cinema .hero-veil{display:block;position:absolute;inset:0;z-index:4;background:#0E0B08;pointer-events:none;animation:veilUp 2s ease .25s forwards}
.cinema .hero-bg{animation:kenburns 16s cubic-bezier(.2,.5,.3,1) forwards}
.cinema .hero-mist{display:block;position:absolute;inset:-6%;z-index:1;pointer-events:none;filter:blur(16px);background:radial-gradient(48% 34% at 24% 70%,rgba(222,212,192,.22),transparent 70%),radial-gradient(40% 26% at 72% 52%,rgba(222,212,192,.13),transparent 72%);animation:mistA 26s ease-in-out infinite alternate}
.cinema .hero-mist::after{content:'';position:absolute;inset:0;filter:blur(20px);background:radial-gradient(52% 30% at 55% 80%,rgba(210,198,176,.16),transparent 70%),radial-gradient(30% 22% at 10% 40%,rgba(210,198,176,.1),transparent 75%);animation:mistB 42s ease-in-out infinite alternate}
.cinema .event-color-bar{transform-origin:left center;animation:barScan 1.6s cubic-bezier(.2,.7,.2,1) .6s both;box-shadow:0 0 14px rgba(217,164,65,.35)}
.cinema .hero .eyebrow{opacity:0;animation:inkIn 1.1s ease-out 1s forwards}
.cinema .hero h1{opacity:0;animation:titleIn 1.7s cubic-bezier(.2,.6,.25,1) 1.25s forwards}
.cinema .hero .sub{opacity:0;animation:inkIn 1.2s ease-out 2s forwards}
.cinema .hero p.intro{opacity:0;animation:inkIn 1.2s ease-out 2.4s forwards}
.cinema .hero .nav{opacity:0;animation:inkIn 1s ease-out 2.85s forwards}
.cinema .hero .stats{opacity:0;animation:inkIn 1s ease-out 3.15s forwards}
/* ============ 動態減量：一律直接顯示 ============ */
@media(prefers-reduced-motion:reduce){
html.js .rv{opacity:1;transform:none;filter:none}
html.js .rv mark.stance{background-size:100% 2px}
.face blockquote i{animation:none;background-size:100% 3px}
.cinema .hero-veil{animation:none;opacity:0}
.cinema .hero-bg,.cinema .hero-mist,.cinema .hero-mist::after,.cinema .event-color-bar,.cinema .hero .eyebrow,.cinema .hero h1,.cinema .hero .sub,.cinema .hero p.intro,.cinema .hero .nav,.cinema .hero .stats{animation:none;opacity:1;transform:none}
}
"""

def _build_laurel_svg() -> str:
    """影展式桂冠：細長尖葉沿弧線排列、左枝計算後右枝鏡射、底部一顆小星，
    文字由 HTML 疊在環心。葉片細瘦尖長（約 7:1），不加粗、不用粗描邊。"""
    cx, cy, radius = 100.0, 66.0, 52.0
    leaf = "M0 0 Q8 -1.9 16.5 0 Q8 1.9 0 0 Z"  # 細長尖葉，尖端在 x=16.5
    leaves = []
    branch_pts = []
    thetas = list(range(102, 259, 7))  # 由左下沿左側掃到左上
    span = thetas[-1] - thetas[0]
    for theta in thetas:
        rad = math.radians(theta)
        x = round(cx + radius * math.cos(rad), 1)
        y = round(cy + radius * math.sin(rad), 1)
        branch_pts.append((x, y))
        t = (theta - thetas[0]) / span
        scale = round(1.0 - 0.44 * t, 3)  # 越靠頂端越小
        rot = round(theta + 40, 1)
        leaves.append(
            f'<path d="{leaf}" transform="translate({x} {y}) rotate({rot}) scale({scale})"/>'
        )
    branch = "M" + " L".join(f"{x} {y}" for x, y in branch_pts)
    branch_path = (
        f'<path d="{branch}" fill="none" stroke="currentColor" '
        'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    left = f'{branch_path}<g fill="currentColor">{"".join(leaves)}</g>'
    star = '<path d="M100 122 l1.8 3.7 4.1.6-3 2.9.7 4.1-3.6-1.9-3.6 1.9.7-4.1-3-2.9 4.1-.6z"/>'
    return (
        '<svg class="laurel" viewBox="0 0 200 132" aria-hidden="true">'
        f"{left}"
        f'<g transform="translate(200,0) scale(-1,1)">{left}</g>'
        f'<g fill="currentColor">{star}</g>'
        "</svg>"
    )


LAUREL_SVG = _build_laurel_svg()


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
        f'<div class="quote"><b>AI 生成｜{esc(sample["title"])}</b><p>{mark_stance(esc(sample["text"]))}</p></div>'
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
        title = item["title"] if item["title"] != "NotebookLM Mind Map" else f'{event["name"].split(" /")[0]} 心智圖'
        if item.get("archived_by") == "author_event":
            badge += '<span class="badge badge-archived">依作者研究事件歸檔</span>'
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


def build_flip_faces() -> list[str]:
    """第一幕：AI 初稿翻頁書的各頁 HTML。FLIPBOOK_PAGES 內含受控 HTML（<i>/<br>），不再轉義。
    整本書只用「一張」紙元素呈現，翻頁時由 JS 在側面（看不見的瞬間）抽換內容，
    避免多張 3D 頁面堆疊在 preserve-3d 下互相穿透。"""
    faces = []
    for page in FLIPBOOK_PAGES:
        if page["kind"] in ("cover", "back"):
            note = f'<p style="margin-top:18px;font-size:12px;color:rgba(239,230,210,.6)">{page["note"]}</p>' if page["note"] else ""
            faces.append(
                '<div class="face cover-face">'
                "<h3>花蓮高商・多元文化與文學</h3>"
                f'<div class="cov-title">{page["title"]}</div>'
                f'<div class="cov-sub">{page["subtitle"]}</div>'
                f'<p>{page["body"]}</p>{note}'
                '<div class="wm">AI 初稿・未經審查</div>'
                "</div>"
            )
        else:
            color = EVENTS[page["event"]]["color"]
            quotes = "".join(f"<blockquote>「{q}」</blockquote>" for q in page["quotes"])
            faces.append(
                f'<div class="face" style="border-top:5px solid {color}">'
                f'<h3>{page["title"]}</h3>{quotes}'
                f'<div class="src">{page["note"]}</div>'
                '<div class="wm">AI 初稿・未經審查</div>'
                '<div class="stamp">AI 生成・不得視為史實</div>'
                "</div>"
            )
    return faces


def render_votes() -> str:
    cards = []
    for vote in REVIEW_VOTES:
        rows = []
        for opt in vote["options"]:
            pct = round(opt["count"] / 14 * 100)
            win = " win" if opt.get("win") else ""
            rows.append(
                f'<div class="vote-row{win}"><span class="opt">{esc(opt["label"])}</span>'
                f'<span class="bar"><i style="--w:{pct}%"></i></span>'
                f'<span class="n">{opt["count"]}</span></div>'
            )
        cards.append(
            f'<article class="vote-card"><h3>{esc(vote["question"])}</h3>{"".join(rows)}'
            f'<div class="verdict">{esc(vote["verdict"])}</div></article>'
        )
    return "".join(cards)


def render_pairs() -> str:
    pairs = []
    for pair in REWRITE_PAIRS:
        color = EVENTS[pair["event"]]["color"]
        pairs.append(
            f'<article class="pair" style="--event-color:{color}">'
            f'<div class="side ai-side"><b>AI 原句（已駁回）</b><p>{esc(pair["ai"])}</p></div>'
            f'<div class="side st-side"><b>學生修訂</b><p>{esc(pair["rewrite"])}</p>'
            f'<p class="why">修訂理由：{esc(pair["reason"])}</p>'
            f'<span class="who">{esc(pair["student"])}</span></div>'
            "</article>"
        )
    return "".join(pairs)


def _medal(label: str) -> str:
    return (
        f'<div class="medal">{LAUREL_SVG}'
        f'<div class="medal-text"><b>入選</b><span>{esc(label)}</span></div></div>'
    )


def render_full_three() -> str:
    """完整三句區：每位同學一張卡，事實／差異／省思三句並列，點擊頒桂冠。"""
    cards = []
    for item in THREE_SENTENCE_STUDENTS:
        event = EVENTS[item["event"]]
        rows = (
            f'<div class="ft-row"><span class="ft-tag">事實</span>'
            f'<p>{esc(item["fact"])}</p></div>'
            f'<div class="ft-row"><span class="ft-tag">差異</span>'
            f'<p>{esc(item["difference"])}</p></div>'
            f'<div class="ft-row"><span class="ft-tag">省思</span>'
            f'<p>{esc(item["reflection"])}</p></div>'
        )
        cards.append(
            f'<article class="ft-card" style="--event-color:{event["color"]}">'
            f'{_medal("完整三句")}'
            f'<div class="ft-rows">{rows}</div>'
            f'<div class="meta-line">{esc(item["student"])}｜<b>{esc(event["name"])}</b></div>'
            '<div class="award-hint">▾ 點擊頒發桂冠</div>'
            "</article>"
        )
    return f'<div class="ft-grid">{"".join(cards)}</div>'


def render_quote_wall() -> str:
    """學生的一句話：未完成三句、但留下一句的同學。"""
    quotes = []
    for item in LAUREL_QUOTES:
        event = EVENTS[item["event"]]
        quotes.append(
            f'<article class="quote-card" style="--event-color:{event["color"]}">'
            f'{_medal("佳句")}'
            f'<p>{esc(item["text"])}</p>'
            f'<div class="meta-line">{esc(item["student"])}｜<b>{esc(event["name"])}</b></div>'
            '<div class="award-hint">▾ 點擊頒發桂冠</div>'
            "</article>"
        )
    return f'<div class="laurel-quotes">{"".join(quotes)}</div>'


# 四事件真實經緯度（與互動／列印地圖共用），用花蓮縣界輪廓畫 locator
LOCATOR_EVENTS = {
    "truku": (121.6213, 24.1572, "太魯閣"),
    "cikasuan": (121.5775, 23.9700, "七腳川"),
    "cepo": (121.5025, 23.4720, "大港口"),
    "dafen": (121.0830, 23.2780, "大分"),
}
GEO_OUTLINE_FILE = ROOT / "data" / "geo" / "hualien_outline.json"
_LOC_VIEW_W = 200.0
_LOC_PAD = 12.0


def _load_locator_geometry():
    """載入花蓮縣界並建立投影，回傳 (viewBox 高, 縣界 path, 投影函式)。失敗回 None。"""
    try:
        outline = json.loads(GEO_OUTLINE_FILE.read_text(encoding="utf-8"))
        ring = outline["main"]
    except Exception:
        return None
    # 點數降採樣，小圖不需高解析，縮小檔案
    step = max(1, len(ring) // 130)
    ring = ring[::step]
    lngs = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    lng_min, lng_max = min(lngs), max(lngs)
    lat_min, lat_max = min(lats), max(lats)
    scale = (_LOC_VIEW_W - 2 * _LOC_PAD) / (lng_max - lng_min)
    view_h = round((lat_max - lat_min) * scale + 2 * _LOC_PAD, 1)

    def project(lng, lat):
        x = _LOC_PAD + (lng - lng_min) * scale
        y = _LOC_PAD + (lat_max - lat) * scale
        return round(x, 1), round(y, 1)

    pts = [project(lng, lat) for lng, lat in ring]
    path = "M" + " L".join(f"{x} {y}" for x, y in pts) + " Z"
    return view_h, path, project


_LOCATOR_GEO = _load_locator_geometry()


def render_locator(active_id: str) -> str:
    """每事件一張花蓮縣界位置小圖（內嵌 SVG，不捲動、離線可用），當前事件亮起。"""
    active_color = EVENTS[active_id]["color"]
    if _LOCATOR_GEO is None:
        svg = ""  # 縣界資料缺漏時略過小圖，仍保留完整地圖連結
    else:
        view_h, outline_path, project = _LOCATOR_GEO
        dots, labels = [], []
        for eid, (lng, lat, short) in LOCATOR_EVENTS.items():
            x, y = project(lng, lat)
            if eid == active_id:
                dots.append(
                    f'<circle cx="{x}" cy="{y}" r="13" fill="{EVENTS[eid]["color"]}" opacity="0.2"/>'
                    f'<circle cx="{x}" cy="{y}" r="6.5" fill="{EVENTS[eid]["color"]}"/>'
                    f'<circle cx="{x}" cy="{y}" r="2.3" fill="#fff" opacity="0.9"/>'
                )
                anchor, lx = ("end", x - 12) if x > _LOC_VIEW_W / 2 else ("start", x + 12)
                labels.append(
                    f'<text class="loc-on" x="{lx}" y="{y + 4}" text-anchor="{anchor}">{short}</text>'
                )
            else:
                dots.append(f'<circle cx="{x}" cy="{y}" r="3" fill="currentColor" opacity="0.45"/>')
        svg = (
            f'<svg viewBox="0 0 200 {view_h}" role="img" aria-label="本事件在花蓮縣的位置">'
            f'<path d="{outline_path}" fill="rgba(245,241,234,0.06)" stroke="currentColor" '
            'stroke-width="1" stroke-linejoin="round" opacity="0.55"/>'
            '<text class="loc-compass" x="14" y="22">北 ↑</text>'
            f'{"".join(dots)}{"".join(labels)}'
            "</svg>"
        )
    return (
        f'<div class="locator" style="--event-color:{active_color}">'
        '<h4>本事件位置</h4>'
        f'<div class="locator-map">{svg}</div>'
        '<a class="locator-link" href="event_map_interactive.html" target="_blank" rel="noopener">看完整互動地圖 ↗</a>'
        "</div>"
    )


def render_contributors(event_id: str) -> str:
    rows = STUDENT_OUTPUTS.get(event_id, [])
    if not rows:
        return ""
    items = "".join(
        f'<li><span class="who">{esc(r["student"])}</span>'
        f'<span class="out">{esc(r["output"])}</span></li>'
        for r in rows
    )
    return (
        '<div class="contrib"><h4>本事件・學生產出</h4>'
        f'<ul class="contrib-list">{items}</ul>'
        '<p class="contrib-note">以班級＋座號代號標示產出者，座號唯一可追蹤；姓名依個資原則屏蔽。</p>'
        "</div>"
    )


def render_literacy() -> str:
    cards = "".join(
        f'<article class="literacy-card"><p>「{esc(item["text"])}」</p><span>{esc(item["student"])}</span></article>'
        for item in AI_LITERACY_QUOTES
    )
    return f'<div class="literacy-grid">{cards}</div>'


def render_prior() -> str:
    rows = []
    for item in PRIOR_KNOWLEDGE:
        pct = round(item["count"] / 14 * 100)
        rows.append(
            f'<div class="pk-row"><span>{esc(item["label"])}</span>'
            f'<span class="bar"><i style="width:{pct}%"></i></span>'
            f'<span class="n">{item["count"]}</span></div>'
        )
    return (
        '<div class="prior"><h4>上這門課之前，你認識這些事件嗎？</h4>'
        '<p class="pk-note">開展前審查會問卷，14 位學生作答，超過七成不是從課堂認識這段歷史的。</p>'
        f'{"".join(rows)}</div>'
    )


def render_exit_wall() -> str:
    quotes = "".join(
        f'<p>「{esc(item["text"])}」<span>{esc(item["student"])}</span></p>' for item in EXIT_WALL
    )
    return (
        f'<div class="exit-list">{quotes}</div>'
        f'<div class="exit-closer"><p>「{esc(EXIT_WALL_CLOSER["text"])}」</p>'
        f'<span>{esc(EXIT_WALL_CLOSER["student"])}</span></div>'
    )


JS_CODE = r"""
(function(){
  var body=document.body,root=document.documentElement;
  root.classList.add('js');
  var reduceMotion=!!(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  function setTheme(t){
    ['theme-dark','theme-light'].forEach(function(c){root.classList.remove(c);body.classList.remove(c);});
    root.classList.add(t);body.classList.add(t);
    var b=document.getElementById('themeToggle');
    if(b){b.textContent=(t==='theme-dark')?'☀ 切換淺色版':'🌙 切換深色版';}
    try{localStorage.setItem('exhibitTheme',t);}catch(e){}
  }
  var saved=null;
  try{saved=localStorage.getItem('exhibitTheme');}catch(e){}
  setTheme(saved==='theme-light'?'theme-light':'theme-dark');
  document.getElementById('themeToggle').addEventListener('click',function(){
    setTheme(body.classList.contains('theme-dark')?'theme-light':'theme-dark');
  });

  // 翻頁書：整本只用一張紙 #bookSheet，翻到側面看不見時抽換內容，避免多層 3D 穿透
  var pages=(window.FLIP_PAGES||[]),sheet=document.getElementById('bookSheet');
  var total=pages.length,last=total-1,current=0,busy=false;
  function setHint(){
    var hint=document.getElementById('bookHint');
    if(hint){hint.textContent=(current>=last)?'翻完了，往下走，看審稿人的決定':'點頁面或按方向鍵翻頁（'+(current+1)+' / '+total+'）';}
  }
  function go(target){
    if(busy||!sheet||target<0||target>last||target===current)return;
    busy=true;
    var dir=(target>current)?1:-1;
    sheet.style.transition='transform .42s ease-in';
    sheet.style.transform='rotateY('+(dir>0?-90:90)+'deg)';
    setTimeout(function(){
      current=target;
      sheet.innerHTML=pages[current];          // 側面瞬間換頁
      sheet.style.transition='none';
      sheet.style.transform='rotateY('+(dir>0?90:-90)+'deg)';
      void sheet.offsetWidth;                    // 強制重排，讓回轉動畫生效
      sheet.style.transition='transform .42s ease-out';
      sheet.style.transform='rotateY(0deg)';
      setHint();
      setTimeout(function(){busy=false;},430);
    },420);
  }
  function next(){go(current+1);}
  function prev(){go(current-1);}
  if(sheet){sheet.addEventListener('click',next);}
  var bp=document.getElementById('bookPrev'),bn=document.getElementById('bookNext');
  if(bp){bp.addEventListener('click',prev);}
  if(bn){bn.addEventListener('click',next);}
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'){next();}
    if(e.key==='ArrowLeft'){prev();}
  });
  setHint();

  Array.prototype.forEach.call(document.querySelectorAll('.laurel-card,.quote-card,.ft-card'),function(card){
    card.addEventListener('click',function(){card.classList.toggle('awarded');});
  });

  // 數字滾動（B-8）：等寬數字由 0 緩升至目標值，動態減量時直接顯示
  function countUp(el,ms){
    var target=parseInt((el.textContent||'').replace(/[^0-9]/g,''),10);
    if(isNaN(target)){return;}
    if(reduceMotion){el.textContent=String(target);return;}
    el.textContent='0';
    var start=null;
    function tick(ts){
      if(start===null){start=ts;}
      var p=Math.min((ts-start)/ms,1);
      p=1-Math.pow(1-p,3);
      el.textContent=String(Math.round(target*p));
      if(p<1){requestAnimationFrame(tick);}
    }
    requestAnimationFrame(tick);
  }

  var verdicts=document.getElementById('verdicts');
  var votesCounted=false;
  function countVotes(){
    if(votesCounted||!verdicts){return;}
    votesCounted=true;
    Array.prototype.forEach.call(verdicts.querySelectorAll('.vote-row .n'),function(n){countUp(n,1100);});
  }
  function revealVerdicts(){
    if(verdicts&&!verdicts.classList.contains('revealed')){
      verdicts.classList.add('revealed');
      countVotes();
    }
  }
  var revealBtn=document.getElementById('revealBtn');
  if(revealBtn&&verdicts){revealBtn.addEventListener('click',function(){
    revealVerdicts();
    verdicts.scrollIntoView({behavior:'smooth'});
  });}
  if(verdicts){
    if('IntersectionObserver' in window){
      var io=new IntersectionObserver(function(entries){
        entries.forEach(function(en){
          if(en.isIntersecting){revealVerdicts();io.disconnect();}
        });
      },{threshold:0.25});
      io.observe(verdicts);
    }else{
      revealVerdicts();
    }
  }

  // 先備知識長條的數字
  var prior=document.querySelector('.prior');
  if(prior){
    if('IntersectionObserver' in window&&!reduceMotion){
      var pio=new IntersectionObserver(function(es){
        es.forEach(function(en){
          if(en.isIntersecting){
            Array.prototype.forEach.call(prior.querySelectorAll('.pk-row .n'),function(n){countUp(n,900);});
            pio.disconnect();
          }
        });
      },{threshold:0.3});
      pio.observe(prior);
    }
  }

  // 展示版片頭：hero 統計數字在標題顯影後滾動
  if(body.classList.contains('cinema')&&!reduceMotion){
    setTimeout(function(){
      Array.prototype.forEach.call(document.querySelectorAll('.hero .stat strong'),function(s){countUp(s,1200);});
    },3200);
  }

  // 墨色顯影（A-2）：標記元素、進入視窗時顯影，同區內錯落，只演一次
  var rvSel='.act-label,main h2,.lead,.notice,.event-head,.book-stage,.pause .q-small,.pause h2,.pause p,.reveal-btn,'
    +'.vote-card,.pair,.ft-card,.quote-card,.literacy-card,.media-card,.notebook,.mindmap-card,.ref-group,'
    +'.exit-list p,.exit-closer,.prior,.contrib,.checklist';
  var rvEls=Array.prototype.slice.call(document.querySelectorAll(rvSel));
  var rvCount={};
  rvEls.forEach(function(el){
    var sec=el.closest?el.closest('section'):null;
    var key=(sec&&sec.id)?sec.id:'x';
    var i=rvCount[key]=(rvCount[key]||0)+1;
    el.classList.add('rv');
    var step=(key==='exit')?400:120;
    el.style.transitionDelay=Math.min((i-1)*step,1600)+'ms';
  });
  if(reduceMotion||!('IntersectionObserver' in window)){
    rvEls.forEach(function(el){el.classList.add('on');});
  }else{
    var rvIO=new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(en.isIntersecting){en.target.classList.add('on');rvIO.unobserve(en.target);}
      });
    },{threshold:0.12,rootMargin:'0px 0px -8% 0px'});
    rvEls.forEach(function(el){rvIO.observe(el);});
  }

  // 四色閱讀進度線（D-3）
  var prog=document.getElementById('progressBar');
  if(prog){
    var ticking=false;
    function setProg(){
      var h=document.documentElement;
      var max=h.scrollHeight-window.innerHeight;
      var p=max>0?((h.scrollTop||body.scrollTop||0)/max):0;
      prog.style.width=(p*100)+'%';
      ticking=false;
    }
    window.addEventListener('scroll',function(){
      if(!ticking){ticking=true;requestAnimationFrame(setProg);}
    },{passive:true});
    setProg();
  }
})();
"""


def build_html(data: dict, cinema: bool = False) -> str:
    """cinema=True 產出展示版（含片頭墨色顯影、Ken Burns、晨霧）；False 為日常版（無開場動畫）。"""
    meta = data["meta"]
    body_class = "theme-dark weave-pattern cinema" if cinema else "theme-dark weave-pattern"
    nav = "".join(f'<a href="#{event["id"]}">{esc(event["name"])}</a>' for event in data["events"])
    mindmaps = "".join(render_mindmap(item) for item in data["mindmaps"])
    reference_sources = render_reference_sources(data["reference_sources"])
    flip_faces = build_flip_faces()
    flip_count = len(flip_faces)
    flip_json = json.dumps(flip_faces, ensure_ascii=False)
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
          <h3>{esc(event["name_dual"])}</h3>
          <p>{esc(event["place"])}</p>
          <div class="name-note">{esc(event["name_note"])}</div>
          <span class="decision-chip">命名方式：學生審查會 14:0 決議雙名並列</span>
          <div class="chips">{focus}</div>
        </div>
      </div>
      <p class="lead" style="margin-top:18px">{esc(event["brief"])}</p>
      <div class="media-grid">{media}</div>
    </div>
    <aside class="panel">
      {render_locator(event["id"])}
      <h4 style="margin-top:18px;padding-top:16px;border-top:1px solid var(--line-soft)">NotebookLM 輸出節錄</h4>
      <div class="notebook-list">{notebooks}</div>
      <p style="margin:10px 0 0;font-family:var(--font-sans);font-size:12px;color:var(--text-muted)">節錄中<mark class="stance">畫紅線</mark>的詞是日方／官方文獻用語，依學生審查決議照錄並標示，不作為本展立場。</p>
      {render_contributors(event["id"])}
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
<body class="{body_class}">
<div class="progress" id="progressBar"></div>
<div class="grain" aria-hidden="true"></div>
<button id="themeToggle" class="theme-toggle" type="button">☀ 切換淺色版</button>
<header class="hero">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="hero-mist" aria-hidden="true"></div>
  <div class="hero-veil" aria-hidden="true"></div>
  <div class="hero-inner">
    <div class="event-color-bar"><div class="seg-cepo"></div><div class="seg-dafen"></div><div class="seg-cikasuan"></div><div class="seg-truku"></div></div>
    <div class="eyebrow">花蓮高商 多元文化與文學・縱谷無言</div>
    <h1>{esc(meta["title"])}</h1>
    <div class="sub">「全班同學善用 AI、從無到有的深度展覽」</div>
    <p class="intro">這學期的「多元文化與文學」，全班從臺灣原住民十大歷史事件出發，深入花東縱谷的四個重大事件。學生用 NotebookLM 讀進政府出版的史料、向 AI 提問、生成自己的摘要、心智圖與簡報，再回頭審查 AI 寫出來的稿：看它哪裡站錯了位置、哪個詞帶著殖民者的立場、哪一句該改寫。從蒐集資料、AI 生成到逐句審查，這個展覽是全班從無到有做出來的。</p>
    <nav class="nav"><a href="#draft">第一幕・AI 初稿</a><a href="#verdicts">第二幕・審稿桌</a>{nav}<a href="#mindmaps">心智圖</a><a href="#fullthree">完整三句</a><a href="#laurels">學生的一句話</a><a href="#process">學習歷程</a><a href="#exit">出口牆</a><a href="#references">參考資料</a></nav>
    <div class="stats">
      <div class="stat"><strong>4</strong><span>大歷史事件</span></div>
      <div class="stat"><strong>14</strong><span>位學生審稿人</span></div>
      <div class="stat"><strong>{esc(meta["notebook_count"])}</strong><span>本 NotebookLM 筆記本</span></div>
      <div class="stat"><strong>{esc(meta["txt_count"])}</strong><span>份 AI 文字輸出</span></div>
      <div class="stat"><strong>{esc(meta["mindmap_count"])}</strong><span>張學生心智圖</span></div>
    </div>
  </div>
</header>
<main>
  <section id="draft">
    <div class="wrap">
      <div class="act-label">第一幕・原稿</div>
      <h2>一份有瑕疵的初稿</h2>
      <p class="lead">這本冊子是 AI 整理史料後寫出的初稿，每一頁都蓋著「未經審查」的浮水印。<b>畫紅線的詞，正是它說錯話的地方。</b>請先把它翻完，知道 AI 怎麼寫，才看得懂學生改掉了什麼。</p>
      <div class="book-stage">
        <div class="book"><div id="bookSheet" class="sheet">{flip_faces[0]}</div></div>
        <div class="book-controls">
          <button id="bookPrev" type="button">← 上一頁</button>
          <span id="bookHint">點頁面或按方向鍵翻頁（1 / {flip_count}）</span>
          <button id="bookNext" type="button">翻頁 →</button>
        </div>
      </div>
      <div class="notice" style="max-width:840px;margin:18px auto 0">本冊所有文句皆為 AI 生成、僅供學生審查教學使用，不得單獨引用為史實。「兇蕃」「歸順」「理蕃」等詞為日方／官方文獻用語，照錄時一律標示立場。</div>
    </div>
  </section>
  <section class="pause">
    <div class="wrap">
      <div class="q-small">翻完初稿，換你想一下</div>
      <h2>「兇蕃」這兩個字，你會怎麼處理？</h2>
      <p>照用？加註？改寫？還是整段撤下？14 位學生審稿人已經做了決定。</p>
      <button id="revealBtn" class="reveal-btn" type="button">看審稿人的決定</button>
    </div>
  </section>
  <section id="verdicts">
    <div class="wrap">
      <div class="act-label">第二幕・審稿桌</div>
      <h2>三項決議</h2>
      <p class="lead">開展前審查會（2026 年 6 月 11 日），14 位學生以 Google Form 表決。每一票都直接改變了這個展覽的長相。</p>
      <div class="vote-grid">{render_votes()}</div>
      <h2 style="margin-top:52px">紅筆對照：AI 原句 ✕ 學生修訂</h2>
      <p class="lead">出自學生的事件理解卡。左邊是被駁回的 AI 原句，右邊是學生的修訂與理由。</p>
      <div class="pairs">{render_pairs()}</div>
    </div>
  </section>
  <section id="halls-intro" style="padding:46px 0">
    <div class="wrap">
      <div class="act-label">第三幕・修訂後的展覽</div>
      <h2>四個事件展區</h2>
      <p class="lead">四個事件沿著花東縱谷由北而南：太魯閣口、七腳川（吉安）、大港口（豐濱海邊）、大分（卓溪深山）。每個展區右側附一張「本事件位置」小圖，告訴你它在縱谷的哪裡；想看可縮放的完整地圖，點圖下方連結即可。以下展區皆已依審查會決議修訂：事件標題雙名並列、殖民用語照錄必標示。</p>
    </div>
  </section>
  {''.join(events_html)}
  {general_html}
  <section id="mindmaps">
    <div class="wrap">
      <h2>學生心智圖</h2>
      <p class="lead">心智圖由學生以 NotebookLM 生成後上傳。原標示「審查中」的 10 張，已依「作者研究的事件」完成歸檔（卡片上有註記）；其餘 4 張為課堂先行確認。若瀏覽器阻擋嵌入預覽，可點「開啟原始 PNG」。</p>
      <div class="mindmap-grid">{mindmaps}</div>
    </div>
  </section>
  <section id="fullthree">
    <div class="wrap">
      <div class="act-label">完成全程的同學</div>
      <h2>完整三句：事實 → 差異 → 省思</h2>
      <p class="lead">這幾位同學走完了整條弧：先寫下查到的事實，再比對官方／AI 與族人記憶的<b>差異</b>，最後收束成自己的<b>省思</b>。三句並列，看得出他們不只是抄 AI，而是判斷過、改寫過。<b>點擊卡片，為這份完整作品頒發桂冠。</b></p>
      {render_full_three()}
    </div>
  </section>
  <section id="laurels">
    <div class="wrap">
      <div class="act-label">學生策展</div>
      <h2>學生的一句話</h2>
      <p class="lead">其餘同學雖未完成三句，仍留下一句最值得上牆的話。<b>點擊卡片頒發桂冠。</b>桂冠掛在學生自己的話上，由觀者親手頒出，不預先掛上。</p>
      {render_quote_wall()}
    </div>
  </section>
  <section id="process">
    <div class="wrap">
      <div class="two-col">
        <div>
          <h2>生成工具與學習歷程</h2>
          <p class="lead">學生用 NotebookLM 把權威史料 PDF 轉成摘要、心智圖、音訊與影片，再回到課堂完成三句寫作與審稿。下面這些話是學生自己寫的，他們很清楚 AI 的限制在哪裡。</p>
          {render_literacy()}
        </div>
        <div>
          <ul class="checklist">
            <li>選定事件，建立自己的研究問題。</li>
            <li>用 NotebookLM 摘要史料，保留人工判讀。</li>
            <li>審查 AI 輸出：歸類心智圖、辨認有立場的用詞。</li>
            <li>比較官方說法與族群記憶，寫出差異。</li>
            <li>把 AI 輸出改寫成自己的話，並補上來源。</li>
          </ul>
          {render_prior()}
        </div>
      </div>
    </div>
  </section>
  <section id="exit">
    <div class="wrap">
      <div class="act-label" style="justify-content:center">尾聲・出口牆</div>
      <h2>離場之前，他們想讓臺灣知道的事</h2>
      <p class="lead" style="margin:0 auto">問卷最後一題：「我認為臺灣的所有人民，應該要知道的事情是？」以下是 14 位審稿人的回答。</p>
      {render_exit_wall()}
    </div>
  </section>
  <section id="references">
    <div class="wrap">
      <h2>參考資料來源</h2>
      <p class="lead">本展史實數字與事件敘述一律以【政府出版品】為準（原住民族委員會「原住民族重大歷史事件系列叢書」、國家教育研究院補充教材）；其餘來源依層級標示。此為全站總參考資料，不對應單一學生作品。</p>
      <div class="refs">{reference_sources}</div>
    </div>
  </section>
</main>
<footer>花蓮高商「多元文化與文學」縱谷無言單元｜素材：NotebookLM 匯出、學生事件理解卡與開展前審查會問卷（2026-06-11）｜學生姓名一律屏蔽，以班級＋座號代號顯示｜頁面更新：{esc(meta["generated_at"])}</footer>
<script>window.FLIP_PAGES={flip_json};</script>
<script>{JS_CODE}</script>
</body>
</html>"""


def main() -> None:
    data = build_data()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(data, cinema=False), encoding="utf-8")
    OUTPUT_HTML_CINEMA.write_text(build_html(data, cinema=True), encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_HTML.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_HTML_CINEMA.relative_to(ROOT)}")
    print(f"copied media: {data['meta']['media_count']}")


if __name__ == "__main__":
    main()
