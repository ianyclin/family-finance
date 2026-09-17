#!/usr/bin/env python3
"""圖表裡判：用 headless Chrome 實際排版 output/full-v60-out.html，量兩張新圖的 SVG 元素有沒有重疊、超框。

只讀 output/；產物全部寫在本資料夾（verify3/render/）。
1. 整份 full-v60-out.html 複製一份，</body> 前插量測腳本，--dump-dom 讀結果（桌面 1280、手機 390）。
2. 另做一頁只含兩張圖（連同所在的卡片），截圖給人眼看（桌面、手機、深色）。
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / 'output' / 'full-v60-out.html'
OUT = HERE / 'render'
OUT.mkdir(exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
IDS = ['country-recovery', 'rebalance-drift']

MEASURE = r"""
<script>
(function(){
  function inter(a,b){var x=Math.max(0,Math.min(a.x2,b.x2)-Math.max(a.x1,b.x1));var y=Math.max(0,Math.min(a.y2,b.y2)-Math.max(a.y1,b.y1));return x*y;}
  function bb(el){var b=el.getBBox();return {x1:b.x,y1:b.y,x2:b.x+b.width,y2:b.y+b.height};}
  function segHitsBox(p,q,box,pad){ // 取樣
    for(var t=0;t<=1.0001;t+=0.02){var x=p[0]+(q[0]-p[0])*t,y=p[1]+(q[1]-p[1])*t;
      if(x>=box.x1-pad&&x<=box.x2+pad&&y>=box.y1-pad&&y<=box.y2+pad) return [x,y];}
    return null;}
  var res={viewport:[window.innerWidth,window.innerHeight],docScrollWidth:document.documentElement.scrollWidth,figs:{}};
  IDS.forEach(function(id){
    var fig=document.querySelector('figure[data-chart="'+id+'"]');
    if(!fig){res.figs[id]='missing';return;}
    var fr=fig.getBoundingClientRect();
    var r={figure_width:fr.width, figure_right:fr.right, svgs:[]};
    fig.querySelectorAll('svg').forEach(function(svg){
      var cs=getComputedStyle(svg); if(cs.display==='none') return;
      var vb=svg.viewBox.baseVal; var sr=svg.getBoundingClientRect();
      var o={cls:svg.getAttribute('class'),viewBox:[vb.width,vb.height],rendered:[sr.width,sr.height],scale:sr.width/vb.width,
             out_of_viewbox:[],text_text_overlap:[],text_mark_overlap:[],text_line_overlap:[]};
      var texts=[].slice.call(svg.querySelectorAll('text')).map(function(t){return {s:t.textContent,b:bb(t)};});
      texts.forEach(function(t){var b=t.b; if(b.x1<-0.5||b.y1<-0.5||b.x2>vb.width+0.5||b.y2>vb.height+0.5) o.out_of_viewbox.push([t.s,b]);});
      for(var i=0;i<texts.length;i++)for(var j=i+1;j<texts.length;j++){var a=inter(texts[i].b,texts[j].b); if(a>0.5) o.text_text_overlap.push([texts[i].s,texts[j].s,a.toFixed(1)]);}
      var marks=[].slice.call(svg.querySelectorAll('rect,circle')).map(function(m){return {tag:m.tagName+(m.getAttribute('fill')||''),b:bb(m)};});
      texts.forEach(function(t){marks.forEach(function(m){
        if(m.tag.indexOf('amber')>=0) return; // 門檻帶是背景色塊，文字壓在上面是設計
        var a=inter(t.b,m.b); if(a>0.5) o.text_mark_overlap.push([t.s,m.tag,a.toFixed(1)]);});});
      var polys=[].slice.call(svg.querySelectorAll('polyline')).filter(function(p){return (p.getAttribute('stroke')||'').indexOf('accent')>=0;});
      polys.forEach(function(p){
        var pts=p.getAttribute('points').trim().split(/\s+/).map(function(s){return s.split(',').map(Number);});
        var sw=parseFloat(p.getAttribute('stroke-width')||'1')/2;
        texts.forEach(function(t){
          for(var k=0;k+1<pts.length;k++){var h=segHitsBox(pts[k],pts[k+1],t.b,sw); if(h){o.text_line_overlap.push([t.s,h.map(function(v){return +v.toFixed(1);})]);break;}}
        });
      });
      // 引線與文字
      [].slice.call(svg.querySelectorAll('line')).forEach(function(l){
        if((l.getAttribute('stroke')||'').indexOf('muted')<0) return;
        var p=[+l.getAttribute('x1'),+l.getAttribute('y1')],q=[+l.getAttribute('x2'),+l.getAttribute('y2')];
        texts.forEach(function(t){var h=segHitsBox(p,q,t.b,0); if(h) o.text_line_overlap.push(['引線:'+t.s,h]);});
      });
      // 最小間距（文字與點、文字與折線）
      var gaps=[];
      texts.forEach(function(t){marks.forEach(function(m){ if(m.tag.indexOf('circle')!==0) return;
        var dx=Math.max(0,m.b.x1-t.b.x2,t.b.x1-m.b.x2), dy=Math.max(0,m.b.y1-t.b.y2,t.b.y1-m.b.y2);
        gaps.push([t.s,'circle',+Math.hypot(dx,dy).toFixed(1)]);});});
      polys.forEach(function(p){
        var pts=p.getAttribute('points').trim().split(/\s+/).map(function(s){return s.split(',').map(Number);});
        var sw=parseFloat(p.getAttribute('stroke-width')||'1')/2;
        texts.forEach(function(t){ var best=1e9;
          for(var k=0;k+1<pts.length;k++){for(var u=0;u<=1.0001;u+=0.02){var x=pts[k][0]+(pts[k+1][0]-pts[k][0])*u,y=pts[k][1]+(pts[k+1][1]-pts[k][1])*u;
            var dx=Math.max(0,t.b.x1-x,x-t.b.x2),dy=Math.max(0,t.b.y1-y,y-t.b.y2); best=Math.min(best,Math.hypot(dx,dy)-sw);}}
          gaps.push([t.s,'line',+best.toFixed(1)]);});
      });
      o.tight_gaps_under_3=gaps.filter(function(g){return g[2]<3;});
      o.texts=texts.map(function(t){return [t.s,+t.b.x1.toFixed(1),+t.b.y1.toFixed(1),+t.b.x2.toFixed(1),+t.b.y2.toFixed(1)];});
      r.svgs.push(o);
    });
    // 圖例、note、figcaption 有沒有超出圖框
    r.children_overflow=[].slice.call(fig.querySelectorAll('.legend li, p.note, figcaption, .chart-head span')).filter(function(e){var b=e.getBoundingClientRect();return b.right>fr.right+0.5||b.left<fr.left-0.5;}).map(function(e){return e.textContent.slice(0,30);});
    res.figs[id]=r;
  });
  var pre=document.createElement('pre'); pre.id='judge-result'; pre.textContent=JSON.stringify(res); document.body.appendChild(pre);
})();
</script>
""".replace('IDS', json.dumps(IDS))


def run_dump(html_path, w, h, dark=False):
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=%d,%d' % (w, h),
           '--virtual-time-budget=4000', '--dump-dom', html_path.as_uri()]
    if dark:
        cmd.insert(3, '--force-dark-mode')
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    m = re.search(r'<pre id="judge-result">(.*?)</pre>', p.stdout, re.S)
    if not m:
        return {'error': p.stderr[-2000:]}
    import html as H
    return json.loads(H.unescape(m.group(1)))


def main():
    s = SRC.read_text(encoding='utf-8')
    base = '<base href="%s/">' % (ROOT / 'output').as_uri()
    page = s.replace('<head>', '<head>' + base, 1).replace('</body>', MEASURE + '</body>', 1)
    full = OUT / 'full-measure.html'
    full.write_text(page, encoding='utf-8')
    results = {}
    for name, (w, h) in {'desktop1280': (1280, 900), 'tablet700': (700, 900), 'mobile390': (390, 844), 'mobile360': (360, 800)}.items():
        results[name] = run_dump(full, w, h)
    (OUT / 'measure.json').write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf-8')

    # 截圖頁：head＋兩張圖所在的卡片或段落
    head = s[:s.find('</head>')]
    parts = []
    for cid in IDS:
        i = s.find('<figure class="chart" data-chart="%s">' % cid)
        j = s.find('</figure>', i) + len('</figure>')
        parts.append('<section class="part"><h3>%s</h3>%s</section>' % (cid, s[i:j]))
    shot = head + base + '</head><body><main>' + '\n'.join(parts) + '</main></body></html>'
    sp = OUT / 'figs-only.html'
    sp.write_text(shot, encoding='utf-8')
    for name, (w, h), dark in (('desktop', (1280, 2000), False), ('mobile390', (390, 2600), False), ('mobile390-dark', (390, 2600), True), ('desktop-dark', (1280, 2000), True)):
        png = OUT / ('figs-%s.png' % name)
        cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=%d,%d' % (w, h),
               '--screenshot=%s' % png, sp.as_uri()]
        if dark:
            cmd.insert(3, '--force-dark-mode')
            cmd.insert(3, '--blink-settings=preferredColorScheme=0')
        subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
