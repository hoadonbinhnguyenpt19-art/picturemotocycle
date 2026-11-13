# -*- coding: utf-8 -*-
"""
Cập nhật dữ liệu cho trang tra cứu bộ kit.

Đọc  : data/danh-sach-anh-bo-kit.xlsx
Ghi  : data/danh-sach-bo-kit.js   (trang index.html dùng, mở được cả khi không có mạng)
       data/danh-sach-bo-kit.csv  (mở bằng Excel, UTF-8 có BOM)
Báo  : ảnh có trong Excel nhưng thiếu trong thư mục anh-bo-kit, và ảnh thừa.

Cách chạy (đứng ở thư mục gốc repo):
    pip install openpyxl
    python cong-cu/cap_nhat_du_lieu.py
"""
import csv
import json
import os
import sys

try:
    import openpyxl
except ImportError:
    sys.exit("Thiếu thư viện openpyxl. Chạy: pip install openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_EXCEL = os.path.join(GOC, "data", "danh-sach-anh-bo-kit.xlsx")
THU_MUC_ANH = os.path.join(GOC, "anh-bo-kit")
FILE_JS = os.path.join(GOC, "data", "danh-sach-bo-kit.js")
FILE_CSV = os.path.join(GOC, "data", "danh-sach-bo-kit.csv")

# Tên khoá ngắn trong JSON  <-  tiêu đề cột trong Excel
COT = [
    ("ma", "Mã bộ"),
    ("ten", "Tên bộ"),
    ("nguon", "Nguồn"),
    ("anh", "Tên ảnh"),
    ("link", "Đường dẫn (dự kiến)"),
    ("pdf", "File PDF gốc"),
    ("trang", "Trang PDF"),
    ("khoi", "Khối catalog"),
    ("khop", "Tỷ lệ mã khớp"),
    ("ghichu", "Ghi chú"),
]


def doc_excel():
    ws = openpyxl.load_workbook(FILE_EXCEL, read_only=True, data_only=True).active
    dong = ws.iter_rows(values_only=True)
    tieu_de = [str(x).strip() if x is not None else "" for x in next(dong)]
    vi_tri = {}
    for khoa, ten_cot in COT:
        if ten_cot not in tieu_de:
            sys.exit(f"Không thấy cột '{ten_cot}' trong file Excel.")
        vi_tri[khoa] = tieu_de.index(ten_cot)

    ket_qua = []
    for r in dong:
        if not r or r[vi_tri["ma"]] in (None, ""):
            continue
        muc = {}
        for khoa, _ in COT:
            v = r[vi_tri[khoa]]
            muc[khoa] = "" if v is None else str(v).strip()
        ket_qua.append(muc)
    return ket_qua


def main():
    du_lieu = doc_excel()

    os.makedirs(os.path.dirname(FILE_JS), exist_ok=True)
    with open(FILE_JS, "w", encoding="utf-8") as f:
        f.write("// File tự sinh bởi cong-cu/cap_nhat_du_lieu.py - không sửa tay\n")
        f.write("window.KIT_DATA = ")
        json.dump(du_lieu, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    with open(FILE_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([t for _, t in COT])
        for m in du_lieu:
            w.writerow([m[k] for k, _ in COT])

    anh_excel = {m["anh"] for m in du_lieu if m["anh"]}
    anh_thu_muc = set()
    if os.path.isdir(THU_MUC_ANH):
        anh_thu_muc = {x for x in os.listdir(THU_MUC_ANH) if x.lower().endswith((".jpg", ".jpeg", ".png"))}

    co_anh = sum(1 for m in du_lieu if m["anh"])
    print(f"Số mã bộ           : {len(du_lieu)}")
    print(f"Số mã có ảnh       : {co_anh}")
    print(f"Số ảnh riêng (Excel): {len(anh_excel)}")
    print(f"Số ảnh trong thư mục: {len(anh_thu_muc)}")

    thieu = sorted(anh_excel - anh_thu_muc)
    thua = sorted(anh_thu_muc - anh_excel)
    if not anh_thu_muc:
        print("\n!! Chưa có thư mục anh-bo-kit hoặc thư mục trống. Chạy 1_CHEP_ANH_VAO_REPO.bat trước.")
    if thieu:
        print(f"\n!! Thiếu {len(thieu)} ảnh (có trong Excel, không có file):")
        for x in thieu:
            print("   -", x)
    if thua:
        print(f"\n-- {len(thua)} ảnh có file nhưng Excel không nhắc tới:")
        for x in thua:
            print("   -", x)
    print("\nĐã ghi:", os.path.relpath(FILE_JS, GOC), "và", os.path.relpath(FILE_CSV, GOC))


if __name__ == "__main__":
    main()
