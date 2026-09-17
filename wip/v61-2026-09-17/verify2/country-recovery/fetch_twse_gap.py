#!/usr/bin/env python3
"""裁判第二輪：抓證交所 FMTQIK 逐日收盤，補 1990-01..1997-06（Yahoo ^TWII 從 1997-07 才有）與 2020-07..09。
只寫到本資料夾的 twse/ 底下。"""
import json, time, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "twse"
OUT.mkdir(exist_ok=True)
months = []
for y in range(1990, 1998):
    for m in range(1, 13):
        if y * 100 + m > 199706:
            break
        months.append("%d%02d" % (y, m))
months += ["202007", "202008", "202009"]
for ym in months:
    f = OUT / ("fmtqik_%s.json" % ym)
    if f.exists() and f.stat().st_size > 200:
        continue
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/FMTQIK?date=%s01&response=json" % ym
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            json.loads(data)
            f.write_bytes(data)
            break
        except Exception as e:  # noqa
            print("retry", ym, e)
            time.sleep(8)
    time.sleep(3.2)
print("done", len(list(OUT.glob("fmtqik_*.json"))))
