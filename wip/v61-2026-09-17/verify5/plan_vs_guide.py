# 施工文件 §6.3（group-situations）與 §7.1（封面入口）的 HTML 樣板，和 guide 逐字比對；入口文字不得以節名開頭
import sys, re, unicodedata
sys.path.insert(0, 'tools')
import build_lite as B
plan = open('wip/v61-2026-09-17/restructure/migration-plan.md', encoding='utf-8').read()
g = open(sys.argv[1] if len(sys.argv) > 1 else 'guide/index.html', encoding='utf-8').read()
blocks = re.findall(r'```html\n(.*?)```', plan, re.S)
sit = next(b for b in blocks if 'id="group-situations"' in b)
tasks = next(b for b in blocks if 'class="tasks"' in b)
for label, b in [('group-situations', sit), ('tasks', tasks)]:
    lines = [l for l in b.strip('\n').split('\n')]
    missing = [l for l in lines if l not in g]
    print(label, 'plan lines', len(lines), 'missing in guide:', len(missing))
    for l in missing: print('   MISSING:', l[:200])
# guide 裡 group-situations 整節和樣板比
m = re.search(r'<section class="part" id="group-situations">.*?</section>', g, re.S)
print('group-situations identical to plan block:', m.group(0).strip() == sit.strip())
if m.group(0).strip() != sit.strip():
    import difflib
    for l in difflib.unified_diff(sit.strip().split('\n'), m.group(0).strip().split('\n'), lineterm='', n=0): print('  ', l[:300])
m2 = re.search(r'<nav class="tasks".*?</nav>', g, re.S)
print('tasks identical to plan block:', m2.group(0).strip() == tasks.strip())
# 入口文字 vs 節名
dom = B.Dom(g)
names = B.section_names(dom)
comp = lambda s: re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))
for a in re.finditer(r'<a ([^>]*)>(.*?)</a>', m2.group(0)):
    t = comp(B.html_text(a.group(2)))
    hits = [(i, n) for i, n in names.items() if t.startswith(comp(n)[:6]) or comp(n).startswith(t[:6])]
    near = [(i, n, len(__import__('os').path.commonprefix([t, comp(n)]))) for i, n in names.items()]
    near = max(near, key=lambda x: x[2])
    print('entry %-40s hits=%s  longest common prefix=%s(%d)' % (t, hits, near[1], near[2]))
