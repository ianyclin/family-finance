# -*- coding: utf-8 -*-
"""黃框 div.story、mark.key、facts.txt 逐字不變檢查（裁判用，只讀）"""
import re, sys, os, subprocess
ROOT='/Users/linyenchu/Cladue Code/family-finance'
sys.path.insert(0, os.path.join(ROOT,'tools'))
sys.path.insert(0, '%s' % os.path.join(ROOT,'tools'))
import guidetools as G
OLD=os.path.join(ROOT,'wip','v63','before-batch2.html')
NEW=os.path.join(ROOT,'guide','index.html')
def blocks(path, cls, tag='div'):
    h=G.read(path)
    if tag=='div':
        return [h[a:b] for a,b in G.div_blocks(h, cls)]
    return re.findall(r'<%s\b(?=[^>]*?(?<![\w-])class="%s")[^>]*>(.*?)</%s>'%(tag,cls,tag), h, re.S)
for cls,tag in (('story','div'),('key','mark')):
    o=blocks(OLD,cls,tag); n=blocks(NEW,cls,tag)
    print('%s: 改前 %d、改後 %d' % (cls,len(o),len(n)))
    if o==n: print('   逐字相同 OK')
    else:
        so,sn=set(o),set(n)
        for x in so-sn: print('   只在改前:', re.sub(r'\s+',' ',x)[:160])
        for x in sn-so: print('   只在改後:', re.sub(r'\s+',' ',x)[:160])
        if so==sn: print('   集合相同、順序不同')
