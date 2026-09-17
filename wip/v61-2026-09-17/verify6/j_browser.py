import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
PAGES={"after":R+"output/full-v60-out.html","before":R+"wip/v61-2026-09-17/stages/polish-before.html","lite":R+"lite/index.html"}
out={}
LAYOUT=r"""(function(){
 document.documentElement.style.scrollBehavior='auto';
 var res={coarse:matchMedia('(pointer:coarse)').matches,innerWidth:innerWidth,scrollWidth:document.documentElement.scrollWidth};
 var tw=[].map.call(document.querySelectorAll('.table-wrap'),function(w,i){
   var t=w.querySelector('table'); var cs=getComputedStyle(w,'::before');
   return {i:i,cls:t?t.className:'',sec:(w.closest('section')||{}).id,over:w.scrollWidth-w.clientWidth,hint:cs.content,inDetailsClosed:!!(w.closest('details')&&!w.closest('details').open)};});
 res.tableWraps=tw;
 // xref sizes in situations table
 var sit=document.querySelector('table.situations');
 if(sit){res.sitLinks=[].map.call(sit.querySelectorAll('a'),function(a){var r=a.getBoundingClientRect();return [a.textContent.slice(0,12),Math.round(r.width),Math.round(r.height)];});}
 // overlapping link boxes (visible links only)
 var as=[].filter.call(document.querySelectorAll('a[href]'),function(a){return a.getClientRects().length>0});
 var boxes=[];as.forEach(function(a){[].forEach.call(a.getClientRects(),function(r){boxes.push([a,r.left+scrollX,r.top+scrollY,r.right+scrollX,r.bottom+scrollY]);});});
 boxes.sort(function(x,y){return x[2]-y[2]});
 var ov=[];for(var i=0;i<boxes.length;i++){for(var j=i+1;j<boxes.length&&boxes[j][2]<boxes[i][4];j++){var a=boxes[i],b=boxes[j];if(a[0]===b[0])continue;var w=Math.min(a[3],b[3])-Math.max(a[1],b[1]),h=Math.min(a[4],b[4])-Math.max(a[2],b[2]);if(w>0.5&&h>0.5)ov.push([a[0].textContent.slice(0,10),b[0].textContent.slice(0,10),Math.round(w),Math.round(h)]);}}
 res.overlapCount=ov.length;res.overlapSample=ov.slice(0,15);
 return JSON.stringify(res);})()"""
def setup(ws,url,w=400):
    ws.call("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
    cdp.load(ws,url)
    ws.call("Emulation.setDeviceMetricsOverride",width=w,height=800,deviceScaleFactor=1,mobile=True)
    ws.call("Page.reload"); time.sleep(3)
p,ws=cdp.start()
try:
    for k in ("before","after"):
        setup(ws,PAGES[k]); out["layout_"+k]=json.loads(cdp.ev(ws,LAYOUT))
    # filter tests on after
    setup(ws,PAGES["after"])
    FILT=r"""(async function(){
     document.documentElement.style.scrollBehavior='auto';
     var sec=document.getElementById('s13');var sleep=function(ms){return new Promise(function(r){setTimeout(r,ms)})};
     var links=[].filter.call(document.querySelectorAll('a[href^="#"]'),function(a){var id=decodeURIComponent(a.getAttribute('href').slice(1));var t=id&&document.getElementById(id);return t&&sec.contains(t)&&!sec.contains(a);});
     var res={nLinks:links.length,fails:[],checked:0,hiddenBefore:0,states:{}};
     var states=['怕晚','怕賠','想控制'];
     for(var s=0;s<states.length;s++){
      var st=states[s];var cnt=0,hid=0,fail=0;
      for(var i=0;i<links.length;i++){
        var a=links[i];if(a.getClientRects().length===0){continue;}
        document.querySelector('[data-s13-filter] button[data-which="'+st+'"]').click();
        var id=decodeURIComponent(a.getAttribute('href').slice(1));var t=document.getElementById(id);
        if(t.closest('[data-s13-hidden]'))hid++;
        a.scrollIntoView({block:'center'});await sleep(30);
        a.click();await sleep(120);
        var r=t.getBoundingClientRect();var ok=t.getClientRects().length>0&&Math.abs(r.top)<60;
        cnt++;if(!ok){fail++;res.fails.push({state:st,href:id,text:a.textContent.slice(0,15),top:Math.round(r.top),shown:t.getClientRects().length>0});}
        // second click on same link after re-filtering (hash unchanged -> no hashchange)
        document.querySelector('[data-s13-filter] button[data-which="'+st+'"]').click();
        a.scrollIntoView({block:'center'});await sleep(30);
        a.click();await sleep(120);
        r=t.getBoundingClientRect();ok=t.getClientRects().length>0&&Math.abs(r.top)<60;
        if(!ok){fail++;res.fails.push({state:st,href:id,second:true,top:Math.round(r.top),shown:t.getClientRects().length>0});}
      }
      res.states[st]={clicked:cnt,targetsHiddenAtClick:hid,fails:fail};
     }
     // hashchange path
     var hc=[];var ids=['s13-miss','s13-bored','s13-control','s13-envy','s13-drop20','s13-crash','s13-switch','s13-family'];
     for(var k=0;k<ids.length;k++){
       history.replaceState(null,'','#top');
       document.querySelector('[data-s13-filter] button[data-which="怕晚"]').click();
       window.scrollTo(0,0);await sleep(30);
       location.hash='#'+ids[k];await sleep(200);
       var t=document.getElementById(ids[k]);var r=t.getBoundingClientRect();
       hc.push([ids[k],t.getClientRects().length>0,Math.round(r.top)]);
     }
     res.hashchange=hc;
     var pressed=document.querySelector('[data-s13-filter] button[aria-pressed="true"]');res.pressedAfter=pressed&&pressed.textContent;
     return JSON.stringify(res);})()"""
    out["filter"]=json.loads(cdp.ev(ws,FILT))
    # plan-blank order: full
    ORDER=r"""(function(sel){
     var d=document.querySelector(sel);if(d&&d.tagName==='DETAILS')d.open=true;
     var root=d.tagName==='DETAILS'?d:d;var tb=root.querySelector('table');
     var items=[].map.call(tb.querySelectorAll(':scope>tbody>tr>td>strong'),function(s){var r=s.getBoundingClientRect();return [s.textContent.trim().slice(0,6),Math.round(r.top+scrollY),Math.round(r.left),Math.round(s.closest('td').getBoundingClientRect().width)];});
     items.sort(function(a,b){return a[1]-b[1]});
     var w=tb.closest('.table-wrap');
     return JSON.stringify({items:items,wrapOver:w.scrollWidth-w.clientWidth,hint:getComputedStyle(w,'::before').content,tableW:Math.round(tb.getBoundingClientRect().width),vw:innerWidth});})"""
    out["planblank_full"]=json.loads(cdp.ev(ws,ORDER+"('details[data-lite-alt~=\"plan-blank\"]')"))
    y=cdp.ev(ws,"(function(){var d=document.querySelector('details[data-lite-alt~=\"plan-blank\"]');d.scrollIntoView();var s=[].filter.call(d.querySelectorAll('strong'),function(x){return x.textContent.indexOf('F 規則')===0})[0];s.scrollIntoView();window.scrollBy(0,-10);return 1})()")
    cdp.shot(ws,"j-full-planblank-F-400.png")
    # lite
    setup(ws,PAGES["lite"])
    out["layout_lite"]=json.loads(cdp.ev(ws,LAYOUT))
    out["planblank_lite"]=json.loads(cdp.ev(ws,r"""(function(){var tb=document.querySelector('table.lite-plan');var items=[].map.call(tb.querySelectorAll(':scope>tbody>tr>td>strong'),function(s){var r=s.getBoundingClientRect();return [s.textContent.trim().slice(0,6),Math.round(r.top+scrollY),Math.round(r.left)]});var w=tb.closest('.table-wrap');return JSON.stringify({items:items,wrapOver:w.scrollWidth-w.clientWidth,hint:getComputedStyle(w,'::before').content,vw:innerWidth,sw:document.documentElement.scrollWidth})})()"""))
    cdp.ev(ws,"(function(){var s=[].filter.call(document.querySelectorAll('table.lite-plan strong'),function(x){return x.textContent.indexOf('F 規則')===0})[0];s.scrollIntoView();window.scrollBy(0,-10);return 1})()")
    cdp.shot(ws,"j-lite-planblank-F-400.png")
finally:
    p.kill()
json.dump(out,open("j_browser_result.json","w"),ensure_ascii=False,indent=1)
print("done")
