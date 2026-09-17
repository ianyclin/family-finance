# g11：第 6 節新增「現在是歷史新高，會不會太高了？」、刪第 6 節等匯率段重複句、第 14 節一題改寫、來源卡、methods
import json, os
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
R = json.load(open(os.path.join(ROOT, 'lite/calc-results.json'), encoding='utf-8'))['ath_returns']
bt = R['book_table']; sp = R['us_monthly_shiller']['split_1950']['5y']
yrs = R['book_facts']['taiex_3y_losing_at_high_start_years']
share_us = R['us_monthly_shiller']['share_months_at_high_pct']
assert 25 <= share_us < 35  # 「大約每十個月就有三個月」
assert yrs == [2005, 2007]
assert R['book_facts']['us_1929_record_10y_ann_pct'] < 0  # 「放十年還是虧的」
rng = R['taiex_daily']['sensitivity']['worst5_starts_1y_not_at_high_range_pct']
assert -55 < rng[0] and rng[1] < -45  # 「一年後一樣跌掉約一半」
w = R['taiex_daily']['sensitivity']['worst5_starts_1y']; assert w[0]['date'] == '2007-10-29' and w[0]['at_high']

rows = ''.join('<tr><td>台股 %d 年</td><td>%d%%</td><td>%d%%</td></tr>' % (r['years'], r['any_day'], r['at_high']) for r in bt['taiex'])
rows += ''.join('<tr><td>美股 %d 年</td><td>%d%%</td><td>%d%%</td></tr>' % (r['years'], r['any_month'], r['at_high']) for r in bt['us'])
b, a = sp['starts_before_1950'], sp['starts_1950_on']

new_block = (
 '<h3>現在是歷史新高，會不會太高了？</h3>\n'
 '<p>「創歷史新高」聽起來像站在山頂，但美股 1871 到 2023 年，大約每十個月就有三個月收在新高。'
 '把第 <a class="xref" href="#s5">5</a> 節那張「打開來是賺的」表，改成只在新高那天買進：</p>'
 '<div class="table-wrap"><table class="compact"><thead><tr><th>抱多久</th><th>任選一天</th><th>只挑創新高那天</th></tr></thead><tbody>'
 + rows + '</tbody></table></div>\n'
 '<p>差得不多，但方向不一致。台股這 23 年是新高那天買的比較差，可是放三年還在虧的新高買點，全部是 %d 到 %d 年買進、接著遇上 2008 年的人；'
 '美股換一段年代，哪一組平均賺得多也會翻過來。所以新高證明不了「別買」，也證明不了「照買沒差」。</p>\n' % tuple(yrs) +
 '<p>讓人受傷的是買進之後那幾年，不是那天剛好是新高：1929 年新高時買進美股的人，放十年還是虧的；台股 2007 年那次，新高前後幾天、沒創新高的日子買進，一年後也跌掉約一半；'
 '一個國家還可能幾十年回不到高點（第 <a class="xref" href="#s4">4</a> 節那張表）。擋得住這種運氣的是用錢期限和股票比例，不是挑日子：五年內要用的錢不放股票（「<a class="xref" href="#start">投資前的安全順序</a>」）；'
 '五年以上不用、比例又睡得著的錢，才照計畫投入，不必等新高過去。每月固定投入的人本來就會買到新高日，第 <a class="xref" href="#s5">5</a> 節那張表已經算進去了。</p>'
 '<p class="small">「新高」是含息指數不低於資料起點以來的最高值。台股是證交所含息報酬指數逐日收盤（2003–2025），只和 2003 年以後比，不是和 1990、2000 年的高點比；'
 '美股是 Shiller 月資料（1871–2023），表上是「任選一個月」和「新高的月份」，價格是當月平均，只能看大方向。每天都當一次買進日，相鄰的日子結果幾乎一樣，新高又成群出現，'
 '真正能互相比較的例子比表上少很多。名目、含息，沒扣物價、費用和稅。'
 '美股起點在 1950 年以前，新高月份放五年平均一年 %s%%、其他月份 %s%%；1950 年以後變成 %s%% 對 %s%%（賺錢的比例兩段都是新高略低）。</p>\n' % (b['at_high']['mean_ann_pct'], b['not_at_high']['mean_ann_pct'], a['at_high']['mean_ann_pct'], a['not_at_high']['mean_ann_pct'])
)
# 自我檢查：兩段年代方向真的相反、賺錢比例兩段都是新高略低
assert b['at_high']['mean_ann_pct'] < b['not_at_high']['mean_ann_pct'] and a['at_high']['mean_ann_pct'] > a['not_at_high']['mean_ann_pct']
assert b['at_high']['positive_share_pct'] < b['not_at_high']['positive_share_pct'] and a['at_high']['positive_share_pct'] < a['not_at_high']['positive_share_pct']

P = []
P.append({'section': 's6', 'why': 'G11：新段落放在一次投入 vs 分批之後、等匯率之前（簡報第 3 節）',
          'old': '只能當方法示例，不能取代正式研究。</p>\n<h3>等匯率，和等股價是同一個問題</h3>',
          'new': '只能當方法示例，不能取代正式研究。</p>\n' + new_block + '<h3>等匯率，和等股價是同一個問題</h3>'})
P.append({'section': 's6', 'why': '篇幅抵銷：「沒有人能可靠地預測匯率」第 5 節已有（匯率沒有人能可靠地預測）',
          'old': '兩個都要猜對兩次（什麼時候開始動、動到哪裡會停），兩個都沒有人能可靠地預測（第 <a class="xref" href="#s5">5</a> 節）。</p>',
          'new': '兩個都要猜對兩次：什麼時候開始動、動到哪裡會停。</p>'})
P.append({'section': 's6', 'why': '篇幅抵銷：「錢沒進去就沒參與」同節開頭已有（等跌的錢放在現金裡…這段就沒賺到）與五人圖圖說',
          'old': '整筆錢晚了好幾個月才開始。上面那張五個人的圖算的是等股價，不是等匯率；但「等」的機制一樣：錢沒進去的那幾個月，就是真的沒有參與。</p>',
          'new': '整筆錢晚了好幾個月才開始。</p>'})
P.append({'section': 's6', 'why': '篇幅抵銷：換匯成本的三項明細第 5 節已逐字列過（即期價差、匯款費、各家券商的優惠）',
          'old': '<p>可以先比的，是換匯本身的成本：即期價差、匯款費、各家券商的優惠，下單前就查得到（「<a class="xref" href="#costs">費用、稅務與帳戶安全</a>」）。「匯率之後會不會更好」查不到，所以它不該拿來當「要不要開始」的條件。要不要買鎖台幣的避險版本，是另一個選擇，寫在第 <a class="xref" href="#s5">5</a> 節。</p>',
          'new': '<p>換匯本身的成本下單前就查得到，可以先比；它和要不要買鎖台幣的避險版本，都寫在第 <a class="xref" href="#s5">5</a> 節與「<a class="xref" href="#costs">費用、稅務與帳戶安全</a>」。「匯率之後會不會更好」查不到，所以它不該拿來當「要不要開始」的條件。</p>'})
P.append({'section': 's13', 'why': 'G11：這一題改成指向第 6 節新段落（簡報第 7 節示範），不新增題目',
          'old': '<li><strong>覺得價格太高而等待回檔</strong>沒有人事先知道高點與回檔日期；等待的期間錢不在市場裡，也可能錯過上漲。<br>',
          'new': '<li><strong>覺得價格太高而等待回檔</strong>創新高本身不是訊號：歷史上新高很常見，新高那天買和其他日子買差得不多，而且不同國家、不同年代，哪邊比較好並不一致。沒有人事先知道回檔什麼時候來、跌到哪裡；先確認這筆錢五年內不用，再照計畫投入。<br>'})
P.append({'section': 'methods', 'why': 'G11 自算口徑',
          'old': '年數是高點到回到前高、一年算 365.25 天。</li>',
          'new': '年數是高點到回到前高、一年算 365.25 天。</li>'
                 '<li>第 <a class="xref" href="#s6">6</a> 節「現在是歷史新高」那張小表：「創新高」是當天（美股是當月）含息指數大於或等於從資料第一天（第一個月）到當天為止的最高值，資料第一天不算新高。'
                 '台股用上面那份證交所含息報酬指數逐日收盤（2003-01-02 到 2025-12-31），視窗和第 <a class="xref" href="#s5">5</a> 節同一套：滿 N 年的同一天，沒開盤就取前一個交易日；台股的新高只和 2003 年以後比。'
                 '美股用 Robert Shiller 公開月資料的 S&amp;P 500 含息指數（1871 年起），價格是當月每日收盤的平均，股利欄截至 2023 年 6 月，N 年就是 N×12 個月後。'
                 '「任選一天」那一欄就是第 5 節的比例，兩欄用同一批起點。每一天（每個月）都當一次買進日，視窗互相重疊，新高又成群出現，不是互相獨立的樣本。名目、含息，沒扣物價、費用和稅。</li>'})
json.dump(P, open(os.path.join(ROOT, 'wip/v61-2026-09-17/stages/g11-patch.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
h = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
for x in P: print(x['section'], h.count(x['old']))
