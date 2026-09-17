import re,html,sys
s=open('guide-v62.html',encoding='utf-8').read()
s=re.sub(r'<script.*?</script>','',s,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>','',s))
locs=[l.strip() for l in open('advisor-lens/locs.txt',encoding='utf-8') if l.strip()]
for l in locs:
    n=t.count(l)
    print(n, l[:60])
