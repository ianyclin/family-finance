import re,sys,html
s=open('guide/index.html',encoding='utf-8').read()
def sec(i):
    m=re.search(r'<(section|header|div)[^>]*id="%s"'%i,s)
    if not m: return None
    st=m.start(); tag=m.group(1)
    # find next section start
    n=re.search(r'<section[^>]*id="',s[st+10:])
    return s[st: st+10+(n.start() if n else 20000)]
def txt(h):
    h=re.sub(r'<(script|style|svg|figure)[\s\S]*?</\1>','',h)
    h=re.sub(r'<a [^>]*href="(#[^"]*)"[^>]*>',lambda m:'[→%s]'%m.group(1),h)
    h=re.sub(r'<(h[1-4]|li|p|tr|summary)[^>]*>',lambda m:'\n<%s> '%m.group(1),h)
    h=re.sub(r'<[^>]+>','',h)
    return re.sub(r'\n\s*\n+','\n',html.unescape(h))
for i in sys.argv[1:]:
    x=sec(i); print('=====',i); print(txt(x) if x else 'NOTFOUND')
