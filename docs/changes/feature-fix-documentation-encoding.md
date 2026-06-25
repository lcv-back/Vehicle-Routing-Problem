# Branch: feature/fix-documentation-encoding

## Mục tiêu

Branch này xử lý cải tiến: **Fix documentation encoding**.

Mục tiêu chính là sửa lỗi mã hóa tiếng Việt trong tài liệu và viết lại README
theo cấu trúc rõ ràng hơn để người đọc hiểu được dự án, dữ liệu, cách chạy và
lộ trình cải tiến tiếp theo.

## Vấn đề trước khi sửa

Một số file Markdown bị lỗi mã hóa tiếng Việt. Ví dụ các ký tự như `đ`, `ư`,
`ế`, `ộ` bị hiển thị thành các chuỗi lỗi như `Ä‘`, `Æ°`, `áº...`.

Lỗi này thường gọi là **mojibake**. Nó xảy ra khi nội dung UTF-8 bị đọc hoặc
lưu bằng sai encoding.

Các file bị ảnh hưởng:

- `README.md`
- `optimized-performance/optimize-performance.md`

## Thay đổi đã thực hiện

### README.md

README đã được viết lại bằng UTF-8 sạch và tổ chức lại theo các phần:

- Problem overview
- Dataset description
- Algorithm
- How to run
- Results
- Improvement roadmap
- Vietnamese summary

Nội dung README mới cũng mô tả rõ cách chạy local bằng:

```bash
python run_vrp.py
```

### optimized-performance/optimize-performance.md

File ghi chú tối ưu hiệu năng đã được viết lại bằng tiếng Việt rõ ràng hơn.
Nội dung mới tập trung vào:

- dùng ma trận khoảng cách đã tính sẵn;
- tối ưu khởi tạo ma trận pheromone;
- tối ưu tính tổng quãng đường;
- tối ưu cập nhật pheromone;
- cải thiện chia tuyến theo tải trọng;
- đưa tham số thuật toán vào cấu hình;
- đề xuất bước tiếp theo.

## Kết quả sau khi sửa

Tài liệu không còn các chuỗi ký tự lỗi encoding dễ thấy. README dễ đọc hơn và
có thể dùng như trang giới thiệu chính của dự án.

Đã kiểm tra lại script local:

```bash
python run_vrp.py
```

Kết quả vẫn chạy thành công với baseline hiện tại:

- số tuyến: `30`
- tổng quãng đường: `11,209.79 km`
- tổng chi phí: `80,354,377`

## Ghi chú

Branch này chỉ thay đổi tài liệu. Không thay đổi logic thuật toán hoặc dữ liệu.
