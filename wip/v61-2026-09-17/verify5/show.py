import re, sys
from struct_lib import *
h=load(sys.argv[1])
secs={s['id']:s for s in sections(h)}
def show(sid):
    b=re.sub(r'<(style|script|svg)\b.*?</\1>','',secs[sid]['body'],flags=re.S)
    b=re.sub(r'data:[^"]+','',b)
    b=re.sub(r'<a\b[^>]*href="#([\w-]+)"[^>]*>(.*?)</a>', lambda m: '['+re.sub('<[^>]+>','',m.group(2))+'→#'+m.group(1)+']', b, flags=re.S)
    b=re.sub(r'</(p|li|h3|h2|tr|div|summary)>', '\n', b)
    t=re.sub(r'<[^>]+>','',b)
    t=re.sub(r'\n\s*\n+','\n',t)
    print('#####',sid,len(t)); print(t)
for s in sys.argv[2:]: show(s)
