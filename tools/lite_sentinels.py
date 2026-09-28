# -*- coding: utf-8 -*-
"""可列印工作表（v6.0 時是新手實作版）哨兵。build_lite.py 每次結束都會呼叫；也可以單獨跑（讀已經產生的 HTML／PDF）。

用法：
  python3 tools/lite_sentinels.py                                   # lite/manifest.json
  python3 tools/lite_sentinels.py --manifest lite/manifest.sample.json

輸出每行一條：OK／FAIL／WARN／SKIP ［類別］ 訊息。最後一行 SENTINELS OK 或 SENTINELS FAILED (n)。
任何 FAIL → exit 1。格式規格見 docs/core-edition/specs/lite-format.md 第 7 節。
"""
import sys, os, re, json, subprocess, glob, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_lite as B

SKIPPABLE = {'version', 'unused_marks', 'facts', 'cases', 'pages'}
# 可列印工作表（v7「三張紙」，spec-v61-worksheet.md 末節）：
#   一塊＝一頁，頁數 5 或 6；6 頁時可以是 6 塊，也可以是 5 塊＋末頁留白（blank_page）。
#   雙面印時 1–2、3–4、5–6 各是同一張紙的正反面，所以塊數也決定了紙數。
#   v6.1 的舊規則是固定 4 塊 4 頁（計畫表、查表頁、年檢表、兩張卡），v7 改設計後放進下面的區間；
#   「每塊一頁」「每塊要有來源」「不得出現章號與附錄」三條沒有放寬，奇偶成對那條從只管前兩頁擴到管每一張紙。
WORKSHEET_PAGES_MIN = 5
WORKSHEET_PAGES_MAX = 6


def worksheet_mode(m):
    """工作表模式：manifest 裡沒有任何一章有章號（label），也沒有目錄（toc）。
    這種 manifest 產的是《可列印工作表》，不是十二章的書；和「章」「目錄」「附 B」綁在一起的哨兵
    在這種模式下沒有東西可查，改印 SKIP（不是通過），另外由 worksheet 那一支把關。"""
    chs = m.get('chapters') or []
    has_label = any(c.get('label') for c in chs)
    has_toc = any(b.get('toc') for c in chs for b in c.get('blocks', []))
    return not has_label and not has_toc


class Report(object):
    def __init__(self, skip):
        self.lines = []; self.fails = 0; self.skip_cats = set(skip)

    def ok(self, cat, msg): self.lines.append('OK   [%s] %s' % (cat, msg)); print(self.lines[-1])

    def fail(self, cat, msg):
        if cat in self.skip_cats:
            self.lines.append('SKIP [%s] （manifest sentinel_skip）%s' % (cat, msg))
        else:
            self.fails += 1; self.lines.append('FAIL [%s] %s' % (cat, msg))
        print(self.lines[-1])

    def warn(self, cat, msg): self.lines.append('WARN [%s] %s' % (cat, msg)); print(self.lines[-1])

    def skip(self, cat, msg): self.lines.append('SKIP [%s] %s' % (cat, msg)); print(self.lines[-1])

    def info(self, msg): self.lines.append('     ' + msg); print(self.lines[-1])


def text_outside(dom, allowed_selectors):
    allowed = []
    for sel in allowed_selectors:
        allowed += B.select(dom, sel)
    allowed = B.outermost(allowed)
    s = dom.s; out = []; i = 0
    for n in sorted(allowed, key=lambda x: x.start):
        if n.start < i: continue
        out.append(s[i:n.start]); out.append('<span> ⟨略⟩ </span>'); i = n.end
    out.append(s[i:])
    body = ''.join(out)
    body = re.sub(r'<head\b.*?</head>', ' ', body, flags=re.S)
    return B.html_text(body)


def page_last_text_pct(pdf_path):
    """每頁最後一段文字（不含只有頁碼的那段）的下緣，占頁高的百分比。"""
    import fitz
    d = fitz.open(pdf_path); out = []
    for p in d:
        ys = [b[3] for b in p.get_text('blocks') if b[4].strip() and not re.fullmatch(r'\s*\d+\s*', b[4])]
        out.append(int(round(max(ys, default=0) / p.rect.height * 100)))
    d.close()
    return out


def json_path(d, path):
    cur = d
    for part in path.split('.'):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def manifest_text_fields(m):
    for ch in m['chapters']:
        for fld in ('title', 'gain'):
            if ch.get(fld): yield ch['id'], fld, ch[fld]
        for b in ch.get('blocks', []):
            if 'glue' in b: yield ch['id'], 'glue', B.html_text(b['glue'])
            if 'action' in b: yield ch['id'], 'action', b['action']


def manifest_srcs(m):
    for ch in m['chapters']:
        for b in ch.get('blocks', []):
            if 'src' in b: yield ch['id'], b['src']


def manifest_alts(m):
    for ch in m['chapters']:
        for b in ch.get('blocks', []):
            if 'alt' in b: yield ch['id'], b['alt']


# ---------------------------------------------------------------- PDF 讀取

def pdf_chapter_pages(pdf_path, m):
    import fitz
    d = fitz.open(pdf_path)
    outline = d.get_toc()
    chs = m['chapters']
    starts = {}
    for ch in chs:
        if ch.get('kind') == 'cover':
            starts[ch['id']] = 1; continue
        want = B.compact(B.chapter_heading(ch))
        hit = [p for lvl, t, p in outline if B.compact(t) == want]
        starts[ch['id']] = hit[0] if hit else None

    def at_top(ch):
        p = starts.get(ch['id'])
        if p is None: return False
        blocks = [b for b in d[p - 1].get_text('blocks') if b[4].strip() and not re.fullmatch(r'\d+', b[4].strip())]
        if not blocks: return False
        blocks.sort(key=lambda b: (round(b[1]), b[0]))
        first = B.compact(blocks[0][4])
        key = B.compact(ch.get('label') or ch['title'])
        return first.startswith(key[:8]) or B.compact(ch['title'])[:8] in first[:40]

    rows = []
    for i, ch in enumerate(chs):
        s = starts[ch['id']]
        if s is None:
            rows.append((ch, None, None, None, None)); continue
        if i + 1 < len(chs) and starts.get(chs[i + 1]['id']):
            nxt = chs[i + 1]; ns = starts[nxt['id']]
            e = ns - 1 if at_top(nxt) else ns
        else:
            e = d.page_count
        top = True if ch.get('kind') == 'cover' else at_top(ch)
        rows.append((ch, s, max(e, s), max(e, s) - s + 1, top))
    info = {'page_count': d.page_count, 'rows': rows, 'outline_starts': starts}
    d.close()
    return info


def toc_printed_numbers(pdf_path, targets, max_page=None):
    """讀目錄連結：targets＝{nameddest: 標題}。同一頁連續指向同一目標的連結（標題換行會拆成好幾塊）先合併，
    合併後的文字要以標題開頭才算目錄項（排除內文的節號連結），結尾的數字就是印出的頁碼。
    回傳 [(nameddest, 連結目標頁, 印出的頁碼)]。"""
    import fitz
    d = fitz.open(pdf_path); out = []
    for p in d:
        if max_page is not None and p.number + 1 >= max_page: break
        groups = []
        for l in p.get_links():
            nd = l.get('nameddest')
            if nd not in targets: continue
            words = p.get_text('words', clip=fitz.Rect(l['from']) + (-1, -1, 1, 1))
            txt = ''.join(w[4] for w in sorted(words, key=lambda w: (w[5], w[6], w[7])))
            if groups and groups[-1][0] == nd:
                groups[-1][2] += txt
            else:
                groups.append([nd, l['page'] + 1, txt])
        for nd, dest, txt in groups:
            t = B.compact(txt)
            if not t.startswith(B.compact(targets[nd])[:6]):
                continue
            mm = re.search(r'(\d+)$', t)
            out.append((nd, dest, int(mm.group(1)) if mm else None))
    d.close()
    return out


# ---------------------------------------------------------------- 主程式

def _section_num(dom, sec):
    """節 h2 裡 span.num 的數字；沒有節號回 None。"""
    h2 = next((c for c in sec.children if c.tag == 'h2'), None)
    if h2 is None:
        return None
    sp = next((c for c in h2.children if c.tag == 'span' and 'num' in c.classes()), None)
    return B.html_text(dom.inner(sp)).strip() if sp is not None else None


def check_toc_order(dom):
    """order：nav.toc 裡 <a href="#id"> 的順序＝正文 section.part 的順序（排除 group-*），每節剛好一次；
    每個 details.toc-part[data-group=X]，X 必須是正文中緊接在該組第一節前面的那個 section。
    回傳 (問題清單, 通過時的說明)。"""
    bad = []
    body = [n.attrs['id'] for n in dom.nodes if n.tag == 'section' and 'part' in n.classes() and n.attrs.get('id')]
    content = [i for i in body if not i.startswith('group-')]
    nav = next((n for n in dom.nodes if n.tag == 'nav' and n.attrs.get('id') == 'toc'), None)
    if nav is None:
        return ['原文找不到 nav#toc'], ''
    toc = re.findall(r'<a href="#([\w-]+)">', dom.outer(nav))
    dups = sorted(set(i for i in toc if toc.count(i) > 1))
    if dups:
        bad.append('目錄同一節出現不只一次：%s' % '、'.join(dups))
    missing = [i for i in content if i not in toc]
    extra = [i for i in toc if i not in content]
    if missing:
        bad.append('正文有、目錄沒有：%s' % '、'.join(missing))
    if extra:
        bad.append('目錄有、正文沒有（或指到 group-* 分組節）：%s' % '、'.join(sorted(set(extra))))
    if not dups and not missing and not extra and toc != content:
        k = next(j for j, (a, b) in enumerate(zip(toc, content)) if a != b)
        bad.append('目錄順序和正文不同：第 %d 條起目錄是 %s，正文是 %s' % (
            k + 1, '→'.join(toc[k:k + 3]), '→'.join(content[k:k + 3])))
    groups = [n for n in dom.nodes if n.tag == 'details' and 'toc-part' in n.classes()
              and any(a is nav for a in n.ancestors()) and n.attrs.get('data-group')]
    for g in groups:
        x = g.attrs['data-group']
        first = re.search(r'<a href="#([\w-]+)">', dom.outer(g))
        if not first:
            bad.append('目錄組 data-group=%s 裡沒有任何節連結' % x); continue
        f = first.group(1)
        if f not in body:
            continue  # 上面已經報過
        k = body.index(f)
        prev = body[k - 1] if k > 0 else None
        if prev != x:
            bad.append('目錄組 data-group=%s：正文裡緊接在該組第一節 %s 前面的是 %s，不是 %s' % (x, f, prev, x))
    return bad, '目錄 %d 條連結的順序＝正文 %d 節（不含 %d 個 group-* 分組節），每節剛好一次；data-group 組 %d 個都對得上' % (
        len(toc), len(content), len(body) - len(content), len(groups))


def check_xref_numbers(dom):
    """xref_num：每個 <a class="xref" href="#X">純數字</a>，數字＝X 所在節（卡片錨點算所屬節）h2 的 span.num。
    v7.0 第四輪（裁判④）：只看「錨文字整串是數字」會漏掉把節號寫進錨文字裡的連結
    （例如 <a class="xref" href="#plan-table">計畫表在第 11 節</a> 連號後沒跟著改）。
    所以再加一類：任何 a[href^="#"]（不限 xref）的錨文字裡出現「第 N 節」，N 也要等於目標所在節的 span.num。"""
    bad = []; n_ok = 0
    IN_TEXT = re.compile(r'第\s*(\d+)\s*節')
    for n in dom.nodes:
        if n.tag != 'a':
            continue
        href0 = n.attrs.get('href') or ''
        txt0 = B.html_text(dom.inner(n)).strip()
        if href0.startswith('#') and not re.fullmatch(r'\d+', txt0):
            for mm in IN_TEXT.finditer(txt0):
                num_in_text = mm.group(1)
                tgt0 = dom.by_id.get(href0[1:])
                if tgt0 is None:
                    bad.append('錨文字「%s」的連結 %s 找不到目標' % (txt0[:24], href0)); continue
                sec0 = dom.section_of(tgt0)
                num0 = _section_num(dom, sec0) if sec0 is not None else None
                where0 = dom.section_of(n)
                loc0 = where0.attrs['id'] if where0 is not None else '封面／節外'
                if num0 is None:
                    bad.append('%s 裡錨文字「%s」連到 %s（所在節 %s 沒有節號）'
                               % (loc0, txt0[:24], href0, sec0.attrs['id'] if sec0 is not None else '無'))
                elif num0 != num_in_text:
                    bad.append('%s 裡錨文字「%s」連到 %s，那一節（%s）顯示的是第 %s 節'
                               % (loc0, txt0[:24], href0, sec0.attrs['id'], num0))
                else:
                    n_ok += 1
        if 'xref' not in n.classes():
            continue
        txt = txt0
        if not re.fullmatch(r'\d+', txt):
            continue
        href = n.attrs.get('href') or ''
        tid = href[1:] if href.startswith('#') else None
        tgt = dom.by_id.get(tid) if tid else None
        if tgt is None:
            bad.append('錨文字 %s 的連結 %s 找不到目標' % (txt, href)); continue
        sec = dom.section_of(tgt)
        num = _section_num(dom, sec) if sec is not None else None
        where = dom.section_of(n)
        loc = where.attrs['id'] if where is not None else '封面／節外'
        if num is None:
            bad.append('%s 裡「第 %s 節」連到 %s（所在節 %s 沒有節號）' % (loc, txt, href, sec.attrs['id'] if sec is not None else '無'))
        elif num != txt:
            bad.append('%s 裡「第 %s 節」連到 %s，那一節（%s）顯示的是第 %s 節' % (loc, txt, href, sec.attrs['id'], num))
        else:
            n_ok += 1
    return bad, '%d 個節號連結（錨文字整串是數字，或錨文字裡寫了「第 N 節」），數字都等於目標所在節的顯示節號' % n_ok


def check_part_maps(dom):
    """part_maps：group-* 分組節的 ol.part-map 清單要和目錄、目標節逐字一致。第 1 批加入分組節地圖後才啟用；
    原文還沒有任何 ol.part-map 時回傳 (None, 理由)。
    v7.0（全書 28 節連號）：地圖每一行都必須有剛好一個 map-num，且等於目標節 h2 的 span.num。
    舊規則「目標節沒有節號時不准有 map-num」在每一節都有號之後只會放過漏補的行，改成直接報錯。"""
    maps = [n for n in dom.nodes if n.tag == 'ol' and 'part-map' in n.classes()]
    if not maps:
        return None, '原文還沒有 ol.part-map（施工文件第 1 批才加入分組節地圖），這一支先不查'
    bad = []; n_li = 0
    txt = lambda n: B.html_text(dom.inner(n)).strip()
    kids = lambda n, tag, cls=None: [c for c in n.children if c.tag == tag and (cls is None or cls in c.classes())]
    nav = next((n for n in dom.nodes if n.tag == 'nav' and n.attrs.get('id') == 'toc'), None)
    toc_groups = {}
    if nav is not None:
        for g in dom.nodes:
            if g.tag == 'details' and 'toc-part' in g.classes() and g.attrs.get('data-group') \
                    and any(a is nav for a in g.ancestors()):
                m = re.search(r'<span class="toc-part-desc">(.*?)</span>', dom.outer(g), re.S)
                desc_t = B.html_text(m.group(1)).strip() if m else None
                toc_groups[g.attrs['data-group']] = (re.findall(r'<a href="#([\w-]+)">', dom.outer(g)), desc_t)
    groups = [n for n in dom.nodes if n.tag == 'section' and 'part' in n.classes()
              and (n.attrs.get('id') or '').startswith('group-')]
    for sec in groups:
        gid = sec.attrs['id']
        pms = [m for m in maps if dom.section_of(m) is sec]
        if len(pms) != 1:
            bad.append('%s 裡應該剛好有 1 個 ol.part-map，實際 %d 個' % (gid, len(pms))); continue
        if gid not in toc_groups:
            bad.append('%s 在目錄裡找不到 details.toc-part[data-group=%s]' % (gid, gid)); continue
        toc_ids, toc_desc = toc_groups[gid]
        lede = next(iter(kids(sec, 'p', 'lede')), None)
        if lede is None or txt(lede) != toc_desc:
            bad.append('%s 的 p.lede（%s）≠ 目錄同組 toc-part-desc（%s）' % (gid, txt(lede) if lede is not None else '無', toc_desc))
        lis = kids(pms[0], 'li')
        hrefs = []
        for li in lis:
            n_li += 1
            a = next(iter(kids(li, 'a')), None)
            if a is None:
                bad.append('%s 地圖有一行沒有連結' % gid); continue
            tid = (a.attrs.get('href') or '')[1:]
            hrefs.append(tid)
            tgt = dom.by_id.get(tid)
            if tgt is None or tgt.tag != 'section':
                bad.append('%s 地圖連到 #%s，那不是一個節' % (gid, tid)); continue
            h2 = next(iter(kids(tgt, 'h2')), None)
            name = B.html_text(re.sub(r'<span\b[^>]*class="num"[^>]*>.*?</span>', '', dom.inner(h2), flags=re.S)).strip() if h2 is not None else None
            if txt(a) != name:
                bad.append('%s 地圖 #%s 的連結文字「%s」≠ 節名「%s」' % (gid, tid, txt(a), name))
            ml = kids(li, 'span', 'map-lede')
            tl = next(iter(kids(tgt, 'p', 'lede')), None)
            if len(ml) != 1 or tl is None or txt(ml[0]) != txt(tl):
                bad.append('%s 地圖 #%s 的 map-lede「%s」≠ 那一節的 p.lede「%s」' % (
                    gid, tid, txt(ml[0]) if len(ml) == 1 else '（%d 個）' % len(ml), txt(tl) if tl is not None else '無'))
            mn = kids(li, 'span', 'map-num')
            num = _section_num(dom, tgt)
            if num is None:
                # v7.0 起全書 28 節連號，每一節都有 h2 span.num；指到沒有節號的節就是漏補。
                bad.append('%s 地圖 #%s 指到的節沒有節號（v7.0 起每一節都有號）' % (gid, tid))
            elif len(mn) != 1 or txt(mn[0]) != num:
                bad.append('%s 地圖 #%s 的 map-num「%s」≠ 那一節的節號 %s' % (gid, tid, txt(mn[0]) if mn else '缺', num))
        if hrefs != toc_ids:
            bad.append('%s 地圖順序 %s ≠ 目錄同組 %s' % (gid, '→'.join(hrefs), '→'.join(toc_ids)))
    stray = [m for m in maps if dom.section_of(m) is None or not dom.section_of(m).attrs['id'].startswith('group-')]
    if stray:
        bad.append('有 %d 個 ol.part-map 不在 group-* 分組節裡' % len(stray))
    return bad, '%d 個分組節地圖、%d 行：順序＝目錄同組，節名、開場白、節號都和目標節逐字一致；分組節 lede＝目錄說明' % (len(groups), n_li)


def run(m, pdf_info=None, build_report=None):
    P = m['_paths']
    skip = m.get('sentinel_skip') or []
    R = Report(skip if not m['_is_main'] else [])
    ws = worksheet_mode(m)
    print('== 哨兵：%s%s ==' % (m['_path'], '（工作表模式）' if ws else ''))
    if m['_is_main'] and skip:
        R.fail('manifest', 'lite/manifest.json 不准有 sentinel_skip（只給示範或實驗用的 manifest）：%s' % skip)
    for k in skip:
        if k not in SKIPPABLE:
            R.fail('manifest', 'sentinel_skip 裡的 %r 不能跳過（可跳過：%s）' % (k, sorted(SKIPPABLE)))

    try:
        src = B.read(P['source']); lite = B.read(P['lite_html']); full = B.read(P['full_html'])
    except IOError as e:
        R.fail('files', '讀不到輸入或輸出：%s' % e)
        print('SENTINELS FAILED (%d)' % R.fails); return 1
    sdom = B.Dom(src); ldom = B.Dom(lite); fdom = B.Dom(full)
    names = B.section_names(sdom)

    # 1. 短稿指紋與數字
    alt_dir = B.rp(P['alt_dir'])
    alt_ids = set(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(alt_dir, '*.html')))
    alt_ids |= set(a for _, a in manifest_alts(m))
    alt_ids |= set(re.findall(r'data-lite-alt-out="([^"]+)"', lite))
    # 退場短稿（lite/alt/retired/）：檔案還在，只是這一版沒有用；原文的標記指到這裡不算錯（v6.1 工作表）
    retired_ids = set(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(alt_dir, 'retired', '*.html')))
    for n in sdom.nodes:
        for a in n.tokens('data-lite-alt'):
            if a not in alt_ids and a not in retired_ids:
                R.fail('unused_marks', '原文標了 data-lite-alt="%s"，但 %s（含 retired/）沒有這份短稿' % (a, P['alt_dir']))
    for aid in sorted(alt_ids):
        try:
            info = B.load_alt(m, aid)
        except B.BuildError as e:
            R.fail('alt', str(e)); continue
        if info['norm'] != B.NORM_VERSION:
            R.fail('alt', '短稿 %s 的 norm 是 %r，目前是 %s' % (aid, info['norm'], B.NORM_VERSION))
        if not info['srcs']:
            R.fail('alt', '短稿 %s 檔頭沒有任何 src 行（先跑 build_lite.py --stamp %s）' % (aid, aid)); continue
        src_nodes = []; bad = False
        for sel, sha, nodes in B.alt_source_nodes(sdom, info):
            if len(nodes) != 1:
                R.fail('alt', '短稿 %s 的 src %r 在完整版對到 %d 個區塊（要剛好 1 個）' % (aid, sel, len(nodes))); bad = True; continue
            src_nodes.append(nodes[0])
            now = B.sha256_block(sdom.outer(nodes[0]))
            if now != sha:
                R.fail('alt', '原文改了，短稿要重看：%s（src %s；記錄 %s…，現在 %s…）' % (aid, sel, sha[:12], now[:12])); bad = True
        for n in sdom.nodes:
            if aid in n.tokens('data-lite-alt') and not any(x.start <= n.start and n.end <= x.end for x in src_nodes):
                sec = sdom.section_of(n)
                R.fail('alt', '原文 #%s 有 data-lite-alt="%s" 的區塊，但短稿檔頭沒有記它的指紋' % (sec.attrs['id'] if sec is not None else '-', aid)); bad = True
        allowed = set()
        for n in src_nodes: allowed |= B.numbers_in(sdom.text(n))
        extra = sorted(B.numbers_in(B.html_text(info['body'])) - allowed, key=lambda x: (len(x), x))
        if extra:
            R.fail('alt', '短稿 %s 有原文區塊裡沒有的數字：%s' % (aid, '、'.join(extra))); bad = True
        if not bad:
            R.ok('alt', '短稿 %s：%d 個原文區塊指紋相符，數字都在原文裡' % (aid, len(src_nodes)))

    # 2. 接合文字無數字
    digit_bad = [(c, f, t) for c, f, t in manifest_text_fields(m) if B.has_digit(t)]
    for c, f, t in digit_bad:
        R.fail('glue', '%s 的 %s 有阿拉伯數字：%r' % (c, f, t[:60]))
    if not digit_bad:
        R.ok('glue', '接合文字、章名、這章做完你會有什麼、動作框都沒有阿拉伯數字')

    # 3. 共同事實
    fp = P.get('facts')
    if not fp or not os.path.exists(B.rp(fp)):
        R.fail('facts', '找不到共同事實清單：%s' % fp)
    else:
        lines = [l.rstrip('\n') for l in open(B.rp(fp), encoding='utf-8')]
        facts = []  # (只查完整版?, 事實)
        for l in lines:
            s = l.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('full-only:'):
                facts.append((True, s.split(':', 1)[1].strip()))   # 這條內容已經不在實作版／工作表裡，只查完整版
            else:
                facts.append((False, s))
        lt = B.compact(B.html_text(lite)); ft = B.compact(B.html_text(full)); miss = 0
        for full_only, f in facts:
            targets = (('完整版', ft),) if full_only else (('實作版', lt), ('完整版', ft))
            for label, t in targets:
                if B.compact(f) not in t:
                    R.fail('facts', '%s 找不到共同事實：%s' % (label, f)); miss += 1
        if not miss:
            nb = len([1 for fo, _ in facts if not fo])
            R.ok('facts', '%d 條共同事實兩份都找得到；另外 %d 條標了 full-only，只查完整版（工作表沒有這些內容）'
                 % (nb, len(facts) - nb))

    # 4. 案例數字
    cp = P.get('case_checks')
    if not cp or not os.path.exists(B.rp(cp)):
        R.fail('cases', '找不到案例數字檢查清單：%s' % cp)
    else:
        calc = json.load(open(B.rp(P['calc_results']), encoding='utf-8'))
        checks = json.load(open(B.rp(cp), encoding='utf-8'))
        nbad = 0
        for c in checks:
            try:
                want = float(json_path(calc, c['path']))
            except Exception:
                R.fail('cases', '%s：calc-results.json 沒有 %s' % (c['id'], c['path'])); nbad += 1; continue
            scope = c.get('scope', 'lite')
            if scope == 'lite':
                t = B.html_text(lite)
            else:
                node = ldom.by_id.get(scope)
                if node is None:
                    R.fail('cases', '%s：實作版沒有 id=%s 的章' % (c['id'], scope)); nbad += 1; continue
                t = ldom.text(node)
            found = [mm.group(1).replace(',', '') for mm in re.finditer(c['pattern'], B.compact(t))]
            tol = float(c.get('tolerance', 0.5))
            if len(found) < int(c.get('min_count', 1)):
                R.fail('cases', '%s：在 %s 找不到 %r（要至少 %d 處）' % (c['id'], scope, c['pattern'], int(c.get('min_count', 1)))); nbad += 1; continue
            for v in found:
                if abs(float(v) - want) > tol:
                    R.fail('cases', '%s：實作版寫 %s，calc-results.json %s＝%s（差超過 %s）' % (c['id'], v, c['path'], want, tol)); nbad += 1
        if not nbad:
            R.ok('cases', '%d 條案例數字和 calc-results.json 相差都在容許範圍內' % len(checks))

    # 5. 代號
    tk = json.load(open(B.rp(P['tickers']), encoding='utf-8'))
    for label, dom, allow in (('實作版', ldom, tk['allow_lite']), ('完整版', fdom, tk['allow_full'])):
        t = text_outside(dom, allow); nb = 0
        for code in tk['codes']:
            for mm in re.finditer(r'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % re.escape(code), t):
                R.fail('tickers', '%s 在允許的位置以外出現代號 %s：…%s…' % (label, code, t[max(0, mm.start() - 20):mm.end() + 20])); nb += 1
        if not nb:
            R.ok('tickers', '%s：%d 個代號只出現在 %s' % (label, len(tk['codes']), '、'.join(allow)))

    # 6. 標籤（v7 第四輪 R5：帶框的 span.label-practice／label-principle 退場，改成句內白話。
    #    不再靠 span 找句子，改用固定的文字前綴：
    #      practice  句首前綴「本指南的做法：」——全份只准用在 labels.json 清單上的那幾句，後面必須接
    #                清單裡的標準開頭之一（白名單），而且清單上的每一件在完整版都不能少。
    #                清單以外的地方一律用不帶冒號的形式（小卡括號「（本指南的做法）」、
    #                句內「…是本指南的做法，你可以自己定」），所以不會誤中。
    #      principle 純文字「原則：」，每章仍然最多一個。
    #    舊規則會漏的：span 被刪掉就不再檢查（清單少一件也綠）。新規則用前綴掃全文＋清單
    #    覆蓋檢查，少一件會紅。)
    lb = json.load(open(B.rp(P['labels']), encoding='utf-8'))
    PRACTICE_PREFIX = lb.get('practice_prefix', '本指南的做法：')
    PRINCIPLE_PREFIX = lb.get('principle_prefix', '原則：')
    starts = [(B.compact(k), item['item']) for item in lb['practice'] for k in item.get('starts', [])]
    for label, dom, sec_sel, need_all in (('實作版', ldom, 'section.lite-ch', False),
                                          ('完整版', fdom, 'section.part', True)):
        ignore = B.outermost([x for sel in lb.get('ignore', []) for x in B.select(dom, sel)])
        secs = B.select(dom, sec_sel)
        nb = 0; npr = 0; nprin = 0; per_item = {}
        max_item = lb.get('practice_max_per_item')
        keep, pos = [], 0
        for x in sorted(ignore, key=lambda n: n.start):
            keep.append(dom.s[pos:x.start]); pos = x.end
        keep.append(dom.s[pos:])
        text = B.compact(B.html_text(''.join(keep)))
        pfx = B.compact(PRACTICE_PREFIX); i = text.find(pfx)
        while i >= 0:
            npr += 1
            tail = text[i + len(pfx):]
            hit = next((it for k, it in starts if tail.startswith(k)), None)
            if hit is None:
                R.fail('labels', '%s「%s」後面接的不是清單裡的標準開頭：%s…' % (label, PRACTICE_PREFIX, tail[:30])); nb += 1
            else:
                per_item[hit] = per_item.get(hit, 0) + 1
            i = text.find(pfx, i + 1)
        if max_item:
            for it, k in sorted(per_item.items()):
                if k > int(max_item):
                    R.fail('labels', '%s「%s」用在「%s」%d 次（每份最多 %s 次）' % (label, PRACTICE_PREFIX, it, k, max_item)); nb += 1
        if need_all:
            missing = [item['item'] for item in lb['practice'] if item['item'] not in per_item]
            if missing:
                R.fail('labels', '%s 少了 labels.json 清單裡的 %d 件（沒有用「%s」寫出來）：%s'
                       % (label, len(missing), PRACTICE_PREFIX, '、'.join(missing))); nb += 1
        prin_pfx = B.compact(PRINCIPLE_PREFIX)
        for s in secs:
            k = B.compact(B.html_text(dom.outer(s))).count(prin_pfx)
            nprin += k
            if k > int(lb.get('principle_max_per_chapter', 1)):
                R.fail('labels', '%s #%s 有 %d 個「%s」（每章最多 %s 個）'
                       % (label, s.attrs.get('id'), k, PRINCIPLE_PREFIX, lb.get('principle_max_per_chapter', 1))); nb += 1
        if not nb:
            R.ok('labels', '%s：「%s」%d 句都是清單裡的標準開頭%s；「%s」%d 個，每章不超過 %s 個'
                 % (label, PRACTICE_PREFIX, npr, '（清單上的一件不少）' if need_all else '',
                    PRINCIPLE_PREFIX, nprin, lb.get('principle_max_per_chapter', 1)))

    # 7. 頁數與目錄頁碼
    edir = B.rp(P['export_dir'])
    lite_pdf_pages = None
    lite_pdf = pdf_info['lite_pdf'] if pdf_info else os.path.join(edir, P['lite_export_name'].format(version=m['version']) + '.pdf')
    full_pdf = pdf_info['full_pdf'] if pdf_info else os.path.join(edir, P['full_export_name'].format(version=m['version']) + '.pdf')
    if not os.path.exists(lite_pdf):
        R.fail('pages', '找不到實作版 PDF：%s（build_lite.py 不加 --no-pdf 才會產生）' % lite_pdf)
    else:
        if pdf_info is None and os.path.getmtime(lite_pdf) < os.path.getmtime(B.rp(P['lite_html'])):
            R.warn('pages', '實作版 PDF 比 HTML 舊，頁數可能不是最新的')
        pi = pdf_chapter_pages(lite_pdf, m)
        lite_pdf_pages = pi['page_count']
        limit = int(m.get('page_limit', 25))
        print('     實作版每章頁數（PDF 共 %d 頁）：' % pi['page_count'])
        print('     %-10s %-6s %-9s %-5s %-6s %-11s %s' % ('id', '起頁', '範圍', '頁數', '目標', '字數/上限', '章名'))
        chars = {}
        for c in m['chapters']:
            node = ldom.by_id.get(c['id'])
            if node is not None:
                chars[c['id']] = len(B.compact(B.html_text(re.sub(r'<div class="lite-verify">.*?</div>', '', ldom.outer(node), flags=re.S))))
        rows = pi['rows']
        # 工作表可以在最後一塊的最後放一張刻意留白頁（湊滿第三張紙的背面）：那一塊量到的是兩頁，第二頁是留白頁
        blank_tail = bool(rows) and any(b.get('blank_page') for b in rows[-1][0].get('blocks', []))
        for i, (ch, s, e, n, top) in enumerate(rows):
            if s is None:
                R.fail('pages', '%s：PDF 書籤裡找不到章名「%s」' % (ch['id'], B.chapter_heading(ch))); continue
            lim = ch.get('char_limit'); cc = chars.get(ch['id'])
            print('     %-10s %-6s %-9s %-5s %-6s %-11s %s' % (ch['id'], s, '%d–%d' % (s, e), n, ch.get('pages_target', '-'),
                  '%s/%s' % (cc if cc is not None else '-', lim if lim else '-'), B.chapter_heading(ch)))
            if lim and cc and cc > lim:
                R.warn('chars', '%s 字數 %d 超過上限 %d' % (ch['id'], cc, lim))
            if ch.get('one_page'):
                nxt_top = (i + 1 >= len(rows)) or rows[i + 1][4] or rows[i + 1][1] != e
                want_n = 2 if (blank_tail and i == len(rows) - 1) else 1
                if n != want_n or not top or not nxt_top:
                    R.fail('pages', '%s「%s」要剛好%s，實際 %s–%s（開頭在頁首：%s；下一章另起一頁：%s）'
                           % (ch['id'], ch['title'], '一頁＋一張留白頁' if want_n == 2 else '一頁', s, e, top, nxt_top))
                else:
                    R.ok('pages', '%s「%s」剛好一頁（第 %d 頁）%s' % (ch['id'], ch['title'], s,
                         '，後面一張刻意留白頁' if want_n == 2 else ''))
        # 每一張紙的正反面：雙面印時第 1–2、3–4、5–6 頁各是同一張紙（主線決定①；v7 從只管前兩頁擴到管每一張紙）
        if ws:
            faces = [(ch['id'], s) for ch, s, e, n, top in rows]
            if blank_tail and rows[-1][1] is not None:
                faces.append(('（留白頁）', rows[-1][1] + 1))
            sbad = 0
            if len(faces) % 2 == 1:
                R.fail('pages', '工作表有 %d 面，最後一面沒有背面；要嘛補一塊，要嘛在最後一塊末尾加 blank_page' % len(faces))
                sbad += 1
            sheets = [(faces[i], faces[i + 1]) for i in range(0, len(faces) - 1, 2)]
            for (fid, fs), (bid, bs) in sheets:
                if fs is None or bs is None:
                    R.fail('pages', '%s／%s：PDF 書籤裡找不到起頁，量不出正反面' % (fid, bid)); sbad += 1
                elif fs % 2 != 1 or bs != fs + 1:
                    R.fail('pages', '%s 要在奇數頁（正面）、%s 緊接在下一頁（背面）；現在是第 %s 頁、第 %s 頁'
                           % (fid, bid, fs, bs)); sbad += 1
            if not sbad:
                R.ok('pages', '%d 張紙雙面印，每一張正反面成對：%s' % (len(sheets), '；'.join(
                    '第 %d 張＝第 %s、%s 頁（%s／%s）' % (i + 1, f[1], b[1], f[0], b[0])
                    for i, (f, b) in enumerate(sheets))))
            # v7 最終修正批（B9）：把 v6 那條指名的檢查補回來——計畫表那一頁的背面必須是查表頁。
            # 上面的成對檢查只管「奇數頁＋下一頁」，不擋把 plan 和 lookup 拆到不同張紙上。
            st = dict((ch['id'], s) for ch, s, e, n, top in rows)
            if st.get('plan') and st.get('lookup'):
                if st['plan'] % 2 == 1 and st['lookup'] == st['plan'] + 1:
                    R.ok('pages', '計畫表第 %d 頁、查表頁第 %d 頁：計畫表那一頁的背面就是查表頁'
                         % (st['plan'], st['lookup']))
                else:
                    R.fail('pages', '計畫表那一頁的背面必須是查表頁：計畫表要在奇數頁、查表頁緊接在下一頁'
                                    '（現在計畫表第 %s 頁、查表頁第 %s 頁）' % (st['plan'], st['lookup']))
            else:
                # v7 第二輪修正批（N9）：st[id] 在「manifest 沒有這一塊」和「PDF 書籤量不到起頁」
                # 兩種情況都會落到這裡，訊息要分得出是哪一種。
                gone = [k for k in ('plan', 'lookup') if k not in st]
                nopage = [k for k in ('plan', 'lookup') if k in st and not st[k]]
                if gone:
                    R.fail('pages', '工作表的 manifest 裡沒有 %s 這一塊，量不出「計畫表背面是查表頁」'
                           % '／'.join(gone))
                else:
                    R.fail('pages', 'PDF 書籤裡量不到 %s 的起頁（書籤標題和章名對不上？），'
                                    '量不出「計畫表背面是查表頁」' % '／'.join(nopage))
        else:
            # 十二章的實作版（工作表模式以外）照舊只管計畫表那一張紙：計畫表在奇數頁、查表頁緊接在下一頁
            st = dict((ch['id'], s) for ch, s, e, n, top in rows)
            if st.get('plan') and st.get('lookup'):
                if st['plan'] % 2 == 1 and st['lookup'] == st['plan'] + 1:
                    R.ok('pages', '計畫表第 %d 頁、查表頁第 %d 頁：整本雙面印剛好是同一張紙的正反面' % (st['plan'], st['lookup']))
                else:
                    R.fail('pages', '計畫表要在奇數頁、查表頁緊接在下一頁（現在計畫表第 %s 頁、查表頁第 %s 頁）' % (st['plan'], st['lookup']))
        if pi['page_count'] > limit:
            R.fail('pages', '實作版 PDF %d 頁，超過上限 %d 頁' % (pi['page_count'], limit))
        else:
            R.ok('pages', '實作版 PDF %d 頁（上限 %d）' % (pi['page_count'], limit))
        targets = dict((c['id'], B.chapter_heading(c)) for c in m['chapters'] if c.get('kind') != 'cover')
        entries = toc_printed_numbers(lite_pdf, targets) if not ws else []
        bad = [(nd, dest, pr, pi['outline_starts'].get(nd)) for nd, dest, pr in entries if not (dest == pr == pi['outline_starts'].get(nd))]
        seen = set(nd for nd, _, _ in entries)
        if ws:
            R.skip('toc', '工作表模式：工作表沒有目錄（四頁各是一張表，翻頁就看得到），這一支只檢查完整版目錄')
        elif bad or (set(targets) - seen and any(b.get('toc') for c in m['chapters'] for b in c.get('blocks', []))):
            for nd, dest, pr, ol in bad:
                R.fail('toc', '實作版目錄 %s：印的是 %s，連結目標第 %s 頁，書籤第 %s 頁' % (nd, pr, dest, ol))
            for nd in sorted(set(targets) - seen):
                R.fail('toc', '實作版目錄沒有 %s 的連結' % nd)
        else:
            R.ok('toc', '實作版目錄 %d 條：印出的頁碼＝連結目標頁＝書籤頁（%s）' % (len(entries), '、'.join('%s→%s' % (nd, pr) for nd, _, pr in entries)))
    if not os.path.exists(full_pdf):
        R.fail('pages', '找不到完整版 PDF：%s' % full_pdf)
    else:
        import fitz
        d = fitz.open(full_pdf); fcount = d.page_count; fmeta = d.metadata; fout = len(d.get_toc()); d.close()
        sec_ids = set(names.keys())
        first = None
        lp, _ = B.link_pages(full_pdf)
        first = min([lp[s] for s in sec_ids if s in lp] or [None]) if lp else None
        entries = toc_printed_numbers(full_pdf, names, max_page=first)
        toc_ids = set(re.findall(r'<a href="#([\w-]+)">', (re.search(r'<nav class="toc".*?</nav>', full, flags=re.S) or re.search('', '')).group(0)))
        for nd in sorted(toc_ids - set(e[0] for e in entries)):
            R.fail('toc', '完整版 PDF 目錄讀不到 %s 的頁碼' % nd)
        bad = [(nd, dest, pr) for nd, dest, pr in entries if dest != pr]
        if bad or not entries:
            for nd, dest, pr in bad:
                R.fail('toc', '完整版目錄 %s：印的是 %s，連結目標第 %s 頁' % (nd, pr, dest))
            if not entries: R.fail('toc', '完整版 PDF 目錄頁讀不到任何目錄連結')
        else:
            R.ok('toc', '完整版 PDF %d 頁、書籤 %d 條；目錄 %d 條印出的頁碼＝連結目標頁' % (fcount, fout, len(entries)))
        R.info('完整版 PDF metadata：title=%r author=%r' % (fmeta.get('title'), fmeta.get('author')))
        # 批 CT：完整版 PDF 大小（插畫印完後由 build_lite.shrink_pdf_images 重壓）；超過 12MB 判 FAIL
        fb = (pdf_info or {}).get('full_bytes')
        fsz = os.path.getsize(full_pdf)
        fmsg = '完整版 %.1f MB%s' % (fsz / 1048576.0,
                                    '（插畫重壓 %d → %d bytes）' % fb if fb else '（這次沒有重印，讀 export 現有的檔）')
        if fsz > 12 * 1048576:
            R.fail('pdf', fmsg + '，超過 12MB 上限')
        else:
            R.ok('pdf', fmsg)
        # 近乎空白的頁（主線決定④）：列出來，超過 3 頁 WARN
        pc = B.page_chars(full_pdf)
        low = [(i + 1, c) for i, c in enumerate(pc) if c < B.NEAR_EMPTY_CHARS]
        msg = '完整版 PDF 文字少於 %d 字的頁 %d 頁：%s' % (B.NEAR_EMPTY_CHARS, len(low), '、'.join('第 %d 頁（%d 字）' % x for x in low) or '無')
        if len(low) > 3:
            R.warn('blank_pages', msg)
        else:
            R.ok('blank_pages', msg)
        # fix-r3：字數被來源卡網址墊高、實際下半頁空白的頁，另外列出給人看（只列，不 WARN）
        half = [(i + 1, pct) for i, pct in enumerate(page_last_text_pct(full_pdf)) if pct < 50]
        R.info('完整版 PDF 最後一行文字在頁面上半（< 50%%）的頁 %d 頁：%s' % (
            len(half), '、'.join('第 %d 頁（%d%%）' % x for x in half) or '無'))
    if os.path.exists(lite_pdf):
        import fitz
        d = fitz.open(lite_pdf); lm = d.metadata; lo = len(d.get_toc()); d.close()
        R.info('實作版 PDF metadata：title=%r author=%r；書籤 %d 條' % (lm.get('title'), lm.get('author'), lo))
        if lm.get('author') != m['author'] or lo == 0:
            R.fail('pdf', '實作版 PDF metadata 或書籤不對')

    # 8. 版本號
    stamp = '%s／%s' % (m['version'], m['date'])
    lc = B.select(ldom, 'header.lite-cover'); fc = B.select(fdom, 'header.cover')
    vbad = False
    if not lc or stamp not in ldom.text(lc[0]):
        R.fail('version', '實作版封面沒有「%s」' % stamp); vbad = True
    if not fc or stamp not in fdom.text(fc[0]):
        R.fail('version', '完整版封面沒有「%s」' % stamp); vbad = True
    if not vbad:
        R.ok('version', '兩份封面都是「%s」' % stamp)

    # 9. manifest 的節 id
    mbad = 0
    for ch in m['chapters']:
        for b in ch.get('blocks', []):
            for sid in b.get('verify', []) or []:
                if sid not in names:
                    R.fail('ids', '%s：verify 的節 id %r 在完整版不存在' % (ch['id'], sid)); mbad += 1
    for cid, s in manifest_srcs(m):
        for i in re.findall(r'#([\w-]+)', s):
            if i not in sdom.by_id:
                R.fail('ids', '%s：src %r 裡的 #%s 在完整版不存在' % (cid, s, i)); mbad += 1
    if not mbad:
        R.ok('ids', 'manifest 用到的節 id 在完整版都存在')

    # 10. 標了 data-lite 卻沒被 manifest 用到
    used_vals = set(s for _, s in manifest_srcs(m) if B.is_mark_value(s))
    marks = set(t for n in sdom.nodes for t in n.tokens('data-lite') if t != 'skip')
    unused = sorted(marks - used_vals)
    if ws:
        # 工作表只抽四塊，完整版那些 data-lite="chN" 是給十二章版留著的；留著不等於錯，所以不判通過也不判失敗
        R.skip('unused_marks', '工作表模式：完整版還留著 %d 種 data-lite 值（%s），工作表沒有章、不以值抽用；'
                               '標記留著是為了將來回復實作版（短稿在 %s/retired，%d 份）'
               % (len(marks), '、'.join(sorted(marks)), P['alt_dir'], len(retired_ids)))
    elif unused:
        R.fail('unused_marks', '完整版標了 data-lite 但 manifest 沒用這些值：%s' % '、'.join(unused))
    else:
        R.ok('unused_marks', '完整版的 data-lite 值（%d 種）manifest 都有用到' % len(marks))

    # 11. 附 B 想查證總表＝各章想查證的聯集（由 manifest 產生，不准手寫）
    tables = [n for n in ldom.nodes if n.tag == 'table' and n.attrs.get('data-lite-verify-table')]
    appb_glue = [c for c in m['chapters'] for b in c.get('blocks', []) if 'glue' in b and '〈' in B.html_text(b['glue'])]
    want = [(lab, [names.get(s, s) for s in sids]) for _, lab, sids in B.verify_rows(m)]
    if appb_glue:
        R.fail('appendix_b', 'manifest 的接合文字裡有手寫的節名（〈…〉），節名要由 verify／verify_table 產生：%s' % '、'.join(c['id'] for c in appb_glue))
    if ws and not any(b.get('verify_table') for c in m['chapters'] for b in c.get('blocks', [])):
        R.skip('appendix_b', '工作表模式：沒有章、沒有附 B 想查證總表（工作表 %d 張想查證框、%d 張總表），'
                             '只保留「接合文字不得手寫節名」那一條' % (len(
            [1 for c in m['chapters'] for b in c.get('blocks', []) if b.get('verify')]), len(tables)))
    elif len(tables) != 1:
        R.fail('appendix_b', '實作版要剛好一張由 verify_table 產生的想查證總表，現在 %d 張' % len(tables))
    else:
        t = tables[0]
        rows = []
        for tr in [x for x in ldom.nodes if x.tag == 'tr' and t.start < x.start < t.end]:
            tds = [x for x in tr.children if x.tag == 'td']
            if len(tds) == 2:
                rows.append((ldom.text(tds[0]), re.findall(r'〈([^〉]+)〉', ldom.text(tds[1]))))
        if rows != want:
            R.fail('appendix_b', '附 B 想查證總表和各章想查證框對不上（表 %d 列、各章 %d 列）' % (len(rows), len(want)))
        else:
            boxes_ok = True
            for c in m['chapters']:
                node = ldom.by_id.get(c['id'])
                vs = [s for b in c.get('blocks', []) for s in (b.get('verify') or [])]
                if node is None or not vs: continue
                box = [x for x in ldom.nodes if x.tag == 'div' and 'lite-verify' in x.classes() and node.start < x.start < node.end]
                got = re.findall(r'〈([^〉]+)〉', ldom.text(box[0]).split('[1]')[0]) if box else []
                if got != [names[s] for s in vs]:
                    R.fail('appendix_b', '%s 的想查證框和 manifest verify 不一致' % c['id']); boxes_ok = False
            if boxes_ok:
                R.ok('appendix_b', '附 B %d 列＝各章想查證框（含前三頁的 verify_index）' % len(rows))

    # 12. 內文提到「第X章」（國字或阿拉伯數字）：章要存在
    CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

    def cn_num(s):
        if s.isdigit(): return int(s)
        if s == '十': return 10
        if s.startswith('十'): return 10 + CN[s[1]]
        if s.endswith('十'): return CN[s[0]] * 10
        if '十' in s: return CN[s[0]] * 10 + CN[s[2]]
        return CN[s]
    ch_text = {}
    for c in m['chapters']:
        mm = re.match(r'第\s*(\d+)\s*章', c.get('label') or '')
        node = ldom.by_id.get(c['id'])
        if mm and node is not None:
            ch_text[int(mm.group(1))] = B.compact(B.html_text(re.sub(r'<div class="lite-verify">.*?</div>', '', ldom.outer(node), flags=re.S)))
    # 註：「那一章真的講到這件事」試過用共用字串判斷，分不出對錯（第一章六個錯裡指錯的第三章也有三字共用），
    # 所以這裡只擋章號不存在，並把每一處引用列出來給人對。
    ref_bad = 0; refs = []
    skip_nodes = [x for x in ldom.nodes if (x.tag == 'ol' and 'lite-toc' in x.classes()) or x.attrs.get('data-lite-verify-table')]
    for c in m['chapters']:
        node = ldom.by_id.get(c['id'])
        if node is None: continue
        for el in [x for x in ldom.nodes if x.tag in ('li', 'p', 'td') and node.start <= x.start < node.end and not any(y.tag in ('li', 'p', 'td') for y in x.children)]:
            if any(s.start <= el.start < s.end for s in skip_nodes): continue
            txt = ldom.text(el)
            for mm in re.finditer(r'第\s*((?:[一二三四五六七八九十]+|\d+)(?:\s*、\s*(?:[一二三四五六七八九十]+|\d+))*)\s*章', txt):
                for x in mm.group(1).split('、'):
                    k = cn_num(x.strip())
                    refs.append('%s→%d' % (c['id'], k))
                    if k not in ch_text and not ws:
                        R.fail('chapter_refs', '%s 提到第 %d 章，實作版沒有這一章：%s' % (c['id'], k, txt[:50])); ref_bad += 1
    if ws:
        # 工作表沒有章，所以「指到的章存在嗎」沒有東西可查；「不准出現章號」由 worksheet 那一支管（比這裡嚴）
        R.skip('chapter_refs', '工作表模式：沒有章可以指（掃到 %d 處章號，工作表一處都不該有，由 worksheet 哨兵判）' % len(refs))
    elif not ref_bad:
        R.ok('chapter_refs', '內文提到章號 %d 處，章都存在（內容對不對要人看：%s）' % (len(refs), '、'.join(refs)))

    # 13. 黃框原文：完整版的黃框純文字＝正式檔（story_reference）逐字相同；實作版的黃框＝完整版黃框經過連結改寫後的樣子
    refp = P.get('story_reference', 'guide/index.html')
    fstories = [n for n in sdom.nodes if n.tag == 'div' and 'story' in n.classes()]
    if not os.path.exists(B.rp(refp)):
        R.fail('stories', '找不到黃框比對用的正式檔：%s' % refp)
    else:
        gdom = B.Dom(B.read(refp))
        gst = [gdom.text(n) for n in gdom.nodes if n.tag == 'div' and 'story' in n.classes()]
        fst = [sdom.text(n) for n in fstories]
        sbad = 0
        if len(gst) != len(fst):
            R.fail('stories', '黃框數量：正式檔 %d 個、完整版候選 %d 個' % (len(gst), len(fst))); sbad += 1
        for i, (a, b) in enumerate(zip(gst, fst)):
            if a != b:
                sec = sdom.section_of(fstories[i])
                R.fail('stories', '完整版第 %d 個黃框（#%s）和正式檔不一樣：%s…' % (i + 1, sec.attrs.get('id') if sec is not None else '-', b[:30])); sbad += 1
        ctx = B.ChapterCtx('story-check', names, B.section_of_ids(sdom))
        allowed = set(B.html_text(B.transform(sdom.outer(n), ctx)) for n in fstories)
        lst = [n for n in ldom.nodes if n.tag == 'div' and 'story' in n.classes()]
        for n in lst:
            if ldom.text(n) not in allowed:
                R.fail('stories', '實作版有黃框和完整版任何一個黃框都對不上（只准連結改寫）：%s…' % ldom.text(n)[:30]); sbad += 1
        if not sbad:
            R.ok('stories', '完整版 %d 個黃框和 %s 逐字相同；實作版 %d 個黃框都等於完整版原文（只有連結改寫）' % (len(fst), refp, len(lst)))

    # 14. 虛構人物聲明：每位人物的標題前面緊接著一個虛構聲明
    PEOPLE = ('小安', '阿凱', '小芸與阿哲', '陳大哥')
    fic = [n for n in ldom.nodes if n.tag == 'p' and 'lite-fiction' in n.classes()]
    heads = [n for n in ldom.nodes if n.tag in ('h3', 'h4') and any(ldom.text(n).startswith(p) or ('範例：%s' % p) in ldom.text(n) for p in PEOPLE)]
    fbad = 0
    for h in heads:
        prev = [f for f in fic if f.end <= h.start]
        between = ldom.s[prev[-1].end:h.start] if prev else None
        if not prev or B.html_text(between) or re.search(r'<h[1-5]\b', between):
            R.fail('fiction', '人物標題「%s」前面沒有緊接著虛構聲明' % ldom.text(h)[:20]); fbad += 1
        elif ldom.text(prev[-1]) != B.FICTION_NOTICE:
            R.fail('fiction', '人物標題「%s」前的虛構聲明文字不對' % ldom.text(h)[:20]); fbad += 1
    if ws and not heads:
        # 工作表沒有人物頁（四個人退場到完整版），所以沒有要聲明的東西；有人物標題時照樣要有聲明（上面那段仍在跑）
        R.skip('fiction', '工作表模式：工作表裡沒有人物頁（%s），沒有虛構聲明要檢查；'
                          '四個人仍在完整版第十五節與案例節裡' % '、'.join(PEOPLE))
    elif len(heads) < len(PEOPLE):
        R.fail('fiction', '實作版只找到 %d 位人物的標題（應有 %d 位）' % (len(heads), len(PEOPLE))); fbad += 1
    if not fbad and heads:
        R.ok('fiction', '%d 個人物標題前面都緊接著虛構聲明' % len(heads))

    # 14b. 工作表（spec-v61-worksheet.md「v7：三張紙」）：
    #      每一塊剛好一頁、每一塊都印得出來、每一塊都有完整版來源、頁數 5 或 6（6 頁時末頁可以是留白頁）、
    #      塊數對得上頁數、沒有章與附錄。奇偶頁成對（正反面）那一條在 pages 那一支。
    if not ws:
        R.skip('worksheet', '不是工作表模式（manifest 還有章號或目錄），這一支不適用')
    else:
        wbad = 0
        chs = m['chapters']
        blanks = sum(1 for c in chs for b in c.get('blocks', []) if b.get('blank_page'))
        want_pages = len(chs) + blanks
        if not (WORKSHEET_PAGES_MIN <= want_pages <= WORKSHEET_PAGES_MAX):
            R.fail('worksheet', '工作表要 %d 到 %d 頁（一塊一頁，末頁可以是留白頁），manifest 有 %d 塊＋%d 張留白：%s'
                   % (WORKSHEET_PAGES_MIN, WORKSHEET_PAGES_MAX, len(chs), blanks,
                      '、'.join(c['id'] for c in chs))); wbad += 1
        if blanks:
            last_blocks = chs[-1].get('blocks', [])
            if blanks > 1 or not (last_blocks and last_blocks[-1].get('blank_page')):
                R.fail('worksheet', '留白頁只准有一張，而且只能放在最後一塊的最後（現在 %d 張）' % blanks); wbad += 1
        srcs = []
        for c in chs:
            if not (c.get('one_page') or c.get('kind') == 'cover'):
                R.fail('worksheet', '%s 沒有 one_page：工作表每一塊都要剛好一頁' % c['id']); wbad += 1
            if ldom.by_id.get(c['id']) is None:
                R.fail('worksheet', '工作表輸出裡找不到 %s 這一塊' % c['id']); wbad += 1
            got = [('src', b['src']) if 'src' in b else ('alt', b['alt'])
                   for b in c.get('blocks', []) if 'src' in b or 'alt' in b]
            if not got:
                R.fail('worksheet', '%s 只有接合文字，沒有任何 src／alt 來源（工作表不得自己寫內容）' % c['id']); wbad += 1
            srcs.append('%s＝%s' % (c['id'], '＋'.join('%s:%s' % g for g in got)))
        if lite_pdf_pages is None:
            R.fail('worksheet', '沒有工作表 PDF，量不到頁數'); wbad += 1
        elif not (WORKSHEET_PAGES_MIN <= lite_pdf_pages <= WORKSHEET_PAGES_MAX):
            R.fail('worksheet', '工作表 PDF %d 頁，要 %d 到 %d 頁'
                   % (lite_pdf_pages, WORKSHEET_PAGES_MIN, WORKSHEET_PAGES_MAX)); wbad += 1
        elif lite_pdf_pages != want_pages:
            R.fail('worksheet', '工作表 PDF %d 頁，但 manifest 是 %d 塊＋%d 張留白＝%d 頁（一塊一頁）'
                   % (lite_pdf_pages, len(chs), blanks, want_pages)); wbad += 1
        ltext = B.html_text(lite)
        chap = re.findall(r'第\s*(?:[一二三四五六七八九十]+|\d+)\s*章', ltext)
        appx = re.findall(r'附錄\s*[0-9A-Za-z一二三四五六七八九十]|附\s*[A-Z](?![a-z])', ltext)
        if chap:
            R.fail('worksheet', '工作表出現章號（十二章已退場）：%s' % '、'.join(sorted(set(chap)))); wbad += 1
        if appx:
            R.fail('worksheet', '工作表出現附錄（附 A／附 B 已退場）：%s' % '、'.join(sorted(set(appx)))); wbad += 1
        if not wbad:
            R.ok('worksheet', '工作表 %d 塊各一頁（＋%d 張留白）、PDF %d 頁＝%d 張紙、沒有章號與附錄；每一塊的來源：%s'
                 % (len(chs), blanks, lite_pdf_pages, (lite_pdf_pages + 1) // 2, '　'.join(srcs)))

    # 15. 完整版 s13 篩選：只在網頁顯示、靜態 HTML 不預先隱藏
    scripts = ''.join(fdom.s[n.open_end:n.inner_end] for n in fdom.nodes if n.tag == 'script')
    s13bad = []
    if 'data-s13-filter' not in scripts:
        s13bad.append('script 裡找不到 data-s13-filter')
    if not re.search(r"@mediaprint\{\[data-s13-filter\]\{display:none", re.sub(r'\s+', '', scripts)):
        s13bad.append('script 裡沒有 @media print 隱藏篩選列')
    if re.search(r'<[a-z][^>]*\sdata-s13-hidden\b', re.sub(r'<script\b.*?</script>', '', full, flags=re.S)):
        s13bad.append('靜態 HTML 裡有 data-s13-hidden（沒有 JS 時會被藏起來）')
    if s13bad:
        for x in s13bad: R.fail('s13_filter', '完整版發布版：' + x)
    else:
        R.ok('s13_filter', '完整版 s13 篩選列印時隱藏，靜態 HTML 沒有預先隱藏的題目')

    # 15b. 結構重排保險（migration-plan §10.2）：原文目錄順序＝正文順序；「第 N 節」錨文字＝該節顯示節號。
    #      完整版專用，只讀 guide/index.html，工作表模式照樣跑。
    obad, oinfo = check_toc_order(sdom)
    if obad:
        for x in obad: R.fail('order', x)
    else:
        R.ok('order', oinfo)
    xbad, xinfo = check_xref_numbers(sdom)
    if xbad:
        for x in xbad: R.fail('xref_num', x)
    else:
        R.ok('xref_num', xinfo)
    pm, pmsg = check_part_maps(sdom)
    if pm is None:
        R.skip('part_maps', pmsg)
    elif pm:
        for x in pm: R.fail('part_maps', x)
    else:
        R.ok('part_maps', pmsg)

    # 16. 單獨跑時：先在記憶體重建一次，和檔案比，抓「原文改了、HTML 還沒重建」
    if build_report is None:
        try:
            lite_now, full_now, _ = B.build(m)
        except B.BuildError as e:
            R.fail('stale', '記憶體重建失敗：%s' % str(e).splitlines()[0])
        else:
            if lite_now != lite:
                R.fail('stale', '%s 和現在的原文、manifest、短稿重建出來的不一樣：先跑 build_lite.py' % P['lite_html'])
            if full_now != full:
                R.fail('stale', '%s 和重建結果不一樣：先跑 build_lite.py' % P['full_html'])
            if lite_now == lite and full_now == full:
                R.ok('stale', '兩份 HTML 和現在的原文重建結果相同')

    # 17. 發布用片段：和兩份輸出去掉外殼後的內容逐字相同
    fragbad = 0; fragdone = []
    for label, srck, dstk in (('完整版', 'full_html', 'full_fragment'), ('實作版', 'lite_html', 'lite_fragment')):
        dst = P.get(dstk)
        if not dst:
            R.fail('fragments', '%s：manifest paths 沒有 %s' % (label, dstk)); fragbad += 1; continue
        try:
            want = B.fragment_of(B.read(P[srck]), 'full' if srck == 'full_html' else 'lite', P[srck], B.lite_cover_title(m))
        except B.BuildError as e:
            R.fail('fragments', '%s 產不出發布用片段：%s' % (label, e)); fragbad += 1; continue
        if not os.path.exists(B.rp(dst)):
            R.fail('fragments', '找不到 %s：重跑 build_lite.py（或交班文件「改完後的固定流程」第 4 步）' % dst); fragbad += 1; continue
        if B.read(dst) != want:
            R.fail('fragments', '%s 不等於 %s 去掉外殼後的內容：重跑 build_lite.py（或交班文件「改完後的固定流程」第 4 步）再發布' % (dst, P[srck])); fragbad += 1; continue
        fragdone.append(dst)
    if not fragbad:
        R.ok('fragments', '發布用片段和兩份輸出一致：%s' % '、'.join(fragdone))

    # 18. guidetools check
    gt = os.path.join(B.ROOT, 'tools', 'guidetools.py')
    for label, p in (('實作版', P['lite_html']), ('完整版發布版', P['full_html'])):
        r = subprocess.run([sys.executable, gt, 'check', B.rp(p)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = r.stdout.decode('utf-8', 'replace').strip().replace('\n', ' | ')
        if r.returncode != 0:
            R.fail('check', '%s guidetools check 失敗：%s' % (label, out))
        else:
            R.ok('check', '%s：%s' % (label, out))

    if R.fails:
        print('SENTINELS FAILED (%d)' % R.fails); return 1
    print('SENTINELS OK'); return 0


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default='lite/manifest.json')
    a = ap.parse_args(argv)
    return run(B.load_manifest(a.manifest))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
