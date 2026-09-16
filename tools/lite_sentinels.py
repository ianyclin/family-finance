# -*- coding: utf-8 -*-
"""新手實作版哨兵。build_lite.py 每次結束都會呼叫；也可以單獨跑（讀已經產生的 HTML／PDF）。

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


class Report(object):
    def __init__(self, skip):
        self.lines = []; self.fails = 0; self.skip = set(skip)

    def ok(self, cat, msg): self.lines.append('OK   [%s] %s' % (cat, msg)); print(self.lines[-1])

    def fail(self, cat, msg):
        if cat in self.skip:
            self.lines.append('SKIP [%s] （manifest sentinel_skip）%s' % (cat, msg))
        else:
            self.fails += 1; self.lines.append('FAIL [%s] %s' % (cat, msg))
        print(self.lines[-1])

    def warn(self, cat, msg): self.lines.append('WARN [%s] %s' % (cat, msg)); print(self.lines[-1])

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

def run(m, pdf_info=None, build_report=None):
    P = m['_paths']
    skip = m.get('sentinel_skip') or []
    R = Report(skip if not m['_is_main'] else [])
    print('== 哨兵：%s ==' % m['_path'])
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
    for n in sdom.nodes:
        for a in n.tokens('data-lite-alt'):
            if a not in alt_ids:
                R.fail('unused_marks', '原文標了 data-lite-alt="%s"，但 %s 沒有這份短稿' % (a, P['alt_dir']))
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
        facts = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        lt = B.compact(B.html_text(lite)); ft = B.compact(B.html_text(full)); miss = 0
        for f in facts:
            for label, t in (('實作版', lt), ('完整版', ft)):
                if B.compact(f) not in t:
                    R.fail('facts', '%s 找不到共同事實：%s' % (label, f)); miss += 1
        if not miss:
            R.ok('facts', '%d 條共同事實兩份都找得到' % len(facts))

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

    # 6. 標籤
    lb = json.load(open(B.rp(P['labels']), encoding='utf-8'))
    for label, dom, sec_sel in (('實作版', ldom, 'section.lite-ch'), ('完整版', fdom, 'section.part')):
        ignore = []
        for sel in lb.get('ignore', []): ignore += B.select(dom, sel)
        secs = B.select(dom, sec_sel)
        nb = 0; npr = 0; nprin = 0; per_item = {}
        max_item = lb.get('practice_max_per_item')
        for n in dom.nodes:
            if n.tag != 'span': continue
            cl = n.classes()
            if 'label-practice' not in cl and 'label-principle' not in cl: continue
            if any(x.start <= n.start and n.end <= x.end for x in ignore): continue
            if 'label-practice' in cl:
                npr += 1
                parent = n.parent
                after = B.html_text(dom.s[n.end:parent.inner_end])
                sentence = re.split(r'[。！？]', after, 1)[0]
                cs = B.compact(sentence)
                # 句首比對：先去掉開頭的括號小註（例如「（不是唯一答案）」），句子要以 starts 其中一個開頭；
                # 沒寫 starts 的項目才退回關鍵詞子字串比對（review r2：子字串比對貼錯句子也會過）
                head = re.sub(r'^[（(][^）)]*[）)]', '', cs)
                hit = None
                for item in lb['practice']:
                    if item.get('starts'):
                        ok = any(head.startswith(B.compact(k)) for k in item['starts'])
                    else:
                        ok = any(B.compact(k) in cs for k in item['keywords'])
                    if ok:
                        hit = item['item']; break
                if hit is None:
                    R.fail('labels', '%s「本指南的做法」貼在清單以外的句子（要以七件事的標準句開頭）：%s' % (label, sentence[:60])); nb += 1
                else:
                    per_item[hit] = per_item.get(hit, 0) + 1
            else:
                nprin += 1
        if max_item:
            for it, k in sorted(per_item.items()):
                if k > int(max_item):
                    R.fail('labels', '%s「本指南的做法」貼在「%s」%d 次（每份最多 %s 次）' % (label, it, k, max_item)); nb += 1
        for s in secs:
            k = len([x for x in dom.nodes if x.tag == 'span' and 'label-principle' in x.classes() and s.start < x.start < s.end
                     and not any(y.start <= x.start and x.end <= y.end for y in ignore)])
            if k > int(lb.get('principle_max_per_chapter', 1)):
                R.fail('labels', '%s #%s 有 %d 個「原則」標籤（每章最多 %s 個）' % (label, s.attrs.get('id'), k, lb.get('principle_max_per_chapter', 1))); nb += 1
        if not nb:
            R.ok('labels', '%s：「本指南的做法」%d 個都在七件事上；「原則」%d 個，每章不超過 %s 個' % (label, npr, nprin, lb.get('principle_max_per_chapter', 1)))

    # 7. 頁數與目錄頁碼
    edir = B.rp(P['export_dir'])
    lite_pdf = pdf_info['lite_pdf'] if pdf_info else os.path.join(edir, P['lite_export_name'].format(version=m['version']) + '.pdf')
    full_pdf = pdf_info['full_pdf'] if pdf_info else os.path.join(edir, P['full_export_name'].format(version=m['version']) + '.pdf')
    if not os.path.exists(lite_pdf):
        R.fail('pages', '找不到實作版 PDF：%s（build_lite.py 不加 --no-pdf 才會產生）' % lite_pdf)
    else:
        if pdf_info is None and os.path.getmtime(lite_pdf) < os.path.getmtime(B.rp(P['lite_html'])):
            R.warn('pages', '實作版 PDF 比 HTML 舊，頁數可能不是最新的')
        pi = pdf_chapter_pages(lite_pdf, m)
        limit = int(m.get('page_limit', 25))
        print('     實作版每章頁數（PDF 共 %d 頁）：' % pi['page_count'])
        print('     %-10s %-6s %-9s %-5s %-6s %-11s %s' % ('id', '起頁', '範圍', '頁數', '目標', '字數/上限', '章名'))
        chars = {}
        for c in m['chapters']:
            node = ldom.by_id.get(c['id'])
            if node is not None:
                chars[c['id']] = len(B.compact(B.html_text(re.sub(r'<div class="lite-verify">.*?</div>', '', ldom.outer(node), flags=re.S))))
        rows = pi['rows']
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
                if n != 1 or not top or not nxt_top:
                    R.fail('pages', '%s「%s」要剛好一頁，實際 %s–%s（開頭在頁首：%s；下一章另起一頁：%s）' % (ch['id'], ch['title'], s, e, top, nxt_top))
                else:
                    R.ok('pages', '%s「%s」剛好一頁（第 %d 頁）' % (ch['id'], ch['title'], s))
        # 計畫表和查表頁要是同一張紙的正反面：整本雙面印時計畫表在奇數頁（正面），查表頁緊接在下一頁（主線決定①）
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
        entries = toc_printed_numbers(lite_pdf, targets)
        bad = [(nd, dest, pr, pi['outline_starts'].get(nd)) for nd, dest, pr in entries if not (dest == pr == pi['outline_starts'].get(nd))]
        seen = set(nd for nd, _, _ in entries)
        if bad or (set(targets) - seen and any(b.get('toc') for c in m['chapters'] for b in c.get('blocks', []))):
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
    if unused:
        R.fail('unused_marks', '完整版標了 data-lite 但 manifest 沒用這些值：%s' % '、'.join(unused))
    else:
        R.ok('unused_marks', '完整版的 data-lite 值（%d 種）manifest 都有用到' % len(marks))

    # 11. 附 B 想查證總表＝各章想查證的聯集（由 manifest 產生，不准手寫）
    tables = [n for n in ldom.nodes if n.tag == 'table' and n.attrs.get('data-lite-verify-table')]
    appb_glue = [c for c in m['chapters'] for b in c.get('blocks', []) if 'glue' in b and '〈' in B.html_text(b['glue'])]
    want = [(lab, [names.get(s, s) for s in sids]) for _, lab, sids in B.verify_rows(m)]
    if appb_glue:
        R.fail('appendix_b', 'manifest 的接合文字裡有手寫的節名（〈…〉），附 B 要用 {"verify_table": true} 產生：%s' % '、'.join(c['id'] for c in appb_glue))
    if len(tables) != 1:
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
                    if k not in ch_text:
                        R.fail('chapter_refs', '%s 提到第 %d 章，實作版沒有這一章：%s' % (c['id'], k, txt[:50])); ref_bad += 1
    if not ref_bad:
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
        if not prev or B.html_text(between) or re.search(r'<h[1-4]\b', between):
            R.fail('fiction', '人物標題「%s」前面沒有緊接著虛構聲明' % ldom.text(h)[:20]); fbad += 1
        elif ldom.text(prev[-1]) != B.FICTION_NOTICE:
            R.fail('fiction', '人物標題「%s」前的虛構聲明文字不對' % ldom.text(h)[:20]); fbad += 1
    if len(heads) < len(PEOPLE):
        R.fail('fiction', '實作版只找到 %d 位人物的標題（應有 %d 位）' % (len(heads), len(PEOPLE))); fbad += 1
    if not fbad:
        R.ok('fiction', '%d 個人物標題前面都緊接著虛構聲明' % len(heads))

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
            want = B.fragment_of(B.read(P[srck]), 'full' if srck == 'full_html' else 'lite', P[srck])
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
