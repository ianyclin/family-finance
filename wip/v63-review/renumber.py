# -*- coding: utf-8 -*-
"""v7.0 全書連號（28 節）的一次性腳本。留著備查，不是常態工具。

做兩件事：
  B1  每個 section 的 h2 都有 <span class="num">新號</span>（沒有的補上，有的改數字）；
      group-* 六個分組節維持沒有節號。
  B2  全書 <a class="xref" href="#X">純數字</a> 的錨文字，依 href 目標 id 所在的節查表重寫。
      **不是**「舊數字＋3」的文字取代——同一個數字在書裡還有很多不是節號的用途。

用法：
  python3 wip/v63-review/renumber.py guide/index.html          # 只報告，不寫檔
  python3 wip/v63-review/renumber.py guide/index.html --write   # 實際改寫
  python3 wip/v63-review/renumber.py --check-numbers <改前.html> <改後.html>
      B11 的驗證：把兩份都「把節號遮掉」（span.num／map-num／數字 xref 錨文字／
      純文字的「第 N 節」都換成 §），再跑 tools/v7_check.py numbers。
      除了節號以外的阿拉伯數字 token 多重集合必須逐節完全相同。
  python3 wip/v63-review/renumber.py --make-allow <舊基準.html> <改後.html> <base-allow.json> <out.json>
      B11 的第二件事：把連號造成的 LOST 整理成 allow 檔（不手打幾百條）。
"""
import json
import os
import re
import subprocess
import sys
import tempfile

# id -> v7.0 的顯示節號（spec-v7-renumber.md 的表）
NUM = {
    'ten': 1, 'start': 2, 'why': 3,
    's1': 4, 's2': 5, 's3': 6, 's4': 7, 's5': 8,
    's6': 9, 's7': 10, 's8': 11, 's9': 12, 's10': 13,
    's11': 14, 'cases': 15, 's12': 16, 's13': 17, 'sidepaths': 18,
    'firstmonth': 19, 'steps': 20, 'products': 21, 'costs': 22,
    'annual': 23, 'lifecycle': 24, 'withdraw': 25,
    'glossary': 26, 'toolbox': 27, 'methods': 28,
}


def section_spans(h):
    """[(start, end, id)]；本書的 <section> 不巢狀（34 個開、34 個關）。"""
    opens = [(m.start(), m.group(1)) for m in
             re.finditer(r'<section\b[^>]*\bid="([^"]+)"', h)]
    spans = []
    for i, (st, sid) in enumerate(opens):
        en = opens[i + 1][0] if i + 1 < len(opens) else len(h)
        spans.append((st, en, sid))
    return spans


def section_of(spans, pos):
    for st, en, sid in spans:
        if st <= pos < en:
            return sid
    return None


def run(path, write):
    h = open(path, encoding='utf-8').read()
    spans = section_spans(h)
    ids = [s[2] for s in spans]
    assert len(ids) == 34, ids
    for sid in NUM:
        assert sid in ids, sid
    for sid in ids:
        assert sid in NUM or sid.startswith('group-'), sid

    # id="…" 出現的位置 -> 所在節
    id_home = {}
    for m in re.finditer(r'(?<![\w-])id="([^"]+)"', h):
        id_home[m.group(1)] = section_of(spans, m.start())

    # ---------------------------------------------------------------- B1
    b1 = []
    out = []
    last = 0
    for st, en, sid in spans:
        m = re.search(r'<h2\b[^>]*>', h[st:en])
        assert m, sid
        hs = st + m.start()
        he = st + h[st:en].index('</h2>', m.end())
        head = h[hs:he + len('</h2>')]
        if sid.startswith('group-'):
            assert 'class="num"' not in head, sid
            continue
        n = str(NUM[sid])
        old = re.search(r'<span class="num">(\d+)</span>', head)
        if old:
            if old.group(1) == n:
                continue
            new_head = head.replace(old.group(0), '<span class="num">%s</span>' % n, 1)
            b1.append((sid, old.group(1), n, '改'))
        else:
            new_head = head.replace(m.group(0), m.group(0) + '<span class="num">%s</span>' % n, 1)
            b1.append((sid, '—', n, '補'))
        out.append(h[last:hs]); out.append(new_head); last = he + len('</h2>')
    out.append(h[last:])
    h = ''.join(out)

    # ---------------------------------------------------------------- B2
    b2 = []
    miss = []

    def fix(m):
        href, txt = m.group(1), m.group(2)
        if not re.fullmatch(r'\d+', txt):
            # 盲點（v7 第四輪裁判④）：錨文字不是「整串數字」但裡面寫了節號的連結（例如
            # <a class="xref" href="#plan-table">計畫表在第 11 節</a>）在這裡被原封放過，要人工改。
            # 補救在哨兵端：tools/lite_sentinels.py 的 check_xref_numbers 現在也查錨文字裡的「第 N 節」。
            return m.group(0)
        home = id_home.get(href)
        if home is None or home not in NUM:
            miss.append((href, txt, home))
            return m.group(0)
        n = str(NUM[home])
        if n != txt:
            b2.append((href, home, txt, n))
        return '<a class="xref" href="#%s">%s</a>' % (href, n)

    h2 = re.sub(r'<a class="xref" href="#([\w-]+)">([^<]*)</a>', fix, h)

    print('== B1 h2 span.num（%d 節）==' % len(b1))
    for sid, o, n, how in b1:
        print('  %-12s %-4s -> %-3s (%s)' % (sid, o, n, how))
    print('== B2 a.xref 錨文字（%d 處改號）==' % len(b2))
    by_t = {}
    for href, home, o, n in b2:
        by_t.setdefault((href, home, o, n), 0)
        by_t[(href, home, o, n)] += 1
    for (href, home, o, n), c in sorted(by_t.items(), key=lambda x: (x[0][1], x[0][0])):
        print('  #%-16s (節 %-10s) %-3s -> %-3s  x%d' % (href, home, o, n, c))
    if miss:
        print('!! 查不到目標所在節的數字 xref：')
        for x in miss:
            print('   ', x)
    if write:
        open(path, 'w', encoding='utf-8').write(h2)
        print('wrote', path)
    else:
        print('(dry run，沒有寫檔)')
    return 1 if miss else 0


# ---------------------------------------------------------------- B11 驗證

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V7CHECK = os.path.join(ROOT, 'tools', 'v7_check.py')


def mask_section_numbers(h):
    """把所有「節號」換成 §，其餘一個字不動。遮四種寫法：
    h2 的 span.num、組地圖的 span.map-num、數字錨文字的 a.xref、純文字的「第 N 節」
    （含「第 2、4、5 節」與「第 1–10 節」這種連號與範圍）。"""
    h = re.sub(r'(<span class="num">)\d+(</span>)', r'\1§\2', h)
    h = re.sub(r'(<span class="map-num">)\d+(</span>)', r'\1§\2', h)
    h = re.sub(r'(<a class="xref" href="#[\w-]+">)\d+(</a>)', r'\1§\2', h)
    h = re.sub(r'第\s*\d+(?:\s*[、～–—-]\s*\d+)*\s*節', '第§節', h)
    return h


def cmd_check_numbers(before, after):
    tmp = tempfile.mkdtemp(prefix='renumber-check-')
    paths = []
    for tag, src in (('before', before), ('after', after)):
        p = os.path.join(tmp, tag + '.html')
        open(p, 'w', encoding='utf-8').write(mask_section_numbers(open(src, encoding='utf-8').read()))
        paths.append(p)
    print('遮掉節號後比數字：%s → %s' % (before, after))
    r = subprocess.run([sys.executable, V7CHECK, 'numbers'] + paths)
    return r.returncode


def cmd_make_allow(baseline, after, base_allow, out):
    """allow 檔 = base_allow 的條目 + 這次連號造成的每節 LOST。
    只在 --check-numbers 已經證明「除了節號，數字一個沒少」之後才可以用。"""
    r = subprocess.run([sys.executable, V7CHECK, 'numbers', baseline, after,
                        '--allow-file', base_allow], capture_output=True, text=True)
    sec = None
    extra = []
    for line in r.stdout.splitlines():
        m = re.match(r'## (\S+)', line)
        if m:
            sec = m.group(1); continue
        m = re.match(r'\s+LOST : (\{.*\})', line)
        if m and sec:
            for tok, n in sorted(eval(m.group(1)).items()):
                extra.append({'section': sec, 'token': tok, 'count': n,
                              'reason': 'v7.0 全書 28 節連號：這一節裡「第 %s 節」的節號變成別的數字。'
                                        '連號只改節號，其餘數字一個沒動——'
                                        '驗證見 wip/v63-review/renumber.py --check-numbers'
                                        '（把兩份的節號都遮成 § 之後，逐節的數字 token 多重集合完全相同）。' % tok})
    base = json.load(open(base_allow, encoding='utf-8'))
    entries = base['allow'] if isinstance(base, dict) else base
    payload = {
        '_comment': 'v7_check.py numbers 的允許清單（v7.0 連號批建立）。內容＝'
                    + os.path.basename(base_allow)
                    + ' 的所有條目 ＋ 全書 28 節連號造成的節號 token 差異（由 '
                      'wip/v63-review/renumber.py --make-allow 產生，沒有手打）。'
                      'v7.0 以後拿 _baseline_v631.html 當基準時用這一份，取代 '
                      + os.path.basename(base_allow) + '。',
        'allow': entries + extra,
    }
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s：舊條目 %d 筆 ＋ 連號條目 %d 筆' % (out, len(entries), len(extra)))
    return 0


if __name__ == '__main__':
    if '--check-numbers' in sys.argv:
        i = sys.argv.index('--check-numbers')
        sys.exit(cmd_check_numbers(sys.argv[i + 1], sys.argv[i + 2]))
    if '--make-allow' in sys.argv:
        i = sys.argv.index('--make-allow')
        sys.exit(cmd_make_allow(*sys.argv[i + 1:i + 5]))
    sys.exit(run(sys.argv[1], '--write' in sys.argv))
