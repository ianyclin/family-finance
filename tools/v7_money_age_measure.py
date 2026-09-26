# -*- coding: utf-8 -*-
"""量第 24 節「每一筆錢都有自己的三十年」（money-age）兩版 SVG 的版面：
桌機 <svg class="d"> 與手機 <svg class="m">，各查四件事——文字估算框互不重疊、文字不出 viewBox、
同一排標籤的中心距夠、粗箭頭箭身不碰標籤盒，其他幾何點也不出 viewBox。SVG 直接從 guide/index.html 讀。
用法：python3 tools/v7_money_age_measure.py [--guide guide/index.html]；全過印 TOTAL OK，exit 0。
批 BR should-2 留下的量測腳本，批 CC 從 scratchpad 收進 tools/（原本是呼叫 v7_g11_money_age 重新產圖，
現在改成讀落地的 guide，量的就是讀者真的會看到的那一份）。
"""
import re, sys, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import essay_charts as E

_args = sys.argv[1:]
GUIDE = _args[_args.index('--guide') + 1] if '--guide' in _args else os.path.join(ROOT, 'guide', 'index.html')

T = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)"[^>]*>(.*?)</text>')

def boxes(svg):
    out = []
    for m in T.finditer(svg):
        x, y, fs, anc, t = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4), html.unescape(m.group(5))
        w = E.textw(t, fs)
        if anc == 'middle': x0 = x - w / 2
        elif anc == 'end':  x0 = x - w
        else:               x0 = x
        # 基線上 0.85em、下 0.2em
        out.append((t, x0, y - fs * 0.85, x0 + w, y + fs * 0.2))
    return out

def _seg_seg(ax, ay, bx, by, cx, cy, dx_, dy):
    """兩條線段：回 (最近距離, 是否相交)。"""
    def cross(ox, oy, px, py, qx, qy):
        return (px - ox) * (qy - oy) - (py - oy) * (qx - ox)
    d1 = cross(cx, cy, dx_, dy, ax, ay); d2 = cross(cx, cy, dx_, dy, bx, by)
    d3 = cross(ax, ay, bx, by, cx, cy); d4 = cross(ax, ay, bx, by, dx_, dy)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0, True
    return min(_pt_seg(ax, ay, cx, cy, dx_, dy), _pt_seg(bx, by, cx, cy, dx_, dy),
               _pt_seg(cx, cy, ax, ay, bx, by), _pt_seg(dx_, dy, ax, ay, bx, by)), False


def _pt_seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    qx, qy = ax + t * vx, ay + t * vy
    return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5


def seg_rect(x1, y1, x2, y2, rx0, ry0, rx1, ry1):
    """線段對矩形：回 (最近距離, 是否相交)。端點落在矩形內也算相交。"""
    for px, py in ((x1, y1), (x2, y2)):
        if rx0 <= px <= rx1 and ry0 <= py <= ry1:
            return 0.0, True
    edges = [(rx0, ry0, rx1, ry0), (rx1, ry0, rx1, ry1),
             (rx1, ry1, rx0, ry1), (rx0, ry1, rx0, ry0)]
    best = float('inf')
    for ex0, ey0, ex1, ey1 in edges:
        d, hit = _seg_seg(x1, y1, x2, y2, ex0, ey0, ex1, ey1)
        if hit:
            return 0.0, True
        best = min(best, d)
    return best, False


def run(name, svg):
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    W, H = int(vb.group(1)), int(vb.group(2))
    bs = boxes(svg)
    print('== %s  viewBox %dx%d  text 元素 %d 個' % (name, W, H, len(bs)))
    bad = 0
    for t, x0, y0, x1, y1 in bs:
        if x0 < 0 or x1 > W or y0 < 0 or y1 > H:
            print('  出界: %-12s box=(%.1f,%.1f)-(%.1f,%.1f)' % (t, x0, y0, x1, y1)); bad += 1
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, b = bs[i], bs[j]
            ox = min(a[3], b[3]) - max(a[1], b[1])
            oy = min(a[4], b[4]) - max(a[2], b[2])
            if ox > 0 and oy > 0:
                print('  重疊: %r 與 %r  重疊 %.1f x %.1f' % (a[0], b[0], ox, oy)); bad += 1
    # 鄰近同排標籤的中心距（規格：≥ 字寬＋4）
    for row_y in sorted(set(round(b[2], 1) for b in bs)):
        row = sorted([b for b in bs if abs(round(b[2], 1) - row_y) < 0.05], key=lambda b: b[1])
        if len(row) < 2: continue
        gaps = []
        for k in range(len(row) - 1):
            c1 = (row[k][1] + row[k][3]) / 2; c2 = (row[k + 1][1] + row[k + 1][3]) / 2
            need = max(row[k][3] - row[k][1], row[k + 1][3] - row[k + 1][1]) + 4
            gaps.append((c2 - c1, need))
        worst = min(gaps, key=lambda g: g[0] - g[1])
        ok = 'OK' if worst[0] >= worst[1] else 'FAIL'
        print('  一排 %d 個標籤（%s…%s）最小中心距 %.1f，需要 ≥ %.1f  %s'
              % (len(row), row[0][0], row[-1][0], worst[0], worst[1], ok))
        if worst[0] < worst[1]: bad += 1
    # 批 BR should-2：粗箭頭的箭身（stroke-width 3.2）不可以和標籤盒（var(--surface) 的 rect）
    # 相交，最近距離要 ≥ 6px。兩版都算、都印數值。
    shaft = re.search(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"'
                      r'[^>]*stroke-width="3\.2"', svg)
    box = re.search(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"'
                    r'[^>]*fill="var\(--surface\)"', svg)
    if shaft and box:
        x1, y1, x2, y2 = map(float, shaft.groups())
        bx, by, bw, bh = map(float, box.groups())
        rx0, ry0, rx1, ry1 = bx, by, bx + bw, by + bh
        d, hit = seg_rect(x1, y1, x2, y2, rx0, ry0, rx1, ry1)
        ok = 'OK' if (not hit and d >= 6.0) else 'FAIL'
        print('  箭身 (%.1f,%.1f)->(%.1f,%.1f)  標籤盒 x∈[%.1f,%.1f] y∈[%.1f,%.1f]'
              % (x1, y1, x2, y2, rx0, rx1, ry0, ry1))
        print('  箭身與標籤盒：%s，最近距離 %.2f px（需要不相交且 ≥ 6.00）  %s'
              % ('相交' if hit else '不相交', d, ok))
        if hit or d < 6.0: bad += 1
    else:
        print('  找不到箭身或標籤盒'); bad += 1

    # 其他幾何：line / polygon / rect / polyline
    pts = []
    for m in re.finditer(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"', svg):
        pts += [(float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))]
    for m in re.finditer(r'points="([^"]+)"', svg):
        for p in m.group(1).split():
            a, b = p.split(','); pts.append((float(a), float(b)))
    for m in re.finditer(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"', svg):
        x, y, w, hh = map(float, m.groups()); pts += [(x, y), (x + w, y + hh)]
    off = [p for p in pts if p[0] < 0 or p[0] > W or p[1] < 0 or p[1] > H]
    print('  幾何點 %d 個，出 viewBox %d 個' % (len(pts), len(off)))
    if off: print('   ', off[:6]); bad += 1
    print('  => %s' % ('OK' if bad == 0 else '%d 個問題' % bad))
    return bad

def read_svgs(path):
    """從 guide/index.html 的 <figure data-chart="money-age"> 裡取出桌機版與手機版兩張 SVG。"""
    doc = open(path, encoding='utf-8').read()
    i = doc.find('data-chart="money-age"')
    if i < 0:
        raise SystemExit('在 %s 找不到 data-chart="money-age"' % path)
    j = doc.find('</figure>', i)
    if j < 0:
        raise SystemExit('money-age 那個 <figure> 沒有收尾')
    fig = doc[i:j]
    svgs = re.findall(r'<svg class="([dm])"[^>]*>.*?</svg>', fig, re.S)
    body = re.findall(r'<svg class="[dm]"[^>]*>.*?</svg>', fig, re.S)
    got = dict(zip(svgs, body))
    if set(got) != {'d', 'm'}:
        raise SystemExit('money-age 應該有 class="d" 與 class="m" 兩張 SVG，實際拿到 %r' % sorted(got))
    return got['d'], got['m']


print('讀 %s' % os.path.relpath(GUIDE, ROOT))
_d, _m = read_svgs(GUIDE)
n = run('桌機 640', _d) + run('手機 375（viewBox 360）', _m)
print('TOTAL', 'OK' if n == 0 else '%d 個問題' % n)
sys.exit(1 if n else 0)
