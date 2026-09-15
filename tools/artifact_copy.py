#!/usr/bin/env python3
"""把 essay/index.html 轉成 Artifact 可發佈的版本（output/essay.html）。

Artifact 發佈時會自己包 doctype／html／head／body，所以只拿掉這幾個外殼，
其餘（title、meta、link、style、內文）原樣保留。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "essay" / "index.html"
DST = ROOT / "output" / "essay.html"


def main():
    s = SRC.read_text(encoding="utf-8")
    s = re.sub(r"^\s*<!doctype[^>]*>\s*", "", s, flags=re.I)
    s = re.sub(r"</?(html|head|body)\b[^>]*>\s*", "", s, flags=re.I)
    DST.write_text(s, encoding="utf-8")
    print("寫出 %s（%.1f KB）" % (DST.relative_to(ROOT), len(s.encode("utf-8")) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
