# -*- coding: utf-8 -*-
"""v4.3.1 → v4.4：排版系統化（只動指南）。字級收成四階、圓角統一、卡片內清單間距、黃框一律在來源之後、
費用節裸標題裝卡片、來源卡標題統一、四條以上來源用格子、用錢節補來源卡。一次性腳本。"""
import re, sys
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read(); n=0
def rep(a,b,c=1):
    global h,n
    if h.count(a)!=c: print('MISMATCH',h.count(a),a[:70]); sys.exit(1)
    h=h.replace(a,b); n+=1

# ── A. CSS ──
css0=re.search(r'<style>(.*?)</style>',h,re.S).group(1); css=css0
def cssrep(sel,old,new):
    global css
    m=None
    for mm in re.finditer(re.escape(sel)+r'\{([^{}]*)\}',css):
        if old in mm.group(1): m=mm; break
    if not m: print('CSS MISMATCH',sel,old); sys.exit(1)
    body=m.group(1).replace(old,new,1); css=css[:m.start(1)]+body+css[m.end(1):]
for sel,old,new in [
 ('.plain-title','font-size:.82rem','font-size:.84rem'),
 ('.source-link','font-size:.88rem','font-size:.84rem'),
 ('.story::before','font-size:.86rem','font-size:.84rem'),
 ('.decision::before','font-size:.82rem','font-size:.84rem'),
 ('.bar-note','font-size:.82rem','font-size:.84rem'),
 ('.tag','font-size:.8rem','font-size:.84rem'),
 ('.table-wrap::before','font-size:.75rem','font-size:.78rem'),
 ('figure.chart .chart-sub','font-size:.8rem','font-size:.84rem'),
 ('figure.chart .note','font-size:.78rem','font-size:.84rem'),
 ('figure.chart details.orig summary','font-size:.85rem','font-size:.84rem'),
 ('.data-card h4','font-size:.95rem','font-size:.9rem'),
 ('.explain','border-radius:14px','border-radius:16px'),
 ('figure.chart','border-radius:14px','border-radius:16px'),
 ('figure.chart','padding:18px 18px 14px','padding:18px 20px 14px'),
 ('.table-wrap','border-radius:12px','border-radius:16px'),
]: cssrep(sel,old,new)
css=css.replace('.data-card h4{','.data-card>ul>li,.data-card>ol>li{margin:.8em 0}.data-card h4{',1)
h=h.replace(css0,css); n+=1

# ── helpers: top-level blocks of a section ──
OPEN=re.compile(r'<(div|p|ol|ul|h2|h3|h4|figure|details|dl|a|table)\b[^>]*>')
def blocks(s):
    out=[];pos=0
    while True:
        m=OPEN.search(s,pos)
        if not m: break
        tag=m.group(1)
        if tag=='div':
            depth=1;i=m.end()
            while depth:
                k=re.compile(r'<(/?)div\b').search(s,i); depth+= -1 if k.group(1) else 1; i=k.end()
            end=s.find('>',i)+1
        else:
            end=s.find('</%s>'%tag,m.end())+len('</%s>'%tag)
        cls=re.search(r'class="([^"]+)"',m.group(0)); out.append([m.start(),end,tag,cls.group(1) if cls else ''])
        pos=end
    return out
def section(sid):
    i=h.find('<section class="part" id="%s">'%sid); j=h.find('</section>',i); assert i>0
    return i,j
def reorder(sid, rule):
    """rule(blocks_list_of_html) -> new list"""
    global h,n
    i,j=section(sid); s=h[i:j]
    bl=blocks(s); parts=[s[a:b] for a,b,_,_ in bl]
    gaps=[s[bl[k][1]:bl[k+1][0]] for k in range(len(bl)-1)]
    kinds=[c for _,_,_,c in bl]
    new=rule(parts,kinds)
    body=s[:bl[0][0]]+('\n'.join(new))+s[bl[-1][1]:]
    h=h[:i]+body+h[j:]; n+=1
def move_story_after_source(parts,kinds):
    # all story blocks go right after the (last) source-card, keeping their relative order; decision stays last
    stories=[p for p,k in zip(parts,kinds) if k=='story']
    rest=[(p,k) for p,k in zip(parts,kinds) if k!='story']
    out=[];placed=False
    idx=max(i for i,(p,k) in enumerate(rest) if k=='source-card')
    for i,(p,k) in enumerate(rest):
        out.append(p)
        if i==idx: out+=stories
    return out
for sid in ['s2','s3','s4','s9','sidepaths']:
    reorder(sid, move_story_after_source)
# s3: story should be after 台灣自己的數字 card (last data-card), not right after source
def s3rule(parts,kinds):
    stories=[p for p,k in zip(parts,kinds) if k=='story']
    rest=[p for p,k in zip(parts,kinds) if k!='story']
    # insert before decision
    d=[i for i,p in enumerate(rest) if 'class="decision"' in p[:30]][0]
    return rest[:d]+stories+rest[d:]
reorder('s3', s3rule)

# ── E. costs 裸標題裝卡片 ──
rep('<h3>台灣投資人常遇到的四層稅務</h3><ul>','<div class="data-card"><h3>台灣投資人常遇到的四層稅務</h3><ul>')
rep('</ul>\n<div class="warning"><strong>稅率不能決定投資方向。','</ul></div>\n<div class="warning"><strong>稅率不能決定投資方向。')
rep('<h3>帳戶安全五件事</h3><ol class="checklist">','<div class="data-card"><h3>帳戶安全五件事</h3><ol class="checklist">')
rep('</ol>\n<div class="source-card"><h3>稅務與安全的官方來源</h3>','</ol></div>\n<div class="source-card"><h3>稅務與安全的官方來源</h3>')

# ── F. 來源卡標題統一 ──
for t in ['研究來源','來源','人力資本與物價的來源','下單與交割','稅務與安全的官方來源']:
    rep('<div class="source-card"><h3>%s</h3>'%t,'<div class="source-card"><h3>直接來源</h3>')

# ── H. withdraw 補來源卡 ──
i,j=section('withdraw'); s=h[i:j]
card=('<div class="source-card"><h3>直接來源</h3><a class="source-link" href="https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_principles_retirement_income.pdf" target="_blank" rel="noopener"><span>Vanguard (2026)：Principles for Retirement Income</span><span class="source-note">報酬順序風險的定義與影響，第 10 頁</span></a>'
'<a class="source-link" href="https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/whitepapers/safeguarding-retirement-bear-market.pdf" target="_blank" rel="noopener"><span>Vanguard Research (2020)：Safeguarding retirement in a bear market</span><span class="source-note">1973 與 1974 年退休的例子；細節在「<a class="xref" href="#lifecycle">槓桿、年齡與退休</a>」第三題</span></a></div>\n')
tgt='<p class="decision">'; assert s.count(tgt)==1
s=s.replace(tgt,card+tgt); h=h[:i]+s+h[j:]; n+=1

# ── G. 四條以上來源用格子 ──
def gridify(m):
    global n
    title,body=m.group(1),m.group(2)
    if 'sources-grid' in body or '<p' in body or body.count('class="source-link"')<4: return m.group(0)
    n+=1
    return '<div class="source-card"><h3>%s</h3><div class="sources-grid">%s</div></div>'%(title,body)
h=re.sub(r'<div class="source-card"><h3>([^<]+)</h3>((?:<a class="source-link".*?</a>)+)</div>',gridify,h,flags=re.S)

open(P,'w',encoding='utf-8').write(h); print('applied',n,'edits',len(h))
