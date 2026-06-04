# 🍊 HỆ THỐNG PHÂN LOẠI TRÁI CÂY TỰ ĐỘNG (AI & EXPERT SYSTEM)

> **Mô hình học máy Deep Learning (MobileNetV2)** kết hợp giao diện đồ họa **PySide6** và công nghệ xử lý ảnh **OpenCV**. Hỗ trợ nhận diện tự động qua Ảnh và Camera thời gian thực, tích hợp Hệ chuyên gia phân tích và tư vấn hành động trong dây chuyền Nông nghiệp.

---

## 🌟 TỔNG QUAN HỆ THỐNG
Hệ thống được thiết kế để tự động hóa hoàn toàn quy trình kiểm định chất lượng (QA) nông sản trong nhà máy.

### 🎯 Tính năng nổi bật 
- **📷 Live Camera & OpenCV:** Hỗ trợ phân tích độ chín trực tiếp qua Camera (Webcam) liên tục theo thời gian thực (Real-time).
- **🎯 Khung Ngắm AI Thông Minh (Target Box):** Hệ thống tự động tạo khung ngắm (Bounding box) tập trung phân tích vùng chứa trái cây, tự động loại bỏ rác/ngoại cảnh xung quanh giúp AI phân tích cực kỳ chính xác.
- **🧠 Hệ Chuyên Gia Tư Vấn (Expert System):** Không chỉ báo "Chín/Xanh", hệ thống tự động sinh ra Báo cáo chi tiết về đặc tính sinh học của quả và đưa ra **Đề xuất Hành động** cho công nhân (Ví dụ: "Cách ly quả hỏng tránh lây nấm mốc", "Ủ túi giấy 2 ngày để kích chín").
- **📊 Lịch Sử Kiểm Định (Logs & Chart):** Tự động lưu lịch sử vào Database (CSV). Cung cấp màn hình hiển thị Bảng lịch sử và **Biểu đồ Thống kê (Donut Chart)** tự động vẽ.
- **📥 Xuất Báo Cáo:** Hỗ trợ xuất dữ liệu ra file Excel/CSV phục vụ báo cáo.
- **🇻🇳 Giao Diện 100% Tiếng Việt:** Ngôn ngữ kỹ thuật chuẩn công nghiệp, thiết kế Dark/Orange Mode sang trọng.

---

## ⚙️ CÔNG NGHỆ SỬ DỤNG
- **Ngôn ngữ:** Python 3.11+
- **Lõi Trí tuệ Nhân tạo:** TensorFlow & Keras (MobileNetV2)
- **Thị giác Máy tính (Computer Vision):** OpenCV (`cv2`)
- **Giao diện đồ họa (GUI):** PySide6 (Qt for Python)
- **Xử lý Ma trận/Hình ảnh:** Numpy, Pillow (PIL)

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### Bước 1: Chuẩn bị môi trường
Yêu cầu cài đặt **Python 3.11**. Mở Terminal chạy lệnh cài đặt thư viện:
```bash
pip install tensorflow numpy pillow PySide6 opencv-python
```

### Bước 2: Chạy ứng dụng Giao diện (App Desktop)
Khởi động phần mềm:
```bash
python app.py
```
1. Giao diện **FRUIT SCANNER AI** sẽ hiện lên.
2. Bạn có thể chọn 1 trong 2 chế độ quét:
   - **⇧ TẢI ẢNH LÊN:** Chọn 1 file ảnh có sẵn trên máy để kiểm định.
   - **📷 BẬT CAMERA:** Đưa trái cây ra trước Webcam để máy tự động quét liên tục. *(Lưu ý: Không đưa mặt người vào)*
3. Kết quả, Biểu đồ %, và Báo cáo Đề xuất sẽ hiển thị ở bảng bên phải.
4. Bấm nút **📜 LỊCH SỬ KIỂM ĐỊNH (LOGS)** để xem biểu đồ tổng hợp và bấm **XUẤT EXCEL/CSV** để lấy báo cáo.

### Bước 3: Chạy ứng dụng bằng Dòng lệnh (Terminal)
Nếu bạn chỉ muốn kiểm tra nhanh qua màn hình đen:
```bash
python predict.py <đường_dẫn_tới_ảnh>
# Ví dụ: python predict.py trai_cam.jpg
```

---

## 🧠 HƯỚNG DẪN HUẤN LUYỆN LẠI (TRAINING)
Nếu muốn bổ sung trái cây mới:
1. Chuẩn bị ảnh bỏ vào `dataset/train/<Tên_Nhãn>`
2. Chạy lệnh: `python train.py`
3. Hệ thống sẽ sinh ra `fruit_model.h5` và `labels.txt` mới để tự động cập nhật AI.

---
**Bản quyền © 2026 - Dự án Machine Learning Nông Nghiệp.**
