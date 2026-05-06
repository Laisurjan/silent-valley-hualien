# 給 Claude Code 的開場 Prompt

> 這份檔案是設計給你（Lai 老師）在 Claude Code 開新專案時，
> 第一輪對話直接複製貼上用的。完整版專案規格請見 PROJECT_BRIEF.md。

---

## 第一輪對話：開場 Prompt（直接複製貼上）

```
你好。我是花蓮高商國文科的 Lai 老師。

我有一個三節課的教學專案要請你幫忙，這個專案是花蓮高商二年級
彈性課程「多元文化與文學」的原住民族單元成果作業，最終會作為
原住民族校定課程計畫的觀課成果展示。

我已經把完整的專案規格寫在 PROJECT_BRIEF.md 中。請你：

1. 完整閱讀 PROJECT_BRIEF.md（從 Part 1 讀到附錄）
2. 讀完後，先告訴我你的理解：
   - 這個專案的目的是什麼？
   - 學生情境是什麼？
   - 設計原則有哪些？
   - 預計產出哪些檔案？
3. 如果有任何不清楚的地方，先問我，不要自己決定
4. 確認理解後，請按照 Part 6.1 的開發順序，
   先做「第一輪：教學端」的三個檔案：
   - student_report_template.html
   - student_sop_poster.html
   - student_resources_handout.html
   
   每完成一個就停下來給我確認，不要一次做三個。

重要：
- 視覺風格嚴格遵守 Part 5.1（誠品提案風 + 教育現場感）
- 配色與字型不可自行修改
- 所有 HTML 應為單檔可開、不需要 build
- 內容資料應與排版分離（用 JSON 結構）
- 你的核心價值是「正確度與一致性」，不是「驚喜」

請先確認你已讀完 PROJECT_BRIEF.md，並回覆你的理解。
```

---

## 後續對話：每完成一輪後的引導語

### 第一輪完成後

```
這三個教學端檔案我都看過了，[列出修改意見或確認 OK]。

現在請進入第二輪：成果彙整工具。請產出：
- parse_student_docs.py
- class_data.json（含 schema）

注意：
- parse_student_docs.py 需要能從 .docx 檔案中抓出
  PROJECT_BRIEF.md Part 2 定義的所有欄位
- 如果無法抓取某欄位（學生沒填），標記為 null 而不是空字串
- JSON schema 要能驗證資料完整性
- 提供至少一份「假學生資料」的 JSON 範例，用來測試後續網頁
```

### 第二輪完成後

```
解析腳本與 JSON 結構我確認過了，[列出修改意見或確認 OK]。

現在請進入第三輪：最終成果展示。請按順序產出：
1. class_showcase.html（班級成果網頁）
2. event_map_interactive.html（互動地圖）
3. event_map_print.svg + event_map_print.pdf（印刷地圖）

請用第二輪的假學生資料先做出可運作版本，
讓我可以看到實際成品再決定要不要調整。
```

---

## 修改時的對話範例

### 範例 A：要修改某個欄位

```
學生報告第三頁的「個人省思」第三題不好回答，
請把「以後我搭火車經過花蓮這個地方時，我會想起＿＿」
改成「我會想跟同學分享這個事件，是因為＿＿」。

需要同步更新：
1. student_report_template.html（學生模板）
2. parse_student_docs.py（解析腳本）
3. class_data.schema.json（資料定義）
4. PROJECT_BRIEF.md Part 2.4（規格文件）
```

### 範例 B：學生作品要彙整時

```
我把全班學生的 Google 文件下載成 docx 了，
放在 data/student_docs/ 資料夾。

請：
1. 執行 parse_student_docs.py 解析所有檔案
2. 把結果寫入 class_data.json
3. 重新生成 class_showcase.html
4. 列出哪些學生有欄位沒填完整（缺漏報告）
```

### 範例 C：要新增一個事件

```
我發現我們漏了一個重要事件「加禮宛事件（1878）」。
撒奇萊雅族的達固湖灣戰役，地點在花蓮市奇萊平原。

請：
1. 在 PROJECT_BRIEF.md 的 Part 4 增加 4.5 節
   （資料來源請你先用 web 搜尋，給我建議清單）
2. 更新 class_data.json schema 為五個事件
3. 更新 class_showcase.html 與 event_map_interactive.html
   讓它們能呈現五個事件

注意：浦忠成文章第五段「奇萊平原上⋯⋯火攻撒奇萊雅部落」
就是這個事件，所以與大港口、大分一樣是文章直接提到的。
```

---

## 緊急情況：Claude Code 偏離規格時

如果 Claude Code 自行發揮、產生不符合規格的東西，可以這樣說：

```
停。你產出的[檔案名]違反了 PROJECT_BRIEF.md 中的規格：
- [列出違反哪一條]

請：
1. 重新閱讀 Part [編號]
2. 解釋你為什麼違反了規格
3. 重新產出符合規格的版本

如果你認為規格本身有問題，請告訴我為什麼，
我會考慮修改規格而不是讓你自己發揮。
```

---

## 觀課前最後檢查清單

觀課前一週，可以這樣對 Claude Code 說：

```
觀課日期是 [日期]，請依照 PROJECT_BRIEF.md Part 7 的
驗收清單，逐項檢查所有產出：

1. 列出每個檔案的狀態（完成 / 有問題 / 缺失）
2. 模擬觀課情境：
   - 投影 class_showcase.html，會看到什麼？
   - 用平板開 event_map_interactive.html，會看到什麼？
   - 印出 event_map_print.pdf 貼牆，會看到什麼？
3. 列出我觀課當天可能會被問到的問題，
   以及對應的回答策略。
```
