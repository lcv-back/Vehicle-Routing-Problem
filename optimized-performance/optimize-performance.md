# Tối ưu hiệu năng thuật toán

Tài liệu này ghi lại các hướng cải tiến hiệu năng cho bài toán Vehicle Routing
Problem (VRP) sử dụng Ant Colony Optimization (ACO). Nội dung cũ bị lỗi mã hóa
tiếng Việt, nên tài liệu đã được viết lại bằng UTF-8 sạch.

## 1. Phân tích bài toán

Các phần xử lý chính trong chương trình gồm:

- khởi tạo và cập nhật ma trận pheromone;
- tính tổng quãng đường của từng tuyến;
- kiểm tra ràng buộc tải trọng xe;
- kiểm tra ràng buộc thời gian giao hàng;
- chia khách hàng thành các tuyến xe;
- tính tổng chi phí vận chuyển;
- trực quan hóa chi phí và quãng đường theo từng vòng lặp.

Các điểm dễ gây chậm là vòng lặp lồng nhau, truy xuất `DataFrame` nhiều lần, và
tính lại khoảng cách giữa cùng một cặp điểm.

## 2. Dùng ma trận khoảng cách đã tính sẵn

Trong notebook gốc, nhiều hàm gọi lại logic tra cứu khoảng cách như
`calcDistAuto`. Cách này dễ chậm khi số khách hàng tăng.

Nên chuyển `distance-matrix.xlsx` thành một ma trận số ngay từ đầu:

```python
distance_matrix = df_distance.set_index("TÊN KHÁCH HÀNG").astype(float)
```

Sau đó truy xuất khoảng cách bằng chỉ số:

```python
distance = distance_matrix.loc[from_customer, to_customer]
```

Lợi ích:

- tránh tính hoặc tra cứu lặp lại;
- giúp hàm tính tổng quãng đường ngắn gọn hơn;
- dễ kiểm tra dữ liệu đầu vào;
- thuận tiện để tối ưu bằng NumPy về sau.

## 3. Tối ưu khởi tạo ma trận pheromone

Phiên bản dùng vòng lặp:

```python
def default_odor_matrix(value, n):
    data = [[0 for _ in range(n)] for _ in range(n)]
    odor_matrix = pd.DataFrame(data)
    for row in range(n):
        for column in range(n):
            if row != column:
                odor_matrix.iloc[row, column] = value
    return odor_matrix
```

Phiên bản nên dùng:

```python
def default_odor_matrix(value, n):
    odor_matrix = np.full((n, n), value)
    np.fill_diagonal(odor_matrix, 0)
    return pd.DataFrame(odor_matrix)
```

Lợi ích:

- ít dòng code hơn;
- giảm vòng lặp Python;
- tận dụng xử lý vector hóa của NumPy.

## 4. Tối ưu tính tổng quãng đường

Phiên bản nên dùng ma trận khoảng cách:

```python
def total_distance(route, distance_matrix):
    distance = 0
    for current_node, next_node in zip(route[:-1], route[1:]):
        distance += distance_matrix.loc[current_node, next_node]
    return round(distance, 2)
```

Nếu tuyến cần quay về kho, nên cộng rõ ràng đoạn từ khách cuối về `Kho`:

```python
distance += distance_matrix.loc[route[-1], "Kho"]
```

Điểm quan trọng là phải thống nhất một quy ước:

- route có bao gồm kho ở đầu/cuối hay không;
- tổng quãng đường có cộng chiều về kho hay không.

## 5. Tối ưu cập nhật pheromone

Hàm bay hơi pheromone có thể viết ngắn gọn:

```python
def evaporate_pheromone(odor_matrix, evaporation_rate=0.1):
    return odor_matrix * (1 - evaporation_rate)
```

Nên truyền `evaporation_rate` từ cấu hình thay vì hard-code trong thân hàm.
Điều này giúp dễ thử nghiệm nhiều bộ tham số khác nhau.

## 6. Tối ưu tạo danh sách cạnh cần cập nhật

Thay vì tạo từng cặp cạnh bằng nhiều thao tác thủ công, có thể dùng NumPy:

```python
def determine_add_edges(route):
    route_array = np.array(route)
    edges = np.column_stack((route_array[:-1], route_array[1:]))
    reverse_edges = edges[:, ::-1]
    return np.vstack((edges, reverse_edges))
```

Cách này phù hợp khi cần cập nhật pheromone cho cả hai chiều của tuyến.

## 7. Cải thiện chia tuyến theo tải trọng

Hàm chia tuyến nên kiểm tra dữ liệu trước khi xử lý:

```python
def split_by_capacity(route, max_capacity, demand_by_node):
    routes = []
    current_route = []
    current_load = 0

    for node in route:
        demand = demand_by_node[node]
        if demand > max_capacity:
            raise ValueError(f"Customer {node} exceeds vehicle capacity")

        if current_load + demand <= max_capacity:
            current_route.append(node)
            current_load += demand
        else:
            routes.append(current_route)
            current_route = [node]
            current_load = demand

    if current_route:
        routes.append(current_route)

    return routes
```

Lợi ích:

- phát hiện khách hàng vượt tải trọng ngay từ đầu;
- tránh sinh tuyến không hợp lệ;
- dễ viết kiểm thử tự động.

## 8. Cấu hình tham số thuật toán

Các giá trị sau nên được đưa vào cấu hình hoặc CLI arguments:

- số vòng lặp;
- số lượng ant;
- `alpha`;
- `beta`;
- tỷ lệ bay hơi pheromone;
- tải trọng xe;
- thời gian tối đa;
- tốc độ xe;
- chi phí cố định;
- chi phí vận chuyển trên mỗi km.

Điều này giúp tái lập kết quả và so sánh nhiều kịch bản tối ưu.

## 9. Đề xuất bước tiếp theo

1. Tách code ACO từ notebook sang module Python.
2. Dùng `distance-matrix.xlsx` làm nguồn khoảng cách duy nhất.
3. Thêm kiểm tra mỗi khách hàng được ghé đúng một lần.
4. Thêm kiểm tra tải trọng và thời gian cho từng tuyến.
5. So sánh kết quả giữa greedy, nearest-neighbor baseline và ACO.
6. Ghi kết quả ra CSV hoặc Excel.
7. Thêm biểu đồ hội tụ chi phí theo vòng lặp.
