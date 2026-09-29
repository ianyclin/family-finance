#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v7_check.py —— v7.0 改版的獨立檢查工具。只用標準函式庫（html.parser／re）。

用法：
  python3 tools/v7_check.py mainline <html> [--json out.json]
      逐節列出去空白字數：total／folded／small／source／story／mainline／visible，並印全書合計。
      visible＝mainline＋small（手機上一眼看得到的字，摺疊、黃框與來源卡都不算）。
  python3 tools/v7_check.py numbers <before.html> <after.html> [--section id ...] [--allow-file allow.json]
      以 section id 為 key 比對阿拉伯數字 token 多重集合；真正的 LOST 會讓 exit code = 1。
  python3 tools/v7_check.py budget <html> <budget.json> [--section id ...]
      budget.json 形如 {"ten": 600, "why": 900, "_total_max": 70000}；超過的節列出來，exit 1。
      另支援 "_visible_total_max"（全書 mainline＋small 上限）與
      "_visible_small_per_section_max"（每節 small 上限，不含來源卡；
      SMALL_EXEMPT 那幾節與 group-* 不查），以及 "_visible_small_overrides"
      （{"節 id": 上限}，只放行點名的那一節；其他節仍照通用上限查，不會被一起放寬）。
      給了 --section 就只檢查指定的節，兩個全書合計改成只印不判（施工中途全書必然超標）。
  python3 tools/v7_check.py planstep <html>
      檢查每個 div.planstep 的結構與位置；結構錯 exit 1。
  python3 tools/v7_check.py anchors <before.html> <after.html>
      改前的 id 在改後都還在；改後的 href="#…" 都有對應 id。
  python3 tools/v7_check.py xrefs <html> [--notes]
      節的稱呼（批 BQ 起的常設哨兵），三件事：
      (1) 節號與 href 對得上：<a class="xref" href="#X">N</a> 的 N 是數字時，
          X 所屬那一節的 <span class="num"> 必須等於 N；
      (2) 引的標題對得上：第 <a class="xref" href="#X">N</a> 節「T」的 T，必須是那一節
          h2 標題全形冒號前那一截，或出現在 X 指到的那一段裡；
      (3) href 指整節、但 T 剛好是節內某個「帶 id」的小標 → 應該改指那個小標的 id。
      小標沒有 id 的那幾處只記成「注意」，不判紅（要不要加 id 由人決定，--notes 列出來）。

「節」的定義：每個 <section id=…>，另加 header#top.cover（記為 cover）與 nav#toc（記為 toc）。
分類優先序（互斥，一段文字只算一次）：folded > story > source > small；
mainline = total − folded − story − source − small。來源卡（.source-card）自成一欄，
既不算 small 也不算 mainline，也不進 visible。來源卡本身是 <details class="source-card">
（v7 第五輪起預設收起、列印全開）時仍算 source，不算 folded。
"""
import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from html.parser import HTMLParser
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guidetools import strip_appendix  # 批 CX：書末附錄是工作表的複本，解析前拿掉（留 #worksheet 空殼）

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'}
SKIP = {'script', 'style', 'svg'}
SMALL_CLASSES = {'small'}
SOURCE_CLASSES = {'source-card'}
# 這幾節整節就是查表／導覽用的小字，不適用「每節看得到的小字 ≤ N 字」；group-* 分組節同理。
SMALL_EXEMPT = {'glossary', 'toolbox', 'methods', 'cover', 'toc'}

WS_RE = re.compile(r'\s+')
# 連續的數字，可含千分位逗號與小數點，可帶前置負號（- 或 −）。
# 尾端的 %、萬、年 等單位不是數字，自然不會進 token。
NUM_RE = re.compile(r'(?<![\d.,])[-−]?\d+(?:[.,]\d+)*')


def nonws_len(s):
    return len(WS_RE.sub('', s))


def norm_token(t):
    """逗號去掉後比較；全形負號統一成 ASCII。"""
    return t.replace(',', '').replace('−', '-')


def tokens(text):
    return Counter(norm_token(m.group(0)) for m in NUM_RE.finditer(text))


def cls_of(attrs):
    return set((attrs.get('class') or '').split())


class Doc(HTMLParser):
    """走一次 DOM，收集：每節的字數分類與全文、id／href、planstep、p.decision 位置。"""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.stack = []          # [(tag, classes)]
        self.sections = OrderedDict()   # id -> dict
        self.sec_stack = []      # [(stack_index, section_id)]
        self.ps_stack = []       # [(stack_index, planstep_record)]
        self.outside = 0         # 不在任何 section 內的去空白字數
        self.ids = []
        self.hrefs = []
        self.plansteps = []
        self.decision_seq = {}   # section_id -> 該節第一個 p.decision 的文件序號
        self.seq = 0

    # ---- helpers ----------------------------------------------------
    def _cur(self):
        return self.sec_stack[-1][1] if self.sec_stack else None

    def _flags(self):
        """回傳祖先狀態：(skip, in_details, in_story, in_source, in_small, in_figure)。"""
        skip = det = sto = src = sml = fig = False
        for tag, cls in self.stack:
            if tag in SKIP:
                skip = True
            elif tag == 'details' and not (cls & SOURCE_CLASSES):
                # 來源卡 v7 第五輪起本身就是 <details class="source-card">（預設收起、列印全開）。
                # 它仍然自成 source 一欄，不算 folded；裡面另外包的 details 照樣算 folded。
                det = True
            elif tag == 'div' and 'story' in cls:
                sto = True
            elif tag == 'figure':
                fig = True
            if cls & SOURCE_CLASSES:
                src = True
            if (cls & SMALL_CLASSES) or tag == 'figcaption' or (tag == 'p' and 'note' in cls):
                sml = True
        return skip, det, sto, src, sml, fig

    @staticmethod
    def _section_name(tag, attrs, cls):
        i = attrs.get('id')
        if tag == 'section' and i:
            return i
        if tag == 'header' and i == 'top' and 'cover' in cls:
            return 'cover'
        if tag == 'nav' and i == 'toc':
            return 'toc'
        return None

    def _new_section(self, name):
        if name not in self.sections:
            self.sections[name] = {'id': name, 'total': 0, 'folded': 0,
                                   'small': 0, 'source': 0, 'story': 0, 'text': []}
        return self.sections[name]

    # ---- parser callbacks -------------------------------------------
    def handle_starttag(self, tag, attrs):
        self.seq += 1
        a = dict(attrs)
        cls = cls_of(a)
        skip, det, sto, src, sml, fig = self._flags()
        cur = self._cur()

        if not skip:
            if a.get('id'):
                self.ids.append(a['id'])
            href = a.get('href')
            if href and href.startswith('#'):
                self.hrefs.append(href)
            if tag == 'p' and 'decision' in cls and cur is not None:
                self.decision_seq.setdefault(cur, self.seq)
            if tag == 'p' and 'planstep-title' in cls and self.ps_stack:
                self.ps_stack[-1][1]['titles'] += 1

        name = None if skip else self._section_name(tag, a, cls)
        if name:
            self._new_section(name)

        rec = None
        if not skip and tag == 'div' and 'planstep' in cls:
            rec = {'seq': self.seq, 'section': cur, 'data_plan': a.get('data-plan'),
                   'titles': 0, 'in_details': det, 'in_story': sto, 'in_figure': fig}
            self.plansteps.append(rec)

        if tag not in VOID:
            self.stack.append((tag, cls))
            if name:
                self.sec_stack.append((len(self.stack) - 1, name))
            if rec is not None:
                self.ps_stack.append((len(self.stack) - 1, rec))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                while self.sec_stack and self.sec_stack[-1][0] >= i:
                    self.sec_stack.pop()
                while self.ps_stack and self.ps_stack[-1][0] >= i:
                    self.ps_stack.pop()
                return

    def handle_data(self, data):
        skip, det, sto, src, sml, fig = self._flags()
        if skip:
            return
        n = nonws_len(data)
        if n == 0:
            return
        cur = self._cur()
        if cur is None:
            self.outside += n
            return
        r = self.sections[cur]
        r['total'] += n
        if det:
            r['folded'] += n
        elif sto:
            r['story'] += n
        elif src:
            r['source'] += n
        elif sml:
            r['small'] += n
        r['text'].append(data)

    # ---- results -----------------------------------------------------
    def rows(self):
        out = []
        for r in self.sections.values():
            m = r['total'] - r['folded'] - r['story'] - r['source'] - r['small']
            out.append({'id': r['id'], 'total': r['total'], 'folded': r['folded'],
                        'small': r['small'], 'source': r['source'], 'story': r['story'],
                        'mainline': m, 'visible': m + r['small']})
        return out

    def section_text(self):
        """每節全文（含 details／small／source-card／figcaption／table，不含 svg/script/style）。
        各文字節點以換行相接，避免相鄰標籤把兩個數字黏成一個。"""
        return OrderedDict((k, '\n'.join(v['text'])) for k, v in self.sections.items())


def parse(path):
    d = Doc()
    with open(path, encoding='utf-8') as f:
        d.feed(strip_appendix(f.read()))
    d.close()
    return d


# ---------------------------------------------------------------- mainline
def cmd_mainline(args):
    d = parse(args.html)
    rows = d.rows()
    w = max([len(r['id']) for r in rows] + [7])
    fmt_h = '%-*s %8s %8s %8s %8s %8s %9s %8s'
    fmt_r = '%-*s %8d %8d %8d %8d %8d %9d %8d'
    print(fmt_h % (w, 'section', 'total', 'folded', 'small', 'source', 'story',
                   'mainline', 'visible'))
    for r in rows:
        print(fmt_r % (w, r['id'], r['total'], r['folded'], r['small'], r['source'],
                       r['story'], r['mainline'], r['visible']))
    tot = {k: sum(r[k] for r in rows)
           for k in ('total', 'folded', 'small', 'source', 'story', 'mainline', 'visible')}
    print(fmt_r % (w, 'TOTAL', tot['total'], tot['folded'], tot['small'], tot['source'],
                   tot['story'], tot['mainline'], tot['visible']))
    print('outside-of-section %d' % d.outside)
    if args.json:
        payload = {'sections': rows, 'totals': tot, 'outside': d.outside, 'source': args.html}
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('wrote', args.json)
    return 0


# ----------------------------------------------------------------- numbers
def diff_numbers(before, after):
    """before/after：OrderedDict(section_id -> text)。
    回傳 (order, result)；result[sec] = {'lost':Counter, 'moved':{tok:{dest:n}}, 'added':Counter}。"""
    ba = OrderedDict((k, tokens(v)) for k, v in before.items())
    aa = OrderedDict((k, tokens(v)) for k, v in after.items())
    order = list(ba.keys()) + [k for k in aa if k not in ba]

    # 全書層級：改後某節多出來的 token，可以吸收別節的 LOST
    gains = OrderedDict()
    for sec in order:
        g = aa.get(sec, Counter()) - ba.get(sec, Counter())
        if g:
            gains[sec] = g

    result = OrderedDict()
    for sec in order:
        lost = ba.get(sec, Counter()) - aa.get(sec, Counter())
        added = aa.get(sec, Counter()) - ba.get(sec, Counter())
        moved = {}
        real = Counter()
        for tok in sorted(lost):
            need = lost[tok]
            for dest in gains:          # DOM 順序，決定性
                if dest == sec or need <= 0:
                    continue
                avail = gains[dest].get(tok, 0)
                if avail <= 0:
                    continue
                take = min(avail, need)
                gains[dest][tok] = avail - take
                moved.setdefault(tok, OrderedDict())[dest] = take
                need -= take
            if need > 0:
                real[tok] = need
        result[sec] = {'lost': real, 'moved': moved, 'added': added}
    return order, result


def load_allow(path):
    """allow.json：[{"section": ..., "token": ..., "reason": ...}] 或 {"allow": [...]}。
    可選 "count"；沒寫 count 就是允許該節該 token 的所有丟失。"""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get('allow', [])
    out = {}
    for e in data:
        key = (e['section'], norm_token(str(e['token'])))
        out[key] = e.get('count')
    return out


def cmd_numbers(args):
    b = parse(args.before).section_text()
    a = parse(args.after).section_text()
    order, result = diff_numbers(b, a)

    want = None
    if args.section:
        want = [s for grp in args.section for s in grp]
        unknown = [s for s in want if s not in result]
        if unknown:
            print('unknown section: %s' % ', '.join(unknown))
            return 1

    allow = load_allow(args.allow_file) if args.allow_file else {}
    allowed_hits = []
    bad = 0
    shown = 0
    for sec in order:
        if want is not None and sec not in want:
            continue
        r = result[sec]
        lost = Counter(r['lost'])
        for tok in list(lost):
            if (sec, tok) in allow:
                cap = allow[(sec, tok)]
                n = lost[tok] if cap is None else min(cap, lost[tok])
                allowed_hits.append((sec, tok, n))
                lost[tok] -= n
                if lost[tok] <= 0:
                    del lost[tok]
        if not (lost or r['moved'] or r['added']):
            continue
        shown += 1
        print('## %s' % sec)
        if lost:
            print('  LOST :', dict(sorted(lost.items())))
            bad += sum(lost.values())
        for tok in sorted(r['moved']):
            for dest, n in r['moved'][tok].items():
                print('  MOVED: %s x%d -> %s' % (tok, n, dest))
        if r['added']:
            print('  ADDED:', dict(sorted(r['added'].items())))
    for sec, tok, n in allowed_hits:
        print('  ALLOWED: %s x%d in %s' % (tok, n, sec))
    if shown == 0 and not allowed_hits:
        print('no differences')
    print('LOST %d token(s)' % bad)
    return 1 if bad else 0


# ------------------------------------------------------------------ budget
def small_checked(sec_id):
    """這一節要不要查「看得到的小字」上限。"""
    return sec_id not in SMALL_EXEMPT and not sec_id.startswith('group-')


def cmd_budget(args):
    d = parse(args.html)
    rows = {r['id']: r for r in d.rows()}
    with open(args.budget, encoding='utf-8') as f:
        budget = json.load(f)

    want = None
    if args.section:
        want = [s for grp in args.section for s in grp]
        unknown = [s for s in want if s not in rows]
        if unknown:
            print('unknown section: %s' % ', '.join(unknown))
            return 1

    over = []
    missing = []
    for k, limit in budget.items():
        if k.startswith('_'):
            continue
        if want is not None and k not in want:
            continue
        if k not in rows:
            missing.append(k)
            continue
        m = rows[k]['mainline']
        mark = 'OVER' if m > limit else 'ok'
        print('%-16s mainline=%-7d limit=%-7d %s' % (k, m, limit, mark))
        if m > limit:
            over.append((k, m, limit))

    smax = budget.get('_visible_small_per_section_max')
    # 個別放行：只有點名的那一節換上限（例如第 8 節多了兩張主線上的圖，圖說本身就是小字）。
    # 不動通用上限，其他節的警報照舊。
    overrides = budget.get('_visible_small_overrides') or {}
    if smax is not None:
        for k, r in rows.items():
            if want is not None and k not in want:
                continue
            if not small_checked(k):
                continue
            lim = overrides.get(k, smax)
            mark = 'OVER' if r['small'] > lim else 'ok'
            print('%-16s small=%-10d limit=%-7d %s%s'
                  % (k, r['small'], lim, mark, '（個別放行）' if k in overrides else ''))
            if r['small'] > lim:
                over.append((k + ' (small)', r['small'], lim))

    total = sum(r['mainline'] for r in rows.values())
    vtotal = sum(r['visible'] for r in rows.values())
    for label, value, limit, field in (('_total_max', total, budget.get('_total_max'), 'mainline'),
                                       ('_visible_total_max', vtotal, budget.get('_visible_total_max'), 'visible')):
        if limit is None:
            print('%-16s %s=%-7d （budget 沒寫上限）' % ('(book total)', field, value))
            continue
        if want is not None:
            print('%-16s %s=%-7d limit=%-7d skipped(--section)' % (label, field, value, limit))
            continue
        mark = 'OVER' if value > limit else 'ok'
        print('%-16s %s=%-7d limit=%-7d %s' % (label, field, value, limit, mark))
        if value > limit:
            over.append((label, value, limit))

    for k in missing:
        print('MISSING SECTION: %s' % k)
    if over or missing:
        print('BUDGET FAILED (%d over, %d missing)' % (len(over), len(missing)))
        return 1
    print('BUDGET OK')
    return 0


# ---------------------------------------------------------------- planstep
def planstep_problems(rec):
    p = []
    if not rec['data_plan']:
        p.append('缺 data-plan')
    if rec['titles'] != 1:
        p.append('p.planstep-title 有 %d 個（要 1 個）' % rec['titles'])
    if rec['section'] is None:
        p.append('不在任何 section 內')
    if rec['in_details']:
        p.append('在 details 內')
    if rec['in_story']:
        p.append('在 div.story 內')
    if rec['in_figure']:
        p.append('在 figure 內')
    return p


def cmd_planstep(args):
    d = parse(args.html)
    bad = 0
    for i, rec in enumerate(d.plansteps, 1):
        p = planstep_problems(rec)
        dec = d.decision_seq.get(rec['section'])
        if dec is not None and rec['seq'] > dec:
            p.append('在同一節的 p.decision 之後')
        print('%-3d %-18s %-8s %s' % (i, rec['section'] or '(none)',
                                      rec['data_plan'] or '(none)',
                                      'OK' if not p else 'ERR: ' + '；'.join(p)))
        if p:
            bad += 1
    print('planstep %d 個，有問題 %d 個' % (len(d.plansteps), bad))
    if bad:
        print('PLANSTEP FAILED')
        return 1
    print('PLANSTEP OK')
    return 0


# ----------------------------------------------------------------- anchors
def cmd_anchors(args):
    b = parse(args.before)
    a = parse(args.after)
    before_ids = list(OrderedDict.fromkeys(b.ids))
    after_ids = set(a.ids)
    gone = [i for i in before_ids if i not in after_ids]
    broken = [h for h in OrderedDict.fromkeys(a.hrefs) if h != '#' and h[1:] not in after_ids]
    print('ids before=%d after=%d, href="#…" after=%d' % (len(before_ids), len(after_ids), len(set(a.hrefs))))
    if gone:
        print('MISSING IDS (%d):' % len(gone))
        for i in gone:
            print('  -', i)
    if broken:
        print('BROKEN HREFS (%d):' % len(broken))
        for h in broken:
            print('  -', h)
    if gone or broken:
        print('ANCHORS FAILED')
        return 1
    print('ANCHORS OK')
    return 0


# ------------------------------------------------------------------- xrefs
SEC_OPEN_RE = re.compile(r'<section\b[^>]*>')
SEC_CLOSE_RE = re.compile(r'</section\s*>')
ID_ATTR_RE = re.compile(r'\bid="([^"]+)"')
H2_NUM_RE = re.compile(r'<h2>\s*<span class="num">(\d+)</span>(.*?)</h2>', re.S)
SUBHEAD_RE = re.compile(r'<(h3|h4|h5)\b([^>]*)>(.*?)</\1>', re.S)
XREF_TAG_RE = re.compile(r'<a class="xref" href="#([^"]+)">([^<]*)</a>')
# 第 <a class="xref" href="#X">N</a> 節「T」
XREF_CITE_RE = re.compile(
    r'第\s*<a class="xref" href="#([^"]+)">(\d+)</a>\s*節\s*「([^」]*)」')
TAG_RE = re.compile(r'<[^>]+>')
FULLWIDTH_COLON = '：'


def _plain(s):
    """去標籤、去空白，只留可比對的字。"""
    return WS_RE.sub('', TAG_RE.sub('', s))


def _head_of(title):
    """h2 標題冒號前那一截（全形冒號切）。"""
    return title.split(FULLWIDTH_COLON)[0]


class _Xrefs(object):
    """把一份 HTML 拆成：節範圍、節號、節標題、id 位置、節內小標。"""

    def __init__(self, src):
        self.src = src
        events = []
        for m in SEC_OPEN_RE.finditer(src):
            idm = ID_ATTR_RE.search(m.group(0))
            events.append((m.start(), 0, idm.group(1) if idm else None, m.end()))
        for m in SEC_CLOSE_RE.finditer(src):
            events.append((m.start(), 1, None, m.end()))
        events.sort()
        stack, self.ranges = [], []
        for pos, kind, sid, end in events:
            if kind == 0:
                stack.append((pos, sid))
            elif stack:
                start, sid2 = stack.pop()
                self.ranges.append((start, end, sid2))

        self.num = OrderedDict()      # section id -> 節號
        self.title = {}               # section id -> h2 標題
        for m in H2_NUM_RE.finditer(src):
            sid = self.owner(m.start())
            if sid:
                self.num[sid] = m.group(1)
                self.title[sid] = TAG_RE.sub('', m.group(2)).strip()

        self.id_pos = {}              # id -> id="…" 出現位置
        self.id_end = {}              # id -> 帶著它的那個標籤的 > 後面一格
        for m in ID_ATTR_RE.finditer(src):
            if m.group(1) in self.id_pos:
                continue
            self.id_pos[m.group(1)] = m.start()
            gt = src.find('>', m.end())
            self.id_end[m.group(1)] = (gt + 1) if gt >= 0 else m.end()

        self.subheads = []            # (pos, level, id or None, 標題文字)
        for m in SUBHEAD_RE.finditer(src):
            idm = ID_ATTR_RE.search(m.group(2))
            self.subheads.append((m.start(), m.group(1),
                                  idm.group(1) if idm else None,
                                  TAG_RE.sub('', m.group(3)).strip()))

    def owner(self, pos):
        """最內層包住 pos 的 section id。"""
        best = None
        for start, end, sid in self.ranges:
            if start <= pos < end and sid and (best is None or start > best[0]):
                best = (start, sid)
        return best[1] if best else None

    def sec_of(self, target):
        """一個錨點屬於哪一節（節 id 就是自己）。"""
        if target in self.num:
            return target
        pos = self.id_pos.get(target)
        return self.owner(pos) if pos is not None else None

    def lineno(self, pos):
        return self.src.count('\n', 0, pos) + 1

    def segment(self, target):
        """錨點指到的那一段：從錨點往後到下一個 h3／h4 或本節結束為止。
        節 id 則是整節。往前再加最近的一個小標，因為有些錨點放在小標後面的段落上。"""
        pos = self.id_pos.get(target)
        if pos is None:
            return ''
        sid = self.sec_of(target)
        sec_end = len(self.src)
        for start, end, s in self.ranges:
            if s == sid:
                sec_end = end
                break
        if target in self.num:
            return _plain(self.src[pos:sec_end])
        start = self.id_end.get(target, pos)
        # 錨點常常是空的 <span id="…"></span>，後面緊跟著它要指的那張卡或小標；
        # 兩者之間只有標籤、沒有字的時候，那個小標算這一段的，不是下一段的開頭。
        nxt = sec_end
        for hpos, level, _hid, _txt in self.subheads:
            if hpos <= start or level not in ('h3', 'h4') or hpos >= nxt:
                continue
            if not _plain(self.src[start:hpos]):
                continue
            nxt = hpos
        prev = ''
        for hpos, _level, _hid, txt in self.subheads:
            if hpos <= pos:
                prev = txt
        return _plain(self.src[start:nxt]) + _plain(prev)


def cmd_xrefs(args):
    with open(args.html, encoding='utf-8') as f:
        src = strip_appendix(f.read())
    x = _Xrefs(src)

    bad_num, bad_title, bad_href, notes = [], [], [], []

    # 一、節號與 href 對得上：連結文字是數字時，它指到的那一節的 num 必須等於它
    n_numeric = 0
    for m in XREF_TAG_RE.finditer(src):
        target, text = m.group(1), m.group(2).strip()
        if not text.isdigit():
            continue
        n_numeric += 1
        if target not in x.id_pos:
            bad_num.append((x.lineno(m.start()), target, text, '沒有這個 id'))
            continue
        sid = x.sec_of(target)
        got = x.num.get(sid)
        if got != text:
            bad_num.append((x.lineno(m.start()), target, text,
                            '#%s 在第 %s 節（%s）' % (target, got or '?', sid or '?')))

    # 二、引的標題：第 <xref>N</xref> 節「T」的 T 必須是該節 h2 冒號前那一截，
    #     或出現在這個錨點指到的那一段裡。
    # 三、href 指整節、但 T 是節內某個「帶 id」的小標 → 應該改指那個 id（可機械修，判紅）。
    #     小標沒有 id 的，只記 note，不判紅（要不要加 id 由主線決定）。
    n_cite = 0
    for m in XREF_CITE_RE.finditer(src):
        target, n, t = m.group(1), m.group(2), m.group(3)
        n_cite += 1
        line = x.lineno(m.start())
        sid = x.sec_of(target)
        h2head = _head_of(x.title.get(sid, ''))
        if _plain(t) == _plain(h2head):
            continue
        if target in x.num:
            hit = None
            for hpos, _level, hid, txt in x.subheads:
                if x.owner(hpos) != sid:
                    continue
                if _plain(txt) == _plain(t) or _plain(_head_of(txt)) == _plain(t):
                    if hid:
                        hit = hid
                        break
            if hit:
                bad_href.append((line, target, n, t, hit))
                continue
            if _plain(t) in x.segment(target):
                notes.append((line, target, n, t))
                continue
            bad_title.append((line, target, n, t, h2head))
            continue
        if _plain(t) in x.segment(target):
            continue
        bad_title.append((line, target, n, t, h2head))

    print('xref 節號連結 %d 個、「第 N 節「標題」」引用 %d 個' % (n_numeric, n_cite))
    if bad_num:
        print('節號與 href 不符（%d）：' % len(bad_num))
        for line, target, text, why in bad_num:
            print('  L%d  連結文字 %s → %s' % (line, text, why))
    if bad_href:
        print('href 指整節、但引的小標有自己的 id（%d）：' % len(bad_href))
        for line, target, n, t, hit in bad_href:
            print('  L%d  第 %s 節「%s」的 href=#%s，應該指 #%s' % (line, n, t, target, hit))
    if bad_title:
        print('引的標題在目標那一段裡找不到，也不是 h2 冒號前那一截（%d）：' % len(bad_title))
        for line, target, n, t, h2head in bad_title:
            print('  L%d  第 %s 節「%s」 href=#%s，h2 冒號前是「%s」' % (line, n, t, target, h2head))
    if notes:
        print('注意（不判紅）：%d 處 href 指整節、引的是節內沒有 id 的小標' % len(notes))
        if args.notes:
            for line, target, n, t in notes:
                print('  L%d  第 %s 節「%s」 href=#%s' % (line, n, t, target))
        else:
            print('  （加 --notes 印清單）')
    if bad_num or bad_href or bad_title:
        print('XREFS FAILED')
        return 1
    print('XREFS OK')
    return 0


# --------------------------------------------------------------------- CLI
def build_parser():
    ap = argparse.ArgumentParser(prog='v7_check.py', description='v7 改版檢查工具')
    sub = ap.add_subparsers(dest='cmd')

    p = sub.add_parser('mainline', help='逐節主線字數')
    p.add_argument('html')
    p.add_argument('--json', help='另外寫一份 JSON')
    p.set_defaults(func=cmd_mainline)

    p = sub.add_parser('numbers', help='逐節阿拉伯數字保全檢查')
    p.add_argument('before')
    p.add_argument('after')
    p.add_argument('--section', action='append', nargs='+', help='只看這些 section id')
    p.add_argument('--allow-file', dest='allow_file', help='允許丟掉的 token 清單 JSON')
    p.set_defaults(func=cmd_numbers)

    p = sub.add_parser('budget', help='主線字數預算')
    p.add_argument('html')
    p.add_argument('budget')
    p.add_argument('--section', action='append', nargs='+', help='只檢查這些 section id')
    p.set_defaults(func=cmd_budget)

    p = sub.add_parser('planstep', help='div.planstep 結構與位置')
    p.add_argument('html')
    p.set_defaults(func=cmd_planstep)

    p = sub.add_parser('anchors', help='錨點保全檢查')
    p.add_argument('before')
    p.add_argument('after')
    p.set_defaults(func=cmd_anchors)

    p = sub.add_parser('xrefs', help='節號連結與引的標題對不對得上')
    p.add_argument('html')
    p.add_argument('--notes', action='store_true', help='把不判紅的那些也列出來')
    p.set_defaults(func=cmd_xrefs)
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if not getattr(args, 'func', None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
