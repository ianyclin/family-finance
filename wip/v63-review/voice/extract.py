#!/usr/bin/env python3
"""把 guide/index.html 的某幾節抽成純文字（給語氣讀者用）。用法：python3 extract.py ten why s1 > out.txt
標記：【】黃線、【【】】淡紅線、〔黃框〕…〔/黃框〕、〔小卡：跳過〕、〔摺疊〕…〔/摺疊〕、〔白話版〕、〔表格：略〕、〔圖：標題〕。"""
import re, sys
s = open('guide/index.html', encoding='utf-8').read()
s = re.sub(r'<(style|script)[\s\S]*?</\1>', '', s)
ids = sys.argv[1:]
secs = [(m.start(), m.group(1)) for m in re.finditer(r'<section[^>]*\bid="([^"]+)"', s)]
for k, (pos, sid) in enumerate(secs):
    if ids and sid not in ids: continue
    end = secs[k+1][0] if k+1 < len(secs) else len(s)
    t = s[pos:end]
    t = re.sub(r'<svg[\s\S]*?</svg>', '', t)
    t = re.sub(r'<div class="planstep"[\s\S]*?</div>', '\n〔小卡：跳過〕\n', t)
    t = re.sub(r'<table[\s\S]*?</table>', '\n〔表格：略〕\n', t)
    t = re.sub(r'<details class="source-card[\s\S]*?</details>', '\n〔來源卡：略〕\n', t)
    t = re.sub(r'<mark class="key top">', '【【', t); t = re.sub(r'<mark class="key">', '【', t)
    t = re.sub(r'</mark>', '】', t)  # 淡紅線的結尾也只印一個】，讀者看開頭分辨
    t = re.sub(r'<div class="story"[^>]*>', '\n〔黃框〕', t)
    t = re.sub(r'<details[^>]*>', '\n〔摺疊〕', t); t = re.sub(r'</details>', '〔/摺疊〕\n', t)
    t = re.sub(r'<span class="chart-title">', '\n〔圖：', t)
    t = re.sub(r'</(p|li|h2|h3|h4|summary|div|figcaption|tr|dd|dt)>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'[ \t]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
    print('\n######## section id=%s ########' % sid); print(t.strip())
