# Ảnh bộ kit – catalog phụ tùng xe máy

Kho này lưu **ảnh trang catalog cho từng bộ kit** (KIT00005, KIT00169-125…) và **danh sách tra cứu** đi kèm, để mọi người trong công ty mở xem hoặc chèn ảnh vào Excel bằng link.

| | |
|---|---|
| Số mã bộ trong danh sách | 4.427 |
| Số mã đã có ảnh | 2.887 |
| Số file ảnh | 373 (một ảnh có thể dùng chung cho nhiều mã, ví dụ bản 125 và 160) |

---

## 1. Các file của phần bộ kit trong kho

Phần bộ kit dùng chung kho `picturemotocycle` với **Thư viện Bộ Nhựa** (xem [README.md](README.md)). Hai phần tách riêng thư mục, không đụng nhau:

```
index.html                    ← Trang tra cứu bộ kit (GitHub Pages)
anh-bo-kit/                   ← Ảnh bộ kit .jpg, đặt tên theo mã bộ
data/danh-sach-anh-bo-kit.xlsx ← File gốc (sửa ở đây khi có thay đổi)
data/danh-sach-bo-kit.csv      ← Bản CSV, mở bằng Excel được
data/danh-sach-bo-kit.js       ← Dữ liệu cho trang tra cứu (tự sinh)
cong-cu/cap_nhat_du_lieu.py    ← Sinh lại .js/.csv và báo ảnh thiếu
.nojekyll                      ← Để GitHub Pages phục vụ nguyên file, không xử lý lại
```

Các thư mục `anh/`, `bo/`, `dong-xe/`, `tra-ma/`, `tools/` và các file `data/bo_nhua…`, `data/tra_ma.csv`, `data/theo-dong-xe/` là của Thư viện Bộ Nhựa.

## Bật trang tra cứu (làm 1 lần)

1. Kho phải để **Public** (Settings → General → Danger Zone → Change visibility).
2. Trên GitHub: **Settings → Pages** → *Source*: **Deploy from a branch** · *Branch*: **main** · **/(root)** → **Save**.
3. Đợi 1–2 phút, trang có ở `https://hoadonbinhnguyenpt19-art.github.io/picturemotocycle/`

## 2. Cách dùng

### 2.1. Tra cứu trên web
Sau khi bật GitHub Pages (mục trên), mở:

```
https://hoadonbinhnguyenpt19-art.github.io/picturemotocycle/
```

- Gõ **mã** (`KIT00169`) hoặc **tên** (`dau quy lat vision`) – không cần gõ dấu.
- Bấm vào một dòng để xem ảnh lớn → **Phóng to**, **Chép link ảnh**, **Mở ảnh gốc**.
- Gửi thẳng link một bộ cho người khác: thêm `#mã` vào cuối, ví dụ
  `…/picturemotocycle/#KIT00169-125`

Không có mạng vẫn xem được: mở file `index.html` trên máy bằng trình duyệt.

### 2.2. Link trực tiếp tới một ảnh
Mẫu link (đã có sẵn ở cột **Đường dẫn (dự kiến)** trong Excel):

```
https://raw.githubusercontent.com/hoadonbinhnguyenpt19-art/picturemotocycle/main/anh-bo-kit/<Tên ảnh>
```

Ví dụ: `…/main/anh-bo-kit/KIT00005.jpg`

### 2.3. Chèn ảnh vào ô Excel (Microsoft 365)
Giả sử cột E là link ảnh:

```
=IMAGE(E2)
```

Hoặc ghép từ tên ảnh ở cột D:

```
=IF(D2="","",IMAGE("https://raw.githubusercontent.com/hoadonbinhnguyenpt19-art/picturemotocycle/main/anh-bo-kit/"&D2))
```

> Hàm `IMAGE` chỉ có trên Excel 365 / Excel web và **repo phải để Public** thì Excel mới tải được ảnh.

### 2.4. Ý nghĩa cột Ghi chú

| Ghi chú | Nghĩa |
|---|---|
| Đúng trang của bộ | Ảnh lấy đúng trang catalog của đời xe đó |
| Trang tham khảo (catalog đời gần nhất…) | Chưa có catalog đúng đời; dùng trang của đời gần nhất có cùng chi tiết – cần đối chiếu mã |
| Chưa có catalog PDF đọc được cho bộ này | Chưa có ảnh |

Cột **Tỷ lệ mã khớp** cho biết bao nhiêu % mã phụ tùng của bộ xuất hiện trên trang đó.

## 3. Cập nhật thêm ảnh / sửa danh sách

1. Bỏ ảnh mới vào `anh-bo-kit/` (tên file = cột **Tên ảnh**).
2. Sửa `data/danh-sach-anh-bo-kit.xlsx`.
3. Chạy (cần Python + `pip install openpyxl`):
   ```
   python cong-cu/cap_nhat_du_lieu.py
   ```
   Lệnh này sinh lại `danh-sach-bo-kit.js`, `.csv` và in ra **ảnh còn thiếu**.
4. Mở GitHub Desktop → ghi chú thay đổi → **Commit to main** → **Push origin**.

Không đổi tên file ảnh cũ – link đã dán trong các file Excel sẽ hỏng.
