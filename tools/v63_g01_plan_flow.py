"""G01（v6.3 第二批 c）：第 11 節「我的投資計畫」A–H 的填表順序圖。

內容來源（全部是第 11 節既有的字，沒有新數字）
    八個區名與內容：第 11 節「把答案寫成一張紙：我的投資計畫」那張卡的 A–H 條列。
    「暫定」那一步：同節欄位表第 12 格——「股票比例要等 E 區做完三問才定：先挑一個打算放的
    比例試算，寫『暫定』；E 區比例改了，回來重查表一，重算 D 區」。
    第一條回頭：欄位表第 14 格——「不夠時照順序①多存②延後③降低目標；還不夠：回頭重想目標，
    不靠調高股票比例（三問第 3 題）」。
    第二條回頭：同節「三問，和答不過時怎麼辦」第 2 題——「沒通過，股票比例降一成（10 個百分點）
    再演練」，第 3 題——補完以後再答、不靠調高股票比例。

規格未定處
    審查報告寫「從 E 往回畫兩條箭頭」。這裡第一條回頭改成從 D 出發（「低那一列到不了」是 D 區
    第 14 格的事，讀者第一次撞牆就在 D），第二條照報告從 E 出發。兩條的標籤文字照報告。

畫法
    桌面和手機同一個結構：由上到下一串方塊，左邊兩條走道畫回頭箭頭（外道 D→A、內道 E→暫定比例），
    只有字級與描述長度不同。純示意，不需要任何數字。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""

# (kind, 代號, 區名, 桌面描述, 手機描述)
ROWS = [
    ('box', 'A', '這筆錢', '用途、哪一年要用、要多少（今天的錢 × 物價倍數）', '用途、哪一年要用、要多少'),
    ('box', 'B', '先顧好的', '預備金、利率高過 4% 的債、重大保障', '預備金、高利率債、保障'),
    ('box', 'C', '現在', '投資圈多少、每月投多少、走哪條路、總費用率', '每月投多少、走哪條路、費用率'),
    ('step', '', '', '先寫一個「暫定」股票比例（要等 E 區做完三問才定案）', '先寫一個「暫定」股票比例'),
    ('box', 'D', '試算', '查表算到期大約多少，只拿「低」那一列做決定', '查表算到期多少，只看「低」'),
    ('loop', 'D→C', '', '低那一列到不了：多存、延後、降低目標，回頭重查', '低那一列到不了：多存、延後、降目標'),
    ('box', 'E', '風險', '股債比、壓力測試、三問、下次什麼時候重做', '股債比、壓力測試、三問'),
    ('loop', 'E→暫定', '', '三問沒過：股票比例降一成，再走一次 D、E', '三問沒過：比例降一成，再走一次'),
    ('box', 'F', '規則', '市場下跌時怎麼做、什麼情況才賣、冷卻期', '下跌時怎麼做、什麼情況才賣'),
    ('box', 'G', '家人', '家裡誰知道這張紙放在哪裡', '誰知道、紙放在哪裡'),
    ('box', 'H', '改計畫紀錄', '每次改：日期、改什麼、理由、冷卻期到哪一天', '日期、改什麼、理由'),
]
LOOP_TARGET = {'D→C': 'C', 'E→暫定': 'step'}


def compute():
    boxes = [r for r in ROWS if r[0] == 'box']
    assert [r[1] for r in boxes] == list('ABCDEFGH')
    loops = [{'from': r[1].split('→')[0], 'to': LOOP_TARGET[r[1]], 'label': r[3]}
             for r in ROWS if r[0] == 'loop']
    assert len(loops) == 2
    return {
        'id': 'plan-flow',
        'illustrative': True,
        'basis': {
            'what': '第 11 節計畫表 A–H 的填表順序，加上兩條一定會回頭的路',
            'no_new_numbers': True,
            'numbers_on_chart': '只有區名裡本來就有的 4%（B 區高利率債的粗尺）',
            'spec_note': '審查報告寫兩條回頭都從 E 出發；這裡第一條改成從 D 出發，'
                         '因為「低那一列到不了」是 D 區第 14 格的事',
        },
        'steps': [{'key': r[1], 'name': r[2], 'desc': r[3]} for r in ROWS if r[0] == 'box'],
        'tentative_step': [r[3] for r in ROWS if r[0] == 'step'][0],
        'loops': loops,
        'source': {'section_id': 's11',
                   'from': ['第 11 節 A–H 條列', '同節欄位表第 12 格（暫定比例）',
                            '同節欄位表第 14 格（不夠時的順序）', '同節「三問，和答不過時怎麼辦」第 2、3 題']},
        'printed': {},
    }


def chart(res):
    import essay_charts as E

    def draw(lay):
        mob = lay.mobile
        pad = 6
        lane_out, lane_in = pad + 1, pad + 10      # 兩條回頭走道（外道 D→A、內道 E→暫定）
        bx0, bx1 = pad + 22, lay.W - pad
        badge_cx = bx0 + 15                        # 徽章在方塊裡面，左邊的走道才空得出來
        name_x = bx0 + 30
        f_name = lay.f
        f_desc = lay.fs
        desc_x = bx0 + (100 if mob else 122)
        gap = 10
        hb, hs, hl = 32, 26, 22                    # 方塊／暫定／回頭 三種列高
        ys, y = {}, 8
        for i, (kind, key, name, d_desc, m_desc) in enumerate(ROWS):
            hh = {'box': hb, 'step': hs, 'loop': hl}[kind]
            ys[i] = (y, hh)
            y += hh + gap
        h = y - gap + 8
        out = [E.svg_open(lay, h, '我的投資計畫 A 到 H 的填表順序：A 這筆錢、B 先顧好的、C 現在、'
                                  '先寫一個暫定的股票比例、D 試算、E 風險、F 規則、G 家人、H 改計畫紀錄；'
                                  'D 算出來不夠時回去改 C 區的每月投入或 A 區的日期與金額，'
                                  'E 三問沒過時回去改暫定的股票比例')]
        # 列與列之間的連接線（只畫在空隙，不穿過方塊）
        for i in range(len(ROWS) - 1):
            y0 = ys[i][0] + ys[i][1]
            y1 = ys[i + 1][0]
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>'
                       % (badge_cx, y0, badge_cx, y1, E.LINE))
        for i, (kind, key, name, d_desc, m_desc) in enumerate(ROWS):
            top, hh = ys[i]
            mid = top + hh / 2
            desc = m_desc if mob else d_desc
            if kind == 'box':
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="6" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.2"/>'
                           % (bx0, top, bx1 - bx0, hh, E.TEAL, E.TEAL))
                out.append('<circle cx="%.1f" cy="%.1f" r="9" fill="%s"/>' % (badge_cx, mid, E.TEAL))
                out.append(E.text(badge_cx, mid + f_name * 0.36, key, f_name, 'middle', E.SURFACE, '800'))
                out.append(E.text(name_x, mid + f_name * 0.36, name, f_name, 'start', E.INK, '800'))
                out.append(E.text(desc_x, mid + f_desc * 0.36, desc, f_desc, 'start', E.MUTED))
            elif kind == 'step':
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="6" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="5 4"/>'
                           % (bx0, top, bx1 - bx0, hh, E.MUTED))
                out.append(E.text(name_x, mid + f_desc * 0.36, desc, f_desc, 'start', E.INK, '700'))
            else:   # loop：往回的說明，字和區名切齊，箭頭走左邊的走道
                out.append(E.text(name_x, mid + f_desc * 0.36, '↩ ' + desc, f_desc, 'start', E.AMBER, '700'))
                lane = lane_out if key == 'D→C' else lane_in
                tgt = LOOP_TARGET[key]
                ti = next(j for j, r in enumerate(ROWS)
                          if (r[0] == 'box' and r[1] == tgt) or (r[0] == 'step' and tgt == 'step'))
                t_top, t_hh = ys[ti]
                t_mid = t_top + t_hh / 2
                out.append('<path d="M%.1f,%.1f H%.1f V%.1f H%.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                           % (name_x - 8, mid, lane, t_mid, bx0 - 6, E.AMBER))
                out.append('<path d="M%.1f,%.1f l-5,-3.5 l0,7 Z" fill="%s"/>' % (bx0 - 1, t_mid, E.AMBER))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(E.TEAL, '計畫表的八個區，照 A 到 H 的順序填'),
                   (E.AMBER, '回頭：算不夠、或三問沒過時，回到前面改了再往下走')])
    # v7 批 7：原本 p.note 後半和下面的 figcaption 逐句重複講同樣兩條回頭的路，留 figcaption 那一份；
    # note 只留圖說沒有的東西（「暫定股票比例」不是一個區、三條路寫在第 14 格、降一成＝10 個百分點）。
    nt = E.note('示意圖，沒有新數字：A 到 H 是第 11 節計畫表的八個區，每一區怎麼填、24 格各要寫什麼，'
                '在同一節的欄位表裡。'
                '「暫定股票比例」不是一個區，是欄位表第 12 格的提醒：股票比例要等 E 區做完三問才定案，'
                '先挑一個打算放的比例試算、寫「暫定」。'
                '兩條回頭的路怎麼走，看下面的圖說；D 算不夠時的三條路（多存、延後、降低目標）'
                '寫在欄位表第 14 格，降一成就是 10 個百分點。')
    caption = ('A 到 H 不是一路填到底：D 區算出來的「低」那一列到不了目標時，回去改 C 區的每月投入'
               '或 A 區的日期與金額（三條路的空格在 D 區）再重查；E 區三問沒過時，把股票比例降一成，'
               '再走一次 D、E。中間那格虛線的「暫定」比例，就是為了這兩次回頭留的。')
    lead = '照 A 到 H 的順序填，中間有兩個地方一定會回頭。下面這張圖把順序和那兩條回頭的路標出來。'
    res['printed'] = {'order': [r[1] for r in ROWS if r[0] == 'box'],
                      'loops': [(l['from'], l['to']) for l in res['loops']],
                      'lead_sentence': lead}
    return dict(title='計畫表怎麼填：A 到 H，還有兩條回頭的路',
                sub='示意：第 11 節計畫表八個區的填寫順序，沒有新數字',
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
