"""裁判抽查：「第一次收盤回到高點」之後有沒有再跌破（日經 FRED 逐日；證交所 FMTQIK 2020-08..2020-12）。"""
import csv, json, time, urllib.request
from datetime import date
from pathlib import Path
nk = [(date.fromisoformat(r["observation_date"]), float(r["NIKKEI225"])) for r in csv.DictReader(open("fred_nikkei225.csv")) if r["NIKKEI225"] not in ("", ".")]
after = [x for x in nk if x[0] > date(2024, 2, 22)]
below = [x for x in after if x[1] < 38915.87]
print("日經 2024-02-22 之後收盤低於 38,915.87 的天數：", len(below), "；最早", below[:1], "；最低", min(after, key=lambda x: x[1]), "；資料最後一天", nk[-1])
rows = []
for m in range(8, 13):
    p = Path("twse_2020%02d.json" % m)
    if not p.exists():
        p.write_bytes(urllib.request.urlopen("https://www.twse.com.tw/exchangeReport/FMTQIK?response=json&date=2020%02d01" % m, timeout=30).read())
        time.sleep(3.5)
    for r in json.loads(p.read_text())["data"]:
        y, mm, d = [int(v) for v in r[0].strip().split("/")]
        rows.append((date(y + 1911, mm, d), float(r[4].replace(",", ""))))
b = [x for x in rows if x[1] < 12495.34]
print("台股 2020-08..12 收盤低於 12,495.34 的天數：", len(b), "；最早", b[:1], "；最低", min(rows, key=lambda x: x[1]))
