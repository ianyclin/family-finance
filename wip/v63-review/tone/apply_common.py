#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""語氣批：逐句取代的共用工具。

用法：在 apply_*.py 裡準備 EDITS = [(標籤, 原文, 新文), ...]，
呼叫 run(EDITS)。每一筆 assert 原文在 guide/index.html 命中恰好 1 次；
命中 0 次或 >1 次就印出附近的 HTML 原文並中止（不落檔）。
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
GUIDE = ROOT / "guide" / "index.html"


def _context(text, needle, width=260):
    """命中 0 次時，用 needle 的前後片段找出最接近的原文並印出。"""
    out = []
    # 由長到短，取 needle 的前綴去找
    for n in (40, 28, 20, 14, 10, 8, 6):
        if n >= len(needle):
            continue
        probe = needle[:n]
        idxs = [m.start() for m in re.finditer(re.escape(probe), text)]
        if idxs:
            for i in idxs[:4]:
                out.append(text[max(0, i - 60):i + width])
            return probe, out
    return None, out


def run(edits, dry_run=False, path=None):
    p = pathlib.Path(path) if path else GUIDE
    text = p.read_text(encoding="utf-8")
    orig = text
    bad = []
    done = []
    for tag, old, new in edits:
        cnt = text.count(old)
        if cnt != 1:
            bad.append((tag, old, cnt))
            continue
        text = text.replace(old, new, 1)
        done.append(tag)
    if bad:
        print("=== 命中數不是 1 的筆數：%d ===" % len(bad))
        for tag, old, cnt in bad:
            print("\n---- %s ：命中 %d 次 ----" % (tag, cnt))
            print("想找：", old[:200])
            probe, ctx = _context(orig, old)
            if probe:
                print("用前綴 %r 找到 %d 段附近原文：" % (probe, len(ctx)))
                for c in ctx:
                    print("   >>>", c.replace("\n", "\\n")[:400])
            else:
                print("   （連短前綴都找不到）")
        print("\n沒有寫檔。成功 %d 筆、失敗 %d 筆。" % (len(done), len(bad)))
        sys.exit(1)
    if dry_run:
        print("dry-run：%d 筆全部命中 1 次，未寫檔。" % len(done))
        return
    p.write_text(text, encoding="utf-8")
    print("OK：%d 筆全部命中 1 次並已寫入 %s" % (len(done), p))


if __name__ == "__main__":
    print(__doc__)
