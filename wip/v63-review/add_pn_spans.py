# -*- coding: utf-8 -*-
"""一次性腳本：替人名加專名號 <span class="pn">…</span>（作者 2026-09-21 指示）。

規格：wip/v63-review/spec-v7-author-r1.md 的 C 項，＋派工當場擴大的範圍
（「真實人名可加，英文不用」）。

做法：不用裸字串取代（會改到 title／aria-label 等屬性），而是掃一遍 HTML，
只在「標籤外面的文字節點」動手；`<script>`／`<style>`／`<svg>`／`<title>` 裡面
和 HTML 註解（短稿檔頭的 note）一律跳過。屬性值裡的 `>` 靠引號狀態機處理。

用法：python3 wip/v63-review/add_pn_spans.py [--check]
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GUIDE = os.path.join(ROOT, 'guide', 'index.html')
ALT_DIR = os.path.join(ROOT, 'lite', 'alt')

SKIP_ELEMS = {'script', 'style', 'svg', 'title', 'textarea'}

# 每一次出現都包（先確認過全書的每一處都是這個人）
GLOBAL_NAMES = [
    # 示範人物（虛構）
    '小安', '阿凱', '小芸', '阿哲', '陳大哥',
    # 真實人名：中文譯名、本名、筆名
    '巴菲特', '湯姆．安德森', '黃嘉斌',
    '陳逸朴', '理財館長', '陳震奇', '狂徒', '周冠男', '張遠',
]

# 只包指定的那一處（同一個詞在別處是書名、站名或普通名詞）
ONE_OFFS = [
    # 綠角：書名《綠角的基金8堂課》與部落格名「綠角財經筆記」不包
    ('版，綠角，經濟日報 2016',
     '版，<span class="pn">綠角</span>，經濟日報 2016'),
    ('<li><strong>綠角</strong>：<a href="https://greenhornfinancefootnote',
     '<li><strong><span class="pn">綠角</span></strong>：<a href="https://greenhornfinancefootnote'),
    # 老人：只在指 Podcast 主持人時包
    ('，主持人老人。中文 Podcast',
     '，主持人<span class="pn">老人</span>。中文 Podcast'),
    # 指數三寶飯：只包 methods 的內文那一處
    ('<li><strong>作者（指數三寶飯）：</strong>',
     '<li><strong>作者（<span class="pn">指數三寶飯</span>）：</strong>'),
]

CSS_ANCHOR = ('a.term{color:var(--blue);text-decoration:none;'
              'border-bottom:1px dotted var(--blue)}')
CSS_ADD = ('.pn{text-decoration:underline;text-decoration-thickness:1px;'
           'text-underline-offset:.22em;text-decoration-color:currentColor}'
           'a .pn{text-decoration:none}')

PAT = re.compile('|'.join(re.escape(n) for n in
                          sorted(GLOBAL_NAMES, key=len, reverse=True)))


def end_of_tag(s, i):
    """回傳 s[i] 這個 '<' 開頭的標籤／註解／宣告的結束位置（不含）。"""
    if s.startswith('<!--', i):
        j = s.find('-->', i)
        return len(s) if j < 0 else j + 3
    if s.startswith('<!', i) or s.startswith('<?', i):
        j = s.find('>', i)
        return len(s) if j < 0 else j + 1
    j = i + 1
    q = None
    while j < len(s):
        ch = s[j]
        if q:
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif ch == '>':
            return j + 1
        j += 1
    return len(s)


def wrap(html, counter):
    """只改文字節點。counter 是 dict，記每個名字包了幾處。"""
    out = []
    i = 0
    skip = []          # 目前在哪些要跳過的元素裡
    n = len(html)
    while i < n:
        lt = html.find('<', i)
        if lt < 0:
            lt = n
        text = html[i:lt]
        if text:
            if skip:
                out.append(text)
            else:
                def rep(m):
                    counter[m.group(0)] = counter.get(m.group(0), 0) + 1
                    return '<span class="pn">%s</span>' % m.group(0)
                out.append(PAT.sub(rep, text))
        if lt >= n:
            break
        end = end_of_tag(html, lt)
        tag = html[lt:end]
        out.append(tag)
        if not tag.startswith('<!'):
            m = re.match(r'</?\s*([A-Za-z][A-Za-z0-9]*)', tag)
            if m:
                name = m.group(1).lower()
                if name in SKIP_ELEMS:
                    if tag.startswith('</'):
                        if skip and skip[-1] == name:
                            skip.pop()
                    elif not tag.rstrip().endswith('/>'):
                        skip.append(name)
        i = end
    return ''.join(out)


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def process(path, add_css, counter):
    h = io.open(path, encoding='utf-8').read()
    if add_css:
        for old, new in ONE_OFFS:
            c = h.count(old)
            assert c == 1, 'ONE_OFF 出現 %d 次（要剛好 1 次）：%r' % (c, old[:40])
            h = h.replace(old, new)
        assert h.count(CSS_ANCHOR) == 1, 'CSS 錨點不唯一'
        h = h.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_ADD)
    before_text = strip_tags(h)
    h = wrap(h, counter)
    after_text = strip_tags(h)
    assert before_text == after_text, '%s：去掉標籤以後的文字變了' % path
    return h


def main():
    check = '--check' in sys.argv
    counter = {}
    files = [(GUIDE, True)]
    for fn in sorted(os.listdir(ALT_DIR)):
        if fn.endswith('.html'):
            files.append((os.path.join(ALT_DIR, fn), False))
    for path, add_css in files:
        new = process(path, add_css, counter)
        old = io.open(path, encoding='utf-8').read()
        if new != old and not check:
            io.open(path, 'w', encoding='utf-8').write(new)
        print('%-44s %s' % (os.path.relpath(path, ROOT),
                            'changed' if new != old else 'unchanged'))
    print()
    for name in GLOBAL_NAMES:
        print('%-8s %d' % (name, counter.get(name, 0)))
    print('one-offs  %d（綠角 x2、老人 x1、指數三寶飯 x1）' % len(ONE_OFFS))


if __name__ == '__main__':
    main()
