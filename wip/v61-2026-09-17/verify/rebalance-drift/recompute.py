"""裁判獨立重算 G10 rebalance-drift。不 import 起草者模組。
讀 research/data/damodaran_histret.xls（xlrd），自己找欄位。
"""
import json, os, statistics
from decimal import Decimal, ROUND_HALF_UP
import xlrd

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
XLS = os.path.join(ROOT, 'research/data/damodaran_histret.xls')


def hu(x, nd='0.1'):
    # half-up，從 float 的最短 repr 出發；另外回傳精確十進位版本以偵測邊界
    a = Decimal(repr(x)).quantize(Decimal(nd), rounding=ROUND_HALF_UP)
    b = Decimal(x).quantize(Decimal(nd), rounding=ROUND_HALF_UP)
    return float(a), (a != b)


def load():
    sh = xlrd.open_workbook(XLS).sheet_by_name('Returns by year')
    # 表頭在第 19 列（0-based），自己確認
    hdr = None
    for r in range(sh.nrows):
        if sh.cell_value(r, 0) == 'Year':
            hdr = r
            break
    names = [str(sh.cell_value(hdr, c)) for c in range(sh.ncols)]
    idx = {n: c for c, n in enumerate(names)}
    c_sp = names.index('S&P 500 (includes dividends)')  # 第一個出現的是年報酬
    c_tb = names.index('US T. Bond (10-year)')
    c_bill = names.index('3-month T.Bill')
    c_baa = names.index(' Baa Corporate Bond')
    d = {}
    for r in range(hdr + 1, sh.nrows):
        y = sh.cell_value(r, 0)
        if isinstance(y, float):
            d[int(y)] = dict(sp=sh.cell_value(r, c_sp), tb=sh.cell_value(r, c_tb),
                             bill=sh.cell_value(r, c_bill), baa=sh.cell_value(r, c_baa))
    return d, names[c_sp], names[c_tb]


def buyhold(d, start, end, defk='tb', w=0.8):
    s, b = w, 1 - w
    out = []
    for y in range(start, end + 1):
        s *= 1 + d[y]['sp']
        b *= 1 + d[y][defk]
        out.append((y, s / (s + b), s + b))
    return out


def annual_reb(d, start, end, defk='tb', w=0.8):
    v = 1.0
    out = []
    for y in range(start, end + 1):
        s = v * w * (1 + d[y]['sp'])
        b = v * (1 - w) * (1 + d[y][defk])
        v = s + b
        out.append((y, s / v, v))
    return out


def outside(sw, strict=True):
    dev = abs(sw - 0.8)
    return dev > 0.05 if strict else dev >= 0.05


def first_out(path, strict=True):
    for y, sw, _ in path:
        if outside(sw, strict):
            return y, sw
    return None


def main():
    d, n1, n2 = load()
    last = max(d)
    R = {'cols': [n1, n2], 'last_year': last}

    p = buyhold(d, 1990, last)
    R['main_series'] = [(y, hu(sw * 100)[0], repr(sw * 100)) for y, sw, _ in p]
    fb = first_out(p)
    R['main_first_breach'] = (fb[0], fb[0] - 1990 + 1, hu(fb[1] * 100), 'above' if fb[1] > .8 else 'below')
    back = [y for y, sw, _ in p if y > fb[0] and not outside(sw)]
    R['main_back_inside'] = back
    lo = min(p, key=lambda t: t[1])
    hi = max(p, key=lambda t: t[1])
    R['main_min'] = (lo[0], hu(lo[1] * 100))
    R['main_max'] = (hi[0], hu(hi[1] * 100))
    R['main_end'] = (p[-1][0], hu(p[-1][1] * 100), hu((1 - p[-1][1]) * 100))
    R['main_years_outside'] = (sum(1 for _, sw, _ in p if outside(sw)), len(p))
    R['main_years_outside_inclusive'] = sum(1 for _, sw, _ in p if outside(sw, False))
    R['main_near_edges'] = [(y, sw * 100) for y, sw, _ in p if abs(abs(sw - .8) - .05) < 0.002]
    # 1990–2012 最高（標籤放 97% 高度會不會壓線）
    R['main_max_through_2012'] = max(hu(sw * 100)[0] for y, sw, _ in p if y <= 2012)
    R['main_first_year_above_97'] = next((y for y, sw, _ in p if sw > .97), None)
    R['main_first_year_above_92'] = next((y for y, sw, _ in p if sw > .92), None)

    for s in (2000, 2009):
        q = buyhold(d, s, last)
        f = first_out(q)
        lo2 = min(q, key=lambda t: t[1])
        R['start_%d' % s] = dict(first=(f[0], hu(f[1] * 100), repr(f[1] * 100)) if f else None,
                                 min=(lo2[0], hu(lo2[1] * 100)), end=hu(q[-1][1] * 100),
                                 series=[(y, repr(sw * 100)) for y, sw, _ in q[:4]])

    rb = annual_reb(d, 1990, last)
    R['reb_pre_breaches'] = [(y, sw * 100) for y, sw, _ in rb if outside(sw)]
    R['reb_pre_min'] = min((hu(sw * 100)[0], y) for y, sw, _ in rb)
    R['reb_pre_max'] = max((hu(sw * 100)[0], y) for y, sw, _ in rb)
    R['growth'] = (p[-1][2] / 1.0, rb[-1][2])

    # 全部起點掃描 1928–2021
    rows = []
    for s in range(1928, 2022):
        q = buyhold(d, s, last)
        f = first_out(q)
        rows.append((s, (f[0] - s + 1) if f else None, ('above' if f and f[1] > .8 else ('below' if f else None))))
    yrs = [r[1] for r in rows if r[1] is not None]
    R['scan'] = dict(n=len(rows), never=sum(1 for r in rows if r[1] is None), min=min(yrs),
                     median=statistics.median(yrs), max=max(yrs),
                     above=sum(1 for r in rows if r[2] == 'above'), below=sum(1 for r in rows if r[2] == 'below'),
                     slower_than_7=sum(1 for y in yrs if y > 7), equal_7=sum(1 for y in yrs if y == 7),
                     faster_than_7=sum(1 for y in yrs if y < 7),
                     slowest=[r for r in rows if r[1] == max(yrs)], fastest_count=sum(1 for y in yrs if y == 1))
    # 掃描延伸到 2024（看 1–16 年範圍會不會因終點截斷而變）
    rows2 = []
    for s in range(1928, last + 1):
        q = buyhold(d, s, last)
        f = first_out(q)
        rows2.append((s, (f[0] - s + 1) if f else None))
    R['scan_to_last'] = dict(never=[r[0] for r in rows2 if r[1] is None],
                             max=max(r[1] for r in rows2 if r[1]))
    # 分佈
    from collections import Counter
    R['scan_hist'] = sorted(Counter(yrs).items())

    # 敏感度：防守換成 3 個月國庫券（較像定存）
    pb = buyhold(d, 1990, last, 'bill')
    fbb = first_out(pb)
    R['bill_1990'] = dict(first=(fbb[0], hu(fbb[1] * 100)), min_after=min(((y, hu(sw * 100)[0]) for y, sw, _ in pb if y > fbb[0]), key=lambda t: t[1]),
                          back_inside=[y for y, sw, _ in pb if y > fbb[0] and not outside(sw)],
                          end=hu(pb[-1][1] * 100), y2008=[hu(sw * 100)[0] for y, sw, _ in pb if y == 2008])
    rowsb = []
    for s in range(1928, 2022):
        q = buyhold(d, s, last, 'bill')
        f = first_out(q)
        rowsb.append((f[0] - s + 1) if f else None)
    yb = [x for x in rowsb if x]
    R['bill_scan'] = dict(min=min(yb), median=statistics.median(yb), max=max(yb), never=sum(1 for x in rowsb if x is None))
    # 起點敏感：1985–1995 起點各自第一次超出
    R['near_starts'] = {s: next(((y - s + 1, hu(sw * 100)[0]) for y, sw, _ in buyhold(d, s, last) if outside(sw)), None)
                        for s in range(1985, 1996)}
    # 2008 年報酬
    R['ret_2008'] = (d[2008]['sp'], d[2008]['tb'], d[2008]['bill'])
    return R


if __name__ == '__main__':
    R = main()
    print(json.dumps(R, ensure_ascii=False, indent=1, default=str))
