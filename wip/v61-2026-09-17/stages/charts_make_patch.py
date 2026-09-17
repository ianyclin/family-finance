import json, sys, os
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import v61_g9_country_recovery as g9, v61_g10_rebalance_drift as g10
c = json.load(open(os.path.join(ROOT, 'lite/calc-results.json'), encoding='utf-8'))
d9 = g9.chart(c['country_recovery'])
r10 = c['rebalance_drift']; d10 = g10.chart(r10)
lead9 = '把上面那張表的三段期間畫在同一條年份軸上，更容易看出「等很久」是幾十年。'
lead10 = r10['printed']['lead_sentence']
assert '3 個月國庫券' in lead10 and '定存' in lead10
h = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
P = []
a = '不能拿來當這裡的證據。</p></div>'
P.append(dict(section='s4', old=a, new='不能拿來當這裡的證據。</p><p>%s</p>\n<figure class="chart" data-chart="country-recovery"><figcaption>%s</figcaption></figure></div>' % (lead9, d9['caption']), why='G9 圖放在美日台回本表後'))
a = '例如債券設 10%，四分之一是 2.5，所以跑到 12.5% 以上或 7.5% 以下才動。</p>\n'
P.append(dict(section='s11', old=a, new=a + '<p>%s</p>\n<figure class="chart" data-chart="rebalance-drift"><figcaption>%s</figcaption></figure>\n' % (lead10, d10['caption']), why='G10 圖放在 5/25 說明後'))
a = '「10% 配置 → 7.5%–12.5%」的例子</span></a></div>'
P.append(dict(section='s11', old=a, new='「10% 配置 → 7.5%–12.5%」的例子</span></a><a class="source-link" href="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html" target="_blank" rel="noopener"><span>Damodaran（紐約大學 Stern）：Historical Returns on Stocks, Bonds and Bills</span><span class="source-note">比例漂移圖：S&amp;P 500 含息與美國 3 個月國庫券年度報酬</span></a></div>', why='G10 資料出處'))
a = '本文不討論，也不放進圖裡。</span></li>'
new = a + ('<li>第 <a class="xref" href="#s4">4</a> 節「單一市場可能等很久」那張時間軸圖：三條都是價格指數（不含股利）、名目、各自幣別，沒有扣物價、費用和稅；日期都是收盤日，長條畫到第一次收盤超過舊高點。美國是道瓊工業指數，日期出自聯準會歷史頁（Federal Reserve History）；日本是日經 225 指數，出自日經官方；台灣是加權股價指數，出自證交所逐日收盤。<br><span class="small">三個指數、幣別不同，不能直接比快慢；這三段是挑出來的著名例子，不是平均。長條畫到第一次收盤超過舊高點，之後還是可能再跌回舊高點以下。</span></li>'
       '<li>第 <a class="xref" href="#s11">11</a> 節比例漂移圖：用同一份 Damodaran 資料集的 S&amp;P 500 含息與 3 個月國庫券兩欄（10 年期公債只在圖下說明對照），名目美元，不是換回台幣的報酬。3 個月國庫券代表本文防守放的定存。<br><span class="small">資料是年度的，圖只看每年年底的比例；兩個年底之間可能早就跑出門檻，圖上看不出來。沒有扣物價、費用和稅，也沒有投入新錢或提領；只用美國一個市場。</span></li>')
P.append(dict(section='methods', old=a, new=new, why='兩張新圖的口徑與出處'))
for p in P:
    assert h.count(p['old']) == 1, p['old']
json.dump(P, open(os.path.join(ROOT, 'wip/v61-2026-09-17/stages/charts-patch.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(lead9); print(d9['caption']); print(lead10); print(d10['caption'])
