"""Bước 2: data.json + ảnh -> kho thư viện GitHub (Markdown + ảnh + CSV/JSON)."""
import json, os, re, sys, shutil, csv, unicodedata, datetime
from collections import defaultdict, OrderedDict
from urllib.parse import quote

WORK, REPO = sys.argv[1], sys.argv[2]
NGAY = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().strftime('%d/%m/%Y')
d = json.load(open(f'{WORK}/data.json'))
if os.path.exists(REPO): shutil.rmtree(REPO)
for p in ('anh', 'bo', 'dong-xe', 'tra-ma', 'data/theo-dong-xe'):
    os.makedirs(f'{REPO}/{p}', exist_ok=True)

def fold(t):
    t = unicodedata.normalize('NFD', t).replace('đ', 'd').replace('Đ', 'D')
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')
def slug(t, n=60):
    t = re.sub(r'[^a-z0-9]+', '-', fold(t).lower()).strip('-')
    return t[:n].rstrip('-')
def md(t):
    return str(t).replace('|', '\\|').replace('\n', ' ').replace('*', '\\*').strip()
def rel(frm, to):
    return quote(os.path.relpath(to, os.path.dirname(frm)).replace(os.sep, '/'))

BOS = OrderedDict((b['ma_bo'], b) for b in d['bos'])
for b in BOS.values():
    for c in b['ct']:
        if c['ghi_chu'] in ('0', '1', '*'): c['ghi_chu'] = ''

# gán bộ -> dòng xe (theo sheet thư viện ảnh)
line_of, title_of = {}, {}
LINES = []
for L in d['lines']:
    L['slug'] = slug(L['ten'])
    LINES.append(L)
    for x in L['xe']:
        if x['ma_bo'] in BOS and x['ma_bo'] not in line_of:
            line_of[x['ma_bo']] = L; title_of[x['ma_bo']] = x['tieu_de']
khac = dict(ten='Khác', tieu_de='BỘ NHỰA KHÁC', slug='khac', xe=[])
for b in BOS:
    if b not in line_of:
        khac['xe'].append(dict(ma_bo=b, tieu_de=BOS[b]['ten'])); line_of[b] = khac; title_of[b] = BOS[b]['ten']
if khac['xe']: LINES.append(khac)

def short_title(b):
    t = BOS[b]['ten'] or title_of.get(b) or b
    return re.sub(r'^Bộ nhựa \(Dàn áo\)\s*', '', t).strip()

path_of = {}
for b, B in BOS.items():
    L = line_of[b]
    path_of[b] = f'bo/{L["slug"]}/{b}-{slug(short_title(b))}.md'
    os.makedirs(f'{REPO}/bo/{L["slug"]}', exist_ok=True)
    if B['anh']: shutil.copy(f'{WORK}/raw/{b}.jpg', f'{REPO}/anh/{b}.jpg')

# chỉ mục mã chi tiết -> bộ
used = defaultdict(lambda: dict(ten='', bo=OrderedDict(), tt_cho=set(), bs=OrderedDict()))
for b, B in BOS.items():
    for c in B['ct']:
        u = used[c['ma']]; u['ten'] = u['ten'] or c['ten']; u['bo'][b] = 1
        for t in c['thay_the']:
            used[t]['tt_cho'].add(c['ma']); used[t]['bs'].setdefault(b, 1)
    for c in B['bs']:
        u = used[c['ma']]; u['ten'] = u['ten'] or c['ten']; u['bs'][b] = 1
_c3 = defaultdict(int)
for _m in used: _c3[_m[:3]] += len(used[_m]['bo']) + len(used[_m]['bs']) + 3
def prefix(m):
    g = m[:3] if m[:3].isdigit() else m[:1]
    return m[:4] if _c3[m[:3]] > 2500 and m[:3].isdigit() else g
def ma_link(frm, m):
    return f'[`{m}`]({rel(frm, "tra-ma/" + prefix(m) + ".md")}#{m.lower()})'

# biến thể .1
fam = defaultdict(list)
for b in BOS: fam[b.split('.')[0]].append(b)

# ---------- trang từng bộ ----------
for b, B in BOS.items():
    p = path_of[b]; L = line_of[b]
    o = [f'[🏠 Trang chủ]({rel(p, "README.md")}) › [{L["ten"]}]({rel(p, "dong-xe/" + L["slug"] + ".md")}) › **{b}**', '',
         f'# {b} · {md(short_title(b))}', '']
    if B['anh']: o += [f'<img src="{rel(p, "anh/" + b + ".jpg")}" alt="{b}" width="480">', '']
    else: o += ['> _Chưa có ảnh đời xe._', '']
    o += ['| | |', '|---|---|', f'| **Mã bộ** | `{b}` |', f'| **Tên bộ** | {md(B["ten"])} |']
    if B['ten_loai']: o.append(f'| **Đời xe** | {md(B["ten_loai"])} |')
    if B['model']: o.append(f'| **Model** | {md(B["model"])} |')
    o.append(f'| **Dòng xe** | {L["ten"]} |')
    o.append(f'| **Số chi tiết** | {len(B["ct"])} |')
    o.append('')
    rel_bo = [x for x in fam[b.split('.')[0]] if x != b]
    if rel_bo:
        o += ['**Bộ liên quan:** ' + ' · '.join(f'[{x}]({rel(p, path_of[x])})' for x in rel_bo), '']
    o += ['## Chi tiết trong bộ', '', '| STT | Mã chi tiết | Tên chi tiết | Dùng chung | Mã thay thế | Ghi chú |',
          '|---:|---|---|:---:|---|---|']
    for c in B['ct']:
        o.append(f'| {c["stt"]} | {ma_link(p, c["ma"])} | {md(c["ten"])} | {"✔" if c["dung_chung"] else ""} | '
                 f'{"<br>".join(ma_link(p, t) for t in c["thay_the"])} | {md(c["ghi_chu"])} |')
    if B['bs']:
        o += ['', '## Mã thiếu bổ sung', '', '_Không tính sẵn trong bộ, thêm khi khách cần._', '',
              '| Mã | Tên |', '|---|---|']
        for c in B['bs']: o.append(f'| {ma_link(p, c["ma"])} | {md(c["ten"])} |')
    o += ['', f'<sub>Cập nhật {NGAY}</sub>', '']
    open(f'{REPO}/{p}', 'w').write('\n'.join(o))

# ---------- trang dòng xe ----------
for L in LINES:
    p = f'dong-xe/{L["slug"]}.md'
    o = [f'[🏠 Trang chủ](../README.md) › **{L["ten"]}**', '', f'# {L["tieu_de"].title() if L["tieu_de"].isupper() else L["tieu_de"]}', '',
         f'{len(L["xe"])} đời/màu xe. Bấm vào ảnh hoặc mã bộ để xem danh sách chi tiết.', '', '<table>']
    xs = L['xe']
    for i in range(0, len(xs), 3):
        o.append('<tr>')
        for x in xs[i:i + 3]:
            b = x['ma_bo']; t = md(short_title(b) if b in BOS else x['tieu_de']) or b
            if b in BOS:
                href = rel(p, path_of[b])
                img = (f'<a href="{href}"><img src="{rel(p, "anh/" + b + ".jpg")}" width="240" alt="{b}"></a>'
                       if BOS[b]['anh'] else '<i>Chưa có ảnh</i>')
                o.append(f'<td align="center" valign="top" width="33%">{img}<br><b>{t}</b><br><a href="{href}"><code>{b}</code></a></td>')
            else:
                o.append(f'<td align="center" valign="top" width="33%"><i>Chưa có dữ liệu</i><br><b>{t}</b><br><code>{b}</code></td>')
        o.append('</tr>')
    o += ['</table>', '']
    open(f'{REPO}/{p}', 'w').write('\n'.join(o))

# ---------- tra theo mã chi tiết ----------
groups = defaultdict(list)
for m in sorted(used): groups[prefix(m)].append(m)
for g, ms in groups.items():
    p = f'tra-ma/{g}.md'
    o = [f'[🏠 Trang chủ](../README.md) › [Tra theo mã](README.md) › **{g}…**', '', f'# Mã chi tiết bắt đầu bằng {g}', '',
         'Nhấn **Ctrl+F** và gõ mã để tìm nhanh trên trang này.', '']
    for m in ms:
        u = used[m]
        o += [f'### {m}', '']
        if u['ten']: o.append(f'**{md(u["ten"])}**  ')
        if u['tt_cho']: o.append('Là mã thay thế cho: ' + ', '.join(ma_link(p, x) for x in sorted(u['tt_cho'])) + '  ')
        if u['bo']:
            o.append(f'Có trong {len(u["bo"])} bộ: ' + ' · '.join(f'[{b}]({rel(p, path_of[b])})' for b in u['bo']))
        if u['bs']:
            o.append('  \nBổ sung / thay thế ở: ' + ' · '.join(f'[{b}]({rel(p, path_of[b])})' for b in u['bs'] if b not in u['bo']))
        o.append('')
    open(f'{REPO}/{p}', 'w').write('\n'.join(o))
o = ['[🏠 Trang chủ](../README.md) › **Tra theo mã**', '', '# Tra theo mã chi tiết', '',
     'Chọn nhóm theo **3–4 số đầu** của mã (ví dụ mã `64301K2TV00` → nhóm **6430**, mã `33708KWW600` → nhóm **337**).', '', '| Nhóm | Số mã |', '|---|---:|']
for g in sorted(groups): o.append(f'| [{g}…]({g}.md) | {len(groups[g])} |')
open(f'{REPO}/tra-ma/README.md', 'w').write('\n'.join(o) + '\n')

# ---------- dữ liệu thô ----------
HDR = ['ma_bo', 'ten_bo', 'dong_xe', 'doi_xe', 'model', 'loai', 'stt', 'ma_chi_tiet', 'ten_chi_tiet', 'dung_chung', 'ma_thay_the', 'ghi_chu', 'anh']
def rows_of(b):
    B = BOS[b]; L = line_of[b]; anh = f'anh/{b}.jpg' if B['anh'] else ''
    for c in B['ct']:
        yield [b, B['ten'], L['ten'], B['ten_loai'], B['model'], 'chinh', c['stt'], c['ma'], c['ten'],
               'x' if c['dung_chung'] else '', ' '.join(c['thay_the']), c['ghi_chu'], anh]
    for c in B['bs']:
        yield [b, B['ten'], L['ten'], B['ten_loai'], B['model'], 'bo_sung', '', c['ma'], c['ten'], '', '', '', anh]
with open(f'{REPO}/data/bo_nhua.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(HDR)
    for b in BOS: w.writerows(rows_of(b))
for L in LINES:
    rs = []
    for x in L['xe']:
        b = x['ma_bo']
        if b in BOS and line_of[b] is L:
            for r in rows_of(b):
                rs.append([b, short_title(b), r[6] if r[5] == 'chinh' else 'bổ sung', r[7], r[8], r[10], r[11]])
    H2 = ['ma_bo', 'doi_xe', 'stt', 'ma_chi_tiet', 'ten_chi_tiet', 'ma_thay_the', 'ghi_chu']
    parts, cur, size = [], [], 0
    for r in rs:
        n = sum(len(str(v).encode()) + 1 for v in r)
        if size + n > 450000 and cur: parts.append(cur); cur, size = [], 0
        cur.append(r); size += n
    if cur: parts.append(cur)
    L['csv'] = []
    for i, part in enumerate(parts):
        fn = f'{L["slug"]}.csv' if len(parts) == 1 else f'{L["slug"]}-{i + 1}.csv'
        L['csv'].append(fn)
        with open(f'{REPO}/data/theo-dong-xe/{fn}', 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(H2); w.writerows(part)
out = dict(cap_nhat=NGAY, dong_xe=[dict(ten=L['ten'], ma_bo=[x['ma_bo'] for x in L['xe']]) for L in LINES],
           bo=[dict(B, dong_xe=line_of[b]['ten'], tieu_de=short_title(b), anh=(f'anh/{b}.jpg' if B['anh'] else None),
                    trang=path_of[b]) for b, B in BOS.items()])
json.dump(out, open(f'{REPO}/data/bo_nhua.json', 'w'), ensure_ascii=False, separators=(',', ':'))
with open(f'{REPO}/data/tra_ma.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['ma_chi_tiet', 'ten', 'co_trong_bo', 'la_ma_thay_the_cho', 'bo_sung_o_bo'])
    for m in sorted(used):
        u = used[m]; w.writerow([m, u['ten'], ' '.join(u['bo']), ' '.join(sorted(u['tt_cho'])), ' '.join(u['bs'])])

# ---------- README ----------
def vn(n): return f'{n:,}'.replace(',', '.')
nct = sum(len(B['ct']) for B in BOS.values()); nanh = sum(B['anh'] for B in BOS.values())
o = ['# 📚 Thư viện Bộ Nhựa Honda 2026', '',
     f'Thư viện tra cứu **{vn(len(BOS))} bộ nhựa (dàn áo)** của **{len(LINES)} dòng xe**, gồm **{vn(nct)}'
     f' dòng chi tiết**, **{vn(len(used))} mã** và **{vn(nanh)} ảnh đời xe**. Xem trực tiếp trên GitHub, không cần cài đặt hay mở web riêng.', '',
     f'<sub>Dữ liệu cập nhật: {NGAY}</sub>', '',
     '## Cách tra cứu', '',
     '| Muốn tìm | Cách làm |', '|---|---|',
     '| **Theo dòng xe** | Bấm tên dòng xe ở bảng bên dưới → bấm vào ảnh đời/màu xe → ra danh sách mã chi tiết. |',
     '| **Theo tên xe hoặc mã bộ** | Ở trang chủ kho, nhấn phím **`t`** rồi gõ, ví dụ `BO0025` hoặc `wave 110s do 313`. Tên file không dấu nên gõ không dấu. |',
     '| **Theo mã chi tiết** | Vào [Tra theo mã](tra-ma/README.md), chọn nhóm theo số đầu của mã rồi **Ctrl+F** gõ mã. Hoặc gõ mã vào ô **Search** trên đầu GitHub (cần đăng nhập). |',
     '| **Lọc cả bảng** | Mở file trong [data/theo-dong-xe](data/theo-dong-xe) — GitHub hiện thành bảng có ô **Search this file**. |',
     '| **Lấy dữ liệu về máy** | Tải [data/bo_nhua.csv](data/bo_nhua.csv) (mở bằng Excel) hoặc [data/bo_nhua.json](data/bo_nhua.json). Bấm nút **Download raw file** ở góc phải. |', '',
     '## Dòng xe', '', '| | Dòng xe | Số đời/màu xe | Bảng dữ liệu |', '|---|---|---:|---|']
for L in LINES:
    first = next((x['ma_bo'] for x in L['xe'] if x['ma_bo'] in BOS and BOS[x['ma_bo']]['anh']), None)
    th = f'<img src="anh/{first}.jpg" width="90">' if first else ''
    o.append(f'| {th} | **[{L["ten"]}](dong-xe/{L["slug"]}.md)** | {len(L["xe"])} | ' + ' · '.join(f'[CSV{"" if len(L["csv"]) == 1 else " " + str(i + 1)}](data/theo-dong-xe/{fn})' for i, fn in enumerate(L["csv"])) + ' |')
o += ['', '## Cấu trúc thư mục', '', '```',
      'README.md               ← trang này',
      'dong-xe/<dong-xe>.md    ← lưới ảnh đời/màu xe của từng dòng',
      'bo/<dong-xe>/BOxxxx-….md ← 1 trang cho mỗi bộ nhựa: ảnh + danh sách chi tiết',
      'tra-ma/<nhom>.md        ← mã chi tiết → có trong bộ nào',
      'anh/BOxxxx.jpg          ← ảnh đời xe theo mã bộ',
      'data/                   ← dữ liệu thô CSV / JSON',
      '```', '',
      '## Quy ước', '',
      '- **Mã bộ** dạng `BO0025`. Mã có đuôi `.1` (ví dụ `BO0768.1`) là bộ liên quan của bộ gốc, xem mục *Bộ liên quan* trong trang bộ.',
      '- **Mã thay thế** gộp từ cột *Mã thay thế* và mã ghi ở cột *Ghi chú* trong file gốc.',
      '- **Mã thiếu bổ sung** không tính sẵn trong bộ, người tra tự thêm khi cần.',
      '- Thư viện **không chứa giá và tồn kho**.', '',
      '## Cập nhật dữ liệu', '',
      'Dữ liệu sinh tự động từ file Excel *Bộ nhựa 2026 tách từng bộ* bằng công cụ trong thư mục [`tools`](tools). Khi file Excel thay đổi, chạy lại công cụ rồi tải đè các thư mục lên kho.', '']
open(f'{REPO}/README.md', 'w').write('\n'.join(o))
print('bo pages', len(BOS), 'lines', len(LINES), 'codes', len(used), 'groups', len(groups))
