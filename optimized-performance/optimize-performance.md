# Optimize performance algorithms

## I. Phân tích bài toán

Gồm các phần chính như sau:

- **Cập nhật mùi (pheromone)** trong ma trận mùi theo thuật toán tối ưu đàn kiến (ACO)
- **Tính toán chi phí và quãng đường tổng hợp** cho các xe tải phục vụ vận chuyển
- **Chia các lộ trình vận chuyển theo giới hạn năng lực và dung tích** của từng xe
- **Trực quan hóa chi phí qua số vòng lặp** bằng biểu đồ

## II. Tối ưu hóa hệ thống

### 1. Tối ưu hiệu suất xử lý dữ liệu

- Cải thiện các vòng lặp, đặc biệt với các thao tác tính toán trên ma trận và danh sách lớn.
- Thay thế các thao tác thủ công bằng các hàm vector hóa của **NumPy hoặc Pandas.**

#### 1.1. Tối ưu hóa hàm khởi tạo ma trận mùi (defaultOdorMatrix)

- Bằng cách sử dụng thư viện **NumPy** để tăng tốc độ xử lý
- **Tăng tốc độ:** Thay vì sử dụng vòng lặp lồng nhau, NumPy giúp xử lý toàn bộ ma trận chỉ trong một vài dòng lệnh.
- **Giảm bộ nhớ:** NumPy sử dụng cấu trúc dữ liệu nhẹ hơn, phù hợp hơn khi làm việc với ma trận lớn.

#### Ban đầu

```python
    def defaultOdorMatrix(x, n):
        # Khởi tạo ma trận nxn toàn số 0
        data = [[0 for _ in range(n)] for _ in range(n)]
        odorMatrix = pd.DataFrame(data)
        for row in range(n):
            for column in range(n):
                if row != column:
                    odorMatrix.iloc[row, column] = x
        return odorMatrix
```

#### **Phân tích hiệu năng**

- Sử dụng vòng lặp lồng nhau có độ phức tạp 𝑂($n^2$) không tối ưu khi 𝑛 lớn.
- Thời gian thực thi lâu và tiêu tốn nhiều tài nguyên.

#### Cải tiến dùng Numpy

```python
    def defaultOdorMatrix(x, n):
        """
        Khởi tạo ma trận mùi với NumPy.
        """
        # Tạo một ma trận nxn toàn số `x`
        odorMatrix = np.full((n, n), x)

        # Đặt đường chéo chính thành 0
        np.fill_diagonal(odorMatrix, 0)

        # Chuyển đổi sang DataFrame (nếu cần)
        return pd.DataFrame(odorMatrix)
```

#### **Phân tích hiệu năng**

- Nhanh hơn: NumPy tối ưu các thao tác ma trận, giúp cải thiện tốc độ xử lý đáng kể.
- Đơn giản hơn: Ít dòng lệnh và không cần vòng lặp phức tạp.
- Tiết kiệm tài nguyên: NumPy được thiết kế để sử dụng hiệu quả bộ nhớ và CPU.

#### **1.2. Tối ưu hàm tính tổng quãng đường (totalDistanceVisited)**

- **Giảm thiểu vòng lặp:** Thay thế các vòng lặp bằng các phép tính vector hóa trong NumPy.
- **Sử dụng các phương pháp NumPy** để tính toán nhanh hơn.

#### **Ban đầu**

```python
    def totalDistanceVisited(road):
        total = 0
        i = 0
        for i in range(len(road)-1):
            placeI = listCustomerAddress[road[i]]
            placeII = listCustomerAddress[road[i+1]]
            distance = calcDistAuto(placeI, placeII)
            total += distance
        return round(total,2)
```

#### **Phân tích hiệu năng**

- **Tính toán lại khoảng cách giữa các điểm nhiều lần:** Hàm gọi calcDistAuto trong mỗi vòng lặp để tính toán khoảng cách giữa các điểm.
- **Hiệu suất thấp với dữ liệu lớn:** Nếu road có nhiều điểm và calcDistAuto tốn thời gian tính toán, hiệu suất sẽ giảm đáng kể khi số lượng điểm tăng.
- **Không tối ưu khi lặp qua nhiều điểm:** Việc duyệt qua tất cả các điểm trong road mà không tối ưu có thể gây ra chi phí tính toán và truy xuất dữ liệu không cần thiết.

#### **Cải tiến**

```python
    def totalDistanceVisited(road, distance_matrix):
        """
        Tính tổng quãng đường đã đi qua sử dụng ma trận khoảng cách.
        road: danh sách các điểm đi qua.
        distance_matrix: ma trận khoảng cách giữa các điểm.
        """
        # Lấy chỉ số các cặp (road[i], road[i+1])
        indices = zip(road[:-1], road[1:])

        # Sử dụng NumPy để tính tổng khoảng cách
        total_distance = sum(distance_matrix[i, j] for i, j in indices)

        # Thêm quãng đường quay lại điểm bắt đầu
        total_distance += distance_matrix[road[-1], road[0]]

        return round(total_distance, 2)
```
