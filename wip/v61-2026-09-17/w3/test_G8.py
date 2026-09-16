import sys, json, re, subprocess
FF = '/Users/linyenchu/Cladue Code/family-finance'
sys.path.insert(0, FF + '/tools')
import v61_g8_recovery_by_mix as G
import essay_charts as E
D = '/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/f330c746-4fb1-4319-8da3-61dfb142160e/scratchpad/w3'
res = G.compute()
json.dumps(res)  # 可 JSON 化
json.dump(res, open(D + '/G8-compute.json', 'w'), ensure_ascii=False, indent=1)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2
fig = E.figure('recovery-by-mix', d['title'], d['sub'], d['svgs'], d['caption'], d['extras'])
g = open(FF + '/guide/index.html', encoding='utf-8').read()
css = '\n'.join(l for l in g.split('\n')[:40] if l.startswith(':root') or l.startswith('figure.chart') or l.startswith('@media (max-width:640px)'))
page = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>%s\nbody{background:var(--paper);margin:0;padding:8px;color:var(--ink);font-family:var(--sans)}</style>%s' % (css, fig)
open(D + '/recovery-by-mix.html', 'w', encoding='utf-8').write(page)
mob = page.replace('<style>', '<style>figure.chart svg.d{display:none!important}figure.chart svg.m{display:block!important}body{width:376px}')
open(D + '/recovery-by-mix-mobile.html', 'w', encoding='utf-8').write(mob)
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
for name, size, src in [('desktop', '720,1100', 'recovery-by-mix.html'), ('mobile', '520,1300', 'recovery-by-mix-mobile.html')]:
    subprocess.run([chrome, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
                    '--screenshot=%s/recovery-by-mix-%s.png' % (D, name), '--window-size=' + size,
                    'file://' + D + '/' + src], check=True, capture_output=True)
print(d['title']); print(d['sub']); print(d['caption']); print(re.sub('<[^>]+>', ' ', d['extras']))
for s in d['svgs']: print(s.split('\n')[0])
