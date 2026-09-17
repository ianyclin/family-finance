import sys,time,json
sys.path.insert(0,'.')
from cdp import *
URL="file:///Users/linyenchu/Cladue%20Code/family-finance/output/full-v60-out.html"
p,ws=start()
ws.call("Page.enable")
def go(frag=""):
    ws.call("Page.navigate",url=URL+frag); time.sleep(2.5)
def click_link(text, within="document"):
    # scroll the link into view, report its position, click via real mouse event
    r=ev(ws,f"""(()=>{{const as=[...{within}.querySelectorAll('a,summary')].filter(a=>a.textContent.includes({json.dumps(text)}) && a.offsetParent!==null);
      if(!as.length) return null; const a=as[0]; a.scrollIntoView({{block:'center',behavior:'instant'}}); return 1}})()""")
    if not r: print("NOT FOUND",text); return None
    time.sleep(0.6)
    r=ev(ws,f"""(()=>{{const as=[...{within}.querySelectorAll('a,summary')].filter(a=>a.textContent.includes({json.dumps(text)}) && a.offsetParent!==null);
      const a=as[0]; const b=a.getBoundingClientRect();
      return {{x:b.left+Math.min(b.width/2,30),y:b.top+Math.min(b.height/2,12),href:a.getAttribute('href'),n:as.length,t:a.textContent.slice(0,60)}}}})()""")
    if not r: print("NOT FOUND",text); return None
    time.sleep(0.3)
    ev(ws,f"""(()=>{{const as=[...{within}.querySelectorAll('a,summary')].filter(a=>a.textContent.includes({json.dumps(text)}) && a.offsetParent!==null); as[0].click();}})()""")
    time.sleep(2.0); print("clicked",r); return r
def where():
    return ev(ws,"""(()=>{const y=window.scrollY;const hs=[...document.querySelectorAll('h2,h3')].filter(h=>h.getBoundingClientRect().top<120);const h=hs[hs.length-1];
    return {scrollY:y,hash:location.hash,pageH:document.documentElement.scrollHeight,pageW:document.documentElement.scrollWidth,heading:h?h.textContent.slice(0,60):null}})()""")
def text_view(n=900):
    return ev(ws,f"""(()=>{{let out='';const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode()){{const e=x.parentElement;if(!e||!e.checkVisibility())continue;const r=x.parentElement.getBoundingClientRect();if(r.bottom>0&&r.top<800){{const s=x.textContent.trim();if(s)out+=s+' '}}}}return out.slice(0,{n})}})()""")
def scroll(dy):
    ev(ws,f"window.scrollBy(0,{dy})"); time.sleep(0.5)
def ypos(sel):
    return ev(ws,f"""(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return null; const r=e.getBoundingClientRect(); return Math.round(r.top+window.scrollY)}})()""")
def screens(a,b):
    ya,yb=ypos(a),ypos(b); return None if ya is None or yb is None else round((yb-ya)/800,1)
def to(sel,off=0):
    ev(ws,f"""(()=>{{const e=document.querySelector({json.dumps(sel)}); window.scrollTo({{top:e.getBoundingClientRect().top+window.scrollY+{off},behavior:'instant'}})}})()"""); time.sleep(0.6)
