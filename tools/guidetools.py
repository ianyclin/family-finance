# -*- coding: utf-8 -*-
"""Guide helper tools.
Usage:
  python3 guidetools.py apply  <base.html> <out.html> <patch1.json> [patch2.json ...]
  python3 guidetools.py check  <html>   # 標籤／id／連結／名詞連結，並印兩級重點句（marks 總數、markstop 淡紅數）
  python3 guidetools.py text   <html> <out.txt>
  python3 guidetools.py diff   <old.html> <new.html> <out.txt>
  python3 guidetools.py numbers <old.html> <new.html>
Patch JSON: [{"section": "...", "old": "...", "new": "...", "why": "..."}]
"""
import sys, json, re, difflib
from collections import Counter
from html.parser import HTMLParser

TAGS = ['div','p','li','ul','ol','a','strong','h3','h4','h5','section','figure','details','summary','table','tr','td','span','dt','dd','dl','mark']

# 重點句兩級（v7 第五輪）：黃線 <mark class="key">、淡紅線 <mark class="key top">。
MARK_ANY = r'<mark\b(?=[^>]*?(?<![\w-])class="key(?: top)?")[^>]*>'
MARK_TOP = r'<mark\b(?=[^>]*?(?<![\w-])class="key top")[^>]*>'
# 兩級都不准出現在這些容器裡（作者 2026-09-20；摘要／標題／小字／圖說／表格儲存格／摺疊／黃框／白話版／來源卡）
VOID_TAGS = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def read(p): return open(p, encoding='utf-8').read()

# 批 CX：書末附錄（可列印工作表）由 tools/build_lite.py 產生、夾在這兩個 marker 之間，是工作表的複本，不是正文。
# 正文哨兵（to_text／check、v7_check 的 Doc 與 xrefs）解析前先拿掉整塊，只留一個空殼，讓 #worksheet 這個 id 還找得到。
APPENDIX_START = '<!-- worksheet-appendix:start -->'
APPENDIX_END = '<!-- worksheet-appendix:end -->'
APPENDIX_SHELL = '<section id="worksheet"></section>'
APPENDIX_RE = re.compile(re.escape(APPENDIX_START) + r'.*?' + re.escape(APPENDIX_END), re.S)

def strip_appendix(h):
    """把 marker 之間的附錄換成空殼 <section id="worksheet"></section>；沒有附錄就原樣回傳。"""
    return APPENDIX_RE.sub(lambda m: APPENDIX_SHELL, h)

# Opening-tag patterns that tolerate extra attributes (e.g. data-lite="ch4") before or after class.
# The class value itself must match exactly (class="story", not class="story x").
def open_tag(tag, cls=None):
    if cls is None: return r'<%s\b[^>]*>' % tag
    return r'<%s\b(?=[^>]*?(?<![\w-])class="%s")[^>]*>' % (tag, re.escape(cls))

def count_open(h, tag, cls=None): return len(re.findall(open_tag(tag, cls), h))

def tag_blocks(h, tag, cls):
    """Yield (start, end) of each <tag class="cls" ...>...</tag>, matching nested same-tag elements."""
    close = '</%s>' % tag
    for m in re.finditer(open_tag(tag, cls), h):
        depth = 0; j = m.start(); k = len(h)
        for t in re.finditer(r'<%s\b[^>]*>|</%s>' % (tag, tag), h[j:]):
            depth += -1 if t.group(0) == close else 1
            if depth == 0: k = j + t.end(); break
        yield j, k

def div_blocks(h, cls):
    """Yield (start, end) of each <div class="cls" ...>...</div>, matching nested divs."""
    return tag_blocks(h, 'div', cls)

class _MarkScan(HTMLParser):
    """走一次 DOM，找出每個 mark.key／mark.key.top 所在的節與祖先鏈。"""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.stack = []          # [(tag, classes)]
        self.sec = []            # [(stack_index, section_id)]
        self.marks = []          # [{'top':bool,'sec':str,'anc':[(tag,cls)],'text':[str]}]
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = set((a.get('class') or '').split())
        if tag == 'mark' and 'key' in cls:
            self.cur = {'top': 'top' in cls, 'sec': self.sec[-1][1] if self.sec else None,
                        'anc': list(self.stack), 'text': []}
            self.marks.append(self.cur)
        if tag not in VOID_TAGS:
            self.stack.append((tag, cls))
            if tag == 'section' and a.get('id'): self.sec.append((len(self.stack) - 1, a['id']))

    def handle_endtag(self, tag):
        if tag in VOID_TAGS: return
        if tag == 'mark': self.cur = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                while self.sec and self.sec[-1][0] >= i: self.sec.pop()
                return

    def handle_data(self, data):
        if self.cur is not None: self.cur['text'].append(data)


def _forbidden(anc):
    """祖先鏈裡的禁止容器名稱（空的表示這一句放對地方）。"""
    out = []
    for t, c in anc:
        if t == 'details': out.append('details')
        elif t in ('h1', 'h2', 'h3', 'h4', 'h5', 'td', 'th', 'figcaption', 'summary'): out.append(t)
        elif t == 'div' and 'story' in c: out.append('div.story')
        elif 'source-card' in c: out.append(t + '.source-card')
        elif t == 'p' and 'explain' in c: out.append('p.explain')
        elif t == 'p' and 'note' in c: out.append('p.note')
        elif 'small' in c: out.append(t + '.small')
    return out


def marks(h):
    """回傳 (黃線數, 淡紅線數, 違規清單)。違規＝重點句落在禁止的容器裡。"""
    p = _MarkScan(); p.feed(h); p.close()
    bad = []
    for m in p.marks:
        f = _forbidden(m['anc'])
        if f:
            bad.append('%s（%s）%s' % ('淡紅' if m['top'] else '黃線', m['sec'],
                                      ''.join(m['text'])[:24] + ' ← 在 ' + '／'.join(f) + ' 裡'))
    top = sum(1 for m in p.marks if m['top'])
    return len(p.marks) - top, top, bad


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
    h = strip_appendix(read(path)); errs = []
    for t in TAGS:
        o = len(re.findall(r'<%s\b[^>]*>' % t, h)); c = len(re.findall(r'</%s>' % t, h))
        if o != c: errs.append('tag %s open=%d close=%d' % (t, o, c))
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', h)
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup: errs.append('duplicate ids %s' % dup)
    bad = [x for x in re.findall(r'href="#([^"]+)"', h) if x not in set(ids)]
    if bad: errs.append('broken hrefs %s' % bad)
    d = 0
    for t in re.finditer(r'<a\b[^>]*>|</a>', h):
        d += -1 if t.group(0) == '</a>' else 1
        if d < 0 or d > 1: errs.append('nested or unbalanced <a>'); break
    H = re.sub(r'data:[^"\')]+', 'DATA', h)
    term = open_tag('a', 'term')
    story_terms = sum(len(re.findall(term, H[a:b])) for a, b in div_blocks(H, 'story'))
    if story_terms: errs.append('term links inside story boxes: %d' % story_terms)
    strong_terms = len(re.findall(r'<strong\b[^>]*>[^<]*' + term, H))
    if strong_terms: errs.append('term links inside strong: %d' % strong_terms)
    n_key, n_top, mark_bad = marks(h)
    for b in mark_bad: errs.append('重點句放在不准放的容器裡：' + b)
    print('marks', n_key + n_top, 'later', len(re.findall(r'<[a-z]+\b(?=[^>]*?(?<![\w-])class="later")[^>]*>', h)),
          'details', count_open(h, 'details'), 'data-chart', len(re.findall(r'(?<![\w-])data-chart=', h)), 'story', count_open(h, 'div', 'story'),
          'markstop', n_top, '(黃線 %d＋淡紅 %d)' % (n_key, n_top))
    if errs:
        print('CHECK FAILED'); [print(' -', e) for e in errs]; sys.exit(1)
    print('CHECK OK')

def strip_blocks(h, cls, tags=('div', 'details')):
    """拿掉整塊 <tag class="cls">…</tag>。來源卡 v7 第五輪起是 <details class="source-card">，
    舊版是 <div class="source-card">，兩種都要認得出來。"""
    spans = sorted(s for t in tags for s in tag_blocks(h, t, cls))
    out = []; i = 0
    for j, k in spans:
        if j < i: continue  # nested inside a block already stripped
        out.append(h[i:j]); i = k
    out.append(h[i:])
    return ''.join(out)

def strip_div(h, cls): return strip_blocks(h, cls, ('div',))

def _term_text(m):
    """a.term 保留 title：〔詞：title〕；沒有 title 的維持〔詞〕。"""
    tt = re.search(r'(?<![\w-])title="([^"]*)"', m.group(1))
    return '〔%s：%s〕' % (m.group(2), tt.group(1)) if tt else '〔%s〕' % m.group(2)

def _ext_link_text(m):
    """外部連結（source-link 以外）寫成「文字（網址）」；a.xref、a.back、# 開頭的 href 不會進到這裡。"""
    if re.search(r'(?<![\w-])class="[^"]*\bsource-link\b', m.group(1)): return m.group(0)
    return '%s（%s）' % (m.group(3), m.group(2))

def to_text(path, keep_sources=False):
    h = strip_appendix(read(path))
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    if not keep_sources: h = strip_blocks(h, 'source-card')
    h = re.sub(r'<svg.*?</svg>', '', h, flags=re.S)
    h = re.sub(open_tag('details', 'orig') + r'.*?</details>', '', h, flags=re.S)
    h = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'〔圖：\1〕', h); h = re.sub(r'<img[^>]*>', '', h)
    h = re.sub(open_tag('div', 'story'), '\n【黃框】', h); h = re.sub(open_tag('summary'), '\n【摺疊】', h)
    h = re.sub(open_tag('p', 'small'), '\n〈小字〉', h); h = re.sub(open_tag('span', 'small'), '〈小字〉', h)
    h = re.sub('(' + open_tag('a', 'term') + r')(.*?)</a>', _term_text, h); h = re.sub(MARK_ANY + r'(.*?)</mark>', r'★\1★', h)
    h = re.sub(open_tag('span', 'later') + r'(.*?)</span>', r'［\1］', h); h = h.replace('<br>', '\n')
    h = re.sub(r'<h2[^>]*>', '\n\n## ', h); h = re.sub(r'<h3[^>]*>', '\n### ', h)
    h = re.sub(r'</(p|li|h2|h3|h4|h5|dd|dt|tr|figcaption|div|summary)>', '\n', h); h = re.sub(r'<t[dh][^>]*>', ' | ', h)
    h = re.sub(r'(<a\b[^>]*?(?<![\w-])href="(https?://[^"]*)"[^>]*>)(.*?)</a>', _ext_link_text, h, flags=re.S)
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
