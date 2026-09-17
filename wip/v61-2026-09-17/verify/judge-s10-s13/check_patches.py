import json, re, sys
base = "/Users/linyenchu/Cladue Code/family-finance/"
old = open(base+"guide/index.v61-pre-w1.backup.html", encoding="utf-8").read()
new = open(base+"guide/index.html", encoding="utf-8").read()
def sec(html, sid):
    m = re.search(r'<section class="part" id="%s">' % re.escape(sid), html)
    s = m.start()
    n = html.find('<section class="part"', m.end())
    return html[s:n]
for key in ["s10","s12","s13","steps","s2","s6","s9"]:
    p = json.load(open(base+"wip/v61-2026-09-17/w1/patch-%s.json"%key, encoding="utf-8"))
    for i,x in enumerate(p):
        print(key, i, "old in backup:", old.count(x["old"]), "old in new:", new.count(x["old"]), "new in new:", new.count(x["new"]))
    so, sn = sec(old,key), sec(new,key)
    # apply patches to old section and compare with new section
    t = so
    for x in p:
        t = t.replace(x["old"], x["new"])
    print(key, "section identical to backup+patches:", t == sn, "len", len(so), len(sn))
