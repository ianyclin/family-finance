import re, html, sys, hashlib
def load(p): return open(p,encoding='utf-8').read()
def div_blocks(h, cls):
    out=[]
    for m in re.finditer(r'<div\b[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>'%cls, h):
        i=m.start(); depth=0; pos=i
        for t in re.finditer(r'<(/?)div\b[^>]*>', h[i:]):
            depth += -1 if t.group(1) else 1
            if depth==0: out.append(h[i:i+t.end()]); break
    return out
B=load('wip/v61-2026-09-17/fix2/before.html'); A=load('guide/index.html')
sb,sa=div_blocks(B,'story'),div_blocks(A,'story')
print('story before/after',len(sb),len(sa),'identical ordered:',sb==sa)
mk=lambda h: re.findall(r'<mark class="key"[^>]*>.*?</mark>',h,flags=re.S)
print('mark.key',len(mk(B)),len(mk(A)),mk(B)==mk(A))
def labels(h):
    res=[]
    for m in re.finditer(r'<span class="(label-practice|label-principle)"[^>]*>(.*?)</span>',h):
        after=html.unescape(re.sub('<[^>]+>','',h[m.end():m.end()+400]))
        res.append((m.group(1),re.split('[。！？]',after,1)[0][:40]))
    return res
lb,la=labels(B),labels(A)
print('labels before',len(lb),'after',len(la),'same:',lb==la)
for x in la: print('  ',x)
# 5/25 facts line verbatim
fact='跑掉一點點不用管。常見的尺叫 5/25：差超過 5 個百分點，或超過原本比例的四分之一，兩個取比較小的那個，到了才動。'
print('5/25 fact in after text:', fact in html.unescape(re.sub('<[^>]+>','',A)))
# data-lite ch8 attr on 5/25 para
for h,n in ((B,'before'),(A,'after')):
    i=h.find('跑掉一點點不用管'); j=h.rfind('<p',0,i); print(n,'5/25 p tag:',h[j:h.find('>',j)+1])
