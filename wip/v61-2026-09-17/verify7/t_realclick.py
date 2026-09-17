import sys, time, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import start, ev, shot
OUT = os.path.dirname(os.path.abspath(__file__))
URL = "file:///Users/linyenchu/Cladue%20Code/family-finance/guide/index.html"
p, ws = start(9372)
try:
    ws.call("Page.enable"); ws.call("Page.navigate", url=URL); time.sleep(3)
    out = []
    for target, filt in (('s13-drop20', '怕輸人'), ('s13-crash', '想控制'), ('s13-control', '怕賠'), ('s13-miss', '無聊')):
        ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"%s\"]').click()" % filt)
        ev(ws, "(function(){var a=document.querySelector('#group-situations a[href=\"#%s\"]');a.scrollIntoView({block:'center',behavior:'instant'});})()" % target)
        time.sleep(1.2)
        pos = ev(ws, "(function(){var a=document.querySelector('#group-situations a[href=\"#%s\"]');var b=a.getBoundingClientRect();var e=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);return [b.left+b.width/2,b.top+b.height/2,a.textContent,e===a||a.contains(e)]})()" % target)
        for t in ('mousePressed', 'mouseReleased'):
            ws.call("Input.dispatchMouseEvent", type=t, x=pos[0], y=pos[1], button='left', clickCount=1)
        time.sleep(1.5)
        st = ev(ws, "(function(){var t=document.getElementById('%s');return [getComputedStyle(t).display!=='none'&&t.getClientRects().length>0, Array.from(document.querySelectorAll('[data-s13-filter] button')).filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent), location.hash, Math.round(t.getBoundingClientRect().top), document.querySelectorAll('[data-s13-hidden]').length]})()" % target)
        out.append([target, filt, pos, st])
        if target == 's13-drop20':
            shot(ws, os.path.join(OUT, 'v7-real-click-drop20.png'))
    print(json.dumps(out, ensure_ascii=False, indent=1))
finally:
    p.terminate()
