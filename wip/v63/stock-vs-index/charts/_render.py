"""測試共用：把 chart(res) 的結果包成指南同樣 CSS 的頁面，用 Chrome headless 截桌面與手機兩張圖。
手機版用固定 400px 寬的包裝頁（圖的手機 SVG viewBox 是 360）。"""
import os, re, json, subprocess

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
OUT = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def visible_numbers(d):
    alltext = d['title'] + d['sub'] + ''.join(d['svgs']) + d['extras'] + d['caption']
    vis = re.sub(r'<[^>]+>', ' ', alltext)
    return sorted(set(re.findall(r'\d+(?:\.\d+)?', vis))), alltext


def flat_numbers(res):
    flat = set()

    def walk(o):
        if isinstance(o, dict):
            [walk(v) for v in o.values()]
        elif isinstance(o, list):
            [walk(v) for v in o]
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            flat.add(str(o))
            if float(o).is_integer():
                flat.add(str(int(o)))
        elif isinstance(o, str):
            for n in re.findall(r'\d+(?:\.\d+)?', o):
                flat.add(n)
    walk(res)
    return flat


def render(cid, d, desktop_h=1100, mobile_h=1600):
    import essay_charts as E
    fig = E.figure(cid, d['title'], d['sub'], d['svgs'], d['caption'], d['extras'])
    g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
    css = re.search(r'<style[^>]*>(.*?)</style>', g, re.S).group(1)
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>%s body{background:var(--paper);padding:8px 16px}</style>'
            '<main style="max-width:760px;margin:auto">%s</main>' % (css, fig))
    html = os.path.join(OUT, cid + '.html')
    open(html, 'w', encoding='utf-8').write(page)
    # 手機：固定 400px 寬的包裝頁，強制顯示 svg.m
    mpage = (page.replace('max-width:760px;margin:auto', 'width:400px;margin:0')
                 .replace('body{background:var(--paper);padding:8px 16px}',
                          'body{background:var(--paper);padding:0;margin:0;width:400px}')
                 .replace('</style>', 'figure.chart svg.d{display:none!important}'
                                      'figure.chart svg.m{display:block!important}'
                                      'figure.chart{margin:0;padding:14px 12px;border-radius:0}</style>'))
    mhtml = os.path.join(OUT, cid + '-mobile.html')
    open(mhtml, 'w', encoding='utf-8').write(mpage)
    shots = []
    for name, size, src in ((cid + '-desktop.png', '900,%d' % desktop_h, html),
                            (cid + '-mobile.png', '400,%d' % mobile_h, mhtml)):
        p = os.path.join(OUT, name)
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=2', '--screenshot=' + p,
                        '--window-size=' + size, 'file://' + src], check=True, capture_output=True)
        shots.append(p)
    return shots
