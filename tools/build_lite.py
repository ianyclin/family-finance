# -*- coding: utf-8 -*-
"""可列印工作表產生程式（單一來源、兩個輸出；v6.0 時產的是十二章的新手實作版）。格式規格：docs/core-edition/specs/lite-format.md

用法：
  python3 tools/build_lite.py                                  # 用 lite/manifest.json，產生兩份 HTML、兩份 PDF，最後跑哨兵
  python3 tools/build_lite.py --manifest lite/manifest.sample.json
  python3 tools/build_lite.py --no-pdf                         # 只產生 HTML；頁數哨兵改讀 export 裡現有的 PDF（比 HTML 舊會 WARN，找不到會 FAIL）
  python3 tools/build_lite.py --stamp ALT_ID                   # 重算短稿檔頭的 sha256（重看過短稿之後才用）
  python3 tools/build_lite.py --fingerprint "#ten div.warning" # 印出選擇器對到的區塊與 sha256

exit code：0＝全部通過；1＝建置錯誤或任何哨兵失敗。
"""
import sys, os, re, json, hashlib, unicodedata, subprocess, shutil, argparse, time
import html as htmlmod
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
NORM_VERSION = 'v1'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
FICTION_NOTICE = '虛構人物，示範怎麼填，不是建議。不要抄比例，抄推理步驟。'
AUTOGEN_COMMENT = '<!-- 自動產生，不要手改：由 tools/build_lite.py 依 %s 產生 -->\n'

DEFAULT_PATHS = {
    'source': 'guide/index.html',
    'alt_dir': 'lite/alt',
    'facts': 'lite/facts.txt',
    'case_checks': 'lite/case-checks.json',
    'tickers': 'lite/tickers.json',
    'labels': 'lite/labels.json',
    'calc_results': 'lite/calc-results.json',
    'lite_html': 'lite/index.html',
    'full_html': 'output/full-v60-out.html',
    'print_dir': 'lite/work/print',
    'lite_text': 'lite/work/lite-v60.txt',
    'full_text': 'lite/work/full-v60.txt',
    'lite_fragment': 'output/lite.html',
    'full_fragment': 'output/guide.html',
    'export_dir': 'export',
    'lite_export_name': '隔離人性-可列印工作表-{version}',
    'full_export_name': '隔離人性-理財新手完整指南-{version}',
}


class BuildError(Exception):
    pass


def rp(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def read(p):
    return open(rp(p), encoding='utf-8').read()


def write(p, s):
    p = rp(p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)


# ---------------------------------------------------------------- DOM 索引（只記位置，不改寫原字串）

class Node(object):
    __slots__ = ('tag', 'attrs', 'start', 'open_end', 'inner_end', 'end', 'parent', 'children', '_text')

    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag = tag; self.attrs = attrs; self.start = start; self.open_end = open_end
        self.inner_end = open_end; self.end = open_end; self.parent = parent; self.children = []; self._text = None

    def classes(self):
        return (self.attrs.get('class') or '').split()

    def tokens(self, name):
        return (self.attrs.get(name) or '').split()

    def ancestors(self):
        p = self.parent
        while p is not None and p.tag != '#root':
            yield p
            p = p.parent


class _Indexer(HTMLParser):
    def __init__(self, s):
        HTMLParser.__init__(self, convert_charrefs=False)
        self.s = s
        self.line_starts = [0] + [m.end() for m in re.finditer('\n', s)]
        self.root = Node('#root', {}, 0, 0, None)
        self.root.end = self.root.inner_end = len(s)
        self.stack = [self.root]
        self.nodes = []

    def off(self):
        ln, col = self.getpos()
        return self.line_starts[ln - 1] + col

    def _open(self, tag, attrs, selfclose):
        start = self.off()
        text = self.get_starttag_text() or ''
        parent = self.stack[-1]
        n = Node(tag, dict((k, v if v is not None else '') for k, v in attrs), start, start + len(text), parent)
        parent.children.append(n); self.nodes.append(n)
        if selfclose or tag in VOID:
            n.inner_end = n.end = n.open_end
        else:
            self.stack.append(n)

    def handle_starttag(self, tag, attrs):
        self._open(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs, True)

    def handle_endtag(self, tag):
        pos = self.off()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                break
        else:
            return
        end = self.s.find('>', pos) + 1
        while len(self.stack) > i:
            n = self.stack.pop()
            n.inner_end = pos
            n.end = end if len(self.stack) == i else pos


class Dom(object):
    def __init__(self, s):
        self.s = s
        p = _Indexer(s); p.feed(s); p.close()
        for n in p.stack[1:]:
            n.inner_end = n.end = len(s)
        self.root = p.root
        self.nodes = p.nodes
        self.by_id = {}
        for n in self.nodes:
            if 'id' in n.attrs:
                self.by_id.setdefault(n.attrs['id'], n)

    def outer(self, n):
        return self.s[n.start:n.end]

    def inner(self, n):
        return self.s[n.open_end:n.inner_end]

    def text(self, n):
        if n._text is None:
            n._text = html_text(self.outer(n))
        return n._text

    def section_of(self, n):
        for a in [n] + list(n.ancestors()):
            if a.tag == 'section' and a.attrs.get('id'):
                return a
        return None


# ---------------------------------------------------------------- 文字與正規化

def html_text(s):
    s = re.sub(r'<(script|style|svg)\b.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = htmlmod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def compact(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))


def normalize_block(s):
    """指紋正規化 v1：拿掉 data-lite／data-lite-alt 屬性 → NFC → 連續空白變一個空格 → 去頭尾空白。"""
    s = re.sub(r'\s+data-lite(?:-alt)?="[^"]*"', '', s)
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'\s+', ' ', s).strip()


def sha256_block(s):
    return hashlib.sha256(normalize_block(s).encode('utf-8')).hexdigest()


NUM_RE = re.compile(r'\d+(?:[.,]\d+)*')


def numbers_in(text):
    t = unicodedata.normalize('NFKC', text)
    out = set()
    for m in NUM_RE.finditer(t):
        out.add(m.group(0).replace(',', ''))
    return out


def has_digit(text):
    return bool(re.search(r'\d', unicodedata.normalize('NFKC', text)))


# ---------------------------------------------------------------- 選擇器（CSS 子集）

def _split_top(sel):
    parts, cur, depth, q = [], '', 0, None
    for ch in sel:
        if q:
            cur += ch
            if ch == q: q = None
            continue
        if ch in '"\'':
            q = ch; cur += ch; continue
        if ch in '[(':
            depth += 1
        elif ch in '])':
            depth -= 1
        if ch.isspace() and depth == 0:
            if cur: parts.append(cur); cur = ''
            continue
        cur += ch
    if cur: parts.append(cur)
    return parts


_COMP_TOKEN = re.compile(r'''
    (?P<tag>^[a-zA-Z][\w-]*|^\*)
  | \#(?P<id>[\w-]+)
  | \.(?P<cls>[\w-]+)
  | \[(?P<an>[\w-]+)(?:(?P<op>~?=)(?:"(?P<v1>[^"]*)"|'(?P<v2>[^']*)'|(?P<v3>[^\]]*)))?\]
  | :contains\((?P<ct>[^)]*)\)
''', re.X)


def parse_compound(c):
    d = {'tag': None, 'id': None, 'cls': [], 'attrs': [], 'contains': []}
    pos = 0
    while pos < len(c):
        m = _COMP_TOKEN.match(c, pos)
        if not m or m.end() == pos:
            raise BuildError('選擇器看不懂：%r（位置 %d）' % (c, pos))
        if m.group('tag'): d['tag'] = None if m.group('tag') == '*' else m.group('tag').lower()
        elif m.group('id'): d['id'] = m.group('id')
        elif m.group('cls'): d['cls'].append(m.group('cls'))
        elif m.group('an'):
            v = m.group('v1') if m.group('v1') is not None else (m.group('v2') if m.group('v2') is not None else m.group('v3'))
            d['attrs'].append((m.group('an'), m.group('op'), v))
        elif m.group('ct') is not None:
            d['contains'].append(m.group('ct').strip().strip('"\''))
        pos = m.end()
    return d


def parse_selector(sel):
    sel = sel.strip(); nth = None
    m = re.search(r':nth\((\d+)\)\s*$', sel)
    if m:
        nth = int(m.group(1)); sel = sel[:m.start()]
    comps = [parse_compound(p) for p in _split_top(sel)]
    if not comps:
        raise BuildError('空的選擇器')
    return comps, nth


def _match(dom, n, c):
    if c['tag'] and n.tag != c['tag']: return False
    if c['id'] and n.attrs.get('id') != c['id']: return False
    cl = n.classes()
    for k in c['cls']:
        if k not in cl: return False
    for an, op, v in c['attrs']:
        if an not in n.attrs: return False
        if op == '=' and n.attrs[an] != v: return False
        if op == '~=' and v not in n.tokens(an): return False
    for t in c['contains']:
        if compact(t) not in compact(dom.text(n)): return False
    return True


def outermost(nodes):
    ids = set(id(n) for n in nodes)
    return [n for n in nodes if not any(id(a) in ids for a in n.ancestors())]


def is_mark_value(src):
    return bool(re.fullmatch(r'[A-Za-z0-9_-]+', src.strip()))


def select(dom, src):
    """src：data-lite 值（例如 ch4）或 CSS 子集選擇器。回傳文件順序、只取最外層的節點。"""
    src = src.strip()
    if is_mark_value(src):
        return outermost([n for n in dom.nodes if src in n.tokens('data-lite')])
    comps, nth = parse_selector(src)
    last, prev = comps[-1], comps[:-1]
    res = []
    for n in dom.nodes:
        if not _match(dom, n, last): continue
        need = list(prev)
        for a in n.ancestors():
            if not need: break
            if _match(dom, a, need[-1]): need.pop()
        if not need: res.append(n)
    res = outermost(res)
    if nth is not None:
        res = res[nth - 1:nth]
    return res


# ---------------------------------------------------------------- manifest 與短稿

def load_manifest(path):
    if not os.path.exists(rp(path)):
        raise BuildError('找不到 manifest：%s' % path)
    try:
        m = json.load(open(rp(path), encoding='utf-8'))
    except ValueError as e:
        raise BuildError('manifest 不是合法 JSON：%s（%s）' % (path, e))
    paths = dict(DEFAULT_PATHS); paths.update(m.get('paths') or {})
    m['_paths'] = paths
    m['_path'] = path
    m['_is_main'] = os.path.basename(path) == 'manifest.json'
    return m


ALT_HEADER_RE = re.compile(r'^\s*<!--\s*lite-alt\b(.*?)-->', re.S)


def load_alt(m, alt_id):
    p = os.path.join(rp(m['_paths']['alt_dir']), alt_id + '.html')
    if not os.path.exists(p):
        raise BuildError('短稿檔不存在：%s' % os.path.relpath(p, ROOT))
    s = open(p, encoding='utf-8').read()
    h = ALT_HEADER_RE.match(s)
    if not h:
        raise BuildError('短稿 %s 缺少檔頭註解 <!-- lite-alt ... -->' % alt_id)
    info = {'id': None, 'norm': None, 'srcs': [], 'path': p, 'body': s[h.end():].strip(), 'raw': s, 'header_span': (h.start(), h.end())}
    for line in h.group(1).splitlines():
        line = line.strip()
        if not line: continue
        k, _, v = line.partition(':')
        k = k.strip(); v = v.strip()
        if k == 'id': info['id'] = v
        elif k == 'norm': info['norm'] = v
        elif k == 'src':
            mm = re.match(r'(.*?)\s+sha256=([0-9a-f]{64}|TODO)\s*$', v)
            if not mm:
                raise BuildError('短稿 %s 的 src 行格式不對：%r' % (alt_id, line))
            info['srcs'].append((mm.group(1).strip(), mm.group(2)))
    if info['id'] != alt_id:
        raise BuildError('短稿檔名 %s 和檔頭 id %r 不一致' % (alt_id, info['id']))
    return info


def alt_source_nodes(dom, info):
    """回傳 [(selector, recorded_sha, [nodes])]。"""
    out = []
    for sel, sha in info['srcs']:
        out.append((sel, sha, select(dom, sel)))
    return out


def stamp_alt(m, alt_id):
    dom = Dom(read(m['_paths']['source']))
    info = load_alt(m, alt_id)
    srcs = info['srcs']
    if not srcs:
        marked = outermost([n for n in dom.nodes if alt_id in n.tokens('data-lite-alt')])
        if not marked:
            raise BuildError('短稿 %s 檔頭沒有 src 行，原文也沒有 data-lite-alt="%s" 的區塊' % (alt_id, alt_id))
        srcs = [('[data-lite-alt~="%s"]:nth(%d)' % (alt_id, i + 1), 'TODO') for i in range(len(marked))]
    lines = ['<!-- lite-alt', 'id: %s' % alt_id, 'norm: %s' % NORM_VERSION]
    for sel, _ in srcs:
        nodes = select(dom, sel)
        if len(nodes) != 1:
            raise BuildError('短稿 %s 的 src %r 對到 %d 個區塊（要剛好 1 個）' % (alt_id, sel, len(nodes)))
        lines.append('src: %s sha256=%s' % (sel, sha256_block(dom.outer(nodes[0]))))
    old_header = info['raw'][info['header_span'][0]:info['header_span'][1]]
    for line in old_header.splitlines():
        if line.strip().startswith('note:'):
            lines.append(line.strip())
    lines.append('-->')
    new = '\n'.join(lines) + '\n' + info['raw'][info['header_span'][1]:].lstrip('\n')
    open(info['path'], 'w', encoding='utf-8').write(new)
    print('stamped', os.path.relpath(info['path'], ROOT))
    for l in lines[3:-1]:
        print('  ' + l)


# ---------------------------------------------------------------- 區塊轉換

A_RE = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S)


def _attr(attrs, name):
    mm = re.search(r'(?<![\w-])%s="([^"]*)"' % re.escape(name), attrs)
    return mm.group(1) if mm else None


def remove_elements(s):
    dom = Dom(s)
    kill = []
    for n in dom.nodes:
        cl = n.classes()
        # 來源卡 v7 第五輪起是 <details class="source-card">（原本是 div），兩種都要拿掉
        if (n.tag == 'p' and 'explain' in cl) or ('source-card' in cl or 'sources-grid' in cl) \
                or n.tag in ('figure', 'svg', 'img', 'script', 'style') or (n.tag == 'a' and 'back' in cl) \
                or (n.tag == 'details' and 'orig' in cl) \
                or 'skip' in n.tokens('data-lite'):
            kill.append(n)
    kill = outermost(kill)
    for n in sorted(kill, key=lambda x: -x.start):
        s = s[:n.start] + s[n.end:]
    return s


class ChapterCtx(object):
    def __init__(self, ch_id, section_names, section_of_id):
        self.ch_id = ch_id; self.urls = []  # [(href, label)]：正文裡有 [n] 的網址，依出現順序編號
        self.extra_urls = []  # [(href, label)]：manifest urls 區塊列出、正文沒有引用的網址（章末不編號）
        self.section_names = section_names; self.section_of_id = section_of_id

    def url_no(self, href, label):
        for i, (h, _) in enumerate(self.urls):
            if h == href:
                return i + 1
        self.urls.append((href, label))
        return len(self.urls)

    def add_extra(self, href, label):
        for i, (h, _) in enumerate(self.urls):
            if h == href:
                self.urls[i] = (h, label)  # 正文已經引用：編號不變，章末改用 manifest 寫的機構名稱
                return
        if any(h == href for h, _ in self.extra_urls):
            return
        self.extra_urls.append((href, label))

    def name_for(self, target):
        sec = self.section_of_id.get(target, target)
        return self.section_names.get(sec)


def rewrite_links(s, ctx):
    xref = r'<a\b[^>]*class="xref"[^>]*>.*?</a>'

    def xname(tag_html, fallback_text=False):
        mm = A_RE.match(tag_html)
        target = (_attr(mm.group(1), 'href') or '#').lstrip('#')
        text = html_text(mm.group(2))
        if fallback_text and not re.fullmatch(r'\d+', text):
            return text
        name = ctx.name_for(target)
        if name is None:
            raise BuildError('xref 指到找不到節名的 id：#%s（%s）' % (target, ctx.ch_id))
        return name

    def grp(mm):
        names = [xname(t) for t in re.findall(xref, mm.group(1), flags=re.S)]
        return '完整版' + '、'.join('〈%s〉' % n for n in names)
    s = re.sub(r'第\s*((?:%s)(?:\s*、\s*%s)*)\s*節' % (xref, xref), grp, s, flags=re.S)
    s = re.sub(r'「\s*(%s)\s*」' % xref, lambda mm: '完整版〈%s〉' % xname(mm.group(1), True), s, flags=re.S)
    s = re.sub(xref, lambda mm: '完整版〈%s〉' % xname(mm.group(0), True), s, flags=re.S)

    def other(mm):
        attrs, inner = mm.group(1), mm.group(2)
        href = _attr(attrs, 'href') or ''
        if re.search(r'(?<![\w-])class="[^"]*\blite-ref\b', attrs):
            return mm.group(0)
        if href.startswith('#') or not href:
            return inner  # 名詞連結、目錄連結、其他站內錨點 → 純文字（title 不保留）
        label = html_text(inner)
        n = ctx.url_no(href, label)
        ref = '<a class="lite-ref" href="#%s-u%d">[%d]</a>' % (ctx.ch_id, n, n)
        if label == href or label.startswith('http'):
            return ref
        return inner + ref
    s = A_RE.sub(other, s)
    s = re.sub(r'(<[a-zA-Z][^>]*?)\sid="[^"]*"', r'\1', s)
    return s


def transform(s, ctx):
    return rewrite_links(remove_elements(s), ctx)


# ---------------------------------------------------------------- 產生實作版

LITE_CSS = r'''
/* ---- 可列印工作表（build_lite.py 附加） ---- */
.lite-cover{padding:48px 0 12px}.lite-cover h1{font-size:clamp(2rem,6vw,3.6rem);line-height:1.1;margin:.1em 0}
.lite-version{color:var(--muted);font-size:.9rem;font-weight:700}
.lite-ch{background:var(--surface);border:1px solid var(--line);border-radius:16px;margin:20px 0;padding:clamp(18px,4vw,36px)}
.lite-ch>h2{font-size:clamp(1.35rem,3.5vw,1.9rem);line-height:1.3;margin:0 0 .4em}
.lite-label{display:block;font-size:.84rem;letter-spacing:.08em;color:var(--green)}
.lite-action{margin:18px 0;border:2px solid var(--green);border-radius:16px;padding:12px 16px;font-weight:700}
.lite-action::before{content:"動作";display:block;color:var(--green);font-size:.84rem}
.lite-verify{margin:18px 0 0;border:1px dashed var(--muted);border-radius:16px;padding:10px 16px;font-size:.84rem;color:var(--muted)}
.lite-verify p{margin:0}.lite-verify ol{margin:.3em 0 0;padding-left:0;list-style:none}.lite-verify li{margin:.15em 0;overflow-wrap:anywhere}
.lite-verify strong{color:var(--ink)}
.lite-ref{font-size:.75em;vertical-align:.3em;text-decoration:none;margin-left:.1em}
.lite-fiction{display:inline-block;margin:0 0 .6em;padding:2px 12px;border:1px solid var(--muted);border-radius:16px;font-size:.84rem;font-weight:700;color:var(--ink)}
.lite-toc{list-style:none;margin:.6em 0;padding:0}.lite-toc li{margin:0;padding:.18em 0;border-bottom:1px dotted var(--line)}
.lite-toc a{display:flex;justify-content:space-between;gap:12px;color:var(--ink);text-decoration:none}
.lite-toc-pg{font-variant-numeric:tabular-nums;color:var(--muted);display:none}
.lite-blank-page{display:none}
.lite-blank{display:inline-block;min-width:3em;height:1.2em;border-bottom:1px solid currentColor;margin:0 .2em;vertical-align:-.2em}
.lite-line{display:flex;flex-wrap:wrap;align-items:flex-end;gap:0}
.lite-line>.lite-fill{flex:1 1 4em}
table.lite-plan{table-layout:fixed;width:100%}table.lite-plan td{vertical-align:top;width:50%}
table.lite-plan td>strong{display:block;margin-top:.5em}
table.lite-plan-h{width:100%;margin-top:.2em}table.lite-plan-h td{height:2.2em;border-bottom:1px solid currentColor;width:auto}
table.lite-plan-stress{width:100%;min-width:0;table-layout:fixed;border-collapse:separate;border-spacing:6px 0;margin:.1em 0 .2em;line-height:1.5}table.lite-plan-stress th{font-weight:400;white-space:nowrap}
table.lite-plan-stress th:first-child,table.lite-plan-stress td:first-child{width:46%}
table.lite-plan-stress td{width:auto;height:2em;vertical-align:bottom;border-bottom:1px solid currentColor}table.lite-plan-stress td:first-child{border-bottom:0;white-space:nowrap}
/* v7 批 4b：第一張紙正面的起步版六行。一欄六列（手機不橫向捲），每一列＝白話問句／小安示範（淡色）／加高的手寫線 */
table.lite-starter{table-layout:fixed;width:100%}
table.lite-starter td{vertical-align:top;width:auto}
table.lite-starter td>p:first-child{margin:0 0 .15em}
table.lite-starter td>p.small{margin:0 0 .35em}
/* 一欄的表不會橫向捲，手機上不要印「表格可左右滑動」的提示（完整版對 table.lite-plan 也做了同一件事） */
@media screen and (max-width:660px){.table-wrap:has(>table.lite-starter)::before{content:none;display:none}}
table.lite-annual td:nth-child(2){font-size:.84rem}table.lite-annual th:nth-child(3){white-space:nowrap}table.lite-annual th:nth-child(4),table.lite-annual td:nth-child(4){width:40%}
@media print{
  .lite-ch h3,.lite-ch h4,.lite-ch>.lede{break-after:avoid}
  .lite-ch>h2{break-inside:avoid}
  .lite-ch .data-card{break-inside:avoid}
  table.lite-plan{font-size:10.5pt;line-height:1.52}   /* v6.1：頁首多了窄橫幅，行距從 2.05 收到 1.9，讓整張計畫表（含 H 區）留在第一頁；v6.3 批 2a 再收到 1.75，吸收 E 區第三格、C 區路徑名稱與 F 區加高的手寫線；v7 批 4b 再收到 1.62，吸收 D 區白話欄名、E 區壓力測試拆三步與三問拆三行 */
  /* 起步版六行是「一眼看得完」那一頁：字比其他頁大、留白多、手寫線高 */
  /* v7 第三輪 B：第 4 題多一格「其餘放＿」、卡底那句改成兩階段的新說法、急救卡多一行適用條件，這一頁掉到第 2 頁。字級維持 11.5pt（這一頁要「一眼看得完」），改收行距與列距把三行吸收回來 */
  table.lite-starter{font-size:11.5pt;line-height:1.38}table.lite-starter td{padding:4px 8px}
  table.lite-starter td>p.small{font-size:9.5pt}
  table.lite-annual{font-size:10pt}table.lite-annual td{padding:9px 5px}
  table.lite-plan-stress{font-size:10pt;line-height:1.5}table.lite-plan-stress th,table.lite-plan-stress td{padding:1px 4px}
  table.lite-lookup th,table.lite-lookup td{padding:0 5px;line-height:1.08}
  /* v7 批 4b：查表頁多了「怎麼用，三步」與算好的例子，表以外的文字收小一點，整頁仍留在一頁 */
  #lookup p,#lookup li{font-size:9.5pt;line-height:1.35}
  #lookup ol,#lookup p{margin:.2em 0}#lookup .checklist li{margin:.1em 0;padding-left:0}
  @page{size:A4;margin:13mm 13mm 15mm;@bottom-center{content:counter(page);font-size:9pt;color:#666}}
  body{font-size:10pt;line-height:1.4;background:white;color:black}
  header,main,footer{width:100%}
  /* 封面：可列印工作表把它壓成第一頁頁首的一條窄橫幅（副標／書名＋版本日期／一句指路），
     讓計畫表和它同一頁（spec-v61-worksheet.md）。有目錄、有章的實作版沒有再用這一支 CSS。 */
  .lite-cover{padding:0 0 4px;margin:0 0 6px;border-bottom:1px solid #999}
  .lite-cover .eyebrow{font-size:8.5pt;margin:0}
  .lite-cover h1{font-size:13pt;display:inline;margin:0}
  .lite-cover .lite-version{display:inline;margin-left:.6em;font-size:8.5pt;font-weight:400}
  .lite-cover p.small{margin:.15em 0 0}
  .lite-ch{border:0;border-radius:0;padding:0;margin:0 0 12px;box-shadow:none;background:white}
  .lite-ch>h2{font-size:15pt;margin:0 0 .25em;break-after:avoid}
  .lite-break{break-before:page}
  .lite-onepage{break-before:page;break-after:page;break-inside:avoid}
  .lite-page-break{break-before:page;height:0}
  .lite-blank-page{display:block;break-before:page;padding-top:110mm;text-align:center;color:#888;font-size:9pt}
  .lede{font-size:10.5pt;margin:0 0 .6em}
  p,ul,ol,dl{margin:.35em 0}
  h3{font-size:11pt;margin:.7em 0 .3em}h4{margin:.5em 0 .2em}
  .data-card,.story,.warning,.decision,.lite-action,.lite-verify{margin:8px 0;padding:8px 12px}
  .checklist li,.qa li,.rules li,.biases li,.data-card>ul>li,.data-card>ol>li{margin:.25em 0}
  table{min-width:0;font-size:8.5pt}th,td{padding:3px 5px}
  .table-wrap{overflow:visible;border-radius:0}
  details{margin:6px 0}summary{font-size:9pt}
  .lite-ref{color:black}
  .lite-verify{color:#333;border-color:#888}
  .lite-toc a{color:black}
}
'''

LITE_PRINT_CSS = '\n.lite-toc-pg{display:inline}\n'
FULL_PRINT_CSS = ('\n.toc-pg{margin-left:.5em;color:var(--muted);font-variant-numeric:tabular-nums}@media screen{.toc-pg{display:none}}\n'
                  # fix-r3：s2「資產每增加 60 萬需要多久」十列小表不切成兩頁（cases 的小表試過，會讓陳大哥表尾那頁空一半，不加）
                  '@media print{#s2 .table-wrap{break-inside:avoid}}\n'
                  # D10＋S6：沒展開的摺疊區，紙本只印 summary，後面補一句提示（年檢那一格的 summary 已寫「網頁版可以展開」，只補「紙本未印」）
                  '@media print{details:not([open])>summary::after{content:"（紙本未印，網頁版可展開）";font-weight:400;color:#666}'
                  '#annual details:not([open])>summary::after{content:"（紙本未印）"}}\n'
                  # v6.3 批 2 修正：引導句和它下面那張圖不分頁（圖本身仍可整塊落到下一頁）
                  '@media print{figure.chart{break-before:avoid}}\n'
                  # S6＋重排 §10.1：所有 group-* 分組節不在目錄裡、tail_flows 管不到；它們很短，接在上一節的節尾頁排，免得前一頁只剩兩三成。
                  # 所有 group-* 分組節印成色帶（淺底、上下細線）；短的整塊不斷頁，part-map 超過 5 行（例如 group-core 10 行）允許斷頁，但每一行不切開。
                  '@media print{section.part[id^="group-"]{break-before:auto!important;page-break-before:auto!important;'
                  'background:#f3f0e8;border-top:1px solid #999;border-bottom:1px solid #999;padding:.5em .8em;margin-top:1em;'
                  '-webkit-print-color-adjust:exact;print-color-adjust:exact}'
                  'section.part[id^="group-"]:not(:has(.part-map li:nth-child(6))){break-inside:avoid}'
                  'section.part[id^="group-"]>h2{break-after:avoid}'
                  'section.part[id^="group-"] .part-map li{break-inside:avoid}}\n')


def section_names(dom):
    names = {}
    for n in dom.nodes:
        if n.tag == 'section' and n.attrs.get('id'):
            h2 = next((c for c in n.children if c.tag == 'h2'), None)
            if h2 is None: continue
            inner = re.sub(r'<span\b[^>]*class="num"[^>]*>.*?</span>', '', dom.inner(h2), flags=re.S)
            names[n.attrs['id']] = html_text(inner)
    return names


def section_of_ids(dom):
    out = {}
    for n in dom.nodes:
        if 'id' in n.attrs:
            sec = dom.section_of(n)
            out[n.attrs['id']] = sec.attrs['id'] if sec is not None else n.attrs['id']
    return out


def esc(s):
    return htmlmod.escape(s, quote=True)


def verify_rows(m):
    """附 B 的列：[(章 id, 表上寫的章名, [節 id])]。來源＝各章 verify（章末想查證框）＋ verify_index（只進附 B）。"""
    rows = []
    for ch in m['chapters']:
        if ch.get('kind') == 'cover':
            continue
        sids = []
        for b in ch.get('blocks', []):
            for sid in (b.get('verify') or []) + (b.get('verify_index') or []):
                if sid not in sids:
                    sids.append(sid)
        if sids:
            rows.append((ch['id'], ch.get('label') or ch['title'], sids))
    return rows


def verify_table_html(m, names):
    trs = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (esc(lab), '、'.join('〈%s〉' % esc(names.get(s, s)) for s in sids))
                  for _, lab, sids in verify_rows(m))
    return ('<div class="table-wrap"><table class="compact prose" data-lite-verify-table="1"><thead><tr><th>實作版</th>'
            '<th>完整版的節</th></tr></thead><tbody>%s</tbody></table></div>' % trs)


def chapter_heading(ch):
    lab = ch.get('label') or ''
    return ('%s %s' % (lab, ch['title'])).strip()


def build(m, alt_cache=None):
    P = m['_paths']
    src_html = read(P['source'])
    dom = Dom(src_html)
    names = section_names(dom)
    sec_of = section_of_ids(dom)
    errors = []
    used_alts = {}
    used_sections = {}  # section id -> [labels]
    chapter_html = []
    toc_items = [c for c in m['chapters'] if c.get('kind') != 'cover']
    ids = [c['id'] for c in m['chapters']]
    if len(set(ids)) != len(ids):
        raise BuildError('manifest 章 id 重複')
    report = {'chapters': []}

    for ch in m['chapters']:
        ctx = ChapterCtx(ch['id'], names, sec_of)
        parts, actions, verify = [], [], []
        pending_urls = []
        alts_done = set()
        src_sections = []

        def add_alt(alt_id):
            if alt_id in alts_done:
                return
            if alt_id in used_alts:
                errors.append('短稿 %s 在實作版出現兩次（%s、%s）' % (alt_id, used_alts[alt_id], ch['id']))
            used_alts[alt_id] = ch['id']; alts_done.add(alt_id)
            info = load_alt(m, alt_id)
            for sel, sha, nodes in alt_source_nodes(dom, info):
                for n in nodes:
                    sec = dom.section_of(n)
                    if sec is not None: src_sections.append(sec.attrs['id'])
            parts.append('<div data-lite-alt-out="%s">%s</div>' % (esc(alt_id), transform(info['body'], ctx)))

        for b in ch.get('blocks', []):
            if 'src' in b:
                nodes = select(dom, b['src'])
                if not nodes:
                    errors.append('%s：src %r 在完整版對不到任何區塊' % (ch['id'], b['src']))
                    continue
                for n in nodes:
                    alt_ids = n.tokens('data-lite-alt')
                    inner_alts = [x for x in dom.nodes if n.start < x.start < n.end and x.tokens('data-lite-alt')]
                    if alt_ids:
                        for a in alt_ids: add_alt(a)
                        continue
                    sec = dom.section_of(n)
                    if sec is not None: src_sections.append(sec.attrs['id'])
                    block = dom.outer(n)
                    if n.tag == 'li':
                        # 抽出的是清單項目：沒有父清單、沒有外框，包成警示框（內容不動）
                        block = '<div class="warning">%s</div>' % dom.inner(n)
                    if inner_alts:
                        # 區塊裡面有標了短稿的子區塊：子區塊換成短稿
                        sub = Dom(block)
                        reps = outermost([x for x in sub.nodes if x.tokens('data-lite-alt')])
                        for x in sorted(reps, key=lambda y: -y.start):
                            ph = ''.join('\x00ALT:%s\x00' % a for a in x.tokens('data-lite-alt'))
                            block = block[:x.start] + ph + block[x.end:]
                        pieces = re.split(r'\x00ALT:([^\x00]+)\x00', block)
                        for i, piece in enumerate(pieces):
                            if i % 2 == 0:
                                if piece.strip(): parts.append(transform(piece, ctx))
                            else:
                                add_alt(piece)
                    else:
                        parts.append(transform(block, ctx))
            elif 'alt' in b:
                add_alt(b['alt'])
            elif 'glue' in b:
                if has_digit(html_text(b['glue'])):
                    errors.append('%s：接合文字有阿拉伯數字：%r' % (ch['id'], html_text(b['glue'])[:60]))
                parts.append(transform(b['glue'], ctx))
            elif b.get('page_break'):
                parts.append('<div class="lite-page-break"></div>')
            elif b.get('toc'):
                lis = ''.join('<li><a href="#%s"><span>%s</span><span class="lite-toc-pg" data-for="%s">00</span></a></li>'
                              % (esc(c['id']), esc(chapter_heading(c)), esc(c['id'])) for c in toc_items)
                parts.append('<ol class="lite-toc">%s</ol>' % lis)
            elif b.get('blank_page'):
                # 列印時自成一頁的「本頁刻意留白」（讓計畫表落在奇數頁、查表頁在它背面）；網頁上不顯示
                parts.append('<div class="lite-blank-page"><p>本頁刻意留白</p></div>')
            elif b.get('notice') == 'fiction':
                parts.append('<p class="lite-fiction">%s</p>' % FICTION_NOTICE)
            elif 'action' in b:
                if has_digit(b['action']):
                    errors.append('%s：動作框有阿拉伯數字：%r' % (ch['id'], b['action']))
                actions.append(b['action'])
            elif 'verify' in b:
                for sid in b['verify']:
                    if sid not in names:
                        errors.append('%s：verify 的節 id %r 在完整版不存在' % (ch['id'], sid))
                    else:
                        verify.append(sid)
            elif 'urls' in b:
                pending_urls.extend(b['urls'])
            elif 'verify_index' in b:
                # 只進附 B 想查證總表，不在本章印想查證框（前三頁這種剛好一頁的頁面用）
                for sid in b['verify_index']:
                    if sid not in names:
                        errors.append('%s：verify_index 的節 id %r 在完整版不存在' % (ch['id'], sid))
            elif b.get('verify_table'):
                parts.append(verify_table_html(m, names))
            else:
                errors.append('%s：看不懂的 block %r' % (ch['id'], b))

        for fld in ('title', 'gain'):
            if ch.get(fld) and has_digit(ch[fld]):
                errors.append('%s：%s 有阿拉伯數字：%r' % (ch['id'], fld, ch[fld]))

        body = '\n'.join(parts)
        for u in pending_urls:
            ctx.add_extra(u['href'], u.get('label') or u['href'])
        for a in actions:
            body += '\n<p class="lite-action">%s</p>' % esc(a)
        if verify or ctx.urls or ctx.extra_urls:
            v = '<div class="lite-verify">'
            if verify:
                v += '<p><strong>想查證</strong>　完整版' + '、'.join('〈%s〉' % esc(names[s]) for s in verify) + '</p>'
            else:
                v += '<p><strong>本章網址</strong></p>'
            if ctx.urls or ctx.extra_urls:
                v += '<ol>' + ''.join('<li id="%s-u%d">[%d] %s　<a href="%s">%s</a></li>' % (
                    esc(ch['id']), i + 1, i + 1, esc(lab) if lab != href else '', esc(href), esc(href))
                    for i, (href, lab) in enumerate(ctx.urls))
                v += ''.join('<li>・%s　<a href="%s">%s</a></li>' % (esc(lab) if lab != href else '', esc(href), esc(href))
                             for href, lab in ctx.extra_urls) + '</ol>'
            v += '</div>'
            body += '\n' + v

        if ch.get('kind') == 'cover':
            html_ch = ('<header class="lite-cover lite-ch" id="%s">\n<div class="eyebrow">%s</div>\n<h1>%s</h1>\n'
                       '<p class="lite-version">%s／%s</p>\n%s\n</header>') % (
                esc(ch['id']), esc(m.get('eyebrow', '')), esc(ch['title']), esc(m['version']), esc(m['date']), body)
        else:
            cls = ['lite-ch']
            if ch.get('one_page'): cls.append('lite-onepage')
            elif ch.get('page_break'): cls.append('lite-break')
            # label 後面用全形空白放在 span 裡：Chrome 產生書籤時會吃掉 span 外的半形空白（review r2 notes 16）
            lab = ('<span class="lite-label">%s　</span>' % esc(ch['label'])) if ch.get('label') else ''
            gain = ('<p class="lede">%s</p>\n' % esc(ch['gain'])) if ch.get('gain') else ''
            html_ch = '<section class="%s" id="%s">\n<h2>%s%s</h2>\n%s%s\n</section>' % (
                ' '.join(cls), esc(ch['id']), lab, esc(ch['title']), gain, body)
        chapter_html.append(html_ch)
        if ch.get('label'):
            for sid in src_sections:
                labs = used_sections.setdefault(sid, [])
                if ch['label'] not in labs: labs.append(ch['label'])
        report['chapters'].append({'id': ch['id'], 'chars': len(compact(html_text(re.sub(r'<div class="lite-verify">.*?</div>', '', html_ch, flags=re.S))))})

    if errors:
        raise BuildError('\n'.join(errors))

    style = re.search(r'<style>(.*?)</style>', src_html, flags=re.S)
    css = (style.group(1) if style else '') + LITE_CSS
    title = '%s｜%s %s' % (m['book_title'], m['edition'], m['version'])
    lite = (AUTOGEN_COMMENT % m['_path']) + (
        '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="color-scheme" content="light dark">\n'
        '<meta name="author" content="%s">\n<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n' % (esc(m['author']), esc(title), css))
    front = [h for c, h in zip(m['chapters'], chapter_html) if c.get('kind') == 'cover']
    rest = [h for c, h in zip(m['chapters'], chapter_html) if c.get('kind') != 'cover']
    lite += '\n'.join(front) + '\n<main>\n' + '\n\n'.join(rest) + '\n</main>\n</body>\n</html>\n'

    # 完整版發布版：被搬用的節 lede 下加一行
    full = src_html
    inserts = []
    for sid, labs in used_sections.items():
        sec = dom.by_id.get(sid)
        lede = next((c for c in sec.children if c.tag == 'p' and 'lede' in c.classes()), None) if sec else None
        joined = '、'.join(labs)
        line = '\n<p class="small" data-lite-link="1">新手實作版%s%s是這一節的做法版。</p>' % (
            joined, ' ' if re.search(r'[A-Za-z0-9]$', joined) else '')
        if lede is None:
            h2 = next((c for c in sec.children if c.tag == 'h2'), None)
            if h2 is None:
                raise BuildError('節 %s 沒有 lede 也沒有 h2，放不下實作版連結那一行' % sid)
            inserts.append((h2.end, line))
        else:
            inserts.append((lede.end, line))
    for pos, line in sorted(inserts, key=lambda x: -x[0]):
        full = full[:pos] + line + full[pos:]
    report['lede_links'] = used_sections
    return lite, full, report


# ---------------------------------------------------------------- PDF

def open_details(s, only_marked=False):
    """PDF 用：把摺疊區展開。工作表（only_marked=False）全部展開；
    完整版（only_marked=True，v6.1 拍板 D10＋S6）只展開帶 data-print 屬性的（要動筆的欄位表、空白版、查表頁），
    教學性的長表維持收合，summary 後面由 FULL_PRINT_CSS 印出「紙本未印」提示。"""
    if only_marked:
        return re.sub(r'<details\b(?=[^>]*\sdata-print=)(?![^>]*\sopen\b)', '<details open', s)
    return re.sub(r'<details\b(?![^>]*\sopen\b)', '<details open', s)


def chrome_pdf(html_path, pdf_path):
    # 注意：加 --user-data-dir 在這台機器上會讓 headless 卡住不出檔（2026-09-16 實測），所以不加。
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--generate-pdf-document-outline',
           '--virtual-time-budget=8000', '--print-to-pdf=' + pdf_path, 'file://' + html_path]
    if os.path.exists(pdf_path): os.remove(pdf_path)
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    except subprocess.TimeoutExpired:
        raise BuildError('Chrome 列印超過 300 秒沒結束：%s' % html_path)
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise BuildError('Chrome 沒有產生 PDF：%s' % pdf_path)


def link_pages(pdf_path):
    import fitz
    d = fitz.open(pdf_path); out = {}
    for p in d:
        for l in p.get_links():
            nd = l.get('nameddest')
            if nd and l.get('page', -1) >= 0:
                out.setdefault(nd, l['page'] + 1)
    n = d.page_count; d.close()
    return out, n


def print_with_toc(html, html_path, pdf_path, span_re, width):
    """兩次（最多四次）列印：第一次讀目錄連結指向的頁，填進目錄再印，直到頁碼不再變。"""
    def fill(s, pages):
        return re.sub(span_re, lambda mm: mm.group(1) + str(pages.get(mm.group(2), '?')).rjust(width) + mm.group(3), s)
    cur = fill(html, {})
    last = None
    for attempt in range(4):
        write(html_path, cur)
        chrome_pdf(html_path, pdf_path)
        pages, n = link_pages(pdf_path)
        if pages == last:
            return pages, n, attempt + 1
        last = pages
        cur = fill(html, pages)
    raise BuildError('目錄頁碼印了四次還在變：%s' % pdf_path)


NEAR_EMPTY_CHARS = 250  # 完整版 PDF：非空白字元少於這個數的頁算「近乎空白」（哨兵也用）


def page_chars(pdf_path):
    import fitz
    d = fitz.open(pdf_path)
    out = [len(re.sub(r'\s', '', p.get_text())) for p in d]
    d.close()
    return out


def tail_flows(pdf_path, pages, order, flows):
    """完整版每節從新的一頁開始。節尾只剩本節行動、黃框或一兩行掉到新頁、那一頁近乎空白時，
    讓下一節接在那一頁排（不另起新頁）。回傳這一輪要新增的節 id。"""
    chars = page_chars(pdf_path)
    starts = [(sid, pages[sid]) for sid in order if sid in pages]
    new = set()
    for (a, pa), (b, pb) in zip(starts, starts[1:]):
        tail = pb - 1
        if b in flows or tail <= pa or tail < 1:
            continue
        if chars[tail - 1] < NEAR_EMPTY_CHARS:
            new.add(b)
    return new


def flow_css(flows):
    if not flows:
        return ''
    sel = ','.join('section.part#%s' % s for s in sorted(flows))
    return '\n@media print{%s{break-before:auto!important;page-break-before:auto!important}}\n' % sel


def set_meta(pdf_path, title, author, subject):
    import fitz
    d = fitz.open(pdf_path)
    meta = d.metadata or {}
    meta.update({'title': title, 'author': author, 'subject': subject})
    d.set_metadata(meta)
    tmp = pdf_path + '.tmp'
    d.save(tmp, garbage=1, deflate=True); d.close()
    os.replace(tmp, pdf_path)


def fix_full_outline(pdf_path, full_html):
    """完整版書籤：Chrome 把 h2 的節號 span 和節名黏在一起（「1投資賺的是誰的錢？」），改成「1 投資賺的是誰的錢？」。
    只改和原文 h2（span.num＋節名）完全對得上的書籤。回傳改了幾條。"""
    import fitz
    want = {}
    for num, rest in re.findall(r'<h2\b[^>]*>\s*<span\b[^>]*class="num"[^>]*>(.*?)</span>(.*?)</h2>', full_html, flags=re.S):
        n = html_text(num).strip(); t = html_text(rest).strip()
        if n and t:
            want[n + t] = n + ' ' + t
    d = fitz.open(pdf_path)
    toc = d.get_toc(simple=False); changed = 0
    for e in toc:
        key = re.sub(r'\s+', '', e[1])
        for k, v in want.items():
            if re.sub(r'\s+', '', k) == key and e[1] != v:
                e[1] = v; changed += 1; break
    if changed:
        d.set_toc(toc)
        tmp = pdf_path + '.tmp'
        d.save(tmp, garbage=1, deflate=True); d.close()
        os.replace(tmp, pdf_path)
    else:
        d.close()
    return changed


def make_pdfs(m, lite, full):
    P = m['_paths']
    pdir = rp(P['print_dir']); edir = rp(P['export_dir'])
    os.makedirs(pdir, exist_ok=True); os.makedirs(edir, exist_ok=True)
    ln = P['lite_export_name'].format(version=m['version'])
    fn = P['full_export_name'].format(version=m['version'])
    lite_pdf = os.path.join(edir, ln + '.pdf'); full_pdf = os.path.join(edir, fn + '.pdf')

    lp = open_details(lite)
    # 目錄頁碼只在 PDF 流程顯示（匯出的 HTML 自己列印時不會印出佔位的 00）
    lp = lp.replace('</style>', LITE_PRINT_CSS + '</style>', 1)
    lpages, ln_pages, lpasses = print_with_toc(lp, os.path.join(pdir, 'print-lite.html'), lite_pdf,
                                               r'(<span class="lite-toc-pg" data-for="([^"]+)">)[^<]*(</span>)', 2)
    set_meta(lite_pdf, '%s｜%s %s' % (m['book_title'], m['edition'], m['version']), m['author'], '%s／%s' % (m['version'], m['date']))

    fp = open_details(full, only_marked=True)
    fp = fp.replace('</style>', FULL_PRINT_CSS + '</style>', 1)
    toc = re.search(r'<nav class="toc".*?</nav>', fp, flags=re.S)
    if toc:
        t2 = re.sub(r'(<a href="#([\w-]+)">.*?)(</a>)', r'\1<span class="toc-pg" data-for="\2">000</span>\3', toc.group(0), flags=re.S)
        fp = fp[:toc.start()] + t2 + fp[toc.end():]
    toc_order = re.findall(r'<a href="#([\w-]+)">', toc.group(0)) if toc else []
    # 近乎空白的節尾頁：讓下一節接著排，再印一次，直到沒有新的（最多四輪）
    flows = set(); fpasses = 0
    for _round in range(4):
        fpx = fp.replace('</style>', flow_css(flows) + '</style>', 1)
        fpages, fn_pages, np_ = print_with_toc(fpx, os.path.join(pdir, 'print-full.html'), full_pdf,
                                               r'(<span class="toc-pg" data-for="([^"]+)">)[^<]*(</span>)', 1)
        fpasses += np_
        new = tail_flows(full_pdf, fpages, toc_order, flows)
        if not new:
            break
        flows |= new
    fix_full_outline(full_pdf, full)  # fix-r3：書籤節號後補空格
    ftitle = re.search(r'<title>(.*?)</title>', full, flags=re.S)
    set_meta(full_pdf, '%s %s' % (html_text(ftitle.group(1)) if ftitle else m['book_title'], m['version']), m['author'], '%s／%s' % (m['version'], m['date']))

    shutil.copyfile(rp(P['lite_html']), os.path.join(edir, ln + '.html'))
    shutil.copyfile(rp(P['full_html']), os.path.join(edir, fn + '.html'))
    return {'lite_pdf': lite_pdf, 'full_pdf': full_pdf, 'lite_pages': ln_pages, 'full_pages': fn_pages,
            'lite_passes': lpasses, 'full_passes': fpasses, 'full_flows': sorted(flows),
            'lite_html_export': os.path.join(edir, ln + '.html'), 'full_html_export': os.path.join(edir, fn + '.html'),
            'lite_print_html': os.path.join(pdir, 'print-lite.html'), 'full_print_html': os.path.join(pdir, 'print-full.html')}


FRAGMENT_TAGS = ['div', 'p', 'li', 'ul', 'ol', 'a', 'strong', 'h3', 'h4', 'section', 'figure',
                 'details', 'table', 'span', 'dt', 'dd', 'dl', 'mark']


def fragment_of(h, kind, label, cover_title=None):
    """發布用片段：去掉 doctype／html／head／body 外殼（和交班文件「改完後的固定流程」第 4 步同一套做法）。
    先做和那段一樣的結構檢查：標籤開關成對、站內連結都有 id、<a> 不巢狀、封面只有一個。
    `cover_title`＝實作版／工作表封面應該印的書名（manifest 第一章的 title），不給就不檢查書名。"""
    for t in FRAGMENT_TAGS:
        o = len(re.findall(r'<%s\b[^>]*>' % t, h)); c = len(re.findall(r'</%s>' % t, h))
        if o != c:
            raise BuildError('%s 的 <%s> 開關不成對（%d 開、%d 關）' % (label, t, o, c))
    ids = set(re.findall(r'id="([^"]+)"', h))
    bad = [x for x in re.findall(r'href="#([^"]+)"', h) if x not in ids]
    if bad:
        raise BuildError('%s 有指不到的站內連結：%s' % (label, '、'.join(sorted(set(bad))[:10])))
    d = 0
    for t in re.finditer(r'<a\b[^>]*>|</a>', h):
        d += -1 if t.group(0) == '</a>' else 1
        if d < 0 or d > 1:
            raise BuildError('%s 的 <a> 巢狀或多了結束標籤' % label)
    s = re.sub(r'<!doctype html>\s*', '', h, flags=re.I)
    s = re.sub(r'</?(html|head|body)\b[^>]*>\s*', '', s)
    if kind == 'full':
        n = s.count('<header class="cover"')
        if n != 1:
            raise BuildError('%s 的完整版封面有 %d 個（要剛好 1 個）' % (label, n))
    else:
        mm = re.findall(r'<header[^>]*class="[^"]*\blite-cover\b[^"]*"', s)
        if len(mm) != 1:
            raise BuildError('%s 的實作版封面有 %d 個（要剛好 1 個）' % (label, len(mm)))
        head = re.sub(r'<[^>]+>', '', s[s.find(mm[0]):s.find(mm[0]) + 800])
        if cover_title and cover_title not in head:
            raise BuildError('%s 的封面找不到書名「%s」' % (label, cover_title))
    return s


def lite_cover_title(m):
    """實作版／工作表封面應該印的書名＝manifest 裡 kind=cover 那一章的 title。"""
    for c in m['chapters']:
        if c.get('kind') == 'cover':
            return c.get('title')
    return None


def write_fragments(m):
    """兩份發布用片段（output/guide.html、output/lite.html），每次 build 都重產。"""
    P = m['_paths']
    done = []
    for kind, srck, dstk in (('full', 'full_html', 'full_fragment'), ('lite', 'lite_html', 'lite_fragment')):
        dst = P.get(dstk)
        if not dst:
            continue
        write(dst, fragment_of(read(P[srck]), kind, P[srck], lite_cover_title(m)))
        done.append(dst)
    return done


def dump_texts(m, pdf):
    """審查用的純文字檔（lite/work/*.txt）：每次 build 都重產，避免審查代理讀到過期的檔。
    完整版從 output/full-v60-out.html 抽（guidetools.to_text）；實作版從剛印好的 PDF 逐頁抽。
    檔頭記抽取時間與來源。--no-pdf 時實作版那一份不動（會印警告）。"""
    P = m['_paths']
    ts = time.strftime('%Y-%m-%d %H:%M')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import guidetools
    done = []
    head = '（抽取時間 %s；來源 %s，由 tools/build_lite.py 產生；產生方式 guidetools.to_text）\n\n' % (ts, P['full_html'])
    write(P['full_text'], head + guidetools.to_text(rp(P['full_html'])) + '\n')
    done.append(P['full_text'])
    if pdf:
        import fitz
        rel = os.path.relpath(pdf['lite_pdf'], ROOT)
        d = fitz.open(pdf['lite_pdf'])
        n = d.page_count
        parts = ['===== 第 %d 頁 / 共 %d 頁 =====\n%s' % (i, n, p.get_text()) for i, p in enumerate(d, 1)]
        d.close()
        write(P['lite_text'], '（抽取時間 %s；來源 %s，共 %d 頁）\n' % (ts, rel, n) + '\n'.join(parts))
        done.append(P['lite_text'])
    return done


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default='lite/manifest.json')
    ap.add_argument('--no-pdf', action='store_true')
    ap.add_argument('--stamp')
    ap.add_argument('--fingerprint')
    a = ap.parse_args(argv)
    try:
        m = load_manifest(a.manifest)
        if a.stamp:
            stamp_alt(m, a.stamp); return 0
        if a.fingerprint:
            dom = Dom(read(m['_paths']['source']))
            nodes = select(dom, a.fingerprint)
            for n in nodes:
                sec = dom.section_of(n)
                print('%s  <%s> in #%s  %s' % (sha256_block(dom.outer(n)), n.tag, sec.attrs['id'] if sec is not None else '-', dom.text(n)[:40]))
            print('%d match(es)' % len(nodes)); return 0 if nodes else 1
        lite, full, report = build(m)
    except BuildError as e:
        print('BUILD FAILED'); print(e); return 1
    P = m['_paths']
    write(P['lite_html'], lite); write(P['full_html'], full)
    print('wrote', P['lite_html'], '(%d bytes)' % len(lite.encode('utf-8')))
    print('wrote', P['full_html'], '(%d bytes)' % len(full.encode('utf-8')))
    for sid, labs in report['lede_links'].items():
        print('  lede link: #%s ← 新手實作版%s' % (sid, '、'.join(labs)))
    try:
        for p in write_fragments(m):
            print('wrote', p)
    except BuildError as e:
        print('FRAGMENT FAILED'); print(e); return 1
    pdf = None
    if not a.no_pdf:
        try:
            pdf = make_pdfs(m, lite, full)
        except BuildError as e:
            print('PDF FAILED'); print(e); return 1
        print('wrote', os.path.relpath(pdf['lite_pdf'], ROOT), '(%d 頁，印 %d 次)' % (pdf['lite_pages'], pdf['lite_passes']))
        print('wrote', os.path.relpath(pdf['full_pdf'], ROOT), '(%d 頁，印 %d 次)' % (pdf['full_pages'], pdf['full_passes']))
        if pdf['full_flows']:
            print('  完整版節尾近乎空白、下一節接著排：%s' % '、'.join(pdf['full_flows']))
    try:
        for p in dump_texts(m, pdf):
            print('wrote', p)
    except Exception as e:
        print('TEXT DUMP FAILED'); print(e); return 1
    if not pdf:
        print('  --no-pdf：%s 沒有重產，可能是舊的' % P['lite_text'])
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lite_sentinels
    return lite_sentinels.run(m, pdf_info=pdf, build_report=report)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
