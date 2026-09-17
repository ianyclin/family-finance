exec(open('walk.py').read())
go(); click_link("年底了，做一年一次的檢查"); print(where()); shot(ws,'walk-4a-annual.png'); print(text_view(400))
print("annual screens", screens('#annual','#lifecycle'))
for k in ['年底細節','計畫表和家庭一頁表','稅和帳戶安全','遇到這六件事','把這七項印出來']:
    y=ev(ws,f"""(()=>{{const e=[...document.querySelectorAll('#annual summary,#annual strong,#annual h3,#annual p.decision')].find(x=>x.textContent.includes({json.dumps(k)}));return e?Math.round(e.getBoundingClientRect().top+scrollY):null}})()""")
    print(k, y and round((y-ypos('#annual'))/800,1))
scroll(1500); shot(ws,'walk-4b-annual-xirr.png'); print(text_view(900))
ev(ws,"""(()=>{const e=[...document.querySelectorAll('#annual strong')].find(x=>x.textContent.includes('計畫表和家庭一頁表'));e.scrollIntoView({block:'start',behavior:'instant'})})()"""); time.sleep(.6); shot(ws,'walk-4c-annual-end.png'); print(text_view(1500))
p.kill()
