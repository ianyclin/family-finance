import re,collections,sys
from html.parser import HTMLParser
def load(p): return open(p,encoding='utf-8').read()
A=load('wip/v61-2026-09-17/stages/polish-before.html'); B=load('guide/index.html')
def ids(s): return re.findall(r'\sid="([^"]+)"',s)
for name,s in (('before',A),('after',B)):
    c=collections.Counter(ids(s)); d=[k for k,v in c.items() if v>1]
    hrefs=set(re.findall(r'href="#([^"]*)"',s)); missing=sorted(h for h in hrefs if h and h not in c)
    print(name,'ids',len(c),'dups',d,'missing href targets',missing)
new=set(ids(B))-set(ids(A)); gone=set(ids(A))-set(ids(B))
print('new ids',sorted(new),'removed ids',sorted(gone))
# element text for ids
import html as H
def strip(x): return re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>','',x))).strip()
for i in ['s5-fx','s13-drop20','s13-crash','s13-switch','lifecycle-sequence','family-sheet','pension','case-chen','plan-table','s13-loss','s6-fx']:
    m=re.search(r'<(\w+)[^>]*\sid="%s"[^>]*>'%re.escape(i),B)
    tag=m.group(1); start=m.start()
    # find closing roughly
    end=B.find('</%s>'%tag,start)
    print('\n#',i,'<%s>'%tag, strip(B[start:end])[:400])
# who links to new ids
for i in ['s5-fx','s13-drop20','s13-crash','s13-switch','lifecycle-sequence','family-sheet','pension']:
    print(i,'inbound',len(re.findall(r'href="#%s"'%re.escape(i),B)),'before',len(re.findall(r'href="#%s"'%re.escape(i),A)))
