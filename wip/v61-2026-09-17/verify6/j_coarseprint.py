import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
p,ws=cdp.start()
try:
    ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
    cdp.load(ws,R+"output/full-v60-out.html")
    ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=False)
    ws.call("Page.reload"); time.sleep(3)
    ws.call("Emulation.setEmulatedMedia",media="print")
    time.sleep(0.5)
    print(cdp.ev(ws,"(function(){var a=document.querySelector('table.situations a.xref');var cs=getComputedStyle(a);return JSON.stringify({coarse:matchMedia('(pointer:coarse)').matches,print:matchMedia('print').matches,td:cs.textDecorationLine+' '+cs.textDecorationStyle,pad:cs.paddingLeft,ml:cs.marginLeft,bb:cs.borderBottomStyle,color:cs.color})})()"))
    ws.call("Emulation.setTouchEmulationEnabled",enabled=False)
    ws.call("Page.reload"); time.sleep(3)
    ws.call("Emulation.setEmulatedMedia",media="print"); time.sleep(0.5)
    print(cdp.ev(ws,"(function(){var a=document.querySelector('table.situations a.xref');var cs=getComputedStyle(a);return JSON.stringify({coarse:matchMedia('(pointer:coarse)').matches,print:matchMedia('print').matches,td:cs.textDecorationLine+' '+cs.textDecorationStyle,pad:cs.paddingLeft,ml:cs.marginLeft,bb:cs.borderBottomStyle})})()"))
finally:
    p.kill()
