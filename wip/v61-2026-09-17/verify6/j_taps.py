import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
JS=r"""(function(){
 document.documentElement.style.scrollBehavior='auto';
 var res={coarse:matchMedia('(pointer:coarse)').matches,vw:innerWidth,sw:document.documentElement.scrollWidth};
 var wraps=[].map.call(document.querySelectorAll('.table-wrap'),function(w){var t=w.querySelector('table');return [t?t.className:'',(w.closest('section')||{}).id,w.scrollWidth-w.clientWidth]}).filter(function(x){return x[2]>0});
 res.overWraps=wraps;
 var as=[].filter.call(document.querySelectorAll('a[href]'),function(a){return a.getClientRects().length>0});
 var stolen=[],n=0;
 as.forEach(function(a){
   var rg=document.createRange();rg.selectNodeContents(a);var rs=rg.getClientRects();
   if(!rs.length)return;
   var r0=rs[0];window.scrollTo(0,r0.top+scrollY-200);
   [].forEach.call(rg.getClientRects(),function(r){
     [0.15,0.5,0.85].forEach(function(fx){
       var x=r.left+r.width*fx,y=r.top+r.height/2; if(x<0||x>=innerWidth||y<0||y>=innerHeight)return;
       n++;var e=document.elementFromPoint(x,y);var got=e&&e.closest&&e.closest('a');
       if(got!==a){stolen.push([a.textContent.slice(0,10),got?got.textContent.slice(0,10):(e?e.tagName:null),fx,(a.closest('section')||{}).id]);}
     });
   });
 });
 res.points=n;res.stolenCount=stolen.length;res.stolen=stolen.slice(0,40);
 return JSON.stringify(res);})()"""
out={}
p,ws=cdp.start()
try:
    for name,url in (("before",R+"wip/v61-2026-09-17/stages/polish-before.html"),("after",R+"output/full-v60-out.html")):
        ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
        cdp.load(ws,url)
        ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=False)
        ws.call("Page.reload"); time.sleep(3)
        out[name]=json.loads(cdp.ev(ws,JS))
        if name=="after":
            cdp.ev(ws,"(function(){var s=document.createElement('style');s.textContent='a.xref{padding:0!important;margin:0!important}';document.head.appendChild(s);return 1})()")
            time.sleep(0.5)
            out["after_nopad"]=json.loads(cdp.ev(ws,JS))
finally:
    p.kill()
json.dump(out,open('j_taps_result.json','w'),ensure_ascii=False,indent=0)
for k,v in out.items():
    print(k,'coarse',v['coarse'],'vw',v['vw'],'sw',v['sw'],'points',v['points'],'stolen',v['stolenCount'])
    print('  overWraps',v['overWraps'])
    print('  stolen sample',v['stolen'][:25])
