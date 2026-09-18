#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/v7_check.py 的自測。用小段 HTML 字串測五個子命令的核心邏輯。
用法：python3 tools/test_v7_check.py（不需要參數，也不讀 guide/index.html）
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'v7_check.py')
spec = importlib.util.spec_from_file_location('v7_check', TOOL)
v7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)

TMP = tempfile.mkdtemp()
fails = 0


def expect(name, cond, detail=''):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(detail)))
    if not cond:
        fails += 1


def w(name, text):
    p = os.path.join(TMP, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    return p


def run(*argv):
    r = subprocess.run([sys.executable, TOOL] + list(argv), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def rows_of(path):
    return {r['id']: r for r in v7.parse(path).rows()}


# ---------------------------------------------------------------- mainline
MAIN_HTML = '''<html><body>
<header class="cover" id="top"><h1>封面標題</h1><p>一句話介紹。</p></header>
<nav class="toc" id="toc"><ul><li><a href="#s1">第一節</a></li></ul></nav>
<main>
<section class="part" id="s1"><h2>第一節</h2>
<p>主線一句。</p>
<p class="small">小字一句。</p>
<p class="note">註解一句。</p>
<div class="source-card">來源卡 2020 年。</div>
<figure><figcaption>圖說一句。</figcaption></figure>
<div class="story">黃框一句。</div>
<details class="more"><summary>想深入</summary><p>摺疊內文。</p><p class="small">摺疊裡的小字。</p></details>
<script>var x = "腳本文字";</script>
<style>.x{content:"樣式文字"}</style>
<svg viewBox="0 0 10 10"><text x="1" y="2">圖上文字 999</text></svg>
</section>
</main>
<footer><p>頁尾文字</p></footer>
</body></html>'''
main_path = w('main.html', MAIN_HTML)
R = rows_of(main_path)

expect('mainline: 三個節（cover／toc／s1）依 DOM 順序',
       [r['id'] for r in v7.parse(main_path).rows()] == ['cover', 'toc', 's1'], list(R))
expect('mainline: header#top.cover 記成 cover，全部算主線',
       R['cover'] == {'id': 'cover', 'total': 10, 'folded': 0, 'small': 0, 'story': 0, 'mainline': 10}, R.get('cover'))
expect('mainline: nav#toc 記成 toc', R['toc']['total'] == 3 and R['toc']['mainline'] == 3, R.get('toc'))
# s1：h2(3)+主線(5) 是主線；small(5)+note(5)+source-card(9)+figcaption(5)=24 是小字；
# story(5)；details 內 summary(3)+內文(5)+小字(7)=15 全算 folded；script/style/svg 不算。
expect('mainline: small/note/source-card/figcaption 歸 small', R['s1']['small'] == 24, R['s1'])
expect('mainline: details 內的一切（含裡面的 small）歸 folded', R['s1']['folded'] == 15, R['s1'])
expect('mainline: div.story 歸 story', R['s1']['story'] == 5, R['s1'])
expect('mainline: total 不含 script/style/svg', R['s1']['total'] == 52, R['s1'])
expect('mainline: mainline = total − folded − small − story', R['s1']['mainline'] == 8, R['s1'])
expect('mainline: section 外的文字（footer）不進任何節', v7.parse(main_path).outside == 4,
       v7.parse(main_path).outside)

# 分類互斥：story 裡的 small 只算一次（本工具的優先序 folded > story > small）
ov = w('ov.html', '<section id="x"><div class="story"><p class="small">一二三四五</p></div></section>')
Rov = rows_of(ov)['x']
expect('mainline: story 裡的 small 不重複扣（story=5, small=0, mainline=0）',
       (Rov['story'], Rov['small'], Rov['mainline']) == (5, 0, 0), Rov)

rc, out = run('mainline', main_path, '--json', os.path.join(TMP, 'm.json'))
j = json.load(open(os.path.join(TMP, 'm.json'), encoding='utf-8'))
expect('mainline CLI: exit 0 且寫出 JSON',
       rc == 0 and j['totals']['mainline'] == 21 and len(j['sections']) == 3, out)

# ----------------------------------------------------------------- numbers
expect('numbers: 千分位逗號去掉後比較', v7.tokens('每月 5,000 元')['5000'] == 1, v7.tokens('每月 5,000 元'))
expect('numbers: 尾端的 % 萬 年 不進 token',
       dict(v7.tokens('跌 10%、3 萬、2020 年')) == {'10': 1, '3': 1, '2020': 1}, v7.tokens('跌 10%、3 萬、2020 年'))
expect('numbers: 小數點與負號（- 與 −）',
       dict(v7.tokens('−1.5 與 -2 與 1,234.5')) == {'-1.5': 1, '-2': 1, '1234.5': 1},
       v7.tokens('−1.5 與 -2 與 1,234.5'))
expect('numbers: 5/25 是兩個 token', dict(v7.tokens('5/25')) == {'5': 1, '25': 1}, v7.tokens('5/25'))
glue = w('glue.html', '<section id="g"><p>共 5</p><p>3 種</p></section>')
expect('numbers: 相鄰標籤不會把 5 和 3 黏成 53',
       dict(v7.tokens(v7.parse(glue).section_text()['g'])) == {'5': 1, '3': 1},
       v7.parse(glue).section_text()['g'])

BEFORE = '''<section id="a"><h2>A</h2><p>每月 5,000 元，跌 10% 時照常投入。年份 2020。</p>
<details><summary>想深入</summary><p>摺疊裡的 42。</p></details>
<div class="source-card">來源 2019 年報告。</div></section>
<section id="b"><h2>B</h2><p>只有 7 天。</p></section>'''
AFTER = '''<section id="a"><h2>A</h2><p>每月 5,000 元，照常投入。</p>
<details><summary>想深入</summary><p>摺疊裡的 42。</p></details>
<div class="source-card">來源 2019 年報告。</div></section>
<section id="b"><h2>B</h2><p>只有 7 天。跌 10% 時照常投入。</p></section>'''
bpath = w('before.html', BEFORE)
apath = w('after.html', AFTER)
order, res = v7.diff_numbers(v7.parse(bpath).section_text(), v7.parse(apath).section_text())
expect('numbers: 搬到別節的 token 判成 MOVED 而不是 LOST',
       res['a']['moved'] == {'10': {'b': 1}}, res['a'])
expect('numbers: 真的不見的 token 留在 LOST', dict(res['a']['lost']) == {'2020': 1}, res['a'])
expect('numbers: details 與 source-card 的數字有被納入比較範圍',
       '42' in v7.parse(bpath).section_text()['a'] and '2019' in v7.parse(bpath).section_text()['a'])
expect('numbers: 沒動的節不報 LOST', dict(res['b']['lost']) == {}, res['b'])

rc, out = run('numbers', bpath, apath)
expect('numbers CLI: 有 LOST → exit 1', rc == 1 and 'LOST' in out and 'MOVED: 10 x1 -> b' in out, out)
rc, out = run('numbers', bpath, bpath)
expect('numbers CLI: 自己比自己 → exit 0', rc == 0 and 'no differences' in out, out)

allow = w('allow.json', json.dumps([{'section': 'a', 'token': '2020', 'reason': '年份重複，移層時併掉'}]))
rc, out = run('numbers', bpath, apath, '--allow-file', allow)
expect('numbers CLI: --allow-file 放行後 exit 0', rc == 0 and 'ALLOWED: 2020' in out, out)
rc, out = run('numbers', bpath, apath, '--section', 'b')
expect('numbers CLI: --section 只看指定的節 → 這裡只有 ADDED，exit 0',
       rc == 0 and '## b' in out and '## a' not in out, out)
rc, out = run('numbers', bpath, apath, '--section', 'a', 'b')
expect('numbers CLI: --section 可給多個 id', rc == 1 and '## a' in out and '## b' in out, out)
rc, out = run('numbers', bpath, apath, '--section', 'nope')
expect('numbers CLI: 不存在的 section id → exit 1', rc == 1 and 'unknown section' in out, out)

# 整節搬家：a 整節消失、內容併進 b
GONE = '<section id="b"><h2>B</h2><p>只有 7 天。每月 5,000 元，跌 10% 時照常投入。年份 2020。摺疊裡的 42。來源 2019 年報告。</p></section>'
gpath = w('gone.html', GONE)
order2, res2 = v7.diff_numbers(v7.parse(bpath).section_text(), v7.parse(gpath).section_text())
expect('numbers: 整節搬走時每個 token 都判 MOVED，沒有真 LOST',
       dict(res2['a']['lost']) == {} and set(res2['a']['moved']) == {'5000', '10', '2020', '42', '2019'},
       res2['a'])

# ------------------------------------------------------------------ budget
bud_ok = w('bud_ok.json', json.dumps({'s1': 8, 'cover': 10, '_total_max': 21}))
bud_bad = w('bud_bad.json', json.dumps({'s1': 5, '_total_max': 10}))
bud_missing = w('bud_missing.json', json.dumps({'nope': 100}))
rc, out = run('budget', main_path, bud_ok)
expect('budget: 剛好等於上限不算超過 → exit 0', rc == 0 and 'BUDGET OK' in out, out)
rc, out = run('budget', main_path, bud_bad)
expect('budget: 超過的節列出來 → exit 1',
       rc == 1 and 'OVER' in out and 's1' in out and '_total_max' in out, out)
rc, out = run('budget', main_path, bud_missing)
expect('budget: budget 裡的節在書裡找不到 → exit 1', rc == 1 and 'MISSING SECTION: nope' in out, out)

# ---------------------------------------------------------------- planstep
PS_OK = '''<section id="s2"><h2>S2</h2>
<div class="planstep" data-plan="C10"><p class="planstep-title">你的計畫・C 區</p><p>小安寫：每月 5,000 元。</p></div>
<p class="decision">本節行動。</p></section>
<section id="s5"><h2>S5</h2>
<div class="planstep" data-plan="E15"><p class="planstep-title">你的計畫・E 區</p><p>你寫：＿＿</p></div>
</section>'''
ps_ok = w('ps_ok.html', PS_OK)
d = v7.parse(ps_ok)
expect('planstep: 列出 section id 與 data-plan',
       [(x['section'], x['data_plan']) for x in d.plansteps] == [('s2', 'C10'), ('s5', 'E15')], d.plansteps)
expect('planstep: 沒有 p.decision 的節不算錯', all(not v7.planstep_problems(x) for x in d.plansteps))
rc, out = run('planstep', ps_ok)
expect('planstep CLI: 合法 → exit 0', rc == 0 and 'PLANSTEP OK' in out and 'planstep 2 個' in out, out)

rc, out = run('planstep', w('ps_none.html', '<section id="s1"><p>沒有 planstep。</p></section>'))
expect('planstep CLI: 書裡還沒有 planstep → 0 個、exit 0',
       rc == 0 and 'planstep 0 個' in out and 'PLANSTEP OK' in out, out)

CASES = [
    ('在 p.decision 之後',
     '<section id="s2"><p class="decision">本節行動。</p>'
     '<div class="planstep" data-plan="C10"><p class="planstep-title">t</p></div></section>',
     '在同一節的 p.decision 之後'),
    ('缺 data-plan',
     '<section id="s2"><div class="planstep"><p class="planstep-title">t</p></div>'
     '<p class="decision">行動</p></section>',
     '缺 data-plan'),
    ('沒有 planstep-title',
     '<section id="s2"><div class="planstep" data-plan="C10"><p>t</p></div></section>',
     'p.planstep-title 有 0 個'),
    ('兩個 planstep-title',
     '<section id="s2"><div class="planstep" data-plan="C10">'
     '<p class="planstep-title">t</p><p class="planstep-title">t2</p></div></section>',
     'p.planstep-title 有 2 個'),
    ('在 details 裡',
     '<section id="s2"><details><div class="planstep" data-plan="C10">'
     '<p class="planstep-title">t</p></div></details></section>',
     '在 details 內'),
    ('在 div.story 裡',
     '<section id="s2"><div class="story"><div class="planstep" data-plan="C10">'
     '<p class="planstep-title">t</p></div></div></section>',
     '在 div.story 內'),
    ('在 figure 裡',
     '<section id="s2"><figure><div class="planstep" data-plan="C10">'
     '<p class="planstep-title">t</p></div></figure></section>',
     '在 figure 內'),
    ('不在任何 section 內',
     '<main><div class="planstep" data-plan="C10"><p class="planstep-title">t</p></div></main>',
     '不在任何 section 內'),
]
for label, html, msg in CASES:
    rc, out = run('planstep', w('ps_%s.html' % abs(hash(label)), html))
    expect('planstep CLI: %s → exit 1' % label, rc == 1 and msg in out and 'PLANSTEP FAILED' in out, out)

# 同一節裡，decision 之前的 planstep 合法、之後的不合法（兩個一起出現）
mixed = w('ps_mixed.html',
          '<section id="s2"><div class="planstep" data-plan="A"><p class="planstep-title">t</p></div>'
          '<p class="decision">行動</p>'
          '<div class="planstep" data-plan="B"><p class="planstep-title">t</p></div></section>')
rc, out = run('planstep', mixed)
expect('planstep CLI: 同節一前一後，只有後面那個紅',
       rc == 1 and 'planstep 2 個，有問題 1 個' in out, out)

# ----------------------------------------------------------------- anchors
A_BEFORE = '<section id="s1"><span id="keep"></span><span id="gone"></span></section>'
A_AFTER_OK = '<section id="s1"><span id="keep"></span><span id="gone"></span><a href="#keep">x</a></section>'
A_AFTER_BAD = '<section id="s1"><span id="keep"></span><a href="#nowhere">x</a></section>'
ab = w('anch_b.html', A_BEFORE)
ao = w('anch_ok.html', A_AFTER_OK)
axx = w('anch_bad.html', A_AFTER_BAD)
rc, out = run('anchors', ab, ao)
expect('anchors: id 都還在、href 都有對應 → exit 0', rc == 0 and 'ANCHORS OK' in out, out)
rc, out = run('anchors', ab, axx)
expect('anchors: 消失的 id 與壞掉的 href 都列出來 → exit 1',
       rc == 1 and 'MISSING IDS (1)' in out and 'gone' in out
       and 'BROKEN HREFS (1)' in out and '#nowhere' in out, out)
rc, out = run('anchors', ab, w('anch_hash.html', '<section id="s1"><span id="keep"></span>'
                               '<span id="gone"></span><a href="#">回頂端</a></section>'))
expect('anchors: href="#" 不算壞連結', rc == 0 and 'ANCHORS OK' in out, out)

# data-id 不可以被當成 id（否則會遮掉壞連結）
rc, out = run('anchors', w('anch_b2.html', '<section id="s1"></section>'),
              w('anch_dataid.html', '<section id="s1"><p data-id="x"></p><a href="#x">x</a></section>'))
expect('anchors: data-id 不算 id → 壞連結照樣紅', rc == 1 and '#x' in out, out)

print('RESULT', 'ALL PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
