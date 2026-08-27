# 🚀 HuyOJ Mini - Hệ Thống Chấm Bài C++ Trực Tuyến

Hệ thống quản lý và chấm bài tập lập trình trực tuyến tối giản, hỗ trợ đa ngôn ngữ gồm **C++** . Dự án được xây dựng bằng Python với framework Flask, giao diện thân thiện và dễ dàng triển khai.

---

## 📋 Tính năng chính
* **Hỗ trợ đa ngôn ngữ:** Cho phép nộp và chấm tự động mã nguồn C++.
* **Hệ thống chấm tự động:** Kiểm tra kết quả trực tiếp với các bộ test mẫu (Sample Test) và trả về trạng thái chuẩn xác như *Accepted (AC)*, *Wrong Answer (WA)*, *Compilation Error*...

---

## 📥 Hướng dẫn cách tải về và cài đặt

Thực hiện theo các bước sau để chạy hệ thống trên máy tính của bạn:

### 1. Clone repository hoặc tải về 
git clone https://github.com/lamhuyn62-lgtm/HUYOJ-MINI-C-.git
### 2. Thiết lập môi trường ảo Python (Khuyên dùng)
Tạo và kích hoạt môi trường ảo để quản lý thư viện gọn gàng:
### Trên macOS / Linux:
python3 -m venv venv
source venv/bin/activate
# Trên Windows:
python -m venv venv
venv\Scripts\activate
### 3. Cài đặt các thư viện phụ thuộc
# Hệ thống sử dụng Flask làm nền tảng web backend. Cài đặt Flask bằng lệnh:
pip install Flask
### Khởi động
python app.py

Sau khi máy chủ khởi động thành công, hãy mở trình duyệt web của bạn và truy cập vào đường dẫn:
👉 http://127.0.0.1:5000
