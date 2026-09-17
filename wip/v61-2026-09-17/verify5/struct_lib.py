import re, html as H
def load(p): return open(p, encoding='utf-8').read()
def text(s): return re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>','',s))).strip()
def sections(h):
    out=[]
    for m in re.finditer(r'<section class="part" id="([^"]+)">(.*?)</section>', h, re.S):
        sid, body = m.group(1), m.group(2)
        h2 = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S).group(1)
        num = re.search(r'<span class="num">(\d+)</span>', h2)
        name = text(re.sub(r'<span class="num">\d+</span>','',h2))
        lede = re.search(r'<p class="lede">(.*?)</p>', body, re.S)
        ids = re.findall(r'\bid="([^"]+)"', body)
        out.append(dict(id=sid, num=num.group(1) if num else None, name=name, lede=text(lede.group(1)) if lede else None, ids=ids, start=m.start(), end=m.end(), body=body))
    return out
def anchor_sec(h):
    d={}
    for s in sections(h):
        d[s['id']]=s
        for i in s['ids']: d[i]=s
    return d
