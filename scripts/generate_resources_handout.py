"""
產出 student_resources_handout.html
四個事件 = 四個 NotebookLM 筆記本，學生在電腦教室用瀏覽器點連結。
紙本只用來：(1) 知道筆記本網址 (2) 看內含哪些資料 (3) 勾選自己讀過的。
"""

# ============================================================
# 資源資料（依 PROJECT_BRIEF Part 4 的清單）
# ============================================================

EVENTS = [
    {
        'id': 'cepo',
        'name': '大港口事件',
        'year': '1877',
        'eng_name': "Cepo' 戰役",
        'ethnic': '阿美族（秀姑巒阿美）',
        'location': '花蓮縣豐濱鄉靜浦村',
        'color': '#C73E3A',
        'notebook_placeholder': '[NOTEBOOK_URL_CEPO]',
        'core': [
            {
                'title': '原民會叢書｜《大港口事件》',
                'url': 'https://www.cip.gov.tw/zh-tw/news/data-list/217054CAE51A3B1A/C89C009B11A070ECB6FF809CEAFB8CC6-info.html',
                'tag': '原民會官方',
                'why': '政府官方出版品，學術可信度高。',
            },
            {
                'title': '原住民族文獻期刊｜阿美族二個歷史事件',
                'url': 'https://ihc.cip.gov.tw/EJournal/EJournalCat/248',
                'tag': '學術期刊',
                'why': '免費、無需登入。',
            },
        ],
        'extra': [
            {
                'title': '維基百科｜大港口事件',
                'url': 'https://zh.wikipedia.org/zh-tw/%E5%A4%A7%E6%B8%AF%E5%8F%A3%E4%BA%8B%E4%BB%B6',
                'tag': '基本架構',
                'why': '提醒學生需與其他來源對照。',
            },
            {
                'title': '公視新聞｜140年前大港口事件',
                'url': 'https://news.pts.org.tw/article/379958',
                'tag': '媒體報導',
                'why': '媒體報導 + 部落觀點，含影像。',
            },
            {
                'title': '聯合新聞網｜2022 正名 Cepo\' 戰役',
                'url': 'https://udn.com/news/story/7328/6569106',
                'tag': '當代記憶',
                'why': '2022 年正名為 Cepo\' 戰役的當代記憶。',
            },
            {
                'title': '臺灣原住民族事典｜大港口事件',
                'url': 'https://aborgpedia.alcd.center/detail?id=10099',
                'tag': '學術整理',
                'why': '含部落遷徙地圖。',
            },
            {
                'title': '《zalan 見識南島》｜蔡中涵口述',
                'url': 'https://www.youtube.com/watch?v=KtVxkMubyaQ',
                'tag': '影片資源',
                'why': '蔡中涵阿美族學者口述，含族語講述。',
            },
            {
                'title': '國家文化記憶庫｜靜浦考古遺址',
                'url': 'https://tcmb.culture.tw/zh-tw/detail?indexCode=Culture_Place&id=587792',
                'tag': '考古證據',
                'why': '屠殺現場的考古證據與圖像。',
            },
        ],
        'level_hints': [
            ('程度較弱', '核心 1 + 補充 1 + 補充 2'),
            ('程度中等', '核心 1 + 補充 3 + 補充 5'),
            ('程度較強', '核心 2 + 補充 4 + 補充 6'),
        ],
    },
    {
        'id': 'dafen',
        'name': '大分事件',
        'year': '1915',
        'eng_name': '布農抗日',
        'ethnic': '布農族',
        'location': '花蓮縣卓溪鄉（玉山國家公園境內）',
        'color': '#2C4A6E',
        'notebook_placeholder': '[NOTEBOOK_URL_DAFEN]',
        'core': [
            {
                'title': '原民會叢書｜《大分事件》',
                'url': 'https://www.cip.gov.tw/zh-tw/news/data-list/217054CAE51A3B1A/C89C009B11A070ECB6FF809CEAFB8CC6-info.html',
                'tag': '原民會官方',
                'why': '海樹兒・犮剌拉菲撰寫。',
            },
            {
                'title': '原文期刊｜拉荷．阿雷大分抗日',
                'url': 'https://toaj.stpi.niar.org.tw/index/journal/volume/article/4b1141f98a026e78018a074797a40171',
                'tag': '學術期刊',
                'why': '免費全文 PDF，無需登入。',
            },
        ],
        'extra': [
            {
                'title': '維基百科｜大分事件',
                'url': 'https://zh.wikipedia.org/zh-tw/%E5%A4%A7%E5%88%86%E4%BA%8B%E4%BB%B6',
                'tag': '基本架構',
                'why': '快速掌握事件。',
            },
            {
                'title': '維基百科｜拉荷．阿雷',
                'url': 'https://zh.wikipedia.org/zh-tw/%E6%8B%89%E8%8D%B7%C2%B7%E9%98%BF%E9%9B%B7',
                'tag': '人物傳記',
                'why': '主要領導者生平。',
            },
            {
                'title': '關鍵評論網｜布農抗日 18 年',
                'url': 'https://www.thenewslens.com/article/15141',
                'tag': '深度報導',
                'why': '完整易讀的事件全貌。',
            },
            {
                'title': '國家文化記憶庫｜布農族抗日大分事件',
                'url': 'https://tcmb.culture.tw/zh-tw/detail?indexCode=Culture_Place&id=599493',
                'tag': '官方記憶庫',
                'why': '含照片與檔案。',
            },
            {
                'title': '原住民族文獻｜布農抗日英雄 Dahu-ali',
                'url': 'https://ihc.cip.gov.tw/EJournal/EJournalCat/155',
                'tag': '學術整理',
                'why': '300 游擊隊 18 年抗戰。',
            },
            {
                'title': '原視新聞｜大分事件後裔訪談',
                'url': 'https://www.youtube.com/watch?v=9wPZBl0c4HQ',
                'tag': '影片資源',
                'why': '100 週年後裔訪談影像。',
            },
        ],
        'level_hints': [
            ('程度較弱', '核心 1 + 補充 3 + 補充 6'),
            ('程度中等', '核心 1 + 補充 1 + 補充 4'),
            ('程度較強', '核心 2 + 補充 5'),
        ],
    },
    {
        'id': 'cikasuan',
        'name': '七腳川事件',
        'year': '1908',
        'eng_name': 'Cikasuan',
        'ethnic': '阿美族（南勢阿美）',
        'location': '花蓮縣吉安鄉',
        'color': '#D9A441',
        'notebook_placeholder': '[NOTEBOOK_URL_CIKASUAN]',
        'core': [
            {
                'title': '原民會叢書｜《七腳川事件》',
                'url': 'https://www.cip.gov.tw/zh-tw/news/data-list/217054CAE51A3B1A/C89C009B11A070ECB6FF809CEAFB8CC6-info.html',
                'tag': '原民會官方',
                'why': '林素珍撰寫。',
            },
            {
                'title': '原民會補充教材 PDF',
                'url': 'https://stv.naer.edu.tw/data/supplementary/原住民族重大歷史事件補充教材-七腳川事件.pdf',
                'tag': '官方教材',
                'why': '含地圖、照片。',
            },
            {
                'title': '華藝免費摘要｜Cikasuan 歷史意識',
                'url': 'https://www.airitilibrary.com/Publication/alDetailedMesh?docid=a0000575-200712-201005170074-201005170074-115-140',
                'tag': '學術論文',
                'why': '林素珍、陳耀芳合著。',
            },
        ],
        'extra': [
            {
                'title': '維基百科｜七腳川事件',
                'url': 'https://zh.wikipedia.org/zh-tw/%E4%B8%83%E8%85%B3%E5%B7%9D%E4%BA%8B%E4%BB%B6',
                'tag': '基本架構',
                'why': '快速掌握事件。',
            },
            {
                'title': '吉安鄉公所｜七腳川紀念碑',
                'url': 'https://www.ji-an.gov.tw/ame/data/5/6',
                'tag': '地方政府',
                'why': '紀念碑現況、地方政府觀點。',
            },
            {
                'title': '臺灣原住民族事典｜七腳川事件',
                'url': 'https://aborgpedia.alcd.center/detail?id=10137',
                'tag': '學術整理',
                'why': '含族群遷徙背景。',
            },
            {
                'title': '關鍵評論網｜阿美族 11 部落聯合祭祖',
                'url': 'https://www.thenewslens.com/article/19540',
                'tag': '當代記憶',
                'why': '當代部落聯合祭祖的記憶。',
            },
            {
                'title': '七腳川事件故事地圖（ArcGIS）',
                'url': 'https://storymaps.arcgis.com/collections/7e917133a47a4548bc33f5138a397474',
                'tag': '互動地圖',
                'why': '視覺化、可互動瀏覽。',
            },
        ],
        'level_hints': [
            ('程度較弱', '核心 1 + 補充 1 + 補充 2'),
            ('程度中等', '核心 2 + 補充 4 + 補充 5'),
            ('程度較強', '核心 3 + 補充 3'),
        ],
    },
    {
        'id': 'truku',
        'name': '太魯閣戰役',
        'year': '1914',
        'eng_name': 'Truku 戰役',
        'ethnic': '太魯閣族',
        'location': '主戰場立霧溪、木瓜溪上游山區',
        'color': '#8B2E2A',
        'notebook_placeholder': '[NOTEBOOK_URL_TRUKU]',
        'core': [
            {
                'title': '原民會叢書｜《太魯閣事件》',
                'url': 'https://www.cip.gov.tw/zh-tw/news/data-list/217054CAE51A3B1A/C89C009B11A070ECB6FF809CEAFB8CC6-info.html',
                'tag': '原民會官方',
                'why': '鴻義章撰寫。',
            },
            {
                'title': '原民會補充教材 PDF',
                'url': 'https://stv.naer.edu.tw/data/supplementary/原住民族重大歷史事件補充教材-太魯閣事件.pdf',
                'tag': '官方教材',
                'why': '免費全文。',
            },
            {
                'title': '戴寶村｜太魯閣戰爭百年回顧',
                'url': 'https://www.ntl.edu.tw/public/Attachment/47111003516.pdf',
                'tag': '學術論文',
                'why': '免費 PDF，國立公共資訊圖書館。',
            },
        ],
        'extra': [
            {
                'title': '維基百科｜太魯閣戰爭',
                'url': 'https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%AD%AF%E9%96%A3%E6%88%B0%E7%88%AD',
                'tag': '基本架構',
                'why': '快速掌握事件。',
            },
            {
                'title': '維基百科｜佐久間左馬太',
                'url': 'https://zh.wikipedia.org/zh-tw/%E4%BD%90%E4%B9%85%E9%96%93%E5%B7%A6%E9%A6%AC%E5%A4%AA',
                'tag': '人物傳記',
                'why': '含族人口述記憶版本（被擊落 vs 自行墜崖）。',
            },
            {
                'title': '環境資訊中心｜合歡越嶺道',
                'url': 'https://e-info.org.tw/node/116809',
                'tag': '深度報導',
                'why': '含古道現況與當代探勘。',
            },
            {
                'title': '臺灣原住民數位博物館｜太魯閣族',
                'url': 'https://www.dmtip.gov.tw/web/page/detail?l1=2&l2=53&l3=41&l4=208',
                'tag': '學術整理',
                'why': '族群遷徙史。',
            },
            {
                'title': '國家文化記憶庫｜佐久間蕃地偵察',
                'url': 'https://tcmb.culture.tw/zh-tw/detail?indexCode=Culture_Object&id=512258',
                'tag': '檔案照片',
                'why': '日方檔案、視覺證據。',
            },
        ],
        'level_hints': [
            ('程度較弱', '核心 1 + 補充 1 + 補充 3'),
            ('程度中等', '核心 1 + 補充 2 + 補充 4'),
            ('程度較強', '核心 3 + 補充 5'),
        ],
    },
]

DIVIDER_BY_EVENT = {
    'cepo': 'divider_mountain.png',
    'dafen': 'divider_water.png',
    'cikasuan': 'divider_mountain.png',
    'truku': 'divider_water.png',
}


# ============================================================
# HTML 產生
# ============================================================

def render_resource_row(idx, item, color):
    """每筆資料一行，含勾選框、標籤、標題、why、URL。"""
    return f'''
      <div class="resource-row">
        <div class="check-cell">
          <span class="check-num" style="background: {color};">{idx}</span>
          <span class="check-box">☐</span>
        </div>
        <div class="resource-body">
          <div class="resource-line">
            <span class="resource-tag" style="color: {color};">{item['tag']}</span>
            <span class="resource-title">{item['title']}</span>
          </div>
          <div class="resource-why">{item['why']}</div>
          <div class="resource-url">{item['url']}</div>
        </div>
      </div>
    '''


def render_event_section(event):
    rows_core = []
    for i, item in enumerate(event['core'], 1):
        rows_core.append(render_resource_row(f'核{i}', item, event['color']))

    rows_extra = []
    for i, item in enumerate(event['extra'], 1):
        rows_extra.append(render_resource_row(f'補{i}', item, event['color']))

    level_html = ''
    for level, suggestion in event['level_hints']:
        level_html += f'''
          <div class="level-row">
            <span class="level-name">{level}</span>
            <span class="level-suggestion">{suggestion}</span>
          </div>
        '''

    note_html = ''
    if 'note' in event:
        note_html = f'<div class="event-note">★ {event["note"]}</div>'

    total_count = len(event['core']) + len(event['extra'])

    divider = DIVIDER_BY_EVENT.get(event['id'], 'divider_mountain.png')
    event_image = f"event_{event['id']}.png"

    return f'''
    <section class="a4 weave-pattern event-page">
      <img class="chapter-divider" src="../assets/images/{divider}" alt="">
      <div class="event-header" style="border-top: 3px solid {event['color']};">
        <div class="event-eyebrow">花 蓮 高 商 ｜ 縱 谷 無 言 ｜ NotebookLM 資 料 清 單</div>
        <div class="event-title-row">
          <div class="event-circle" style="background: {event['color']};">{event['name'][0]}</div>
          <div>
            <div class="event-meta" style="color: {event['color']};">{event['ethnic']} ｜ {event['year']}</div>
            <h2 class="event-title">{event['name']}</h2>
            <div class="event-loc">{event['location']}</div>
          </div>
        </div>
      </div>

      <img class="event-ink-image" src="../assets/images/{event_image}" alt="">

      {note_html}

      <div class="notebook-card" style="border-left: 4px solid {event['color']};">
        <div class="notebook-eyebrow" style="color: {event['color']};">N O T E B O O K L M ‧ 此 事 件 專 屬 筆 記 本</div>
        <div class="notebook-url-line">
          <span class="notebook-url-label">網 址</span>
          <span class="notebook-url">{event['notebook_placeholder']}</span>
        </div>
        <div class="notebook-hint">在電腦教室開瀏覽器，貼上網址，登入學校 Google 帳號即可進入。可在 NotebookLM 內直接問問題、做摘要。</div>
        <div class="notebook-stat">本筆記本內含 <strong>{total_count}</strong> 筆資料來源（{len(event['core'])} 核心 + {len(event['extra'])} 補充）</div>
      </div>

      <div class="layer-head">
        <span class="layer-tag" style="background: {event['color']};">核 心 層</span>
        <span class="layer-hint">每位學生必看，至少參考 1 筆</span>
      </div>
      <div class="resource-list">{''.join(rows_core)}</div>

      <div class="layer-head" style="margin-top: 0.9rem;">
        <span class="layer-tag" style="background: {event['color']}; opacity: 0.7;">補 充 層</span>
        <span class="layer-hint">依程度選用，建議至少看過 2 筆</span>
      </div>
      <div class="resource-list">{''.join(rows_extra)}</div>

      <div class="level-suggestions" style="border-top: 2px solid {event['color']}33;">
        <div class="level-suggestions-head">
          <span class="layer-tag" style="background: {event['color']};">差 異 化 建 議</span>
        </div>
        {level_html}
      </div>

      <div class="page-foot">
        <span class="foot-event" style="color: {event['color']};">{event['name']}</span>
        <span class="foot-info">縱 谷 無 言 ‧ N o t e b o o k L M 清 單</span>
      </div>
    </section>
    '''


def build_html():
    sections = ''.join(render_event_section(ev) for ev in EVENTS)

    css = '''
      body {
        margin: 0;
        background: var(--bg-page);
        padding: 1rem 0;
        font-family: var(--font-serif);
      }
      .a4 {
        width: 210mm;
        min-height: 297mm;
        margin: 1rem auto;
        padding: 14mm 12mm;
        box-sizing: border-box;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      }

      /* ---- 封面 ---- */
      .cover-page .cover-hero {
        border-top: 3px solid var(--bg-strong);
        background: var(--bg-card);
        padding: 1.6rem 1.4rem 1.4rem;
        margin-bottom: 1.4rem;
      }
      .cover-eyebrow {
        font-family: var(--font-sans);
        font-size: 11px;
        letter-spacing: 0.4em;
        color: var(--text-second);
        margin-bottom: 0.7rem;
      }
      .cover-title {
        font-size: 32px;
        font-weight: 600;
        color: var(--text-title);
        margin: 0 0 0.4rem;
        letter-spacing: 0.04em;
      }
      .cover-title .dot { color: var(--color-cepo); }
      .cover-sub {
        font-family: var(--font-sans);
        font-size: 11px;
        letter-spacing: 0.2em;
        color: var(--text-second);
        margin-bottom: 1rem;
      }

      .cover-events {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.7rem;
        margin: 1rem 0;
      }
      .cover-event-card {
        padding: 0.9rem 1rem;
        background: var(--bg-card);
      }
      .cover-event-card .meta {
        font-family: var(--font-sans);
        font-size: 10px;
        letter-spacing: 0.25em;
        font-weight: 600;
        margin-bottom: 4px;
      }
      .cover-event-card .name {
        font-size: 17px;
        font-weight: 600;
        color: var(--text-title);
        margin-bottom: 4px;
      }
      .cover-event-card .loc {
        font-family: var(--font-sans);
        font-size: 10.5px;
        color: var(--text-second);
      }

      .how-to {
        margin: 1.5rem 0 0;
        padding: 1rem 1.2rem;
        background: var(--bg-card);
        border-top: 2px solid var(--color-cikasuan);
      }
      .how-to h3 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-title);
        margin: 0 0 0.6rem;
        display: flex; align-items: center; gap: 10px;
      }
      .how-to h3 .icon {
        background: var(--color-cikasuan);
        color: white;
        font-family: var(--font-sans);
        font-size: 12px;
        padding: 3px 8px;
        letter-spacing: 0.25em;
      }
      .how-to ol {
        margin: 0; padding-left: 1.4rem;
      }
      .how-to li {
        font-size: 13px;
        line-height: 1.95;
        margin-bottom: 4px;
      }
      .how-to li strong { color: var(--bg-strong); }

      .layer-legend {
        margin: 1rem 0 0;
        padding: 0.9rem 1.1rem;
        background: var(--bg-card);
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        border-top: 0.5px solid var(--line-soft);
      }
      .layer-legend .legend-item {
        display: flex; align-items: flex-start; gap: 8px;
      }
      .layer-legend .legend-dot {
        font-family: var(--font-sans);
        font-size: 10px;
        color: white;
        padding: 3px 8px;
        letter-spacing: 0.2em;
        flex-shrink: 0;
        font-weight: 600;
      }
      .legend-dot.core  { background: var(--bg-strong); }
      .legend-dot.extra { background: var(--text-muted); }
      .layer-legend .legend-text {
        font-size: 11.5px;
        line-height: 1.7;
      }

      /* ---- 事件頁 ---- */
      .event-header {
        background: var(--bg-card);
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
      }
      .chapter-divider {
        width: 100%;
        height: 28mm;
        object-fit: cover;
        display: block;
        margin: 0 0 0.9rem;
        opacity: 0.72;
      }
      .event-ink-image {
        width: 100%;
        height: 44mm;
        object-fit: cover;
        display: block;
        margin: -0.35rem 0 0.9rem;
        opacity: 0.82;
      }
      .event-eyebrow {
        font-family: var(--font-sans);
        font-size: 9.5px;
        letter-spacing: 0.35em;
        color: var(--text-second);
        margin-bottom: 0.6rem;
      }
      .event-title-row {
        display: flex; align-items: center; gap: 14px;
      }
      .event-circle {
        width: 48px; height: 48px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: white;
        font-size: 22px;
        font-weight: 600;
        flex-shrink: 0;
      }
      .event-meta {
        font-family: var(--font-sans);
        font-size: 10px;
        letter-spacing: 0.3em;
        font-weight: 600;
        margin-bottom: 2px;
      }
      .event-title {
        font-size: 22px;
        font-weight: 600;
        color: var(--text-title);
        margin: 0 0 2px;
        letter-spacing: 0.04em;
      }
      .event-loc {
        font-family: var(--font-sans);
        font-size: 10.5px;
        color: var(--text-second);
      }

      .event-note {
        margin-bottom: 0.8rem;
        padding: 0.6rem 0.9rem;
        background: rgba(217,164,65,0.15);
        border-left: 3px solid var(--color-cikasuan);
        font-size: 11.5px;
        color: var(--text-primary);
        line-height: 1.7;
      }

      /* ---- NotebookLM 卡片 ---- */
      .notebook-card {
        background: var(--bg-card);
        padding: 0.9rem 1rem 0.9rem 1.1rem;
        margin-bottom: 1rem;
      }
      .notebook-eyebrow {
        font-family: var(--font-sans);
        font-size: 10px;
        letter-spacing: 0.3em;
        font-weight: 600;
        margin-bottom: 0.4rem;
      }
      .notebook-url-line {
        display: flex; align-items: baseline; gap: 10px;
        margin-bottom: 0.4rem;
        flex-wrap: wrap;
      }
      .notebook-url-label {
        font-family: var(--font-sans);
        font-size: 10px;
        letter-spacing: 0.25em;
        color: var(--text-muted);
        font-weight: 600;
        flex-shrink: 0;
      }
      .notebook-url {
        font-family: 'Courier New', monospace;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-title);
        word-break: break-all;
        background: rgba(43,37,32,0.06);
        padding: 3px 8px;
        letter-spacing: 0.02em;
      }
      .notebook-hint {
        font-family: var(--font-sans);
        font-size: 11px;
        color: var(--text-second);
        line-height: 1.65;
        margin-bottom: 0.4rem;
      }
      .notebook-stat {
        font-family: var(--font-sans);
        font-size: 10.5px;
        color: var(--text-muted);
        letter-spacing: 0.05em;
      }
      .notebook-stat strong {
        color: var(--bg-strong);
        font-size: 12px;
      }

      .layer-head {
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 0.5rem;
      }
      .layer-tag {
        color: white;
        font-family: var(--font-sans);
        font-size: 10px;
        letter-spacing: 0.3em;
        padding: 4px 10px;
        font-weight: 600;
      }
      .layer-hint {
        font-family: var(--font-sans);
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 0.1em;
      }

      /* ---- 資料列（單欄、勾選） ---- */
      .resource-list {
        display: flex;
        flex-direction: column;
      }
      .resource-row {
        display: grid;
        grid-template-columns: 38px 1fr;
        gap: 10px;
        padding: 8px 4px 8px 6px;
        border-bottom: 0.5px solid var(--line-thin);
      }
      .resource-row:last-child {
        border-bottom: none;
      }
      .check-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        padding-top: 1px;
      }
      .check-num {
        color: white;
        font-family: var(--font-sans);
        font-size: 9px;
        font-weight: 600;
        padding: 2px 6px;
        letter-spacing: 0.05em;
        line-height: 1.3;
      }
      .check-box {
        font-size: 18px;
        color: var(--text-muted);
        line-height: 1;
      }
      .resource-body {
        min-width: 0;
      }
      .resource-line {
        display: flex;
        align-items: baseline;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 2px;
      }
      .resource-tag {
        font-family: var(--font-sans);
        font-size: 9.5px;
        letter-spacing: 0.2em;
        font-weight: 600;
        flex-shrink: 0;
      }
      .resource-title {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-title);
        line-height: 1.4;
      }
      .resource-why {
        font-family: var(--font-sans);
        font-size: 10.5px;
        color: var(--text-second);
        line-height: 1.6;
        margin-bottom: 2px;
      }
      .resource-url {
        font-family: 'Courier New', monospace;
        font-size: 8.5px;
        color: var(--text-muted);
        word-break: break-all;
        line-height: 1.4;
      }

      .level-suggestions {
        margin-top: 0.9rem;
        padding-top: 0.7rem;
      }
      .level-suggestions-head {
        margin-bottom: 0.5rem;
      }
      .level-row {
        display: grid;
        grid-template-columns: 90px 1fr;
        gap: 12px;
        align-items: baseline;
        margin-bottom: 0.3rem;
        font-size: 12px;
      }
      .level-name {
        font-family: var(--font-sans);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.2em;
        color: var(--bg-strong);
      }
      .level-suggestion {
        color: var(--text-primary);
      }

      .page-foot {
        margin-top: 1rem;
        padding-top: 0.6rem;
        border-top: 0.5px solid var(--line-soft);
        display: flex;
        justify-content: space-between;
        font-family: var(--font-sans);
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 0.25em;
      }
      .foot-event { font-weight: 600; }

      /* ---- 列印 ---- */
      @page { size: A4; margin: 0; }
      @media print {
        body { padding: 0; background: white; }
        .a4 {
          margin: 0;
          box-shadow: none;
          page-break-after: always;
        }
        .a4:last-child { page-break-after: auto; }
        .preview-bar { display: none; }
      }

      .preview-bar {
        max-width: 210mm;
        margin: 0 auto 1rem;
        padding: 12px 16px;
        background: rgba(43,37,32,0.92);
        color: #F5F1EA;
        font-family: var(--font-sans);
        font-size: 12px;
        letter-spacing: 0.1em;
        line-height: 1.7;
      }
      .preview-bar strong { color: var(--color-cikasuan-dark); letter-spacing: 0.2em; }
    '''

    cover = '''
    <section class="a4 weave-pattern cover-page">
      <div class="cover-hero">
        <div class="cover-eyebrow">花 蓮 高 商 ｜ 二 年 級 ｜ 多 元 文 化 與 文 學</div>
        <h1 class="cover-title">NotebookLM 資料清單<span class="dot">．</span>原住民族重大歷史事件</h1>
        <div class="cover-sub">縱 谷 無 言 ｜ 三 節 課 學 生 紙 本 工 具 ｜ 電 腦 教 室 用</div>
        <div class="event-color-bar" style="margin: 0.8rem 0 0;">
          <div class="seg-cepo"></div>
          <div class="seg-dafen"></div>
          <div class="seg-cikasuan"></div>
          <div class="seg-truku"></div>
        </div>
      </div>

      <div class="cover-events">
        <div class="cover-event-card" style="border-left: 3px solid var(--color-cepo);">
          <div class="meta" style="color: var(--color-cepo);">阿 美 族 ｜ 1 8 7 7</div>
          <div class="name">大港口事件</div>
          <div class="loc">花蓮縣豐濱鄉靜浦村</div>
        </div>
        <div class="cover-event-card" style="border-left: 3px solid var(--color-dafen);">
          <div class="meta" style="color: var(--color-dafen);">布 農 族 ｜ 1 9 1 5</div>
          <div class="name">大分事件</div>
          <div class="loc">花蓮縣卓溪鄉</div>
        </div>
        <div class="cover-event-card" style="border-left: 3px solid var(--color-cikasuan);">
          <div class="meta" style="color: #B0822A;">阿 美 族 ｜ 1 9 0 8</div>
          <div class="name">七腳川事件</div>
          <div class="loc">花蓮縣吉安鄉</div>
        </div>
        <div class="cover-event-card" style="border-left: 3px solid var(--color-truku);">
          <div class="meta" style="color: var(--color-truku);">太 魯 閣 族 ｜ 1 9 1 4</div>
          <div class="name">太魯閣戰役</div>
          <div class="loc">立霧溪、木瓜溪上游</div>
        </div>
      </div>

      <div class="how-to">
        <h3><span class="icon">使 用</span>怎麼用這份清單</h3>
        <ol>
          <li><strong>找到自己選的事件</strong>：翻到該事件那一頁，看頂端的 NotebookLM 網址。</li>
          <li><strong>登入學校 Google 帳號</strong>：在電腦教室瀏覽器貼上網址，登入即可進入該事件專屬筆記本。</li>
          <li><strong>NotebookLM 怎麼用</strong>：左側是老師預先匯入的資料（核心+補充），中央可以直接問問題、做摘要、找引用。</li>
          <li><strong>讀過就勾</strong>：每筆資料左側有 ☐ 勾選框，讀完一筆就勾起來，方便自己追蹤。</li>
          <li><strong>程度差異化建議</strong>：每頁底部有「程度較弱／中等／較強」搭配，可照著挑。</li>
          <li><strong>資料來源欄要寫</strong>：報告第捌題要填 3 筆來源，請從本清單的核心+補充中挑選並抄下完整 URL。</li>
        </ol>
      </div>

      <div class="layer-legend">
        <div class="legend-item">
          <span class="legend-dot core">核 心</span>
          <div class="legend-text">官方／學術為主，正確度高，<strong>每位學生至少看 1 筆</strong>。</div>
        </div>
        <div class="legend-item">
          <span class="legend-dot extra">補 充</span>
          <div class="legend-text">媒體／部落／影像／互動資源，依程度選用，<strong>建議看 2 筆</strong>。</div>
        </div>
      </div>

      <div class="page-foot">
        <span>使 用 說 明</span>
        <span>頁 1 / 5</span>
      </div>
    </section>
    '''

    html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>縱谷無言．NotebookLM 資料清單</title>
<link rel="stylesheet" href="../assets/styles/design_tokens.css">
<style>{css}</style>
</head>
<body class="theme-light weave-pattern">

<div class="preview-bar no-print">
  <strong>NotebookLM 資料清單．印刷紙本</strong>
  共 5 頁（封面 1 + 事件 4），建議 A4 雙面列印。每位學生發一份。
  四個 <code>[NOTEBOOK_URL_*]</code> 佔位符請於老師建立完 NotebookLM 後手動替換。
</div>

{cover}
{sections}

</body>
</html>
'''
    return html


if __name__ == '__main__':
    html = build_html()
    output_path = 'teaching_materials/student_resources_handout.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'已產出：{output_path}')

    total = sum(len(ev['core']) + len(ev['extra']) for ev in EVENTS)
    print(f'共 {len(EVENTS)} 個事件，{total} 筆資料來源（待您匯入 4 個 NotebookLM）。')
    print('佔位符：[NOTEBOOK_URL_CEPO] [NOTEBOOK_URL_DAFEN] [NOTEBOOK_URL_CIKASUAN] [NOTEBOOK_URL_TRUKU]')
