import json,re,html
base="/Users/linyenchu/Cladue Code/family-finance/"
def plain(s): return html.unescape(re.sub(r'<[^>]+>','',s))
def sents(t): return sorted(x for x in re.split(r'(?<=[。])',t) if x)
p10=json.load(open(base+"wip/v61-2026-09-17/w1/patch-s10.json",encoding="utf-8"))
o,n=plain(p10[0]["old"]),plain(p10[0]["new"])
print("OLD:",o); print("NEW:",n)
n2=n.replace("規則：","",1)
print("same multiset of sentences after removing 規則：", sents(o)==sents(n2))
print("same char multiset:", sorted(o)==sorted(n2))
p13=json.load(open(base+"wip/v61-2026-09-17/w1/patch-s13.json",encoding="utf-8"))
o,n=plain(p13[2]["old"]),plain(p13[2]["new"])
print("OLD:",o); print("NEW:",n)
from collections import Counter
co,cn=Counter(o),Counter(n)
print("chars only in old:",dict(co-cn)); print("chars only in new:",dict(cn-co))
