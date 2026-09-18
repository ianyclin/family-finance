# -*- coding: utf-8 -*-
"""從證交所開放資料算兩個數：終止上市逐年家數、2003 年底上市公司到今天還在名單上的有幾家。
預設吃 data/ 底下 2026-09-18 抓下來的快照；加 --live 會重新抓一次證交所 API。
資料來源：
  https://openapi.twse.com.tw/v1/company/suspendListingCsvAndHtml （終止上市公司）
  https://openapi.twse.com.tw/v1/opendata/t187ap03_L （上市公司基本資料）
2003 年底上市公司家數 669 家，取自證交所 60 週年專刊〈歷年上市公司家數統計〉（民國 92 年那一格）。
"""
import json, os, sys, collections, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = '--live' in sys.argv
API = {'delist': 'https://openapi.twse.com.tw/v1/company/suspendListingCsvAndHtml',
       'listed': 'https://openapi.twse.com.tw/v1/opendata/t187ap03_L'}
SNAP = {'delist': 'data/twse-suspendListing-20260918.json',
        'listed': 'data/twse-listed-slim-20260918.json'}

def load(k):
    if LIVE:
        req = urllib.request.Request(API[k], headers={'User-Agent': 'Mozilla/5.0'})
        d = json.load(urllib.request.urlopen(req, timeout=60))
        if k == 'listed':
            d = [{'code': r['公司代號'], 'name': r['公司簡稱'], 'listed': r['上市日期'], 'asof': r['出表日期']} for r in d]
        return d
    return json.load(open(os.path.join(HERE, SNAP[k]), encoding='utf-8'))

delist, listed = load('delist'), load('listed')

c = collections.Counter()
for r in delist:
    c[int(r['DelistingDate'].split('/')[0]) + 1911] += 1
print('終止上市逐年家數（開放資料只回到民國 90 年；沒有區分合併、轉上櫃、私有化或經營不善）')
for y in sorted(c):
    print('  %d  %d' % (y, c[y]))
print('  合計 %d 家（%d–%d）' % (sum(c.values()), min(c), max(c)))

asof = listed[0]['asof']
n_now = len(listed)
n_2003 = sum(1 for r in listed if r['listed'] <= '20031231')
print('\n上市公司基本資料出表日期：%s，名單上 %d 家' % (asof, n_now))
print('  其中上市日期在 2003-12-31 以前：%d 家' % n_2003)
print('  2003 年底 669 家裡還在名單上：%d 家（%.1f%%）；不在名單上：%d 家（%.1f%%）'
      % (n_2003, n_2003 / 669 * 100, 669 - n_2003, (669 - n_2003) / 669 * 100))
print('  今天名單上 2004 年以後才上市的：%d 家（占今天的 %.1f%%）'
      % (n_now - n_2003, (n_now - n_2003) / n_now * 100))
