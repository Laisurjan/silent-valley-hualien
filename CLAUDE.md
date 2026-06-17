# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這個 repo 是什麼

花蓮高商二年級「多元文化與文學」原住民族單元（縱谷無言）的教學設計與配套產出。使用者是授課教師（Lai 老師），所有溝通與產出文字一律使用**繁體中文（台灣）**。主題是花東縱谷四個原住民族重大歷史事件，學生用 NotebookLM 輔助史料閱讀。成果（展覽網頁、事件地圖、教學遊戲）用於原住民族課程計畫的**委員觀課展示**——產出品質直接面對外部審查。

完整專案規格在 `PROJECT_BRIEF.md`（設計決策已寫死，疑問先問老師，不要自行決定）；課程脈絡見 `README.md` 與 `低動機跑班版課程調整建議.txt`。

## 常用指令

沒有 build 系統、沒有測試框架、沒有套件管理檔。Python 3.13，直接執行產生器：

```bash
python scripts/generate_0604_exhibit.py    # 觀課展覽頁，一次產兩版：
#   outputs/ai_history_learning_exhibit.html         瀏覽版（無開場動畫）
#   outputs/ai_history_learning_exhibit_cinema.html  展示版（片頭墨色顯影＋Ken Burns，錄影用）
#   + data/0604_exhibit_data.json
python scripts/generate_lesson_pptx.py     # 三週教學 PPT → teaching_materials/
python scripts/generate_event_map.py       # 互動事件地圖（Leaflet）→ outputs/event_map_interactive.html
python scripts/generate_event_map_print.py # 列印版地圖 PDF
python scripts/generate_template_docx.py   # 學習單 docx
python scripts/parse_student_docs.py       # 收回的學生 docx → class_data.json
# generate_showcase.py 仍在，但班級成果頁（class_showcase.html）已自公開站下架，不再產出公開頁
```

**部署＝push 到 `main`**：GitHub Pages 由 repo 根目錄提供服務、首頁就是 `README.md`（站台 github.com/Laisurjan/silent-valley-hualien）。改完產生器→重跑→推 main 即上線（Pages 有快取，約一兩分鐘）。

**改動後一律本機驗證**（無測試框架，靠這幾個檢查）：
- HTML 內嵌 JS 用 `node --check`（環境有 node；展覽頁有兩段 inline script，都要過）。
- **個資檢查**：grep 產出 HTML 確認沒有任何學生完整姓名外洩（公開頁只能出現班級＋座號＋姓O名代號）。
- `outputs/governor_game.html` 改動後建議用 DOM stub 模擬器跑自動對局（本 repo 曾以 2000 局隨機 bot 測平衡：抽出 `<script>`、stub document/window、覆寫 `flyNext=()=>nextTurn()` 後自動 `resolve()`）。

## 架構

**核心模式：產生器 → 產出。絕對不要直接改產出檔**（會被重跑覆蓋）；要改內容就改 `scripts/generate_*.py` 再重跑。唯一例外：`outputs/governor_game.html`（教學遊戲「總督的算盤」）是手寫單檔，沒有產生器——牌庫資料在檔內 `DECK` 區塊，文本初稿與史實查核在根目錄 `總督的算盤_遊戲文本初稿.md`。

資料流：

```
學生 Google Docs ──parse_student_docs.py──▶ data/class_data.json ──▶ generate_event_map.py（地圖）
NotebookLM 匯出（C:\Users\godof\Downloads\0604\…，外部目錄）──▶ generate_0604_exhibit.py ──▶ outputs/ + data/0604_exhibit_data.json
```

- **展覽頁的學生內容不是來自 class_data.json，而是以「屏蔽後的常數」直接寫死在 `generate_0604_exhibit.py` 裡**（`REVIEW_VOTES` 表決、`REWRITE_PAIRS` 紅筆對照、`THREE_SENTENCE_STUDENTS` 完整三句、`LAUREL_QUOTES` 佳句、`AI_LITERACY_QUOTES`、`EXIT_WALL`、`STUDENT_OUTPUTS`、`MINDMAP_MANIFEST`）。要改學生句子／歸屬就改這些常數。引文出自學生事件理解卡與審查會問卷，輕修錯字不改原意。
- 展覽頁是**三幕敘事**：第一幕 AI 初稿翻頁書（整本只用一張紙 `#bookSheet`，翻到側面時 JS 換頁，避免多層 3D 穿透）→ 第二幕審稿桌（表決＋紅筆對照）→ 第三幕修訂後展區。`build_html(data, cinema=bool)` 用同一份資料產瀏覽版與展示版。
- 事件展區每區嵌一張「本事件位置」locator：用 `data/geo/hualien_outline.json` 縣界輪廓畫的**內嵌 SVG**（非 iframe，避免巢狀捲軸），當前事件亮起。完整互動地圖另開分頁。
- `generate_event_map.py` 的互動地圖已**純化為地理導覽**：移除學生句與人數，只留事件位置與短語（曾因嵌入測試學生句而下架重做）。
- `generate_0604_exhibit.py` 的 NotebookLM 部分依賴外部 Downloads 目錄；影音有「來源消失時沿用 outputs/media 既有複本」的 fallback。筆記本歸屬事件用 `FOLDER_EVENT_OVERRIDES`（資料夾編號→事件）明確指定，**不要**退回關鍵字猜測（"Amis" 這種泛用詞曾造成七腳川筆記本被誤歸大港口）。
- 四事件固定 id：`cepo`（大港口 1877）、`truku`（太魯閣 1896-1914）、`dafen`（大分 1914-1933）、`cikasuan`（七腳川 1908）。展覽頁標題依審查會 14:0 決議採雙名並列（如「大港口事件／O lalood i Cepo'」）。四色事件配色與深淺雙模式的權威定義在 `assets/styles/design_tokens.css`；視覺樣板以根目錄 `style_dark.html`（網頁用）、`style_light.html`（出版用）為準，文字描述與樣板衝突時以樣板 HTML 為準。
- `scripts/_utils.py` 的 `mask_name()` / `with_masked_names()`：地圖／成果頁這類「吃 class_data.json」的產生器靠它屏蔽姓名（王小明→王O明）；展覽頁因資料是寫死常數，直接以班級＋座號＋姓O名代號手動屏蔽。

## 不可違反的限制

1. **所有 HTML 單檔可直接開啟**：不新增 build 流程、不引外部 CDN／字型（教室可能斷網）。
2. **學生工具只有 Google 文件 + NotebookLM**，不再增加。
3. **個資**：`data/submissions/`、真實班級資料不入 repo；公開頁面學生姓名屏蔽或用班級＋座號代號。
4. **著作權**：第三方 PDF（原民會叢書、國教院教材）不入 repo（`pdf/` 只有 README）。MIT License 不含這些 PDF 與 AI 生成圖。
5. **文化倫理**（觀課委員是原住民族計畫委員，這些是紅線）：
   - 不放族群儀式／人物像，配圖用水墨地景（`assets/images/`）。
   - AI 生成文字一律標示，不得呈現為史實；「蕃」「歸順」「理蕃」等殖民用語照錄時須註明為日方視角。
   - 不替族人杜撰台詞——族人聲音只用有出處的真實引文（遊戲中族人「零直接引語」是刻意設計，不是缺漏）。
   - 史實數字優先採政府出版品（原民會叢書、國史館臺灣文獻館等）；查不到就用概數，不要編。

## 目前進行中的脈絡（2026-06）

- 「開展前審查會」（2026-06-11，14 位學生）**已完成並回灌**展覽頁：表決結果、紅筆對照、完整三句、佳句、心智圖歸屬都已是上線內容。心智圖原「審查中」標籤已移除，10 張改依「作者研究的事件」歸檔。
- 成果展現以**錄影**送審（委員不到場）：展示版 `_cinema.html` 有片頭動畫，錄影分鏡在 `teaching_materials/觀課影片分鏡腳本.md`。
- 含學生個資的素材（問卷 zip、原始作業）只放 `data/submissions/`（gitignored）；展覽頁所有學生內容皆已屏蔽。
- `teaching_materials/審查會表單題目清單.md`（gitignored，含 Drive 連結）為審查會題目；`0604_成果網頁兩週工作清單.md` 是工作總表；`IMPLEMENTATION_LOG.md` 記錄開發歷程。
