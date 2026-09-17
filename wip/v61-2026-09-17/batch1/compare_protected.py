import re, sys
from collections import Counter
def blocks(h, tag, cls):
    out = []
    for m in re.finditer(r'<%s\b[^>]*class="%s"[^>]*>' % (tag, cls), h):
        d = 0
        for t in re.finditer(r'<%s\b[^>]*>|</%s>' % (tag, tag), h[m.start():]):
            d += -1 if t.group(0).startswith('</') else 1
            if d == 0:
                out.append(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h[m.start():m.start()+t.end()])).strip()); break
    return out
old, new = (open(p, encoding='utf-8').read() for p in sys.argv[1:3])
for tag, cls in [('div', 'story'), ('mark', 'key'), ('div', 'warning')]:
    a, b = Counter(blocks(old, tag, cls)), Counter(blocks(new, tag, cls))
    print(tag, cls, 'OK' if a == b else ('LOST %s / ADDED %s' % (a - b, b - a)))
for pat in ['class="term"', 'class="xref"', '<details', 'data-chart=', '<mark class="key"']:
    print(pat, old.count(pat), '->', new.count(pat))
