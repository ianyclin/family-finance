import sys, time, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import start, ev, shot
OUT = os.path.dirname(os.path.abspath(__file__))
URL = "file:///Users/linyenchu/Cladue%20Code/family-finance/guide/index.html"
p, ws = start(9371)
try:
    ws.call("Page.enable")
    ws.call("Page.navigate", url=URL)
    time.sleep(3)
    res = {}
    res['buttons'] = ev(ws, "Array.from(document.querySelectorAll('[data-s13-filter] button')).map(b=>[b.textContent,b.getAttribute('aria-pressed'),Math.round(b.getBoundingClientRect().top),Math.round(b.getBoundingClientRect().right)])")
    res['bar_count'] = ev(ws, "document.querySelectorAll('[data-s13-filter]').length")
    res['docW'] = ev(ws, "[document.documentElement.scrollWidth, innerWidth]")
    # group map: for each h3 in s13 whose text starts with name + '（'
    setup = r"""
    window.__names=['怕晚','怕錯過','怕賠','怕輸人','無聊','想控制'];
    window.__groups=function(){var sec=document.getElementById('s13');var g={};
      Array.from(sec.querySelectorAll('h3')).forEach(function(h){var t=h.textContent.replace(/\s+/g,'');
        __names.forEach(function(n){var ol=h.nextElementSibling; if(t.indexOf(n+'（')===0&&ol&&ol.tagName==='OL') g[n]=[h,ol];});});return g;};
    window.__vis=function(el){return getComputedStyle(el).display!=='none' && el.getClientRects().length>0;};
    window.__state=function(){var g=__groups();var o={};__names.forEach(function(n){o[n]=[__vis(g[n][0]),__vis(g[n][1]),g[n][1].querySelectorAll(':scope>li').length];});
      o.pressed=Array.from(document.querySelectorAll('[data-s13-filter] button')).filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent);
      o.hiddenCount=document.querySelectorAll('[data-s13-hidden]').length; return o;};
    true
    """
    ev(ws, setup)
    res['group_headings'] = ev(ws, "(function(){var g=__groups();return __names.map(n=>[n,g[n]?g[n][0].textContent:null,g[n]?g[n][0].id:null,g[n]?g[n][1].querySelectorAll(':scope>li').length:0])})()")
    res['initial'] = ev(ws, "__state()")
    # non-group visible parts of s13 (for info)
    per = {}
    for w in ['怕晚', '怕錯過', '怕賠', '怕輸人', '無聊', '想控制', '全部']:
        ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"%s\"]').click()" % w)
        time.sleep(0.15)
        st = ev(ws, "__state()")
        ok = True
        for n in ['怕晚', '怕錯過', '怕賠', '怕輸人', '無聊', '想控制']:
            want = (w == '全部' or w == n)
            if st[n][0] != want or st[n][1] != want:
                ok = False
        if st['pressed'] != [w]:
            ok = False
        per[w] = {'ok': ok, 'state': st}
    res['per_button'] = per
    # visible question numbers per filter (li values)
    # screenshot of bar with 怕輸人 pressed and 無聊 pressed
    ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"無聊\"]').click(); document.querySelector('[data-s13-filter]').scrollIntoView({block:'start'})")
    shot(ws, os.path.join(OUT, 'v7-filter-bored.png'))
    ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"全部\"]').click()")
    # links into group targets
    links = ev(ws, r"""(function(){var g=__groups();var els=[];__names.forEach(n=>els.push(g[n][0],g[n][1]));
      function grp(t){for(var n of __names){if(g[n][0]===t||g[n][1].contains(t)||g[n][0].contains(t))return n;}return null;}
      return Array.from(document.querySelectorAll('a[href^="#"]')).map(function(a,i){var id=decodeURIComponent(a.getAttribute('href').slice(1));var t=id&&document.getElementById(id);
        if(!t)return null; var sec=a.closest('section'); return [i,id,grp(t),sec?sec.id:null,a.textContent.trim().slice(0,30)];}).filter(x=>x&&x[2]);})()""")
    res['links_into_groups'] = links
    fails = []
    checks = 0
    for (i, id_, grp, secid, txt) in links:
        for w in ['怕晚', '怕錯過', '怕賠', '怕輸人', '無聊', '想控制']:
            if w == grp:
                continue
            ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"%s\"]').click()" % w)
            ev(ws, "document.querySelectorAll('a[href^=\"#\"]')[%d].click()" % i)
            time.sleep(0.05)
            r = ev(ws, "(function(){var t=document.getElementById(%s);return [!t.closest('[data-s13-hidden]'), __vis(t), __state().pressed, location.hash]})()" % json.dumps(id_))
            checks += 1
            if not (r[0] and r[1] and r[2] == ['全部']):
                fails.append([i, id_, grp, secid, w, r])
    res['link_checks'] = checks
    res['link_fails'] = fails
    # hashchange path
    hfails = []
    for (i, id_, grp, secid, txt) in links:
        w = '怕晚' if grp != '怕晚' else '無聊'
        ev(ws, "location.hash='#top-dummy-%d'" % i)
        time.sleep(0.1)
        ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"%s\"]').click()" % w)
        ev(ws, "location.hash=%s" % json.dumps('#' + id_))
        time.sleep(0.25)
        r = ev(ws, "(function(){var t=document.getElementById(%s);return [__vis(t), __state().pressed, Math.round(t.getBoundingClientRect().top)]})()" % json.dumps(id_))
        if not (r[0] and r[1] == ['全部']):
            hfails.append([id_, w, r])
    res['hash_fails'] = hfails
    # real mouse click on situations index link to #s13-drop20 while 怕輸人 pressed
    ev(ws, "document.querySelector('[data-s13-filter] button[data-which=\"怕輸人\"]').click()")
    pos = ev(ws, r"""(function(){var a=document.querySelector('#group-situations a[href="#s13-drop20"]')||document.querySelector('a[href="#s13-drop20"]');a.scrollIntoView({block:'center'});var b=a.getBoundingClientRect();return [b.left+b.width/2,b.top+b.height/2,a.closest('section').id,a.textContent]})()""")
    time.sleep(0.3)
    for t in ('mousePressed', 'mouseReleased'):
        ws.call("Input.dispatchMouseEvent", type=t, x=pos[0], y=pos[1], button='left', clickCount=1)
    time.sleep(0.6)
    res['real_click'] = [pos, ev(ws, "(function(){var t=document.getElementById('s13-drop20');return [__vis(t),__state().pressed,location.hash,Math.round(t.getBoundingClientRect().top)]})()")]
    shot(ws, os.path.join(OUT, 'v7-after-situation-click.png'))
    # page load directly with hash
    ws.call("Page.navigate", url=URL + "#s13-envy")
    time.sleep(2.5)
    ev(ws, setup)
    res['load_with_hash'] = ev(ws, "(function(){var t=document.getElementById('s13-envy');return [__vis(t),__state().pressed,Math.round(t.getBoundingClientRect().top)]})()")
    res['console_errors'] = None
    print(json.dumps(res, ensure_ascii=False, indent=1))
finally:
    p.terminate()
