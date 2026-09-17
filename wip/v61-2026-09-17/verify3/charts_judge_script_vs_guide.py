#!/usr/bin/env python3
"""圖表裡判：腳本產生的兩張圖（不寫檔）vs guide/index.html 與 output/full-v60-out.html 裡的圖。

只讀：import essay_charts 後直接呼叫 country_recovery()/rebalance_drift()，不呼叫 do_guide()。
比對 title、sub、svg、legend+note、caption；另外把 SVG 座標反推回數字。
"""
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import essay_charts as E  # noqa: E402


def figs(path):
    s = path.read_text(encoding='utf-8')
    return {m.group(1): m.group(0) for m in re.finditer(r'<figure class="chart" data-chart="([^"]+)">.*?</figure>', s, re.S)}


def plain(x):
    return unescape(re.sub(r'<[^>]+>', '', x)).strip()


guide = figs(ROOT / 'guide' / 'index.html')
full = figs(ROOT / 'output' / 'full-v60-out.html')
report = []
for cid, fn in (('country-recovery', E.country_recovery), ('rebalance-drift', E.rebalance_drift)):
    d = fn()
    built = E.figure(cid, d['title'], d['sub'], d['svgs'], d['caption'], d.get('extras', ''))
    g = guide.get(cid)
    f = full.get(cid)
    report.append('== %s' % cid)
    report.append('guide 有這張圖: %s；full-v60-out 有這張圖: %s' % (g is not None, f is not None))
    cap_g = plain(re.search(r'<figcaption>(.*?)</figcaption>', g, re.S).group(1))
    report.append('caption 腳本==指南: %s' % (plain(E.esc(d['caption'])) == cap_g))
    if plain(E.esc(d['caption'])) != cap_g:
        report.append('  腳本: ' + d['caption'])
        report.append('  指南: ' + cap_g)
    # 除 figcaption 以外整張比
    strip = lambda x: re.sub(r'<figcaption>.*?</figcaption>', '', x, flags=re.S)
    report.append('除 figcaption 外 腳本==指南（逐字）: %s' % (strip(built) == strip(g)))
    if f is not None:
        # full 版可能被 build_lite 改寫（class、data-print 之類），先比純文字與 svg
        svg_g = re.findall(r'<svg.*?</svg>', g, re.S)
        svg_f = re.findall(r'<svg.*?</svg>', f, re.S)
        report.append('SVG 指南==full-v60-out: %s（%d/%d 個）' % (svg_g == svg_f, len(svg_g), len(svg_f)))
        report.append('純文字 指南==full-v60-out: %s' % (plain(g) == plain(f)))
    if cid == 'rebalance-drift':
        report.append('printed: %s' % d.get('printed', {}))

# ---- SVG 反推 ----
g = guide['rebalance-drift']
svgs = re.findall(r'<svg class="(d|m)" viewBox="0 0 (\d+) (\d+)".*?</svg>', g, re.S)
for cls, W, H in svgs:
    body = re.search(r'<svg class="%s" viewBox.*?</svg>' % cls, g, re.S).group(0)
    grid = {int(t.rstrip('%')): float(y) for y, t in re.findall(r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="[\d.]+" stroke="var\(--line\)"[^>]*/>\s*<text[^>]*>(\d+%)</text>', body)}
    y70, y100 = grid[70], grid[100]
    val = lambda y: 70 + (y70 - y) * 30 / (y70 - y100)
    pts = re.search(r'<polyline points="([^"]+)" fill="none" stroke="var\(--accent\)"', body).group(1).split()
    pts = [tuple(map(float, p.split(','))) for p in pts]
    xs = [p[0] for p in pts]
    step = (xs[-1] - xs[0]) / (len(xs) - 1)
    yrs = [1989 + round((x - xs[0]) / step) for x in xs]
    vals = [round(val(y), 2) for _, y in pts]
    report.append('== rebalance-drift %s: %d 點，年份 %s..%s' % (cls, len(pts), yrs[0], yrs[-1]))
    report.append('  反推值: %s' % list(zip(yrs, vals)))
    band = re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*fill="var\(--amber\)"', body)
    report.append('  門檻帶 y 範圍反推: %.2f%% ~ %.2f%%' % (val(float(band.group(2)) + float(band.group(4))), val(float(band.group(2)))))
    dash = re.search(r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="[\d.]+" stroke="var\(--ink\)" stroke-width="1.6" stroke-dasharray="6 5"', body)
    report.append('  虛線反推: %.2f%%' % val(float(dash.group(1))))
    report.append('  文字: %s' % [plain(t) for t in re.findall(r'<text[^>]*>.*?</text>', body)])

g = guide['country-recovery']
for cls in ('d', 'm'):
    body = re.search(r'<svg class="%s" viewBox.*?</svg>' % cls, g, re.S).group(0)
    ticks = [(float(x), int(t)) for x, t in re.findall(r'<text x="([\d.]+)" y="[\d.]+" font-size="[\d.]+" text-anchor="middle" fill="var\(--muted\)">(\d{4})</text>', body)]
    (xa, ta), (xb, tb) = ticks[0], ticks[-1]
    yr = lambda x: ta + (x - xa) * (tb - ta) / (xb - xa)
    rects = re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"', body)
    report.append('== country-recovery %s: 長條起訖反推 %s' % (cls, [(round(yr(float(x)), 3), round(yr(float(x) + float(w)), 3)) for x, w in rects]))
    report.append('  文字: %s' % [plain(t) for t in re.findall(r'<text[^>]*>.*?</text>', body) if not re.fullmatch(r'<text[^>]*>\d{4}</text>', t)])

print('\n'.join(report))
