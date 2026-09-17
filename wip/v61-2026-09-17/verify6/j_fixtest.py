import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
p,ws=cdp.start()
try:
    ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
    cdp.load(ws,R+"output/full-v60-out.html")
    ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=True)
    ws.call("Page.reload"); time.sleep(3)
    print(cdp.ev(ws,r"""(function(){var s=document.createElement('style');s.textContent='@media screen and (pointer:coarse){.table-wrap:has(>table.situations){overflow-x:clip}}';document.head.appendChild(s);
    var w=document.querySelector('.table-wrap:has(>table.situations)');w.scrollLeft=100;var a=[].filter.call(w.querySelectorAll('a.xref'),function(x){return x.textContent==='5'})[0];a.scrollIntoView({block:"center"});var r=a.getBoundingClientRect();
    return JSON.stringify({ov:getComputedStyle(w).overflowX,oy:getComputedStyle(w).overflowY,scrollLeft:w.scrollLeft,hit5:[Math.round(r.width),Math.round(r.height)]})})()"""))
finally:
    p.kill()
