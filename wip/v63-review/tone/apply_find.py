#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""印出 guide/index.html 裡含某個片語的附近原文（含 HTML 標籤）。

用法：python3 apply_find.py '片語' [前後字元數]
"""
import re
import sys
import pathlib

GUIDE = pathlib.Path(__file__).resolve().parents[3] / "guide" / "index.html"


def main():
    probe = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    text = GUIDE.read_text(encoding="utf-8")
    idxs = [m.start() for m in re.finditer(re.escape(probe), text)]
    print("命中 %d 次" % len(idxs))
    for i in idxs:
        print("-----")
        print(text[max(0, i - width): i + len(probe) + width])


if __name__ == "__main__":
    main()
