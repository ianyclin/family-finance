# -*- coding: utf-8 -*-
"""把 guide/illus/*.webp 內嵌進 guide/index.html（批 CT）。

用法：
  python3 tools/embed_illus.py            # 把每個 <img data-illus="NN-name" src="…"> 的 src 換成 guide/illus/NN-name.webp 的 base64
  python3 tools/embed_illus.py --check    # 哨兵：只比對、不寫檔；每個 data-illus 的 src 都要和檔案一致、
                                          # img 的 width／height 要等於檔案實際寬高（用 PIL 讀；沒有 PIL 就跳過並提示），印 ILLUS OK 才過
  python3 tools/embed_illus.py --check path/to/other.html   # 對別的 HTML 比對（例如 output/guide.html）

規則：
- 鍵是 img 上的 data-illus 屬性（留在 HTML 裡），值對應 guide/illus/<鍵>.webp；圖只有這一個來源，改圖只要換檔再重跑。
- 等冪：src 已經和檔案一致就不動，重跑結果逐位元相同。
- 只認帶 data-illus 的 img；圖表（figure.chart／data-chart）與其他 img 一律不碰。
- 找不到檔、HTML 裡某個鍵沒有 src、或 guide/illus 裡有檔沒被任何 img 用到，都算錯（--check 判紅；寫入模式直接停，不寫檔）。
"""
import base64
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, 'guide', 'index.html')
ILLUS_DIR = os.path.join(ROOT, 'guide', 'illus')

IMG_RE = re.compile(r'<img\b[^>]*>')
KEY_RE = re.compile(r'(?<![\w-])data-illus="([^"]+)"')
SRC_RE = re.compile(r'(?<![\w-])src="([^"]*)"')
WIDTH_RE = re.compile(r'(?<![\w-])width="(\d+)"')
HEIGHT_RE = re.compile(r'(?<![\w-])height="(\d+)"')


def data_uri(key):
    p = os.path.join(ILLUS_DIR, key + '.webp')
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        return 'data:image/webp;base64,' + base64.b64encode(f.read()).decode('ascii')


def scan(html):
    """回傳 [(match, key, src)]，只列帶 data-illus 的 img。"""
    out = []
    for m in IMG_RE.finditer(html):
        k = KEY_RE.search(m.group(0))
        if not k:
            continue
        s = SRC_RE.search(m.group(0))
        out.append((m, k.group(1), s.group(1) if s else None))
    return out


def main(argv):
    check = '--check' in argv
    rest = [a for a in argv if a != '--check']
    path = os.path.abspath(rest[0]) if rest else GUIDE
    with open(path, encoding='utf-8') as f:
        html = f.read()
    imgs = scan(html)
    files = sorted(f[:-5] for f in os.listdir(ILLUS_DIR) if f.endswith('.webp'))
    problems = []
    if not imgs:
        problems.append('HTML 裡沒有任何 <img data-illus>')
    used = set()
    want = {}
    for m, key, src in imgs:
        used.add(key)
        uri = want.get(key) or data_uri(key)
        if uri is None:
            problems.append('%s：guide/illus/%s.webp 不存在' % (key, key))
            continue
        want[key] = uri
        if src is None:
            problems.append('%s：img 沒有 src 屬性' % key)
    unused = [f for f in files if f not in used]
    for f in unused:
        problems.append('guide/illus/%s.webp 沒有被任何 <img data-illus> 用到' % f)

    stale = [key for m, key, src in imgs if key in want and src is not None and src != want[key]]
    rel = os.path.relpath(path, ROOT)
    print('%s：<img data-illus> %d 個（%d 個鍵）；guide/illus 檔 %d 個；src 與檔案不一致 %d 個'
          % (rel, len(imgs), len(used), len(files), len(stale)))

    if check:
        # 每個 webp 的實際寬高要等於 img 的 width／height 屬性（換圖換了比例，版面預留的高度才不會錯）
        try:
            from PIL import Image
        except ImportError:
            Image = None
            print('（沒有 PIL，跳過寬高比對；pip install pillow 以後再跑一次）')
        if Image is not None:
            ndim = 0
            for m, key, src in imgs:
                p = os.path.join(ILLUS_DIR, key + '.webp')
                if not os.path.exists(p):
                    continue
                with Image.open(p) as im:
                    real = im.size
                w = WIDTH_RE.search(m.group(0)); h = HEIGHT_RE.search(m.group(0))
                attr = (int(w.group(1)) if w else None, int(h.group(1)) if h else None)
                ndim += 1
                if attr != real:
                    problems.append('%s：img 寫 width=%s height=%s，檔案實際 %d×%d' % (key, attr[0], attr[1], real[0], real[1]))
            print('寬高比對 %d 個' % ndim)
        for key in stale:
            problems.append('%s：src 和 guide/illus/%s.webp 不一致（重跑 python3 tools/embed_illus.py）' % (key, key))
        if problems:
            for p in problems:
                print(' -', p)
            print('ILLUS FAILED')
            return 1
        print('ILLUS OK')
        return 0

    if problems:
        for p in problems:
            print(' -', p)
        print('沒有寫檔')
        return 1
    if not stale:
        print('全部一致，沒有改動（等冪）')
        return 0

    def repl(m):
        tag = m.group(0)
        k = KEY_RE.search(tag)
        if not k:
            return tag
        return SRC_RE.sub(lambda s: 'src="%s"' % want[k.group(1)], tag, count=1)

    new = IMG_RE.sub(repl, html)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    print('換了 %d 個 src：%s' % (len(stale), '、'.join(stale)))
    print('檔案大小 %d → %d 字元' % (len(html), len(new)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
