# -*- coding: utf-8 -*-
"""Guide helper tools.
Usage:
  python3 guidetools.py apply  <base.html> <out.html> <patch1.json> [patch2.json ...]
  python3 guidetools.py check  <html>
  python3 guidetools.py text   <html> <out.txt>
  python3 guidetools.py diff   <old.html> <new.html> <out.txt>
  python3 guidetools.py numbers <old.html> <new.html>
Patch JSON: [{"section": "...", "old": "...", "new": "...", "why": "..."}]
"""
import sys, json, re, difflib
from collections import Counter

TAGS = ['div','p','li','ul','ol','a','strong','h3','h4','section','figure','details','summary','table','tr','td','span','dt','dd','dl','mark']

def read(p): return open(p, encoding='utf-8').read()

def apply(base, out, patches):
    h = read(base); P = []
    for f in patches: P += json.load(open(f, encoding='utf-8'))
    problems = []; spans = []
    for x in P:
        c = h.count(x['old'])
        if c != 1:
            problems.append('old count=%d section=%s old=%r' % (c, x.get('section'), x['old'][:80]))
            continue
        i = h.find(x['old']); spans.append((i, i + len(x['old']), x.get('section')))
    spans.sort()
    for a, b in zip(spans, spans[1:]):
        if a[1] > b[0]: problems.append('overlap %s / %s' % (a[2], b[2]))
    if problems:
        print('APPLY FAILED'); [print(' -', p) for p in problems]; sys.exit(1)
    for x in P: h = h.replace(x['old'], x['new'])
    open(out, 'w', encoding='utf-8').write(h)
    print('applied', len(P), 'patches ->', out)

def check(path):
    h = read(path); errs = []
    for t in TAGS:
        o = len(re.findall(r'<%s\b[^>]*>' % t, h)); c = len(re.findall(r'</%s>' % t, h))
        if o != c: errs.append('tag %s open=%d close=%d' % (t, o, c))
    ids = re.findall(r'id="([^"]+)"', h)
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup: errs.append('duplicate ids %s' % dup)
    bad = [x for x in re.findall(r'href="#([^"]+)"', h) if x not in set(ids)]
    if bad: errs.append('broken hrefs %s' % bad)
    d = 0
    for t in re.finditer(r'<a\b[^>]*>|</a>', h):
        d += -1 if t.group(0) == '</a>' else 1
        if d < 0 or d > 1: errs.append('nested or unbalanced <a>'); break
    H = re.sub(r'data:[^"\')]+', 'DATA', h)
    story_terms = sum(len(re.findall(r'<a class="term"', m.group(0))) for m in re.finditer(r'<div class="story">.*?</div>', H, flags=re.S))
    if story_terms: errs.append('term links inside story boxes: %d' % story_terms)
    strong_terms = len(re.findall(r'<strong>[^<]*<a class="term"', H))
    if strong_terms: errs.append('term links inside strong: %d' % strong_terms)
    print('marks', h.count('<mark class="key">'), 'later', h.count('class="later"'),
          'details', h.count('<details'), 'data-chart', h.count('data-chart='), 'story', h.count('<div class="story">'))
    if errs:
        print('CHECK FAILED'); [print(' -', e) for e in errs]; sys.exit(1)
    print('CHECK OK')

def strip_div(h, cls):
    out = []; i = 0
    while True:
        j = h.find('<div class="%s"' % cls, i)
        if j < 0: out.append(h[i:]); break
        out.append(h[i:j]); depth = 0; k = j
        for m in re.finditer(r'<div\b|</div>', h[j:]):
            depth += 1 if m.group(0) == '<div' else -1
            if depth == 0: k = j + m.end(); break
        i = k
    return ''.join(out)

def to_text(path, keep_sources=False):
    h = read(path)
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    if not keep_sources: h = strip_div(h, 'source-card')
    h = re.sub(r'<svg.*?</svg>', '', h, flags=re.S)
    h = re.sub(r'<details class="orig">.*?</details>', '', h, flags=re.S)
    h = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'〔圖：\1〕', h); h = re.sub(r'<img[^>]*>', '', h)
    h = h.replace('<div class="story">', '\n【黃框】'); h = h.replace('<summary>', '\n【摺疊】')
    h = re.sub(r'<p class="small">', '\n〈小字〉', h); h = re.sub(r'<span class="small">', '〈小字〉', h)
    h = re.sub(r'<a class="term"[^>]*>(.*?)</a>', r'〔\1〕', h); h = re.sub(r'<mark class="key">(.*?)</mark>', r'★\1★', h)
    h = re.sub(r'<span class="later">(.*?)</span>', r'［\1］', h); h = h.replace('<br>', '\n')
    h = re.sub(r'<h2[^>]*>', '\n\n## ', h); h = re.sub(r'<h3[^>]*>', '\n### ', h)
    h = re.sub(r'</(p|li|h2|h3|h4|dd|dt|tr|figcaption|div|summary)>', '\n', h); h = re.sub(r'<t[dh][^>]*>', ' | ', h)
    h = re.sub(r'<[^>]+>', '', h); h = h.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    h = re.sub(r'[ \t]+', ' ', h); h = re.sub(r'\n\s*\n+', '\n\n', h)
    return h.strip()

def sections(text):
    parts = re.split(r'\n## ', '\n' + text); out = {}
    for p in parts:
        if not p.strip(): continue
        title = p.split('\n', 1)[0].strip()
        body = '\n'.join(l for l in p.split('\n') if not l.startswith('【黃框】'))
        out[title] = body
    return out

def numbers(old, new):
    a = sections(to_text(old)); b = sections(to_text(new))
    num = lambda s: Counter(re.findall(r'\d+(?:[.,]\d+)*', s))
    for k in list(a.keys()) + [k for k in b if k not in a]:
        ca = num(a.get(k, '')); cb = num(b.get(k, ''))
        lost = ca - cb; added = cb - ca
        if lost or added:
            print('## %s' % k)
            if lost: print('  LOST :', dict(lost))
            if added: print('  ADDED:', dict(added))

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'apply': apply(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == 'check': check(sys.argv[2])
    elif cmd == 'text': open(sys.argv[3], 'w', encoding='utf-8').write(to_text(sys.argv[2])); print('ok')
    elif cmd == 'diff':
        a = to_text(sys.argv[2]).splitlines(); b = to_text(sys.argv[3]).splitlines()
        open(sys.argv[4], 'w', encoding='utf-8').write('\n'.join(difflib.unified_diff(a, b, 'old', 'new', lineterm='', n=1))); print('ok')
    elif cmd == 'numbers': numbers(sys.argv[2], sys.argv[3])
