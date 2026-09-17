# 列出完整版 PDF 目錄頁前（max_page=第一節所在頁）被 toc_printed_numbers 當成目錄項的連結，看封面連結有沒有被誤抓
import sys, re, glob
sys.path.insert(0, 'tools')
import build_lite as B
import lite_sentinels as L
full = open('guide/index.html', encoding='utf-8').read()
dom = B.Dom(full)
names = B.section_names(dom)
pdf = glob.glob('export/*完整指南*.pdf')[0]
lp, _ = B.link_pages(pdf)
first = min([lp[s] for s in names if s in lp])
print('first section page', first)
ents = L.toc_printed_numbers(pdf, names, max_page=first)
for e in ents: print(e)
import fitz
d = fitz.open(pdf)
for pno in range(0, 2):
    p = d[pno]
    print('--- page', pno+1)
    for l in p.get_links():
        nd = l.get('nameddest')
        words = p.get_text('words', clip=fitz.Rect(l['from']) + (-1, -1, 1, 1))
        txt = ''.join(w[4] for w in sorted(words, key=lambda w: (w[5], w[6], w[7])))
        print(' ', nd, repr(txt[:40]))
