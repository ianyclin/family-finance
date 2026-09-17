import sys, time, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import start, ev, shot
URL = "file:///Users/linyenchu/Cladue%20Code/family-finance/guide/index.html"
p, ws = start(9373)
try:
    ws.call("Page.enable"); ws.call("Page.navigate", url=URL); time.sleep(3)
    out = []
    for target, filt in (('s13-crash', '想控制'), ('s13-loss', '怕晚'), ('s13-envy', '怕賠'), ('s13-bored', '怕輸人')):
        ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"%s\"]').click()" % filt)
        ev(ws, "(function(){var a=document.querySelector('#group-situations a[href=\"#%s\"]');a.scrollIntoView({block:'center',behavior:'instant'});})()" % target)
        time.sleep(1.2)
        pos = ev(ws, "(function(){var a=document.querySelector('#group-situations a[href=\"#%s\"]');var r=a.getClientRects()[0];var x=r.left+Math.min(8,r.width/2),y=r.top+r.height/2;var e=document.elementFromPoint(x,y);return [x,y,a.textContent,e===a||a.contains(e),a.getClientRects().length,e&&e.outerHTML.slice(0,80)]})()" % target)
        for t in ('mousePressed', 'mouseReleased'):
            ws.call("Input.dispatchMouseEvent", type=t, x=pos[0], y=pos[1], button='left', clickCount=1)
        time.sleep(1.5)
        st = ev(ws, "(function(){var t=document.getElementById('%s');return [getComputedStyle(t).display!=='none'&&t.getClientRects().length>0, Array.from(document.querySelectorAll('[data-s13-filter] button')).filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent), location.hash, Math.round(t.getBoundingClientRect().top), document.querySelectorAll('[data-s13-hidden]').length]})()" % target)
        out.append([target, filt, pos, st])
    print(json.dumps(out, ensure_ascii=False))
finally:
    p.terminate()
