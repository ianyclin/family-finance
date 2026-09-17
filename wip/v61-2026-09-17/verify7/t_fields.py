import sys, time, json, os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import start, ev
OUT = os.path.dirname(os.path.abspath(__file__))
AFTER = "file:///Users/linyenchu/Cladue%20Code/family-finance/guide/index.html"
BEFORE = "file:///Users/linyenchu/Cladue%20Code/family-finance/wip/v61-2026-09-17/stages/smallfix-before.html"
SEL = '#s11 details[data-print="open"]:not([data-lite-alt])>.table-wrap>table'
PROBE = r"""(function(){
 var S=%s; var tabs=document.querySelectorAll(S); var t=tabs[0]; var w=t.parentNode; var d=w.parentNode; d.open=true;
 var rows=Array.from(t.querySelectorAll('tbody>tr'));
 var tdcounts=rows.map(r=>r.children.length);
 var spans=t.querySelectorAll('[rowspan],[colspan]').length;
 var ths=Array.from(t.querySelectorAll('thead th')).map(x=>x.textContent.trim());
 var beforeLabels=[1,2,3,4].map(i=>{var c=t.querySelector('tbody>tr>td:nth-child('+i+')');return getComputedStyle(c,'::before').content;});
 var empties=Array.from(t.querySelectorAll('tbody td')).filter(c=>c.textContent.trim()===''&&c.children.length===0);
 var emptyNotMatched=Array.from(t.querySelectorAll('tbody td')).filter(c=>c.textContent.trim()===''&&!c.matches(':empty')).length;
 var overflow=Array.from(t.querySelectorAll('tbody td')).filter(c=>c.scrollWidth>c.clientWidth+1).length;
 var nonfirstEmpty=Array.from(t.querySelectorAll('tbody td:not(:nth-child(1))')).filter(c=>c.textContent.trim()==='').length;
 return {matches:tabs.length, allTables_in_s11:document.querySelectorAll('#s11 table').length, rows:rows.length, tdcounts:[...new Set(tdcounts)], spans:spans, ths:ths,
  theadDisplay:getComputedStyle(t.querySelector('thead')).display, tdDisplay:getComputedStyle(t.querySelector('tbody td')).display,
  beforeLabels:beforeLabels, emptyCells:empties.length, emptyDisplay:empties.map(c=>getComputedStyle(c).display).filter((v,i,a)=>a.indexOf(v)===i), emptyNotMatched:emptyNotMatched, nonfirstEmpty:nonfirstEmpty,
  overflowCells:overflow, wrapScroll:[w.scrollWidth,w.clientWidth], wrapBefore:getComputedStyle(w,'::before').content, docScroll:[document.documentElement.scrollWidth,innerWidth],
  tableH:Math.round(t.getBoundingClientRect().height), firstTdFont:getComputedStyle(t.querySelector('tbody td')).fontSize,
  otherWrapBefore: Array.from(document.querySelectorAll('.table-wrap')).filter(x=>x!==w).slice(0,3).map(x=>getComputedStyle(x,'::before').content)};
})()"""
p, ws = start(9374)
res = {}
try:
    ws.call("Page.enable")
    for name, url in (('after', AFTER), ('before', BEFORE)):
        ws.call("Page.navigate", url=url); time.sleep(3)
        for wdt in (360, 400, 660, 661, 900):
            ws.call("Emulation.setDeviceMetricsOverride", width=wdt, height=800, deviceScaleFactor=2, mobile=wdt < 700)
            time.sleep(0.6)
            res['%s-%d' % (name, wdt)] = ev(ws, PROBE % json.dumps(SEL))
        # print media at 900
        ws.call("Emulation.setDeviceMetricsOverride", width=794, height=1123, deviceScaleFactor=1, mobile=False)
        ws.call("Emulation.setEmulatedMedia", media="print")
        time.sleep(0.6)
        res['%s-print794' % name] = ev(ws, PROBE % json.dumps(SEL))
        ws.call("Emulation.setDeviceMetricsOverride", width=400, height=800, deviceScaleFactor=2, mobile=True)
        time.sleep(0.6)
        res['%s-print400' % name] = ev(ws, PROBE % json.dumps(SEL))
        ws.call("Emulation.setEmulatedMedia", media="")
    # screenshots of after at 400
    ws.call("Page.navigate", url=AFTER); time.sleep(3)
    ws.call("Emulation.setDeviceMetricsOverride", width=400, height=800, deviceScaleFactor=2, mobile=True)
    time.sleep(0.8)
    r = ev(ws, "(function(){var t=document.querySelector(%s);t.parentNode.parentNode.open=true;var b=t.parentNode.getBoundingClientRect();return [b.top+scrollY-40,b.height+60]})()" % json.dumps(SEL))
    y, h = r; part = 0
    while h > 0 and part < 6:
        hh = min(h, 1500)
        d = ws.call("Page.captureScreenshot", format="png", captureBeyondViewport=True, clip=dict(x=0, y=y, width=400, height=hh, scale=1))["data"]
        open(os.path.join(OUT, 'v7-fields-400-%d.png' % part), 'wb').write(base64.b64decode(d))
        y += hh; h -= hh; part += 1
    res['shots'] = part
    print(json.dumps(res, ensure_ascii=False, indent=1))
finally:
    p.terminate()
