import json, re, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/linyenchu/Cladue Code/family-finance")
sys.path.insert(0, str(ROOT / "tools"))
import v61_g9_country_recovery as M
import essay_charts as E
OUT = Path(__file__).resolve().parent

res = M.compute()
json.dumps(res)
rows = {r["key"]: r for r in res["rows"]}
# 到日的起訖
assert (rows["us"]["peak"], rows["us"]["recover"]) == ("1929-09-03", "1954-11-23")
assert (rows["jp"]["peak"], rows["jp"]["recover"]) == ("1989-12-29", "2024-02-22")
assert (rows["tw"]["peak"], rows["tw"]["recover"]) == ("1990-02-10", "2020-07-27")
# 年數（half-up）與指南 #s4 表：25 年、34 年 2 個月、約 30 年
assert rows["us"]["years_label"] == "約 25 年" and rows["us"]["years_int"] == 25
assert rows["jp"]["years_label"] == "34 年 2 個月"
assert rows["tw"]["years_label"] == "約 30 年" and rows["tw"]["years_int"] == 30
assert res["table_check"] == "指南 #s4 表：美國 相符、日本 相符、台灣 相符", res["table_check"]
print({k: (r["months_exact"], r["years_exact"], r["months_rounded"], r["years_label"]) for k, r in rows.items()})
# half-up 邊界
assert int(M.half_up(2.5)) == 3 and int(M.half_up(3.5)) == 4

# 表不在時不 raise
real = M.GUIDE
M.GUIDE = OUT / "no-such-guide.html"
r2 = M.compute(); assert r2["table_check"] == "指南 #s4 表不在，未比對"
assert [r["years_label"] for r in r2["rows"]] == [r["years_label"] for r in res["rows"]]
M.GUIDE = real

c = M.chart(res)
txt = c["caption"] + c["extras"] + c["sub"]
assert "只到月" not in txt
assert "還沒回到買進時的點位" not in txt
assert "第一次收盤" in c["caption"] and "第一次收盤" in c["sub"]
assert "第一次收盤超過舊高點；之後還是可能再跌回舊高點以下" in c["extras"]
assert "早一些" not in txt and "早很多年" not in txt
assert 'class="legend"' not in c["extras"]
for d in ("1929-09-03", "1954-11-23", "1990-02-10", "2020-07-27", "1989-12-29", "2024-02-22"):
    assert all(d in s for s in c["svgs"]), d
print("caption:", c["caption"]); print("note:", re.sub("<[^>]+>", "", c["extras"]))

fig = E.figure("country-recovery", c["title"], c["sub"], c["svgs"], c["caption"], c["extras"])
g = (ROOT / "guide/index.html").read_text(encoding="utf-8")
css = "\n".join(re.findall(r"^figure\.chart[^\n]*$", g, re.M))
root = re.search(r":root\{[^}]*\}", g).group(0)
page = ('<!doctype html><meta charset="utf-8"><style>%s\nbody{margin:0;padding:16px;background:var(--paper);color:var(--ink);font-family:var(--sans)}main{max-width:760px;margin:auto}\n%s</style><main>%s</main>' % (root, css, fig))
(OUT / "country-recovery.html").write_text(page, encoding="utf-8")
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mob = page.replace("main{max-width:760px;margin:auto}", "main{width:392px;margin:0}figure.chart svg.d{display:none!important}figure.chart svg.m{display:block!important}")
(OUT / "country-recovery-mobile.html").write_text(mob, encoding="utf-8")
for name, size, src in (("country-recovery-desktop.png", "900,760", "country-recovery.html"), ("country-recovery-mobile.png", "440,900", "country-recovery-mobile.html")):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--screenshot=%s" % (OUT / name), "--window-size=%s" % size, (OUT / src).as_uri()],
                   check=True, capture_output=True)
    print("wrote", OUT / name)
print("OK")
