import re, sys, html as H
def blocks(path):
    h=open(path,encoding='utf-8').read()
    h=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)
    h=re.sub(r'<svg.*?</svg>','[SVG]',h,flags=re.S)
    # mark section ids
    h=re.sub(r'<section[^>]*id="([^"]+)"[^>]*>',lambda m:'\n@@SECTION '+m.group(1)+'\n',h)
    h=re.sub(r'</?(p|li|h[1-6]|dd|dt|td|th|tr|figcaption|div|ul|ol|table|details|summary|figure|section|a class="source-link"[^>]*)\b[^>]*>','\n',h)
    h=re.sub(r'<[^>]+>','',h)
    h=H.unescape(h)
    out=[l.strip() for l in h.split('\n') if l.strip()]
    return out
if __name__=='__main__':
    for l in blocks(sys.argv[1]): print(l)
