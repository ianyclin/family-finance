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
      SMALL_EXEMPT 那幾節與 group-* 不查）。
      給了 --section 就只檢查指定的節，兩個全書合計改成只印不判（施工中途全書必然超標）。
  python3 tools/v7_check.py planstep <html>
      檢查每個 div.planstep 的結構與位置；結構錯 exit 1。
  python3 tools/v7_check.py anchors <before.html> <after.html>
      改前的 id 在改後都還在；改後的 href="#…" 都有對應 id。

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
        d.feed(f.read())
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
    if smax is not None:
        for k, r in rows.items():
            if want is not None and k not in want:
                continue
            if not small_checked(k):
                continue
            mark = 'OVER' if r['small'] > smax else 'ok'
            print('%-16s small=%-10d limit=%-7d %s' % (k, r['small'], smax, mark))
            if r['small'] > smax:
                over.append((k + ' (small)', r['small'], smax))

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
