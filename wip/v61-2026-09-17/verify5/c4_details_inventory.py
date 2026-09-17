# 列出改後 guide/index.html 所有 <details>：所在節、屬性、summary、內文開頭（供 PDF 比對）
import re, html, json, bisect
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
H = open(ROOT + '/guide/index.html', encoding='utf-8').read()
secs = [(m.start(), m.group(1)) for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"', H)]
pos = [p for p, _ in secs]
def txt(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<svg\b.*?</svg>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s); s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()
# 用堆疊配對 details
out = []; stack = []
for m in re.finditer(r'<details\b[^>]*>|</details>', H):
    if m.group(0).startswith('<details'):
        stack.append((m.start(), m.group(0)))
    else:
        st, tag = stack.pop()
        body = H[st:m.end()]
        sm = re.search(r'<summary\b[^>]*>(.*?)</summary>', body, flags=re.S)
        after_sum = body[sm.end():] if sm else body
        sec = secs[bisect.bisect_right(pos, st) - 1][1]
        out.append(dict(start=st, depth=len(stack), section=sec, tag=tag[:160], data_print=re.search(r'\sdata-print="([^"]*)"', tag).group(1) if 'data-print=' in tag else None,
                        open_attr=bool(re.search(r'\sopen\b', tag.replace('data-print="open"', ''))), summary=txt(sm.group(1)) if sm else '', body=txt(after_sum)[:400], body_len=len(txt(after_sum))))
out.sort(key=lambda d: d['start'])
json.dump(out, open('details_inventory.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i, d in enumerate(out):
    print('%02d d%d %-17s print=%-5s open=%-5s | %s | body %d字' % (i, d['depth'], d['section'], d['data_print'], d['open_attr'], d['summary'][:60], d['body_len']))
