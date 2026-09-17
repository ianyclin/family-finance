# 裁判（成本與風險）用的掃描：只讀 guide/index.html，不改任何東西
import re, sys, json, collections
path = sys.argv[1] if len(sys.argv) > 1 else 'guide/index.html'
h = open(path, encoding='utf-8').read()
secs = []
for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>', h):
    secs.append((m.start(), m.group(1)))
secs.append((len(h), None))
def sec_at(i):
    cur = None
    for s, sid in secs:
        if s > i: break
        cur = sid
    return cur
num_of = {}
for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>\s*<h2[^>]*>\s*<span[^>]*class="num"[^>]*>(\d+)</span>', h):
    num_of[m.group(1)] = int(m.group(2))
order = [sid for _, sid in secs if sid]
# story spans
story = []
for m in re.finditer(r'<div\b(?=[^>]*class="story")[^>]*>', h):
    d = 0; k = len(h)
    for t in re.finditer(r'<div\b[^>]*>|</div>', h[m.start():]):
        d += -1 if t.group(0) == '</div>' else 1
        if d == 0: k = m.start() + t.end(); break
    story.append((m.start(), k))
def in_story(i): return any(a <= i < b for a, b in story)
# 1) numeric xrefs
xr = list(re.finditer(r'<a\b[^>]*class="xref"[^>]*href="#([\w-]+)"[^>]*>(.*?)</a>', h, flags=re.S))
xr += list(re.finditer(r'<a\b[^>]*href="#([\w-]+)"[^>]*class="xref"[^>]*>(.*?)</a>', h, flags=re.S))
seen=set(); rows=[]
for m in xr:
    if m.start() in seen: continue
    seen.add(m.start())
    txt = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    rows.append((m.start(), sec_at(m.start()), m.group(1), txt, in_story(m.start())))
numeric = [r for r in rows if re.fullmatch(r'\d+', r[3])]
named = [r for r in rows if not re.fullmatch(r'\d+', r[3])]
print('xref total', len(rows), 'numeric', len(numeric), 'named', len(named))
c = collections.Counter(r[2] for r in numeric)
print('numeric xref by target:', dict(sorted(c.items(), key=lambda x: -x[1])))
bad = [r for r in numeric if r[2] in num_of and int(r[3]) != num_of[r[2]]]
print('numeric xref whose text != target num (now):', len(bad), bad[:5])
print('numeric xrefs inside story boxes:', [(r[1], r[2], r[3]) for r in numeric if r[4]])
print('named xrefs inside story boxes:', [(r[1], r[2], r[3]) for r in named if r[4]])
# xref targets that are not section ids (card anchors)
secids=set(order)
cardt = collections.Counter(r[2] for r in rows if r[2] not in secids)
print('xref to non-section anchors:', dict(cardt))
# section-number mentions not linked (plain 第 N 節 / 第X節)
plain = []
body = re.sub(r'<a\b[^>]*class="xref"[^>]*>.*?</a>', 'XREF', h, flags=re.S)
for m in re.finditer(r'第\s*([0-9０-９一二三四五六七八九十]+)\s*節', re.sub(r'<[^>]+>', '', h)):
    pass
txt_all = re.sub(r'<style.*?</style>', '', h, flags=re.S)
unl = re.findall(r'第\s*[一二三四五六七八九十]+\s*節', re.sub(r'<[^>]+>', '', txt_all))
print('Chinese-numeral 第X節 in text:', collections.Counter(unl))
json.dump({'order': order, 'num_of': num_of}, open('/dev/null','w'))
# 2) forward/back link counts by order
pos = {sid: i for i, sid in enumerate(order)}
def fwdback(ordr, rows):
    p = {sid: i for i, sid in enumerate(ordr)}
    f = b = 0
    # map card anchors to their section
    for r in rows:
        src, tgt = r[1], r[2]
        tsec = tgt if tgt in p else anchor_sec.get(tgt)
        if src is None or tsec is None or tsec == src or src not in p or tsec not in p: continue
        if p[tsec] > p[src]: f += 1
        else: b += 1
    return f, b
anchor_sec = {}
for m in re.finditer(r'\bid="([^"]+)"', h):
    anchor_sec[m.group(1)] = sec_at(m.start())
print('fwd/back xrefs current order:', fwdback(order, rows))
