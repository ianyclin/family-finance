import json, re, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/linyenchu/Cladue Code/family-finance")
sys.path.insert(0, str(ROOT / "tools"))
import v61_g9_country_recovery as M
import essay_charts as E
OUT = Path(__file__).resolve().parent
res = M.compute()
json.dumps(res)
print([(r["market"], r["years_label"]) for r in res["rows"]])
c = M.chart(res)
fig = E.figure("country-recovery", c["title"], c["sub"], c["svgs"], c["caption"], c["extras"])
g = (ROOT / "guide/index.html").read_text(encoding="utf-8")
css = "\n".join(re.findall(r"^figure\.chart[^\n]*$", g, re.M))
root = re.search(r":root\{[^}]*\}", g).group(0)
page = ('<!doctype html><meta charset="utf-8"><style>%s\nbody{margin:0;padding:16px;background:var(--paper);color:var(--ink);font-family:var(--sans)}main{max-width:760px;margin:auto}\n%s</style><main>%s</main>' % (root, css, fig))
(OUT / "country-recovery.html").write_text(page, encoding="utf-8")
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mob = page.replace("main{max-width:760px;margin:auto}", "main{width:392px;margin:0}figure.chart svg.d{display:none!important}figure.chart svg.m{display:block!important}")
(OUT / "country-recovery-mobile.html").write_text(mob, encoding="utf-8")
for name, size, src in (("country-recovery-desktop.png", "900,900", "country-recovery.html"), ("country-recovery-mobile.png", "440,1000", "country-recovery-mobile.html")):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--screenshot=%s" % (OUT / name), "--window-size=%s" % size, (OUT / src).as_uri()],
                   check=True, capture_output=True)
    print("wrote", OUT / name)
