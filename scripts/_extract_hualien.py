"""
從 g0v 公開的台灣縣市界 GeoJSON 抽出花蓮縣輪廓並簡化，
存成輕量檔 data/geo/hualien_outline.json。

只需執行一次（或當原始檔更新時）；後續 generate_event_map_print.py 會用此輕量檔。

來源資料：
  https://github.com/g0v/twgeojson  (CC0)
  原始 9 MB 檔案可丟掉，要時再用以下指令重抓：
    curl -L -o data/geo/tw_counties.geo.json \
      https://raw.githubusercontent.com/g0v/twgeojson/master/json/twCounty2010.geo.json

產出格式（自訂、輕量）：
{
  "license": "...",
  "source": "...",
  "main": [[lng, lat], ...],          # 主島簡化後座標（外環）
  "islets": [[[lng, lat], ...], ...]  # 周邊小島／離島（已簡化）
}
"""

import json
from pathlib import Path
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / 'data' / 'geo' / 'tw_counties.geo.json'
DST  = ROOT / 'data' / 'geo' / 'hualien_outline.json'

# 簡化容差（單位：經緯度，約 1° ≈ 111km）
# 0.001° ≈ 110m，足以印 A2 不失真
TOLERANCE_MAIN  = 0.0008
TOLERANCE_ISLET = 0.0015


def main():
    raw = json.loads(SRC.read_text(encoding='utf-8'))
    feat = next(f for f in raw['features']
                if '花蓮' in f['properties'].get('COUNTYNAME', ''))

    geom = shape(feat['geometry'])  # MultiPolygon
    polys = list(geom.geoms)
    polys.sort(key=lambda p: p.area, reverse=True)

    main_poly = polys[0].simplify(TOLERANCE_MAIN, preserve_topology=True)
    main_ring = list(main_poly.exterior.coords)

    islets = []
    for p in polys[1:]:
        s = p.simplify(TOLERANCE_ISLET, preserve_topology=True)
        if s.is_empty or s.area < 0.00001:
            continue
        islets.append(list(s.exterior.coords))

    out = {
        'license':     'CC0 1.0',
        'source':      'g0v/twgeojson (twCounty2010.geo.json) — 花蓮縣',
        'simplified_with': f'shapely.simplify(tolerance={TOLERANCE_MAIN})',
        'main':        [[round(x, 5), round(y, 5)] for x, y in main_ring],
        'islets':      [[[round(x, 5), round(y, 5)] for x, y in r] for r in islets],
    }

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'已輸出：{DST.relative_to(ROOT)}')
    print(f'  主島：{len(out["main"])} 點（原 {len(list(polys[0].exterior.coords))} 點）')
    print(f'  小島：{len(out["islets"])} 個')
    print(f'  檔案：{DST.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
