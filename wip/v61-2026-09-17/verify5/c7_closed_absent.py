# 沒有 data-print 的教學摺疊：內文句子在 summary 那頁與後兩頁出現的比例（應接近 0），並印出 summary 那一行（看提示）
import json, re, fitz, html as h
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
doc = fitz.open(ROOT + '/export/隔離人性-理財新手完整指南-v6.1.pdf')
raw = [p.get_text() for p in doc]
pages = [re.sub(r'\s+', '', p) for p in raw]
inv = json.load(open('details_inventory.json', encoding='utf-8'))
H = open(ROOT + '/guide/index.html', encoding='utf-8').read()
def body_full(st):
    depth = 0
    for m in re.finditer(r'<details\b[^>]*>|</details>', H[st:]):
        depth += 1 if m.group(0).startswith('<details') else -1
        if depth == 0: blk = H[st:st + m.end()]; break
    blk = re.sub(r'<summary\b.*?</summary>', '', blk, count=1, flags=re.S)
    blk = re.sub(r'<svg\b.*?</svg>', '', blk, flags=re.S)
    return h.unescape(re.sub(r'<[^>]+>', '\n', blk))
for d in inv:
    if d['data_print'] is not None: continue
    s = re.sub(r'\s+', '', d['summary'])[:16]
    sp = [i for i, p in enumerate(pages) if s in p]
    if not sp: print('summary not found', d['summary']); continue
    i0 = sp[0]
    win = ''.join(pages[i0:i0 + 3])
    pieces = [re.sub(r'\s+', '', x) for x in re.split(r'[。；\n]', body_full(d['start']))]
    pieces = [x for x in pieces if len(x) >= 10]
    hit = [x for x in pieces if x in win]
    line = [l for l in raw[i0].splitlines() if d['summary'][:8].replace(' ', '') in l.replace(' ', '')]
    # 提示可能折到下一行：取 summary 行與下一行
    L = raw[i0].splitlines(); idx = next((k for k, l in enumerate(L) if d['summary'][:8].replace(' ', '') in l.replace(' ', '')), None)
    shown = ' / '.join(L[idx:idx + 2]) if idx is not None else ''
    print('p%-3d %-9s 內文長句 %d 句，出現在 summary 頁起三頁內 %d 句 %s | %s' % (i0 + 1, d['section'], len(pieces), len(hit), [x[:20] for x in hit][:3], shown[:120]))
