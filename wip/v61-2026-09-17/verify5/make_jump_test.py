# 複製 output/full-v60-out.html，注入一段腳本：逐一點狀況索引與封面入口的連結，記錄目標是否可見、跳完後目標離視窗頂端多遠
import sys
src = '../../../output/full-v60-out.html'
h = open(src, encoding='utf-8').read()
js = r'''<script>
window.addEventListener('load', function(){ setTimeout(async function(){
  document.documentElement.style.scrollBehavior = 'auto';
  var out = [];
  var links = Array.prototype.slice.call(document.querySelectorAll('table.situations a, nav.tasks a, #group-life .part-map a, #group-situations p.small a'));
  for (var i=0;i<links.length;i++){
    var a = links[i]; var id = a.getAttribute('href').slice(1); var t = document.getElementById(id);
    var tr = a.closest('tr');
    var r = {where: tr ? tr.cells[0].textContent.slice(0,18) : (a.closest('nav.tasks') ? 'cover' : a.closest('section').id), href: id, text: a.textContent.slice(0,20)};
    if (!t){ r.err='MISSING'; out.push(r); continue; }
    var hid = null;
    for (var e=t; e; e=e.parentElement){ var cs=getComputedStyle(e); if (cs.display==='none'||cs.visibility==='hidden'){ hid=e.tagName+'.'+e.className+'#'+e.id; break;} if (e!==t && e.tagName==='DETAILS' && !e.open){ hid='closed-details'; break;} }
    r.hidden = hid;
    window.scrollTo(0,0);
    await new Promise(function(res){setTimeout(res,30);});
    a.click();
    await new Promise(function(res){setTimeout(res,80);});
    var rect = t.getBoundingClientRect();
    r.top = Math.round(rect.top); r.scrollY = Math.round(window.scrollY);
    var nxt = t; if (!t.textContent.trim()) { nxt = t.nextElementSibling; }
    r.lands = (nxt ? nxt.textContent.trim().replace(/\s+/g,' ').slice(0,30) : '');
    out.push(r);
  }
  var pre=document.createElement('pre'); pre.id='jump-result'; pre.textContent=JSON.stringify({vw: window.innerWidth, docW: document.documentElement.scrollWidth, res: out});
  document.body.appendChild(pre);
}, 300); });
</script>'''
h = h.replace('</body>', js + '</body>')
open('jump-test.html', 'w', encoding='utf-8').write(h)
print('ok', len(h))
