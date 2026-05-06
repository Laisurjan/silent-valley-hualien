# 縱谷無言

花蓮高商「多元文化與文學」第三學期單元教學設計與配套產出。

主題：花東縱谷四個原住民族重大歷史事件（大港口 / 大分 / 七腳川 / 太魯閣），用 NotebookLM 與三句寫作（事實句 / 差異句 / 省思句），帶低動機學生在三節課內走完「認識 → 對照 → 省思」的弧。

> 「下次經過靜浦、富源、吉安、太魯閣口 — 你不會再什麼都看不到。」

## 為什麼這個 repo 存在

不是給學生用的成品 — 學生用 NotebookLM 與紙本／HTML 學習單即可。

這個 repo 是**給其他想做類似教學設計的老師參考**：
- 跑班、低動機、混合年級的教室，怎麼用 NotebookLM 不變成「學生抄整段答案」
- 三週漏斗設計（事實 → 差異 → 省思）的 slide 與評量設計
- 自動生成 PowerPoint、互動地圖、班級成果頁的 Python 工具

## 結構

```
.
├── COURSE_PROPOSAL.md          # 課程提案（給校方用）
├── PROJECT_BRIEF.md            # 教學設計詳細說明
├── IMPLEMENTATION_LOG.md       # 開發過程紀錄
├── 低動機跑班版課程調整建議.txt   # 班型實作筆記
│
├── scripts/                    # 自動化工具（Python）
│   ├── generate_lesson_pptx.py     # 三週 PPT 產生器（含講師備忘）
│   ├── generate_event_map.py       # 互動事件地圖（Leaflet）
│   ├── generate_event_map_print.py # 列印版事件地圖（PDF）
│   ├── generate_resources_handout.py # 學生資源頁
│   ├── generate_showcase.py        # 班級成果頁
│   ├── generate_template_docx.py   # 學習單 docx 模板
│   ├── parse_student_docs.py       # 收回 docx → JSON
│   └── ...
│
├── teaching_materials/         # 給老師 / 學生的成品
│   ├── lesson_week1.pptx ~ week3.pptx
│   ├── student_report_template.html  # 學習單 HTML 版
│   ├── student_report_template.docx  # 學習單 docx 版
│   ├── student_resources_handout.html
│   ├── student_sop_poster.html
│   └── notebooklm_teacher_setup.html # NotebookLM 教師端建置清單
│
├── outputs/                    # 產出（地圖 HTML / PDF、班級成果頁）
│   ├── event_map_interactive.html
│   ├── event_map_print.pdf
│   └── class_showcase.html
│
├── assets/                     # 圖片與樣式
│   ├── images/                 # AI 生成的水墨風配圖
│   └── styles/
│
└── data/                       # 資料 schema 與班級資料
    ├── *.schema.json
    ├── geo/                    # 事件地理座標
    └── images/                 # 地圖底圖等
```

## 不在 repo 內的東西（為什麼）

| 不在這 | 為什麼 | 怎麼取得 |
|---|---|---|
| `pdf/`（原民會叢書、國教院補充教材） | 第三方著作權，不應公開散布 | 老師自行向原機關取得，並上傳至自己的 NotebookLM |
| `data/submissions/`（學生作品） | 個資（PII） | 課堂收回後本機保存，不公開 |
| `data/class_data.json`（班級資料） | 個資 | 同上 |

## 使用方法

### 1. 設定 NotebookLM（教師端）

打開 `teaching_materials/notebooklm_teacher_setup.html`，按清單做：
1. 為四個事件各建一本 Notebook
2. 每本上傳該事件的兩本權威資料 PDF（原民會叢書 + 國教院補充教材）
3. 取得 Education Viewer 分享連結
4. 把連結貼到 `student_resources_handout.html` 對應位置

### 2. 產生教材

```bash
# 三週 PPT
python scripts/generate_lesson_pptx.py

# 互動地圖（HTML）+ 列印版（PDF）
python scripts/generate_event_map.py
python scripts/generate_event_map_print.py

# 學生資源頁
python scripts/generate_resources_handout.py

# 學習單 docx 模板
python scripts/generate_template_docx.py
```

### 3. 上課

- 第一節（探路）：認識四事件、學 NotebookLM、寫一句「事實／印象句」
- 第二節（對照）：學立場詞、找官方／族人說法差異、寫「差異句」
- 第三節（省思）：四個地景對應四個事件、同儕互評、寫「省思句」、上傳成果

### 4. 收回作品 → 班級成果頁

```bash
# 把學生 docx 解析成 JSON
python scripts/parse_student_docs.py

# 產出班級成果頁與更新事件地圖 panel
python scripts/generate_showcase.py
python scripts/generate_event_map.py
```

## 設計原則

- **跑班、低動機**：第一週門檻刻意低，先有印象再深化
- **NotebookLM 而非 ChatGPT**：可引用、有頁碼、不會亂講
- **viewer 權限**：學生弄不壞，老師不必盯
- **三句一弧**：事實 → 差異 → 省思，每週只多寫一句
- **不放族群儀式 / 人物像**：圖像用水墨地景代替，避免文化挪用
- **公開地圖、班級成果頁**：學生句子會被同學看到，學生就會認真寫

## 授權

教學設計、Python 程式、HTML 模板：MIT License（隨意使用、改、教）。

不含第三方 PDF（請自行向原機關取得）；不含 AI 生成圖片（assets/images 內為作者使用 OpenAI 圖像 API 生成，水墨風為作者選擇，可按相同比例自行重生）。
