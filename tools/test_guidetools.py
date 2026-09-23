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
    # v7 第五輪：來源卡改成 <details class="source-card" data-print="open">，屬性放在 class 前面也要認得
    h = h.replace('<details class="source-card"', '<details data-lite="skip" class="source-card"')
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

# --- v7 第五輪：兩級重點句（黃線 mark.key／淡紅線 mark.key.top）
def field(line, name):
    t = line.split()
    return int(t[t.index(name) + 1])

expect('counts line reports markstop', 'markstop' in counts0, counts0)
rc, out = run_check(base.replace('</body>', '<p><mark class="key top">x</mark><mark class="key">y</mark></p></body>'))
expect('marks +2 / markstop +1',
       rc == 0 and field(out.splitlines()[0], 'marks') == field(counts0, 'marks') + 2
       and field(out.splitlines()[0], 'markstop') == field(counts0, 'markstop') + 1, out)

for wrap, label in (('<details><summary>s</summary><p><mark class="key">x</mark></p></details>', 'details'),
                    ('<div class="story"><p><mark class="key top">x</mark></p></div>', 'div.story'),
                    ('<p class="explain"><mark class="key">x</mark></p>', 'p.explain'),
                    ('<p class="small"><mark class="key">x</mark></p>', 'p.small'),
                    ('<h3><mark class="key">x</mark></h3>', 'h3'),
                    ('<h5><mark class="key">x</mark></h5>', 'h5'),
                    ('<figure><figcaption><mark class="key">x</mark></figcaption></figure>', 'figcaption'),
                    ('<table><tr><td><mark class="key top">x</mark></td></tr></table>', 'td')):
    rc, out = run_check(base.replace('</body>', wrap + '</body>'))
    expect('mark in %s -> FAILED' % label, rc == 1 and '重點句放在不准放的容器裡' in out, out)

# 放在 strong／li／p 裡是合法的
rc, out = run_check(base.replace('</body>', '<ul><li><mark class="key"><strong>x</strong></mark></li></ul></body>'))
expect('mark in li>strong -> OK', rc == 0, out)

# --- v7 批 BE：h5 進 TAGS 與容器清單（第 15 節的人物卡用 h5）
rc, out = run_check(base.replace('</body>', '<h5>沒關的小標</body>'))
expect('unbalanced h5 -> FAILED', rc == 1 and 'tag h5' in out, out)
p5 = os.path.join(tmp, 'h5.html')
open(p5, 'w', encoding='utf-8').write(base.replace('</body>', '<h5>小標</h5><p>下一段</p></body>'))
expect('to_text breaks line after </h5>', '小標\n下一段' in gt.to_text(p5))

p2 = os.path.join(tmp, 'two.html')
open(p2, 'w', encoding='utf-8').write(base.replace('</body>', '<p><mark class="key top">頂級句</mark></p></body>'))
expect('to_text turns key top into ★…★', '★頂級句★' in gt.to_text(p2))

# --- v7 第五輪：來源卡改成 <details class="source-card">，to_text 仍要整塊拿掉
sc = base.replace('</body>', '<details class="source-card" data-print="open"><summary>直接來源（1 筆）</summary>'
                             '<a class="source-link" href="#x">來源卡裡的字不該出現在正文</a></details></body>')
p3 = os.path.join(tmp, 'sc.html'); open(p3, 'w', encoding='utf-8').write(sc)
expect('to_text strips details.source-card', '來源卡裡的字不該出現在正文' not in gt.to_text(p3))
expect('to_text keep_sources keeps it', '來源卡裡的字不該出現在正文' in gt.to_text(p3, keep_sources=True))
p4 = os.path.join(tmp, 'sc2.html')
open(p4, 'w', encoding='utf-8').write(base.replace('</body>', '<div class="source-card"><p>舊版來源卡</p></div></body>'))
expect('to_text still strips div.source-card', '舊版來源卡' not in gt.to_text(p4))

print('RESULT', 'ALL PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
