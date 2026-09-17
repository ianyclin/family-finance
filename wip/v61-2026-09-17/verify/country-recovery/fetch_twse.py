"""裁判重算用：抓證交所 FMTQIK（每月逐日收盤）1989-06..1990-05、2019-11..2020-08，另抽 1997-08、2000-02、2018-01 當中間期的高點抽查。"""
import json, time, urllib.request
from pathlib import Path
months = [(1989, m) for m in range(6, 13)] + [(1990, m) for m in range(1, 6)] \
       + [(2019, 11), (2019, 12)] + [(2020, m) for m in range(1, 9)] \
       + [(1997, 8), (2000, 2), (2018, 1), (2018, 10), (2019, 4)]
out = {}
for y, m in months:
    p = Path("twse_%04d%02d.json" % (y, m))
    if not p.exists():
        url = "https://www.twse.com.tw/exchangeReport/FMTQIK?response=json&date=%04d%02d01" % (y, m)
        p.write_bytes(urllib.request.urlopen(url, timeout=30).read())
        time.sleep(3.5)
    d = json.loads(p.read_text())
    out["%04d-%02d" % (y, m)] = d.get("data")
Path("twse_months.json").write_text(json.dumps(out, ensure_ascii=False))
print("ok", len(out))
