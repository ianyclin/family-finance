# 狀況索引與封面入口：每個連結的目標在哪、在哪一節、是否藏在摺疊裡、卡片內容
import sys, re
sys.path.insert(0, 'tools')
import build_lite as B
path = sys.argv[1] if len(sys.argv) > 1 else 'guide/index.html'
h = open(path, encoding='utf-8').read()
dom = B.Dom(h)
names = B.section_names(dom)

def secnum(sec):
    h2 = next((c for c in sec.children if c.tag == 'h2'), None)
    sp = next((c for c in h2.children if c.tag == 'span' and 'num' in c.classes()), None) if h2 else None
    return B.html_text(dom.inner(sp)) if sp else None

def following(n, limit=900):
    """n 之後同層兄弟的文字，到下一個 h3 或 limit 字為止"""
    sibs = n.parent.children
    i = sibs.index(n)
    out = []
    tot = 0
    for s in sibs[i+1:]:
        if s.tag in ('h3', 'h2') and out: break
        t = dom.text(s)
        out.append('[%s.%s] %s' % (s.tag, '.'.join(s.classes()), t))
        tot += len(t)
        if tot > limit: break
    return '\n      '.join(out)

def describe(tid):
    n = dom.by_id.get(tid)
    if n is None:
        return 'MISSING'
    sec = dom.section_of(n)
    if sec is None:
        return '  target <%s id=%s> (not in a section)' % (n.tag, tid)
    dets = [a for a in n.ancestors() if a.tag == 'details']
    detinfo = ['details(%s open=%s data-print=%s alt=%s)' % ('.'.join(a.classes()), 'open' in a.attrs, a.attrs.get('data-print'), a.attrs.get('data-lite-alt')) for a in dets]
    prot = [a for a in [n] + list(n.ancestors()) if a.attrs.get('data-lite-alt') or a.attrs.get('data-lite') or 'story' in a.classes()]
    lines = ['  target <%s id=%s> in section %s (num %s, 「%s」)' % (n.tag, tid, sec.attrs['id'], secnum(sec), names.get(sec.attrs['id']))]
    if detinfo: lines.append('  INSIDE ' + ' > '.join(detinfo))
    if prot: lines.append('  inside protected: ' + ', '.join('%s[%s]' % (a.tag, a.attrs.get('data-lite-alt') or a.attrs.get('data-lite') or 'story') for a in prot))
    if n.tag == 'section':
        h2 = next(c for c in n.children if c.tag == 'h2')
        lede = next((c for c in n.children if c.tag == 'p' and 'lede' in c.classes()), None)
        h3s = [dom.text(x) for x in dom.nodes if x.tag == 'h3' and x.start > n.start and x.end <= n.end]
        lines.append('  h2: %s | lede: %s' % (dom.text(h2), dom.text(lede) if lede else '-'))
        lines.append('  h3s: ' + ' / '.join(h3s))
    elif n.tag == 'h3':
        lines.append('  h3: %s' % dom.text(n))
        lines.append('  parent <%s class=%s alt=%s>' % (n.parent.tag, n.parent.attrs.get('class'), n.parent.attrs.get('data-lite-alt')))
        lines.append('  after: ' + following(n)[:1500])
    elif n.tag == 'span' and not B.html_text(dom.inner(n)):
        sibs = n.parent.children; nxt = sibs[sibs.index(n)+1] if sibs.index(n)+1 < len(sibs) else None
        gap = h[n.end:nxt.start] if nxt else ''
        lines.append('  empty span; gap before next=%r; next <%s class=%s data-lite=%s alt=%s>' % (gap, nxt.tag, nxt.attrs.get('class'), nxt.attrs.get('data-lite'), nxt.attrs.get('data-lite-alt')))
        lines.append('  next text: ' + dom.text(nxt)[:1500])
    else:
        lines.append('  text: ' + dom.text(n)[:1200])
    return '\n'.join(lines)

def dump_links(block_node, label):
    print('=' * 20, label)
    for a in [x for x in dom.nodes if x.tag == 'a' and x.start > block_node.start and x.end <= block_node.end]:
        href = a.attrs.get('href', '')
        tr = next((p for p in a.ancestors() if p.tag == 'tr'), None)
        row = dom.text(tr.children[0])[:30] if tr is not None else ''
        print('\n- [%s] <a href=%s class=%s>%s</a>' % (row, href, a.attrs.get('class'), dom.text(a)))
        if href.startswith('#'):
            print(describe(href[1:]))

gs = dom.by_id['group-situations']
tbl = next(x for x in dom.nodes if x.tag == 'table' and 'situations' in x.classes())
dump_links(tbl, 'situations table')
tasks = next(x for x in dom.nodes if x.tag == 'nav' and 'tasks' in x.classes())
dump_links(tasks, 'cover tasks')
