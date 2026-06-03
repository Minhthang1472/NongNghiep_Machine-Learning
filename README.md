# 🍊 HỆ THỐNG PHÂN LOẠI TRÁI CÂY ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI)

> **Mô hình học máy Deep Learning (MobileNetV2)** kết hợp giao diện đồ họa **PySide6** để nhận diện và kiểm định chất lượng tự động cho Nông nghiệp.

---

## 🌟 TỔNG QUAN HỆ THỐNG
Hệ thống này được thiết kế để tự động hóa quy trình kiểm định chất lượng (QA) nông sản. Cốt lõi của hệ thống là mô hình học sâu (Deep Learning) sử dụng kiến trúc **MobileNetV2** do Google phát triển, đã được huấn luyện với hơn **13.500 bức ảnh** để nhận diện và phân tích chính xác trạng thái của trái cây.

### 🎯 Tính năng nổi bật:
- **Nhận diện Đa lớp (21 Classes):** Nhận diện 7 loại trái cây bao gồm: **Táo, Chuối, Nho, Cam, Ổi, Lựu, Dâu Tây**.
- **Đánh giá Trạng thái (Ripeness):** Phân tích chính xác 3 trạng thái sinh học: **Chín, Xanh, Hư hỏng**.
- **QA Tự động (Auto QA):** Đưa ra kết luận ngay lập tức và đề xuất cách xử lý cho từng trạng thái quả (Ví dụ: "Chuối còn xanh, cần ủ thêm 2-3 ngày").
- **Giao diện Modern UI:** Giao diện Desktop Đen-Cam mang phong cách Sci-Fi/Industrial cực kỳ trực quan.
- **Độ chính xác (Accuracy):** Đạt ngưỡng **~95%** trong môi trường giả định.

---

## ⚙️ CÔNG NGHỆ SỬ DỤNG
- **Ngôn ngữ:** Python 3.11+
- **Lõi Trí tuệ Nhân tạo:** TensorFlow & Keras
- **Giao diện đồ họa (GUI):** PySide6 (Qt for Python)
- **Xử lý Ma trận/Hình ảnh:** Numpy, Pillow (PIL)

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### Bước 1: Chuẩn bị môi trường
Yêu cầu máy tính phải cài đặt sẵn **Python 3.10** hoặc **3.11**. Mở Terminal (Command Prompt / PowerShell) và chạy lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
*(Nếu chưa có file requirements.txt, hãy tự chạy `pip install tensorflow numpy pillow PySide6`)*

### Bước 2: Chạy ứng dụng Giao diện (App Desktop)
Sau khi cài đặt xong thư viện, bạn chạy lệnh sau để khởi động phần mềm:
```bash
python app.py
```
1. Giao diện phần mềm `FRUIT_SCANNER_V1.0` sẽ hiện lên.
2. Bấm vào nút **⇧ UPLOAD_IMAGE** màu cam ở góc trái.
3. Chọn một bức ảnh trái cây (Táo, Cam, Chuối...) từ máy tính của bạn.
4. Chờ 1 giây để hệ thống phân tích. Kết quả QA sẽ hiện ở bảng bên phải.

### Bước 3: Chạy ứng dụng bằng Dòng lệnh (Terminal)
Nếu bạn không muốn dùng giao diện, bạn có thể kiểm tra ảnh nhanh bằng file `predict.py`:
```bash
python predict.py <đường_dẫn_tới_ảnh>
# Ví dụ: python predict.py trai_oi.jpg
```

---

## 🧠 HƯỚNG DẪN HUẤN LUYỆN LẠI (TRAINING)
Nếu bạn muốn bổ sung thêm trái cây mới vào bộ não AI, hãy thực hiện các bước sau:
1. Chuẩn bị ảnh và bỏ vào trong thư mục `dataset/train/` theo định dạng tên nhãn (ví dụ: `dataset/train/Xoai_Chin`, `dataset/train/Xoai_Xanh`).
2. Chạy lệnh:
```bash
python train.py
```
3. Sau khi chạy xong, hệ thống sẽ xuất ra 2 file mới là `fruit_model.h5` và `labels.txt`. Mặc định phần mềm sẽ tự động cập nhật và sử dụng mô hình mới này.

---
**Bản quyền © 2026 - Dự án Machine Learning Nông Nghiệp.**
