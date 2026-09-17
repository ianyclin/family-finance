#!/usr/bin/env python3
"""圖表裡判（手機字級）：390／360 寬 iframe 裡，全書每張 figure.chart 的手機 SVG 實際寬度與最小字的實際像素。
用來判斷 country-recovery 放在 data-card 裡、手機字太小，是新問題還是全書既有的情況。
先跑 charts_judge_render.py（要用 render/full-measure.html 的 base 設定）。
"""
import html as H
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'render'
ROOT = HERE.parents[2]
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

SCRIPT = r"""
<script>
(function(){
  var rows=[];
  document.querySelectorAll('figure.chart').forEach(function(f){
    [].slice.call(f.querySelectorAll('svg')).filter(function(x){return getComputedStyle(x).display!=='none';}).forEach(function(svg){
      var vb=svg.viewBox.baseVal, w=svg.getBoundingClientRect().width, sc=w/vb.width;
      var fs=[].slice.call(svg.querySelectorAll('text')).map(function(t){return parseFloat(t.getAttribute('font-size')||'0');}).filter(Boolean);
      var mn=fs.length?Math.min.apply(null,fs):0;
      rows.push([f.getAttribute('data-chart'), svg.getAttribute('class'), Math.round(vb.width), Math.round(w), +sc.toFixed(2), mn, +(mn*sc).toFixed(1), !!f.closest('.data-card')]);
    });
  });
  parent.postMessage(JSON.stringify({w:window.innerWidth, rows:rows}),'*');
})();
</script>"""


def main():
    s = (ROOT / 'output' / 'full-v60-out.html').read_text(encoding='utf-8')
    base = '<base href="%s/">' % (ROOT / 'output').as_uri()
    page = s.replace('<head>', '<head>' + base, 1).replace('</body>', SCRIPT + '</body>', 1)
    inner = OUT / 'full-fontsize.html'
    inner.write_text(page, encoding='utf-8')
    res = {}
    for w in (390, 360):
        wp = OUT / ('wrap-fontsize-%d.html' % w)
        wp.write_text('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">'
                      "<script>window.addEventListener('message',function(e){var p=document.createElement('pre');p.id='relay';p.textContent=e.data;document.body.appendChild(p);});</script>"
                      '<iframe src="%s" width="%d" height="800" style="border:0"></iframe></body></html>' % (inner.as_uri(), w), encoding='utf-8')
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1000,900',
                            '--virtual-time-budget=8000', '--dump-dom', wp.as_uri()], capture_output=True, text=True, timeout=300)
        m = re.search(r'<pre id="relay">(.*?)</pre>', p.stdout, re.S)
        res[w] = json.loads(H.unescape(m.group(1))) if m else {'error': p.stderr[-1000:]}
    (OUT / 'mobile-fontsize.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for w, r in res.items():
        print('== 視窗', w)
        print('   chart, svg, viewBox寬, 實際寬, 縮放, 最小font-size, 實際px, 在data-card裡')
        for row in r.get('rows', []):
            print('  ', row)


if __name__ == '__main__':
    main()
