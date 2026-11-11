# Cập nhật thư viện từ file Excel mới

Cần Python 3 có `openpyxl` và `Pillow` (`pip install openpyxl pillow`).

```
python extract.py "Bộ nhựa 2026 tách từng bộ.xlsx" work
python build.py work thu-vien-bo-nhua 11/11/2026
```

Thư mục `thu-vien-bo-nhua` tạo ra là toàn bộ nội dung kho. File Excel cần giữ cấu trúc: sheet **T bo** (A mã bộ, B tên bộ, I STT, J mã chi tiết, K tên, L dùng chung, M ghi chú, Y mã thay thế, AA/AB mã thiếu bổ sung) và các sheet dòng xe (tiêu đề → ảnh → ô "Click xem bộ nhựa" + mã bộ ở ô bên phải).
