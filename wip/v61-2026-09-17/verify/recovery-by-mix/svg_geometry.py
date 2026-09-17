#!/usr/bin/env python3
"""讀起草者的預覽 HTML（不 import 模組），估文字寬度，檢查超框與同列重疊。"""
import re, html, unicodedata
W3 = '/Users/linyenchu/Cladue Code/family-finance/wip/v61-2026-09-17/w3/'
src = open(W3 + 'recovery-by-mix.html', encoding='utf-8').read()

def width(s, size, weight):
    w = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in 'WF':
            w += 1.0
        elif ch in '−%':
            w += 0.75
        elif ch == ' ':
            w += 0.28
        else:
            w += 0.6
    return w * size * (1.05 if weight and int(weight) >= 700 else 1)

for svg in re.findall(r'<svg class="(d|m)" viewBox="0 0 (\d+) (\d+)".*?</svg>', src, flags=re.S):
    pass
svgs = re.findall(r'(<svg class="([dm])" viewBox="0 0 (\d+) (\d+)"[^>]*>.*?</svg>)', src, flags=re.S)
for whole, kind, W, H in svgs:
    W, H = int(W), int(H)
    items = []
    for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)" fill="[^"]+"(?: font-weight="(\d+)")?>([^<]*)</text>', whole):
        x, y, fs, anc, wt, s = float(m[1]), float(m[2]), float(m[3]), m[4], m[5], html.unescape(m[6])
        w = width(s, fs, wt)
        x0 = x if anc == 'start' else (x - w if anc == 'end' else x - w / 2)
        items.append(('T', x0, y - fs * 0.8, x0 + w, y + fs * 0.2, s))
    for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', whole):
        x, y, w, h = map(float, m.groups())
        items.append(('R', x, y, x + w, y + h, 'rect'))
    print('== %s W=%d H=%d  texts=%d rects=%d' % (kind, W, H, sum(1 for i in items if i[0] == 'T'), sum(1 for i in items if i[0] == 'R')))
    for it in items:
        if it[1] < 0 or it[3] > W or it[2] < 0 or it[4] > H:
            print('  OUT OF BOX:', it)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if a[0] == 'R' and b[0] == 'R':
                continue
            ox = min(a[3], b[3]) - max(a[1], b[1])
            oy = min(a[4], b[4]) - max(a[2], b[2])
            if ox > 0.5 and oy > 0.5:
                print('  OVERLAP %.1fx%.1f: %s | %s' % (ox, oy, a, b))
    # 最小水平間距（同一基線的文字）
    ts = [i for i in items if i[0] == 'T']
    gaps = []
    for a in ts:
        for b in ts:
            if a is not b and abs(a[4] - b[4]) < 1 and b[1] >= a[3]:
                gaps.append((b[1] - a[3], a[5], b[5]))
    gaps.sort()
    print('  tightest same-line gaps:', [(round(g, 1), x, y) for g, x, y in gaps[:6]])
