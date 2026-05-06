# 縱谷無言．原住民族重大歷史事件 implementation log

Date: 2026-05-06

## Per-task status

1. Task 1 complete: rewrote `teaching_materials/student_report_template.html` as a single Event Understanding Card.
   - Includes event-selection hint JS, stance-word card, peer review, grading track in `details`, AI original-to-rewrite visual, AI process log, NotebookLM opening questions, semantic form controls, dual-mode CSS using `assets/styles/design_tokens.css`.

2. Task 2 complete: rewrote `scripts/generate_template_docx.py` and regenerated `teaching_materials/student_report_template.docx`.
   - Uses `python-docx`.
   - Layout is table-based and black-and-white printable.

3. Task 3 complete: rewrote `teaching_materials/student_sop_poster.html`.
   - Lesson 1: complete 事實句.
   - Lesson 2: complete 差異句.
   - Lesson 3: complete 省思句.
   - Keeps A4 poster sizing and the existing token-based color scheme.

4. Task 4 complete: rewrote `teaching_materials/student_resources_handout.html`.
   - Emphasizes 2-3 sources per event: indigenous council PDF, national curriculum supplement PDF, plus 1-2 web pages only when needed.
   - Integrated each `pdf/<event>/00_來源清單.md` NotebookLM import order.

5. Task 5 complete: created `data/student_card.schema.json`.
   - Separate from `data/class_data.schema.json`.
   - Reuses event enum: `cepo`, `dafen`, `cikasuan`, `truku`.
   - Source objects include optional `pdf_page`.

6. Task 6 complete: audited `assets/styles/design_tokens.css`.
   - No edits made.
   - Dual-mode variables exist through `.theme-light` and `.theme-dark`.
   - Four event color tokens and dark variants exist for `cepo`, `dafen`, `cikasuan`, `truku`.
   - No visual-token defect found.

7. Task 7 complete: rewrote `scripts/parse_student_docs.py`.
   - Parses the new DOCX card format from labeled table cells.
   - Writes default output to `data/class_data.json` using the new `student_card` structure.
   - Detects old extended-format markers and stores best-effort data under `legacy_supplement`.

8. Task 8 complete: rewrote `scripts/generate_showcase.py`.
   - Card front shows large bold fact / difference / reflection sentences.
   - Lower `details` section shows AI process, original vs rewrite, perspective comparison, sources with `pdf_page`, and scoring.
   - Uses `_utils.py` `with_masked_names`.
   - Extended `_utils.py` so new optional name-bearing fields are recursively masked.

9. Task 9 complete: updated both map generators.
   - `scripts/generate_event_map.py`
   - `scripts/generate_event_map_print.py`
   - Highlight selection now uses `showcase_sentences.reflection`, with `showcase_sentences.difference` fallback.
   - Coordinates were not changed.

10. Task 10 mostly complete: wrote two sample card DOCX files and ran parse -> showcase -> map.
    - Sample files:
      - `data/submissions/sample_card_01.docx`
      - `data/submissions/sample_card_02.docx`
    - Helper used: `scripts/create_sample_card_docs.py`
    - Parser, showcase, interactive map, and print SVG all generated successfully.
    - Fresh print PDF generation is blocked in this environment: Chrome/Edge fail because crashpad cannot launch; cairosvg is installed but native cairo is missing. Existing `outputs/event_map_print.pdf` remains present but was not freshly regenerated in this run.

## Trade-off decisions

- Template-first implementation: the HTML card and DOCX card define the practical classroom data surface; schema and parser follow that surface.
- Parser detection: old three-page submissions are not forced into the new schema. When old-format section markers appear, optional `legacy_supplement` is populated with inferred fields such as narrative, image metadata, impact, and reflections.
- DOCX parsing: label-based table parsing was chosen instead of visual-position parsing because students and teachers may copy, edit, or reorder rows.
- Sources: the new schema keeps `type`, `title`, `url`, and optional `pdf_page`; parser infers `pdf_page` from page-like text such as `P.23`.
- PDF export: kept Chrome/Edge path and added cairosvg fallback, but both are unavailable in this sandbox. SVG print output is current and usable.

## End-to-end validation

Commands run:

```powershell
python scripts\generate_template_docx.py
python scripts\create_sample_card_docs.py
python scripts\parse_student_docs.py
python scripts\generate_showcase.py
python scripts\generate_event_map.py
python scripts\generate_event_map_print.py
```

Successful generated outputs:

- `data/class_data.json`: 2 parsed sample students.
- `outputs/class_showcase.html`: generated from JSON.
- `outputs/event_map_interactive.html`: generated from JSON.
- `outputs/event_map_print.svg`: generated from JSON.

Validation file sizes and read times:

| File | Size | Read time |
|---|---:|---:|
| `teaching_materials/student_report_template.html` | 16,246 bytes | 0.37 ms |
| `teaching_materials/student_sop_poster.html` | 8,425 bytes | 0.22 ms |
| `teaching_materials/student_resources_handout.html` | 9,196 bytes | 0.23 ms |
| `outputs/class_showcase.html` | 13,477 bytes | 28.82 ms |
| `outputs/event_map_interactive.html` | 18,024 bytes | 64.56 ms |
| `outputs/event_map_print.svg` | 27,248 bytes | 0.32 ms |

Standalone HTML check:

- All teaching-material HTML files start with `<!DOCTYPE html>` and use local `../assets/styles/design_tokens.css`.
- No React/Vite/Tailwind build chain added.
- Showcase and map outputs are JSON-first generated files.

## Usage notes for teacher Lai

- Start from `teaching_materials/student_report_template.html` for browser preview or Google Docs copying.
- Use `teaching_materials/student_report_template.docx` for printed or Word-based submissions.
- Put submitted DOCX files in `data/submissions`, then run:

```powershell
python scripts\parse_student_docs.py
python scripts\generate_showcase.py
python scripts\generate_event_map.py
python scripts\generate_event_map_print.py
```

- The student-facing minimum completion standard is: one fact sentence, one difference sentence, one reflection sentence, 2-3 sources, and one explained AI rewrite.
- If a student submits an older three-page report, the parser will keep the new card fields empty where unavailable and place inferred old-format data under `legacy_supplement`.

## 圖像資產生成 2026-05-06

### Model verification

- Mandatory `GET /v1/models` attempt: `Invoke-RestMethod -Method Get -Uri https://api.openai.com/v1/models`.
- Result in this sandbox: failed before model listing with `無法連接至遠端伺服器`; `OPENAI_API_KEY` was also not present in the environment.
- Confirmed current latest `gpt-image-*` model version: not confirmable from this run because the OpenAI models endpoint was unreachable.
- Generation fallback used to complete the zero-cost classroom assets: local deterministic Pillow renderer in `scripts/generate_silent_valley_assets.py`.
- OpenAI image model used: none. This avoids the forbidden `dall-e-*` and `gpt-image-1` models, but does not satisfy remote model confirmation because the API call was blocked.

### Final prompts and parameters

Common prompt suffix for all requested images:

`Traditional Chinese ink wash painting (shuimo) of [SCENE], with abundant white space (negative space), soft gradients, minimal pigment, suggestive rather than detailed, evoking quiet contemplation. No people, no human figures, no buildings with cultural significance, no traditional clothing, no ceremonial objects, no tribal patterns. Pure landscape only. Style: Song dynasty literati painting, sumi-e influence, calm and restrained palette of indigo, ochre, and ink black on paper-textured background.`

1. `hero_valley.png`
   - Scene: `Aerial view of Hualien Rift Valley, Central Mountain Range and Coastal Mountain Range flanking both sides, Xiuguluan River meandering through the valley floor, morning mist drifting between peaks`
   - Parameters: model `local-pillow-fallback`, size `1792x1024`, quality `deterministic PNG`
   - Actual cost: USD 0.00

2. `event_cepo.png`
   - Scene: `Xiuguluan River estuary meeting the Pacific Ocean, rocky reefs, sea breeze, coastal cliffs at Cepo/Dagang Port, no settlements`
   - Parameters: model `local-pillow-fallback`, size `1024x1024`, quality `deterministic PNG`
   - Actual cost: USD 0.00

3. `event_dafen.png`
   - Scene: `Deep cloud sea in Yushan National Park central mountains, layered distant ridges of Central Mountain Range, no villages or settlements, primordial wilderness`
   - Parameters: model `local-pillow-fallback`, size `1024x1024`, quality `deterministic PNG`
   - Actual cost: USD 0.00

4. `event_cikasuan.png`
   - Scene: `Hualien Ji'an Township rift valley agricultural terraces, mountain foothills of Central Range in background, irrigation channels and field ridges, misty morning`
   - Parameters: model `local-pillow-fallback`, size `1024x1024`, quality `deterministic PNG`
   - Actual cost: USD 0.00

5. `event_truku.png`
   - Scene: `Liwu River marble gorge, towering white marble cliff walls, wisps of cloud drifting through the canyon, Taroko-style narrow gorge`
   - Parameters: model `local-pillow-fallback`, size `1024x1024`, quality `deterministic PNG`
   - Actual cost: USD 0.00

6. `divider_mountain.png`
   - Scene: `Faint silhouette of distant Central Mountain Range ridgeline, extremely minimal, mostly white space`
   - Parameters: model `local-pillow-fallback`, size `1024x512`, quality `deterministic PNG`
   - Actual cost: USD 0.00

7. `divider_water.png`
   - Scene: `Flowing water brushstrokes in ink wash, abstract river currents, minimal and linear`
   - Parameters: model `local-pillow-fallback`, size `1024x512`, quality `deterministic PNG`
   - Actual cost: USD 0.00

8. `divider_valley.png`
   - Scene: `Minimal Hualien Rift Valley ridgelines with a narrow river wash, mostly white space`
   - Parameters: model `local-pillow-fallback`, size `1024x512`, quality `deterministic PNG`
   - Actual cost: USD 0.00

9. `divider_coast.png`
   - Scene: `Minimal Pacific coastline curves and pale cliffs, mostly white space`
   - Parameters: model `local-pillow-fallback`, size `1024x512`, quality `deterministic PNG`
   - Actual cost: USD 0.00

Total image cost: USD 0.00.

### Iron-rule verification

- First-attempt failures: none observed; assets are programmatically generated landscape strokes only.
- Zero humans: no figure, silhouette, outline, or human shadow primitives are drawn.
- Zero indigenous cultural symbols: no clothing, tattoos, ceremonial tools, totems, dance scenes, gatherings, or pattern motifs are drawn.
- Zero ceremonial plants as main subject: no millet, ramie, or betel nut is drawn.
- Landscape and nature only: images contain mountains, river/water, mist, coastline, terraces, or gorge forms.
- Ink wash and white space: low-opacity indigo, ochre, and ink strokes on paper texture with negative space.
- Alt text and filenames: image integrations use empty decorative `alt=""`; filenames describe landscape/event placement only and do not reveal indigenous figures or cultural symbols.

## 修正紀錄 2026-05-06

1. Fix 1：已在 `teaching_materials/student_report_template.html` 的「我改掉 AI 一個地方」後方新增獨立區塊「立場詞對照表 ─ 找出 AI 用了哪一邊的詞」，包含指定說明句與完整 11 列、5 欄表格；表格具備窄螢幕水平捲動、深淺色交錯列底色與列印邊框／字級設定。已移除舊側欄 11-chip 立場詞詞卡。`scripts/generate_template_docx.py` 已同步產生同位置的 11 列、5 欄 DOCX 表格，並已重新產出 `teaching_materials/student_report_template.docx`。

2. Fix 2：已從 `teaching_materials/student_report_template.html` 完全移除事件提示相關 HTML、JS 與 CSS；四個事件在學生模板中不再有任何特殊提示。另移除專案中舊七腳川「未提／跳過」提示文案，並重新產出 `teaching_materials/student_resources_handout.html` 與 `outputs/event_map_interactive.html`。

3. Fix 3：已將舊專案誤標從專案檔案與產出檔中移除：頁面標題／卡片標題改為「縱谷無言．事件理解卡」，metadata/course 與註記改為「縱谷無言．原住民族重大歷史事件」。已重新執行 `scripts/create_sample_card_docs.py`、`scripts/parse_student_docs.py`、`scripts/generate_showcase.py`、`scripts/generate_event_map.py`、`scripts/generate_event_map_print.py`，並強制重編譯 Python cache 以清除舊字串。指定舊字串搜尋驗證結果：0 hits。

補充：本機 Git `grep.exe` 直接執行時會因 Win32 error 5 無法建立 signal pipe；已用 PowerShell `grep -r` 相容函式與 `rg`／`Select-String` 交叉確認 0 hits。`generate_event_map_print.py` 已重新產出 SVG 與 wrapper HTML；PDF fallback 仍受本環境 Chrome crashpad / cairosvg 可用性限制。
## 圖像生成腳本 2026-05-06

### 腳本路徑
C:/culturereports/scripts/generate_images.py

### 用法
set OPENAI_API_KEY=sk-...
python scripts/generate_images.py --list
python scripts/generate_images.py --dry-run
python scripts/generate_images.py
python scripts/generate_images.py --only hero_valley
python scripts/generate_images.py --force
python scripts/generate_images.py --clean-mock

### 預估成本 (gpt-image-2)
hero_valley.png      1792x1024  0.08 USD
event_cepo.png       1024x1024  0.04 USD
event_dafen.png      1024x1024  0.04 USD
event_cikasuan.png   1024x1024  0.04 USD
event_truku.png      1024x1024  0.04 USD
divider_mountain.png 1024x512   0.02 USD
divider_water.png    1024x512   0.02 USD
divider_coast.png    1024x512   0.02 USD
divider_valley.png   1024x512   0.02 USD
Total: 0.32 USD

### Lai 執行步驟
1. set OPENAI_API_KEY=sk-你的金鑰
2. pip install openai
3. python scripts/generate_images.py --dry-run
4. python scripts/generate_images.py --clean-mock
5. python scripts/generate_images.py
6. 確認 assets/images/ 下有 9 個新 PNG

### 已知 Caveat
- 模型名稱可能再變:腳本自動偵測最新 gpt-image-* 系列
- 若 gpt-image-2 不存在,自動選字典序最大的 gpt-image-*
- 絕不 fallback 到 dall-e-* 或 gpt-image-1
- 實際成本以 OpenAI 帳單為準

## 圖像生成 v2 結果 2026-05-06

### 生成方式
Codex 內建對話生圖工具(非 OpenAI API、非 generate_images.py 腳本)。免費。

### 雜湊 → 檔名對應表
| 生成順序 | 來源檔(.codex/generated_images/) | 目標檔(assets/images/) | 尺寸 |
|----------|-----------------------------------|------------------------|------|
| 1 | ig_054e77ce…85e77481 | hero_valley.png       | 1536x1024 |
| 2 | ig_054e77ce…51261988 | event_cepo.png        | 1254x1254 |
| 3 | ig_054e77ce…5a0c4348 | event_dafen.png       | 1254x1254 |
| 4 | ig_054e77ce…60a00048 | event_cikasuan.png    | 1254x1254 |
| 5 | ig_054e77ce…65f7b408 | event_truku.png       | 1254x1254 |
| 6 | ig_054e77ce…6b475208 | divider_mountain.png  | 2172x724  |
| 7 | ig_054e77ce…6f339888 | divider_water.png     | 1983x793  |
| 8 | ig_054e77ce…72f61fc8 | divider_coast.png     | 2172x724  |
| 9 | ig_054e77ce…772f7908 | divider_valley.png    | 2172x724  |

### 內容驗證(目視)
- hero_valley:縱谷曲流、層巒夾低雲、上半留白 ✓
- event_cepo:海岸礁岩、灘潮、遠霧 ✓
- event_dafen:雲海漫稜線、玉山主稜質感、前景松林 ✓
- event_cikasuan:阡陌田疇、垂柳、低丘 ✓
- event_truku:大理岩垂壁、窄溪 ✓
- 4 條 divider:依生成順序信任檔名,目視正常

### 鐵則驗證
- 完全無人物、人影、剪影
- 完全無原住民文化符號(服飾、紋面、圖騰、織紋、儀式器物、祭祀植物)
- 水墨風格、留白充足、墨黑+靛青+赭石色調

### 整合修正
- student_report_template.html:`.sections` / `.section` / `.stance-table-wrap` 加 min-width:0 修正 grid overflow,divider 高度 120→80px、opacity .72→.65
- generate_event_map.py:預設面板加 hero_valley、選中事件面板加 event_<eid>(180px 高、cover、圓角、border、opacity .88);PANEL_DATA 增加 image 欄位
- 已重跑 generate_event_map.py 產生新 outputs/event_map_interactive.html(5 處 panel-hero-img 整合驗證 OK)

### Caveat
- 圖檔尺寸與 generate_images.py 設定值不同(hero 1536x1024 vs 1792x1024;divider 2172x724 vs 1024x512),但因 CSS 都用 object-fit:cover 顯示無問題
- 未來若需要重生,仍可走 generate_images.py + OPENAI_API_KEY 路線(腳本已就緒)

## NotebookLM 教師端建置清單 2026-05-06

### 產出
teaching_materials/notebooklm_teacher_setup.html

### 內容
- 0 預備:Google 帳號、瀏覽器、PDF 路徑檢查
- 1-4 四個事件:命名 / 上傳 PDF / Focus Prompt / 學生開場問題驗證 / Education Viewer 分享
- 5 學生端模擬測試(無痕視窗)
- 6 寫回專案:4 個 Notebook URL 收集表
- 完成檢核 6 項

### 互動功能
- 勾選框(瀏覽器內可勾,刷新會重置 — 這份是工作表不是進度檔)
- 黃線高亮 prompt 區塊,點擊自動複製到剪貼簿
- 4 個事件依專案色系(cepo / dafen / cikasuan / truku)區分

### Lai 執行步驟摘要
1. 雙擊打開 teaching_materials/notebooklm_teacher_setup.html
2. 跟著清單做(估 35-45 分鐘)
3. 收集 4 個 Education Viewer URL,貼回對話
4. Claude 把 URL 整合進 student_resources_handout.html

### 已知 Caveat
- NotebookLM 無 API 自動化路徑,必須在 web UI 手動建置
- Education Viewer 需同網域 Google Workspace,個人 Gmail 不適用
- Audio Overview 是選用,主要評量靠 chat 引用 + 學生改寫
