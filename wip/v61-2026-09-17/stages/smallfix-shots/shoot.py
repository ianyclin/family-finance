import sys,time,json,base64,os
sys.path.insert(0,'/Users/linyenchu/Cladue Code/family-finance/wip/v61-2026-09-17/verify5')
from cdp import start, ev
OUT=os.path.dirname(os.path.abspath(__file__))
p,ws=start(9341)
ws.call("Page.enable")
ws.call("Page.navigate",url="file:///Users/linyenchu/Cladue%20Code/family-finance/guide/index.html")
time.sleep(3)
def clip(sel,name,maxh=2400,pre=""):
    r=ev(ws,pre+"(function(){var e=document.querySelector(%s);e.scrollIntoView();var b=e.getBoundingClientRect();return [b.left+scrollX,b.top+scrollY,b.width,b.height]})()"%json.dumps(sel))
    time.sleep(0.5)
    x,y,w,h=r
    d=ws.call("Page.captureScreenshot",format="png",captureBeyondViewport=True,clip=dict(x=0,y=y-10,width=400,height=min(h+20,maxh),scale=1))["data"]
    open(os.path.join(OUT,name),"wb").write(base64.b64decode(d)); print(name,r)
W='#s11 details[data-print="open"]:not([data-lite-alt])'
ev(ws,"document.querySelector(%s).open=true"%json.dumps(W))
clip(W+'>.table-wrap','t1-fields-top.png',1400)
print(ev(ws,"(function(){var t=document.querySelector(%s);return [t.scrollWidth,t.clientWidth,getComputedStyle(t,'::before').content, document.documentElement.scrollWidth]})()"%json.dumps(W+'>.table-wrap')))
# rest of table
r=ev(ws,"(function(){var b=document.querySelector(%s).getBoundingClientRect();return [b.top+scrollY,b.height]})()"%json.dumps(W+'>.table-wrap'))
d=ws.call("Page.captureScreenshot",format="png",captureBeyondViewport=True,clip=dict(x=0,y=r[0]+1390,width=400,height=min(r[1]-1390,2400),scale=1))["data"]
open(os.path.join(OUT,'t1-fields-rest.png'),"wb").write(base64.b64decode(d))
clip('[data-s13-filter]','t2-filter-bar.png',400)
print(ev(ws,"Array.from(document.querySelectorAll('[data-s13-filter] button')).map(b=>b.textContent+':'+b.getAttribute('aria-pressed')+':'+Math.round(b.getBoundingClientRect().top))"))
# click 怕輸人, then simulate xref to s13-drop20 (in 怕賠) -> should switch to 全部
ev(ws,"document.querySelector('[data-s13-filter] button[data-which=\"怕輸人\"]').click()")
print('after 怕輸人', ev(ws,"Array.from(document.querySelectorAll('#s13 h3')).filter(h=>getComputedStyle(h).display!='none').map(h=>h.textContent)"))
clip('[data-s13-filter]','t2-filter-pressed.png',700)
ev(ws,"var a=document.createElement('a');a.href='#s13-drop20';a.textContent='x';document.body.appendChild(a);a.click()")
time.sleep(0.5)
print('after link', ev(ws,"Array.from(document.querySelectorAll('[data-s13-filter] button')).map(b=>b.textContent+':'+b.getAttribute('aria-pressed'))"), ev(ws,"document.querySelectorAll('[data-s13-hidden]').length"))
clip('#group-life ol.part-map + p.small','t5-group-life.png',400)
p.terminate()
