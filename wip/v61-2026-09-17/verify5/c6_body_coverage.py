# 對 data-print="open" 的案例摺疊與六個錯：把內文拆成句子（以。；分），逐句在 PDF 全文（去空白、去列表編號）找，列出找不到的句子
import json, re, sys, fitz
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
doc = fitz.open(ROOT + '/export/隔離人性-理財新手完整指南-v6.1.pdf')
pages = [re.sub(r'\s+', '', p.get_text()) for p in doc]
inv = json.load(open('details_inventory.json', encoding='utf-8'))
H = open(ROOT + '/guide/index.html', encoding='utf-8').read()
import html as h
def body_full(d):
    # 重新抓完整內文（inventory 只存 400 字）
    st = d['start']; depth = 0
    for m in re.finditer(r'<details\b[^>]*>|</details>', H[st:]):
        depth += 1 if m.group(0).startswith('<details') else -1
        if depth == 0:
            blk = H[st:st + m.end()]; break
    blk = re.sub(r'<summary\b.*?</summary>', '', blk, count=1, flags=re.S)
    blk = re.sub(r'<svg\b.*?</svg>', '', blk, flags=re.S)
    blk = re.sub(r'<[^>]+>', '\n', blk)
    return h.unescape(blk)
targets = [k for k, d in enumerate(inv) if d['section'] in ('cases', 'ten')]
for k in targets:
    d = inv[k]
    t = body_full(d)
    pieces = [re.sub(r'\s+', '', x) for x in re.split(r'[。；\n]', t)]
    pieces = [x for x in pieces if len(x) >= 6]
    miss = []
    found_pages = set()
    for x in pieces:
        hit = [i + 1 for i, p in enumerate(pages) if x in p and ((d["section"] == "ten" and 3 <= i + 1 <= 5) or (d["section"] == "cases" and 83 <= i + 1 <= 96))]
        if hit: found_pages.update(hit[:1])
        else: miss.append(x)
    print('== %s | %s | 片段 %d，找不到 %d，出現頁 %s' % (d['section'], d['summary'][:30], len(pieces), len(miss), sorted(found_pages)))
    for x in miss[:40]: print('   MISS:', x[:80])
