import re,sys,html
H=open('output/full-v60-out.html',encoding='utf-8').read()
ids=['ten','why','start','glossary','s1','s2','s3','s5','s6','s10','s11','s12','s13','cases','costs','products','methods','annual','lifecycle','withdraw']
pos={}
for i in ids:
    m=re.search(r'id="%s"'%i,H); pos[i]=m.start()
order=sorted(pos.items(),key=lambda x:x[1])
def totext(h):
    h=re.sub(r'<script.*?</script>','',h,flags=re.S)
    h=re.sub(r'<style.*?</style>','',h,flags=re.S)
    h=re.sub(r'<(h[1-6]|p|li|tr|div|dt|summary|figcaption)\b[^>]*>','\n',h)
    h=re.sub(r'</(td|th|dt)>',' | ',h)
    h=re.sub(r'<[^>]+>','',h)
    h=html.unescape(h)
    h=re.sub(r'[ \t]+',' ',h)
    h=re.sub(r'\n\s*\n+','\n',h)
    return h.strip()
want=sys.argv[1:]
for k,(i,p) in enumerate(order):
    if i not in want: continue
    end=order[k+1][1] if k+1<len(order) else len(H)
    # back up to start of tag
    st=H.rfind('<',0,p)
    print(f"\n{'='*70}\n### SECTION id={i}\n{'='*70}")
    print(totext(H[st:end]))
