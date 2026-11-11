"""Bước 1: đọc file Bộ nhựa 2026 -> data.json + ảnh gốc."""
import openpyxl, warnings, json, re, sys, os, io, bisect
from PIL import Image
warnings.filterwarnings('ignore')
SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT + '/raw', exist_ok=True)
wb = openpyxl.load_workbook(SRC)
ws = wb['T bo']

CODE_RE = re.compile(r'^[0-9A-Z]{8,}$')
def s(v):
    if v is None: return ''
    v = str(v).strip()
    return '' if v.startswith('=') else v
def codes_in(v):
    out = []
    for t in re.split(r'[\s,;/+]+', s(v).upper()):
        t = t.strip('*.-')
        if CODE_RE.match(t) and re.search(r'\d', t) and not t.startswith('BO'):
            out.append(t)
    return out

bos = {}; order = []; first_row = {}
for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    b = s(r[0])
    if not b: continue
    if b not in bos:
        bos[b] = dict(ma_bo=b, ten=s(r[1]), ten_loai=s(r[4]) or s(r[2]), model=s(r[5]) or s(r[3]),
                      ct=[], bs=[])
        order.append(b); first_row[b] = i
    B = bos[b]
    if not B['ten'] and s(r[1]): B['ten'] = s(r[1])
    if not B['ten_loai'] and (s(r[4]) or s(r[2])): B['ten_loai'] = s(r[4]) or s(r[2])
    stt = r[8]
    ma = s(r[9]).upper().replace(' ', '')
    if isinstance(stt, (int, float)) and ma and ma != b:
        note = s(r[12])
        tt = []
        for c in codes_in(r[24]) + codes_in(note):
            if c != ma and c not in tt: tt.append(c)
        ghichu = '' if codes_in(note) else note
        if ghichu in ('1', '*'): ghichu = ''
        B['ct'].append(dict(stt=int(stt), ma=ma, ten=s(r[10]), dung_chung=bool(re.search(r'dùng\s*chung', s(r[11]), re.I)),
                            thay_the=tt, ghi_chu=ghichu))
    aa = s(r[26]).upper().replace(' ', '')
    if aa and CODE_RE.match(aa) and aa != b:
        if aa not in [x['ma'] for x in B['bs']]:
            B['bs'].append(dict(ma=aa, ten=s(r[27])))

# ảnh trong sheet T bo (cột N) -> bộ theo dòng bắt đầu
starts = sorted((v, k) for k, v in first_row.items()); sr = [x for x, _ in starts]
tbo_img = {}
for im in sorted(ws._images, key=lambda im: im.anchor._from.row):
    row = im.anchor._from.row + 1
    j = bisect.bisect_right(sr, row) - 1
    if j < 0: continue
    tbo_img.setdefault(starts[j][1], im)

# sheet thư viện ảnh theo dòng xe
lines = []; gal_img = {}
for name in wb.sheetnames:
    if name == 'T bo': continue
    g = wb[name]
    cells = {}
    for row in g.iter_rows():
        for c in row:
            if c.value is not None: cells[(c.row, c.column)] = c.value
    imgs = {}
    for im in g._images:
        f = im.anchor._from
        imgs.setdefault((f.row + 1, f.col + 1), im)   # 1-based
    items = []
    for (rr, cc), v in sorted(cells.items()):
        if isinstance(v, str) and v.strip().lower().startswith('click xem'):
            bo = s(cells.get((rr, cc + 1))).upper()
            # tiêu đề: ô cùng cột, phía trên gần nhất
            title = ''
            for up in range(rr - 1, max(rr - 20, 0), -1):
                t = cells.get((up, cc))
                if isinstance(t, str) and t.strip() and not t.lower().startswith('click') and 'chưa có ảnh' not in t.lower():
                    title = t.strip(); trow = up; break
            # ảnh: neo giữa tiêu đề và nút, cột cc-1..cc+2
            im = None
            for (ir, ic), cand in imgs.items():
                if title and trow <= ir < rr and cc - 1 <= ic <= cc + 2:
                    im = cand; break
            items.append(dict(ma_bo=bo, tieu_de=title))
            if bo and im is not None and bo not in gal_img: gal_img[bo] = im
    title_line = s(cells.get((1, 2))) or name
    lines.append(dict(ten=name, tieu_de=title_line, xe=items))

def save(im, path):
    data = im._data()
    try:
        p = Image.open(io.BytesIO(data)); p.load()
    except Exception:
        return False
    if p.mode not in ('RGB', 'L'):
        bg = Image.new('RGB', p.size, 'white')
        bg.paste(p, mask=p.convert('RGBA').split()[-1]); p = bg
    p.thumbnail((900, 900))
    p.convert('RGB').save(path, 'JPEG', quality=80, optimize=True, progressive=True)
    return True

nimg = 0
for b in order:
    im = gal_img.get(b) or tbo_img.get(b)
    bos[b]['anh'] = False
    if im is not None and save(im, f'{OUT}/raw/{b}.jpg'):
        bos[b]['anh'] = True; nimg += 1

json.dump(dict(lines=lines, bos=[bos[b] for b in order]), open(f'{OUT}/data.json', 'w'), ensure_ascii=False)
print('bo', len(order), 'anh', nimg, 'gal', len(gal_img), 'tbo', len(tbo_img),
      'ct', sum(len(bos[b]['ct']) for b in order), 'bs', sum(len(bos[b]['bs']) for b in order))
print('lines', [(l['ten'], len(l['xe'])) for l in lines])
inline = {x['ma_bo'] for l in lines for x in l['xe']}
print('bo not in gallery', len([b for b in order if b not in inline]), [b for b in order if b not in inline][:20])
print('gallery codes not in T bo', [x for x in inline if x not in bos][:20])
