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

#### **Phân tích**

- **Tăng tốc độ:** Bằng cách tính toán ma trận khoảng cách trước, chúng ta tránh tính toán lại các khoảng cách giống nhau nhiều lần.
- **Giảm độ phức tạp tính toán:** Sử dụng ma trận thay vì gọi hàm nhiều lần.
- **Cải thiện khả năng mở rộng:** Nếu số lượng điểm trong road lớn, việc tính toán khoảng cách trước và lưu trữ sẽ giúp giảm đáng kể thời gian xử lý.

#### **1.3. Tối ưu hàm cập nhật mùi (notTraveled)**

#### **Ban đầu**

```python
    def notTraveled(odorPrevious):
        evap_coef = 0.1
        return (1 - evap_coef) * odorPrevious
```

#### **Phân tích**

- Khởi tạo biến evap_coef liên tục làm chậm bài toán

```python
    def notTravaled(odor_matrix, evap_coef=0.1):
        return odor_matrix * (1 - evap_coef)
```

#### **Cải tiến**

- Áp dụng cập nhật mùi trên toàn bộ ma trận mùi cùng lúc.

#### **1.4. Tối ưu hàm tính ma trận mùi sau khi cập nhật (determineAddEdges):**

```python
    def determineAddEdges(roadSavedNodes):
        listDeterminedAddEdges = []
        for i in range(len(roadSavedNodes) - 1):
            pair = [roadSavedNodes[i], roadSavedNodes[i+1]]
            listDeterminedAddEdges.append(pair)
            pair = [roadSavedNodes[i+1], roadSavedNodes[i]]
            listDeterminedAddEdges.append(pair)
        return listDeterminedAddEdges
```

#### **Phân tích**

- Dài dòng và không tối ưu bằng Numpy khi dùng for bình thường

```python
    def optimized_determineAddEdges(roadSavedNodes):
        """
        Tạo danh sách các cạnh cần cập nhật mùi bằng NumPy.
        """
        # Chuyển danh sách thành mảng NumPy
        road_array = np.array(roadSavedNodes)

        # Lấy các cặp cạnh
        edges = np.column_stack((road_array[:-1], road_array[1:]))

        # Thêm cạnh quay lại điểm đầu
        reverse_edges = edges[:, ::-1]

        return np.vstack((edges, reverse_edges))
```

#### **Cải tiến**

- Dùng Numpy tối ưu hóa khi liên quan đến vector

#### **1.5.Tối ưu hóa hàm cắt mảng split_array**

```python
    def split_array(arr, max_sum):
        result = []  # Danh sách chứa các mảng con
        current_subarray = []  # Mảng con hiện tại
        current_sum = 0  # Tổng hiện tại của mảng con

        for num in arr[1:]:
            if current_sum + capacitylist[num] <= max_sum:
                current_subarray.append(num)
                current_sum += capacitylist[num]
            else:
                result.append(current_subarray)
                current_subarray = [num]
                current_sum = capacitylist[num]

        # Thêm mảng con cuối cùng vào kết quả
        if current_subarray:
            result.append(current_subarray)
        return result
```

#### **Phân tích**

- Thiếu kiểm tra tính hợp lệ của phần tử đầu tiên
- Có thể dùng numpy giúp nhanh hơn

```python
    def split_array(arr, max_sum, capacitylist):
        result = []
        current_subarray = []
        current_sum = 0

        # Kiểm tra tính hợp lệ của phần tử đầu tiên
        if capacitylist[arr[0]] > max_sum:
            return []  # Không thể tạo mảng con nếu phần tử đầu tiên đã vượt quá max_sum

        for num in arr:
            # Sử dụng NumPy cho phép tính toán nhanh hơn
            if current_sum + capacitylist[num] <= max_sum:
                current_subarray.append(num)
                current_sum += capacitylist[num]
            else:
                result.append(current_subarray)
                current_subarray = [num]
                current_sum = capacitylist[num]

        # Thêm mảng con cuối cùng vào kết quả
        if current_subarray:
            result.append(current_subarray)

        return result
```

#### **Cải tiến**

- **Tính hợp lệ cao hơn:** Kiểm tra tính hợp lệ của các chỉ số trước khi truy cập vào capacitylist.
- **Tăng tốc độ:** Sử dụng NumPy để xử lý mảng, giúp cải thiện hiệu suất khi làm việc với dữ liệu lớn.

#### **1.6.Cải tiến hàm tổng chi phí và tổng quảng đường**

```python
    def Total_Cost_and_totaldistance(FixCost, routeofant, TranCost):
        num = len(routeofant)
        totalcosteachroute = {}
        total = 0
        total_dis = 0
        for j in range(num):

        finalTotal = 0
        finalTotalPart2 = totalDistanceVisited(routeofant[j])
        finalTotal = finalTotalPart2

        value1 = df['Coordinates Valid'][routeofant[j][0]]
        dist = calcDistAuto(centerPlace, value1)
        finalTotal += dist

        value2 = df['Coordinates Valid'][routeofant[j][-1]]
        finalTotal += calcDistAuto(value2, centerPlace)

        totalcosteachroute[f"Truck {j+1}"] = FixCost + finalTotal*TranCost

        total_dis += finalTotal
        total += totalcosteachroute[f"Truck {j+1}"]

        print(totalcosteachroute)

        return round(total,0), total_dis
```

#### **Phân tích**

- Tính toán tổng chi phí và tổng quãng đường **trong cùng một vòng lặp**, giảm độ phức tạp.
- Sử dụng **NumPy** cho phép tính toán nhanh hơn nếu dữ liệu lớn.

```python
    def Total_Cost_and_totaldistance(FixCost, routeofant, TranCost, centerPlace, df):
        num = len(routeofant)
        totalcosteachroute = {}
        total = 0
        total_dis = 0

        # Tính toán khoảng cách từ centerPlace ra tất cả các tọa độ trước và sau một lần để tránh tính lại nhiều lần
        coordinates_valid = df['Coordinates Valid'].values  # Lấy toàn bộ tọa độ một lần

        for j in range(num):
            finalTotal = 0

            # Tính tổng khoảng cách của chuyến đi
            finalTotalPart2 = totalDistanceVisited(routeofant[j])  # Tổng quãng đường cho route
            finalTotal += finalTotalPart2

            # Tính khoảng cách từ centerPlace tới điểm đầu và điểm cuối
            value1 = coordinates_valid[routeofant[j][0]]  # Điểm đầu tiên của route
            dist = calcDistAuto(centerPlace, value1)
            finalTotal += dist

            value2 = coordinates_valid[routeofant[j][-1]]  # Điểm cuối cùng của route
            finalTotal += calcDistAuto(value2, centerPlace)

            # Tính chi phí của chuyến đi
            totalcosteachroute[f"Truck {j+1}"] = FixCost + finalTotal * TranCost

            # Cộng dồn tổng chi phí và tổng quãng đường
            total_dis += finalTotal
            total += totalcosteachroute[f"Truck {j+1}"]

        print(totalcosteachroute)
        return round(total, 0), total_dis
```

#### **Cải tiến**

- **Các phép tính khoảng cách giữa centerPlace và các điểm đã được tính toán một lần**, giúp giảm số lần tính toán và tăng tốc độ.
- **Truy cập vào df['Coordinates Valid'] chỉ một lần** thay vì trong mỗi vòng lặp.
- **Cải tiến cấu trúc mã giúp giảm độ phức tạp** vòng lặp và tăng tính mở rộng.
- **Mã được tối ưu với NumPy** và việc tái sử dụng các phép toán, làm cho hàm xử lý nhanh hơn khi dữ liệu lớn.
