exec(open('walk.py').read())
go("#group-life"); click_link("12","document.querySelector('#group-life p.small')"); print(where()); shot(ws,'walk-5e-chen.png'); print(text_view(900))
print(ev(ws,"""[...document.querySelectorAll('#group-life p.small a, nav.tasks a')].map(a=>{const r=a.getBoundingClientRect();return [a.textContent.slice(0,12),Math.round(r.width),Math.round(r.height)]})"""))
# count tiny numeric xrefs site-wide
print(ev(ws,"""(()=>{const a=[...document.querySelectorAll('a.xref')].filter(x=>/^\\d+$/.test(x.textContent.trim()));return [a.length, document.querySelectorAll('a.xref').length]})()"""))
print("css scroll-margin/behavior", ev(ws,"getComputedStyle(document.documentElement).scrollBehavior"))
print("cover buttons bottom", ev(ws,"(()=>{window.scrollTo(0,0);return [...document.querySelectorAll('nav.tasks li')].map(l=>Math.round(l.getBoundingClientRect().bottom))})()"))
p.kill()
