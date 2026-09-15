# -*- coding: utf-8 -*-
"""Tests: guidetools check/text must survive extra attributes (data-lite) on elements.
Usage: python3 test_guidetools.py <guidetools_dir> <guide/index.html>
"""
import sys, os, re, subprocess, tempfile, importlib.util

tooldir, guide = sys.argv[1], sys.argv[2]
tool = os.path.join(tooldir, 'guidetools.py')
spec = importlib.util.spec_from_file_location('gt', tool); gt = importlib.util.module_from_spec(spec); spec.loader.exec_module(gt)
tmp = tempfile.mkdtemp()
fails = 0

def run_check(html):
    p = os.path.join(tmp, 'x.html'); open(p, 'w', encoding='utf-8').write(html)
    r = subprocess.run([sys.executable, tool, 'check', p], capture_output=True, text=True)
    return r.returncode, r.stdout

def expect(name, cond, detail=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + detail))
    if not cond: fails += 1

base = open(guide, encoding='utf-8').read()
rc0, out0 = run_check(base)
counts0 = out0.splitlines()[0]
expect('baseline check OK', rc0 == 0, out0)

# 1. add data-lite AFTER class on every counted element
def add_after(h):
    h = h.replace('<div class="story">', '<div class="story" data-lite="ch8">')
    h = h.replace('<mark class="key">', '<mark class="key" data-lite="ch4">')
    h = h.replace('<span class="later">', '<span class="later" data-lite="skip">')
    h = h.replace('<p class="small">', '<p class="small" data-lite="ch4">')
    h = re.sub(r'<details(?=[\s>])', '<details data-lite="ch9"', h)
    h = h.replace('<a class="term"', '<a class="term" data-lite="x"')
    h = h.replace('<strong>', '<strong data-lite="x">')
    return h
# 2. add data-lite BEFORE class
def add_before(h):
    h = h.replace('<div class="story">', '<div data-lite="ch8" class="story">')
    h = h.replace('<mark class="key">', '<mark data-lite="ch4" class="key">')
    h = h.replace('<span class="later">', '<span data-lite="skip" class="later">')
    h = h.replace('<p class="small">', '<p data-lite="ch4" class="small">')
    h = h.replace('<div class="source-card">', '<div data-lite="skip" class="source-card">')
    h = h.replace('<a class="term"', '<a data-lite="x" class="term"')
    return h

for label, fn in (('attrs-after', add_after), ('attrs-before', add_before)):
    H = fn(base)
    rc, out = run_check(H)
    expect(label + ': check still OK', rc == 0, out)
    expect(label + ': counts unchanged', out.splitlines()[0] == counts0, out.splitlines()[0] + ' vs ' + counts0)
    p = os.path.join(tmp, label + '.html'); open(p, 'w', encoding='utf-8').write(H)
    expect(label + ': text output identical', gt.to_text(p) == gt.to_text(guide))

# 3. errors must still be caught when attributes are present
i = base.find('<div class="story">'); j = base.find('>', i) + 1
term = '<a class="term" href="#g-etf" title="t">ETF</a>'
bad = base[:j] + term + base[j:]
bad_attr = add_after(bad)
rc, out = run_check(bad_attr)
expect('term in story (attr after) -> FAILED', rc == 1 and 'term links inside story boxes: 1' in out, out)
rc, out = run_check(add_before(bad))
expect('term in story (attr before) -> FAILED', rc == 1 and 'term links inside story boxes: 1' in out, out)

# term placed after a nested <div> inside the story box
nested = base[:j] + '<div class="inner" data-lite="x">內層</div>' + term + base[j:]
rc, out = run_check(add_after(nested))
expect('term after nested div inside story -> FAILED', rc == 1 and 'term links inside story boxes: 1' in out, out)

# term inside strong with attributes
k = base.find('<strong>')
bad_strong = base[:k] + '<strong data-lite="x">重點' + '<a data-lite="y" class="term" href="#g-etf">ETF</a>' + '</strong>' + base[k:]
rc, out = run_check(bad_strong)
expect('term in strong (attrs) -> FAILED', rc == 1 and 'term links inside strong: 1' in out, out)

# counts react to added elements with attributes
more = add_after(base).replace('</body>', '<div data-lite="a" class="story">x</div><mark class="key" data-lite="b">y</mark><details data-lite="c"><summary>s</summary></details></body>')
rc, out = run_check(more)
c = dict(zip(out.split()[0:10:2], out.split()[1:10:2]))
c0 = dict(zip(counts0.split()[0:10:2], counts0.split()[1:10:2]))
expect('counts +1 story/mark/details with attrs',
       int(c['story']) == int(c0['story']) + 1 and int(c['marks']) == int(c0['marks']) + 1 and int(c['details']) == int(c0['details']) + 1, out)

# data-id must not be read as an id (would hide broken hrefs / fake duplicates)
dup = base.replace('</body>', '<p data-id="s1">x</p></body>')
rc, out = run_check(dup)
expect('data-id not counted as duplicate id', rc == 0, out)
broken = base.replace('</body>', '<p data-lite-id="nowhere">x</p><a href="#nowhere">x</a></body>')
rc, out = run_check(broken)
expect('href to data-*-id only -> broken href FAILED', rc == 1 and 'broken hrefs' in out, out)

# class value must match exactly: story-title is not a story box
rc, out = run_check(base.replace('</body>', '<div class="story-title" data-lite="x"><a class="term" href="#g-etf">E</a></div></body>'))
expect('class="story-title" not treated as story', rc == 0, out)

print('RESULT', 'ALL PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
