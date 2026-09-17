#!/usr/bin/env python3
"""圖表裡判（手機）：headless Chrome 視窗最窄 500，所以用 iframe 做出真正 390／360 寬的視窗。

1. figs-only.html 放進 390、360 寬的 iframe 截圖（淺色、深色）。
2. full-measure.html（整份指南＋量測腳本）放進 390、360 寬 iframe，iframe 內把結果 postMessage 給外層，外層寫進 DOM 後 --dump-dom。
先跑 charts_judge_render.py 產生 render/ 裡的兩個 html。
"""
import html as H
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'render'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def wrapper(inner, w, h, relay=False):
    js = ''
    if relay:
        js = ("<script>window.addEventListener('message',function(e){var p=document.createElement('pre');"
              "p.id='relay';p.textContent=e.data;document.body.appendChild(p);});</script>")
    return ('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#888}'
            'iframe{border:0;display:block;background:#fff}</style></head><body>%s'
            '<iframe src="%s" width="%d" height="%d"></iframe></body></html>' % (js, inner.as_uri(), w, h))


def main():
    full = OUT / 'full-measure.html'
    s = full.read_text(encoding='utf-8')
    # 量測腳本改成也 postMessage 給外層，外加整頁水平溢出的元素清單
    extra = r"""
<script>
(function(){
  var pre=document.getElementById('judge-result'); var data=JSON.parse(pre.textContent);
  data.innerWidth=window.innerWidth; data.docScrollWidth=document.documentElement.scrollWidth;
  var wide=[]; document.querySelectorAll('figure.chart[data-chart="country-recovery"] *, figure.chart[data-chart="rebalance-drift"] *').forEach(function(e){
    var b=e.getBoundingClientRect(); if(b.right>window.innerWidth+0.5) wide.push(e.tagName+'.'+(e.getAttribute('class')||'')+':'+Math.round(b.right));});
  data.fig_elements_past_viewport=wide.slice(0,20);
  var fr={}; ['country-recovery','rebalance-drift'].forEach(function(id){var f=document.querySelector('figure[data-chart="'+id+'"]'); var b=f.getBoundingClientRect(); fr[id]=[Math.round(b.left),Math.round(b.right)];
    var svg=[].slice.call(f.querySelectorAll('svg')).filter(function(x){return getComputedStyle(x).display!=='none';})[0]; fr[id+'_svg']=[svg.getAttribute('class'),Math.round(svg.getBoundingClientRect().width)];});
  data.fig_lr=fr;
  parent.postMessage(JSON.stringify(data),'*');
})();
</script>"""
    s2 = s.replace('</body>', extra + '</body>', 1)
    full2 = OUT / 'full-measure-relay.html'
    full2.write_text(s2, encoding='utf-8')
    res = {}
    for w in (390, 360):
        wp = OUT / ('wrap-measure-%d.html' % w)
        wp.write_text(wrapper(full2, w, 800, relay=True), encoding='utf-8')
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1000,900',
                            '--virtual-time-budget=8000', '--dump-dom', wp.as_uri()], capture_output=True, text=True, timeout=300)
        m = re.search(r'<pre id="relay">(.*?)</pre>', p.stdout, re.S)
        res[w] = json.loads(H.unescape(m.group(1))) if m else {'error': p.stderr[-1500:]}
    (OUT / 'measure-mobile.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')

    figs = OUT / 'figs-only.html'
    for w in (390, 360):
        for dark in (False, True):
            wp = OUT / ('wrap-shot-%d%s.html' % (w, '-dark' if dark else ''))
            wp.write_text(wrapper(figs, w, 2700), encoding='utf-8')
            png = OUT / ('figs-iframe-%d%s.png' % (w, '-dark' if dark else ''))
            cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=%d,2700' % (w + 10),
                   '--virtual-time-budget=3000', '--screenshot=%s' % png, wp.as_uri()]
            if dark:
                cmd.insert(3, '--force-dark-mode')
                cmd.insert(3, '--blink-settings=preferredColorScheme=0')
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    for w, r in res.items():
        print(w, json.dumps({k: r.get(k) for k in ('innerWidth', 'docScrollWidth', 'fig_elements_past_viewport', 'fig_lr', 'error')}, ensure_ascii=False))
        for fid, f in (r.get('figs') or {}).items():
            for o in f['svgs']:
                print('  ', fid, o['cls'], {k: o[k] for k in ('out_of_viewbox', 'text_text_overlap', 'text_mark_overlap', 'text_line_overlap')},
                      'children_overflow', f['children_overflow'])


if __name__ == '__main__':
    main()
