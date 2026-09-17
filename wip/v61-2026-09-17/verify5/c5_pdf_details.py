# 完整版 PDF：每個 details 的 summary 在哪一頁、後面有沒有「紙本未印」提示、內文是否印出（取內文多段 14 字片段比對）
import json, re, fitz
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
PDF = ROOT + '/export/隔離人性-理財新手完整指南-v6.1.pdf'
inv = json.load(open('details_inventory.json', encoding='utf-8'))
doc = fitz.open(PDF)
pages = [re.sub(r'\s+', '', p.get_text()) for p in doc]
allt = ''.join(pages)
open('pdf_pages.txt', 'w', encoding='utf-8').write('\n'.join('=== p%d ===\n%s' % (i + 1, doc[i].get_text()) for i in range(doc.page_count)))
def norm(s): return re.sub(r'\s+', '', s)
def where(s):
    return [i + 1 for i, p in enumerate(pages) if s in p]
print('pages', doc.page_count)
HINT = '（紙本未印，網頁版可展開）'
for k, d in enumerate(inv):
    b = norm(d['body'])
    L = 14
    chunks = [b[i:i + L] for i in range(0, max(len(b) - L, 1), max((len(b) - L) // 6, 1))][:7]
    hits = [bool(where(c)) for c in chunks if len(c) == L]
    s = norm(d['summary'])[:18]
    sp = where(s)
    hint_ok = None
    if sp:
        # summary 那頁，summary 之後 60 字內有沒有提示
        p = pages[sp[0] - 1]; j = p.find(s)
        seg = p[j:j + len(norm(d['summary'])) + 40]
        hint_ok = ('紙本未印' in seg)
    print('%02d %-8s print=%-5s summary頁=%s 提示=%s 內文片段命中 %d/%d  | %s' % (k, d['section'], d['data_print'], sp[:3], hint_ok, sum(hits), len(hits), d['summary'][:40]))
