import subprocess, os, sys, time
C='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
D=os.getcwd(); F='file:///Users/linyenchu/Cladue%20Code/family-finance'
jobs=[
 ('after-default', F+'/output/full-v60-out.html', []),
 ('after-w400', F+'/output/full-v60-out.html', ['--window-size=400,900']),
 ('after-w400-nojs', F+'/output/full-v60-out.html', ['--window-size=400,900','--blink-settings=scriptEnabled=false']),
 ('jsonly-w400', F+'/wip/v61-2026-09-17/verify6/j-print-nocssfallback.html', ['--window-size=400,900']),
 ('neither-w400', F+'/wip/v61-2026-09-17/verify6/j-print-neither.html', ['--window-size=400,900']),
 ('before-w400', F+'/wip/v61-2026-09-17/stages/polish-before.html', ['--window-size=400,900']),
]
only=sys.argv[1:]
for name,url,extra in jobs:
    if only and name not in only: continue
    out=os.path.join(D,'j-print-%s.pdf'%name)
    if os.path.exists(out): os.rename(out,out+'.old')
    cmd=[C,'--headless=new','--disable-gpu','--no-pdf-header-footer','--virtual-time-budget=8000','--print-to-pdf='+out]+extra+[url]
    t=time.time()
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240); code=r.returncode
    except subprocess.TimeoutExpired: code='timeout'
    print(name,code,round(time.time()-t),os.path.getsize(out) if os.path.exists(out) else None,flush=True)
