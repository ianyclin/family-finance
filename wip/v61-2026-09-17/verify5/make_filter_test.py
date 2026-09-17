# 第 14 節篩選按鈕按下「怕賠」之後，再從狀況索引點其他感受的連結，看會不會跳不過去
src = '../../../output/full-v60-out.html'
h = open(src, encoding='utf-8').read()
js = r'''<script>
window.addEventListener('load', function(){ setTimeout(async function(){
  document.documentElement.style.scrollBehavior = 'auto';
  var out = [];
  var btn = document.querySelector('[data-s13-filter] button[data-which="怕賠"]');
  out.push({filterButton: !!btn});
  if (btn) btn.click();
  var links = Array.prototype.slice.call(document.querySelectorAll('table.situations a[href^="#s13-"]'));
  for (var i=0;i<links.length;i++){
    var a=links[i], id=a.getAttribute('href').slice(1), t=document.getElementById(id);
    window.scrollTo(0, document.getElementById('group-situations').offsetTop);
    var before = Math.round(window.scrollY);
    a.click();
    await new Promise(function(res){setTimeout(res,80);});
    out.push({href:id, displayed: t.getClientRects().length>0, before: before, after: Math.round(window.scrollY), top: Math.round(t.getBoundingClientRect().top)});
  }
  var pre=document.createElement('pre'); pre.id='filter-result'; pre.textContent=JSON.stringify(out);
  document.body.appendChild(pre);
}, 300); });
</script>'''
open('filter-test.html', 'w', encoding='utf-8').write(h.replace('</body>', js + '</body>'))
