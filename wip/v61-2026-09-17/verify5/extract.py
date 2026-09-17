# 抽出指定 section 的純文字（保留段落分行），寫到 verify5/txt/<id>.txt
import re, os, sys, html
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'guide/index.html')
tag = sys.argv[2] if len(sys.argv) > 2 else 'after'
H = open(src, encoding='utf-8').read()
os.makedirs('txt', exist_ok=True)
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"', H)]
for i, (pos, sid) in enumerate(starts):
    end = starts[i+1][0] if i+1 < len(starts) else len(H)
    chunk = H[pos:end]
    chunk = re.sub(r'<(script|style)\b.*?</\1>', '', chunk, flags=re.S)
    chunk = re.sub(r'</?(p|li|h[1-6]|tr|summary|figcaption|div|table|ul|ol|details|blockquote|dt|dd)\b[^>]*>', '\n', chunk)
    chunk = re.sub(r'<(td|th)\b[^>]*>', ' | ', chunk)
    chunk = re.sub(r'<[^>]+>', '', chunk)
    chunk = html.unescape(chunk)
    chunk = re.sub(r'\n\s*\n+', '\n', chunk)
    open('txt/%s-%s.txt' % (tag, sid), 'w', encoding='utf-8').write(chunk)
print(len(starts), 'sections')
