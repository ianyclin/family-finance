import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
p,ws=cdp.start()
try:
    cdp.load(ws,R+"output/full-v60-out.html")
    ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=False)
    ws.call("Page.reload"); time.sleep(3)
    print(cdp.ev(ws,r"""(function(){var vw=document.documentElement.clientWidth;var out=[];[].forEach.call(document.querySelectorAll('body *'),function(e){var r=e.getBoundingClientRect();if(r.right>vw+1&&!e.closest('.table-wrap')&&!e.closest('svg')){var inner=[].some.call(e.children,function(c){return c.getBoundingClientRect().right>vw+1});if(!inner)out.push([e.tagName,(e.closest('section')||{}).id,Math.round(r.right),e.textContent.slice(0,60)]);}});return JSON.stringify({vw:vw,sw:document.documentElement.scrollWidth,items:out.slice(0,10)})})()"""))
finally:
    p.kill()
