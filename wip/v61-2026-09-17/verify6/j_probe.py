import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
p,ws=cdp.start()
try:
    R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
    ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
    cdp.load(ws,R+"output/full-v60-out.html")
    ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=2,mobile=True)
    ws.call("Page.reload"); time.sleep(2.5)
    print(cdp.ev(ws,"JSON.stringify({coarse:matchMedia('(pointer:coarse)').matches, anyc:matchMedia('(any-pointer:coarse)').matches, hoverNone:matchMedia('(hover:none)').matches, w:innerWidth, sw:document.documentElement.scrollWidth})"))
finally:
    p.kill()
