import sys; sys.path.insert(0,'.')
import j_cdp as cdp, json, time
R="file:///Users/linyenchu/Cladue%20Code/family-finance/"
FILT=r"""(async function(){
 document.documentElement.style.scrollBehavior='auto';
 var sec=document.getElementById('s13');var sleep=function(ms){return new Promise(function(r){setTimeout(r,ms)})};
 function vtop(t){var r=t.getBoundingClientRect();var vv=window.visualViewport;return Math.round(r.top+scrollY-(vv?vv.pageTop:scrollY));}
 function pressed(){var p=document.querySelector('[data-s13-filter] button[aria-pressed="true"]');return p&&p.textContent;}
 var links=[].filter.call(document.querySelectorAll('a[href^="#"]'),function(a){var id=decodeURIComponent(a.getAttribute('href').slice(1));var t=id&&document.getElementById(id);return t&&sec.contains(t)&&!sec.contains(a)&&a.getClientRects().length>0;});
 var res={nLinks:links.length,rows:[]};
 var states=['怕晚','怕賠','想控制'];
 for(var s=0;s<states.length;s++){
  var st=states[s];
  for(var i=0;i<links.length;i++){
    var a=links[i];var id=decodeURIComponent(a.getAttribute('href').slice(1));var t=document.getElementById(id);
    for(var rep=0;rep<2;rep++){
      document.querySelector('[data-s13-filter] button[data-which="'+st+'"]').click();
      var hid=!!t.closest('[data-s13-hidden]');
      a.scrollIntoView({block:'center'});await sleep(40);
      a.click();await sleep(150);
      res.rows.push([st,id,a.textContent.slice(0,8),rep,hid,t.getClientRects().length>0,vtop(t),pressed(),location.hash]);
    }
  }
 }
 var hc=[];var ids=['s13-miss','s13-bored','s13-control','s13-envy','s13-drop20','s13-crash','s13-switch','s13-family','s13-loss'];
 for(var k=0;k<ids.length;k++){
   history.replaceState(null,'','#top');
   var st2=(ids[k]==='s13-control')?'怕賠':'想控制';
   document.querySelector('[data-s13-filter] button[data-which="'+st2+'"]').click();
   var t=document.getElementById(ids[k]);var hid=!!t.closest('[data-s13-hidden]');
   window.scrollTo(0,0);await sleep(40);
   location.hash='#'+ids[k];await sleep(250);
   hc.push([ids[k],st2,hid,t.getClientRects().length>0,vtop(t),pressed()]);
 }
 res.hashchange=hc;
 return JSON.stringify(res);})()"""
out={}
p,ws=cdp.start()
try:
    for mobile in (True,False):
        ws.call("Emulation.setTouchEmulationEnabled",enabled=mobile,maxTouchPoints=5 if mobile else 1)
        cdp.load(ws,R+"output/full-v60-out.html")
        ws.call("Emulation.setDeviceMetricsOverride",width=400,height=800,deviceScaleFactor=1,mobile=mobile)
        ws.call("Page.reload"); time.sleep(3)
        out['mobile' if mobile else 'narrow']=json.loads(cdp.ev(ws,FILT))
finally:
    p.kill()
json.dump(out,open('j_filter_result.json','w'),ensure_ascii=False,indent=0)
for k,v in out.items():
    rows=v['rows']; bad=[r for r in rows if not r[5] or abs(r[6])>40]
    print(k,'links',v['nLinks'],'clicks',len(rows),'hiddenAtClick',sum(1 for r in rows if r[4]),'bad',len(bad))
    for r in bad[:10]: print('  BAD',r)
    print('  hashchange',v['hashchange'])
    print('  sample',rows[:3])
