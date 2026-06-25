# Branch: feature/complete-optimized-notebook

## Mục tiêu

Branch này xử lý nhóm cải tiến tiếp theo cho notebook tối ưu:

- hoàn thiện `optimized-data-processing.ipynb`;
- dùng ma trận khoảng cách NumPy trong thuật toán;
- đưa tham số ACO vào một khu vực cấu hình;
- thêm kiểm tra tính đúng đắn của tuyến;
- thêm bảng so sánh kết quả;
- thêm phần trực quan hóa kết quả.

## Vấn đề trước khi sửa

Notebook `optimized-data-processing.ipynb` trước đó chỉ tối ưu một số hàm nhỏ
như khởi tạo pheromone hoặc tính khoảng cách, nhưng thiếu các phần downstream
quan trọng:

- chia tuyến theo tải trọng;
- tính tổng chi phí;
- chạy vòng lặp ACO đầy đủ;
- kiểm tra khách hàng đã được giao đúng một lần;
- so sánh greedy, original ACO và optimized ACO;
- biểu đồ cost/distance/convergence.

Ngoài ra, code cũ vẫn còn xu hướng tra cứu khoảng cách bằng `DataFrame` hoặc
hàm trung gian nhiều lần. Đây là điểm chậm lớn khi số khách hàng tăng.

## Thay đổi đã thực hiện

### 1. Viết lại notebook thành workflow đầy đủ

Notebook mới gồm các phần:

- Configuration
- Load dataset and build NumPy distance matrix
- Shared route utilities
- Greedy baseline
- Original-style ACO
- Optimized ACO with NumPy distance matrix
- Result comparison
- Route summary table
- Visualizations
- Notes for future route map

### 2. Dùng NumPy distance matrix

`distance-matrix.xlsx` được đọc một lần, sau đó chuyển thành:

```python
distance_matrix = distance_df.to_numpy(dtype=float)
```

Trong thuật toán tối ưu, khoảng cách được truy xuất trực tiếp bằng:

```python
distance_matrix[i, j]
```

Cách này nhanh hơn nhiều so với tra cứu `DataFrame.loc` lặp lại.

### 3. Thêm config cho ACO

Các tham số được gom vào `CONFIG`:

- `number_of_ants`
- `number_of_loops`
- `alpha`
- `beta`
- `evaporation_rate`
- `vehicle_capacity`
- `max_duration`
- `speed`
- `service_hours`
- `fixed_cost`
- `transport_cost`
- `random_seed`

Điều này giúp thử nghiệm lại dễ hơn và tránh hard-code rải rác trong notebook.

### 4. Thêm validation

Notebook mới kiểm tra:

- mỗi khách hàng được ghé đúng một lần;
- không có khách hàng bị thiếu;
- không có khách hàng bị lặp;
- mỗi route bắt đầu và kết thúc tại depot `Kho`;
- không route nào vượt tải trọng xe;
- không route nào vượt thời gian tối đa.

### 5. Thêm so sánh kết quả

Notebook tạo bảng `comparison_df` gồm:

- tổng quãng đường;
- tổng chi phí;
- số route/vehicle;
- runtime;
- phần trăm cải thiện so với greedy baseline.

Kết quả kiểm tra hiện tại:

| Method | Total distance | Total cost | Routes | Runtime | Improvement |
| --- | ---: | ---: | ---: | ---: | ---: |
| greedy_baseline | 11,209.79 | 80,354,376.68 | 30 | 0.0016s | 0.00% |
| original_style_aco | 9,775.28 | 71,910,557.76 | 28 | 81.44s | 10.51% |
| optimized_aco | 9,712.64 | 71,629,178.88 | 28 | 3.31s | 10.86% |

### 6. Thêm visualizations

Notebook có cell vẽ:

- cost per loop;
- distance per loop;
- convergence chart;
- route distance by route.

Nếu môi trường chưa cài `matplotlib`, notebook sẽ in hướng dẫn:

```bash
pip install -r requirements.txt
```

## Kết quả sau khi sửa

Notebook đã chạy end-to-end thành công trong phần thuật toán và validation.

Trong môi trường hiện tại, `matplotlib` chưa được cài nên phần biểu đồ không
render trực tiếp, nhưng cell visualization đã có fallback rõ ràng và sẽ chạy
khi dependencies được cài bằng `requirements.txt`.

## Ghi chú

Branch này tập trung vào notebook tối ưu. Chưa thêm route map vì dữ liệu hiện
tại trong `Coordinates Valid` là địa chỉ text, chưa phải tọa độ latitude /
longitude ổn định.
