import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
p,ws=cdp.start()
try:
    ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
    cdp.load(ws,R+"output/full-v60-out.html")
    ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=True)
    ws.call("Page.reload"); time.sleep(3)
    print(cdp.ev(ws,r"""(function(){var out=[];[].forEach.call(document.querySelectorAll('.table-wrap'),function(w){var over=w.scrollWidth-w.clientWidth;if(over<=0)return;var wr=w.getBoundingClientRect();var tb=w.querySelector('table').getBoundingClientRect();
      var culprits=[].filter.call(w.querySelectorAll('a.xref'),function(a){return [].some.call(a.getClientRects(),function(r){return r.right>wr.right-1})}).map(function(a){return a.textContent.slice(0,12)+'@'+(a.closest('tr')?[].indexOf.call(a.closest('tr').parentNode.children,a.closest('tr')):'')});
      out.push({cls:w.querySelector('table').className,sec:(w.closest('section')||{}).id,over:over,tableW:Math.round(tb.width),wrapW:Math.round(wr.width),culprits:culprits});});
     w=document.querySelector('.table-wrap:has(>table.situations)');w.scrollLeft=100;out.push({situationsScrollLeftAfterSet:w.scrollLeft});return JSON.stringify(out)})()"""))
finally:
    p.kill()
