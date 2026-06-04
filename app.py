import sys
import os
import csv
import shutil
from datetime import datetime
import numpy as np
import tensorflow as tf
from keras.preprocessing import image
import cv2
from PIL import Image
import io

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                               QFrame, QProgressBar, QGridLayout, QGraphicsDropShadowEffect,
                               QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QTimer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
IMG_SIZE = (224, 224)

QSS = """
QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #050505); }
QLabel { color: #E0E0E0; font-family: 'Segoe UI', Arial, sans-serif; }
QLabel#TitleLabel { color: #FF9800; font-size: 26px; font-weight: 900; letter-spacing: 3px; margin-bottom: 10px; }
QLabel#SectionTitle { color: #FFFFFF; font-size: 14px; font-weight: bold; letter-spacing: 2px; }
QLabel#DataLabel { color: #777777; font-size: 12px; font-weight: bold; letter-spacing: 1px; }
QLabel#DataValue { color: #FF9800; font-size: 18px; font-weight: bold; }
QLabel#StatusValue { font-size: 16px; font-weight: bold; }
QLabel#PctLabel { font-size: 13px; font-weight: bold; padding: 5px; background-color: #222; border-radius: 4px; }

QPushButton#UploadBtn { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F57C00, stop:1 #FF9800); color: #000000; font-weight: 900; font-size: 13px; border: none; border-radius: 8px; padding: 15px; letter-spacing: 1px; }
QPushButton#UploadBtn:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFB74D, stop:1 #FFA726); }
QPushButton#UploadBtn:pressed { background-color: #E65100; }

QPushButton#CameraBtn { background-color: #2196F3; color: #FFFFFF; font-weight: 900; font-size: 13px; border: none; border-radius: 8px; padding: 15px; letter-spacing: 1px; }
QPushButton#CameraBtn:hover { background-color: #42A5F5; }
QPushButton#CameraBtn:pressed { background-color: #1976D2; }
QPushButton#CameraBtn[is_active="true"] { background-color: #F44336; }
QPushButton#CameraBtn[is_active="true"]:hover { background-color: #EF5350; }

QPushButton#LogBtn { background-color: #2A2A2A; color: #AAAAAA; font-weight: 900; font-size: 13px; border: 1px solid #444; border-radius: 8px; padding: 15px; letter-spacing: 1px; }
QPushButton#LogBtn:hover { background-color: #333333; color: #FFFFFF; }
QPushButton#ExportBtn { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 6px; }
QPushButton#ExportBtn:hover { background-color: #45a049; }

QProgressBar { background-color: #252525; border: none; border-radius: 4px; height: 8px; text-align: right; color: transparent; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F57C00, stop:1 #FFCA28); border-radius: 4px; }
QFrame#AnalysisFrame, QFrame#ImageFrame { background-color: #141414; border-radius: 12px; border: 1px solid #282828; }
"""

class ChartLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.stats = {"Chín": 0, "Xanh": 0, "Hỏng": 0}
        self.setFixedSize(160, 160)
        
    def update_stats(self, chin, xanh, hong):
        self.stats = {"Chín": chin, "Xanh": xanh, "Hỏng": hong}
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = sum(self.stats.values())
        if total == 0:
            painter.setPen(QColor("#777"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Chưa có dữ liệu")
            return
            
        rect = self.rect().adjusted(10, 10, -10, -10)
        start_angle = 0
        colors = {"Chín": QColor("#34C759"), "Xanh": QColor("#FFCC00"), "Hỏng": QColor("#FF3B30")}
        
        for key, value in self.stats.items():
            if value == 0: continue
            span_angle = int((value / total) * 360 * 16)
            painter.setBrush(colors[key])
            painter.setPen(Qt.NoPen)
            painter.drawPie(rect, start_angle, span_angle)
            start_angle += span_angle
            
        painter.setBrush(QColor("#121212"))
        painter.drawEllipse(rect.adjusted(30, 30, -30, -30))

class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LỊCH SỬ KIỂM ĐỊNH")
        self.setGeometry(200, 200, 850, 500)
        self.setStyleSheet("""
            QDialog { background-color: #121212; }
            QTableWidget { background-color: #1A1A1A; color: #E0E0E0; gridline-color: #333333; border: 1px solid #333333; font-size: 13px; }
            QHeaderView::section { background-color: #2C2C2C; color: #FF9800; padding: 8px; font-weight: bold; border: 1px solid #333333; }
        """)
        layout = QHBoxLayout(self)
        
        left_layout = QVBoxLayout()
        lbl_title = QLabel("📜 DANH SÁCH QUÉT")
        lbl_title.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(lbl_title)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["THỜI GIAN", "TÊN FILE", "ĐỐI TƯỢNG", "TRẠNG THÁI", "ĐỘ TIN CẬY"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self.table)
        
        right_layout = QVBoxLayout()
        lbl_stat = QLabel("📊 THỐNG KÊ")
        lbl_stat.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold;")
        lbl_stat.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(lbl_stat)
        
        self.chart = ChartLabel()
        right_layout.addWidget(self.chart, alignment=Qt.AlignCenter)
        
        self.lbl_chin = QLabel("● Chín đạt chuẩn: 0")
        self.lbl_chin.setStyleSheet("color: #34C759; font-weight: bold; font-size: 14px;")
        self.lbl_xanh = QLabel("● Quả xanh: 0")
        self.lbl_xanh.setStyleSheet("color: #FFCC00; font-weight: bold; font-size: 14px;")
        self.lbl_hong = QLabel("● Hư hỏng: 0")
        self.lbl_hong.setStyleSheet("color: #FF3B30; font-weight: bold; font-size: 14px;")
        
        right_layout.addWidget(self.lbl_chin)
        right_layout.addWidget(self.lbl_xanh)
        right_layout.addWidget(self.lbl_hong)
        right_layout.addStretch()
        
        btn_export = QPushButton("📥 XUẤT EXCEL/CSV")
        btn_export.setObjectName("ExportBtn")
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.clicked.connect(self.export_csv)
        right_layout.addWidget(btn_export)
        
        layout.addLayout(left_layout, stretch=3)
        layout.addLayout(right_layout, stretch=1)
        
        self.load_logs()
        
    def load_logs(self):
        if not os.path.exists("scan_logs.csv"): return
        chin_count, xanh_count, hong_count = 0, 0, 0
        with open("scan_logs.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            rows = list(reader)
            rows.reverse()
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, data in enumerate(row_data):
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter)
                    if col == 3:
                        if "Chín" in data or "RIPE" in data:
                            item.setForeground(QColor("#34C759"))
                            chin_count += 1
                        elif "Xanh" in data or "UNRIPE" in data:
                            item.setForeground(QColor("#FFCC00"))
                            xanh_count += 1
                        elif "hỏng" in data or "ROTTEN" in data:
                            item.setForeground(QColor("#FF3B30"))
                            hong_count += 1
                    self.table.setItem(row, col, item)
        self.chart.update_stats(chin_count, xanh_count, hong_count)
        self.lbl_chin.setText(f"● Chín đạt chuẩn: {chin_count}")
        self.lbl_xanh.setText(f"● Quả xanh: {xanh_count}")
        self.lbl_hong.setText(f"● Hư hỏng: {hong_count}")

    def export_csv(self):
        if not os.path.exists("scan_logs.csv"):
            QMessageBox.warning(self, "Trống", "Chưa có dữ liệu để xuất!")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo", "BaoCao_KiemDinh_TraiCay.csv", "CSV Files (*.csv)")
        if save_path:
            shutil.copy("scan_logs.csv", save_path)
            QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo tại:\n{save_path}")

class RoundedImageLabel(QLabel):
    def __init__(self, parent=None, radius=12):
        super().__init__(parent)
        self.radius = radius
        self.pixmap_val = None
        self.setAlignment(Qt.AlignCenter)

    def setPixmap(self, pixmap):
        self.pixmap_val = pixmap
        self.update()

    def paintEvent(self, event):
        if not self.pixmap_val:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        painter.setClipPath(path)
        x = (self.width() - self.pixmap_val.width()) // 2
        y = (self.height() - self.pixmap_val.height()) // 2
        painter.drawPixmap(x, y, self.pixmap_val)

def create_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setColor(QColor(0, 0, 0, 150))
    shadow.setOffset(0, 5)
    return shadow

class FruitScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PHẦN MỀM KIỂM ĐỊNH TRÁI CÂY")
        self.setGeometry(50, 50, 1050, 780) 
        self.setStyleSheet(QSS)
        
        self.model = None
        self.labels = []
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_frame)
        self.frame_counter = 0
        self.camera_active = False

        self.load_model_data()
        self.init_ui()

    def load_model_data(self):
        model_path = 'fruit_model.h5'
        label_path = 'labels.txt'
        try:
            self.model = tf.keras.models.load_model(model_path)
            with open(label_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Lỗi tải model: {e}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)
        
        # CỘT TRÁI
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        title_lbl = QLabel("🍊 KẾT QUẢ KIỂM ĐỊNH")
        title_lbl.setObjectName("TitleLabel")
        left_layout.addWidget(title_lbl)
        
        img_frame = QFrame()
        img_frame.setObjectName("ImageFrame")
        img_frame.setGraphicsEffect(create_shadow())
        
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_img_title = QLabel("ĐỐI TƯỢNG KIỂM ĐỊNH")
        lbl_img_title.setObjectName("DataLabel")
        
        self.img_display = RoundedImageLabel(radius=12)
        self.img_display.setText("HỆ THỐNG SẴN SÀNG")
        self.img_display.setStyleSheet("color: #444; font-size: 14px; background-color: #0c0c0c; border-radius: 12px;")
        self.img_display.setFixedSize(380, 380)
        
        img_layout.addWidget(lbl_img_title)
        img_layout.addWidget(self.img_display)
        left_layout.addWidget(img_frame)
        
        btn_layout = QHBoxLayout()
        self.btn_upload = QPushButton("⇧ TẢI ẢNH LÊN")
        self.btn_upload.setObjectName("UploadBtn")
        self.btn_upload.clicked.connect(self.select_image)
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        
        self.btn_camera = QPushButton("📷 BẬT CAMERA")
        self.btn_camera.setObjectName("CameraBtn")
        self.btn_camera.setProperty("is_active", "false")
        self.btn_camera.clicked.connect(self.toggle_camera)
        self.btn_camera.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.btn_upload)
        btn_layout.addWidget(self.btn_camera)
        left_layout.addLayout(btn_layout)
        
        btn_logs = QPushButton("📜 LỊCH SỬ KIỂM ĐỊNH (LOGS)")
        btn_logs.setObjectName("LogBtn")
        btn_logs.clicked.connect(self.show_logs)
        btn_logs.setCursor(Qt.PointingHandCursor)
        left_layout.addWidget(btn_logs)
        
        main_layout.addLayout(left_layout)
        
        # CỘT PHẢI
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 30, 0, 0) 
        
        analysis_frame = QFrame()
        analysis_frame.setObjectName("AnalysisFrame")
        analysis_frame.setGraphicsEffect(create_shadow())
        
        a_layout = QVBoxLayout(analysis_frame)
        a_layout.setSpacing(20)
        a_layout.setContentsMargins(30, 30, 30, 30)
        
        a_title = QLabel("BẢNG ĐIỀU KHIỂN & PHÂN TÍCH")
        a_title.setObjectName("SectionTitle")
        a_layout.addWidget(a_title)
        
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        
        lbl_type_title = QLabel("LOẠI TRÁI CÂY")
        lbl_type_title.setObjectName("DataLabel")
        self.lbl_type_val = QLabel("---")
        self.lbl_type_val.setObjectName("DataValue")
        self.lbl_type_val.setAlignment(Qt.AlignRight)
        
        lbl_status_title = QLabel("TRẠNG THÁI AI")
        lbl_status_title.setObjectName("DataLabel")
        self.lbl_status_val = QLabel("---")
        self.lbl_status_val.setObjectName("StatusValue")
        self.lbl_status_val.setAlignment(Qt.AlignRight)
        self.lbl_status_val.setStyleSheet("color: #555555;")
        
        grid.addWidget(lbl_type_title, 0, 0)
        grid.addWidget(self.lbl_type_val, 0, 1)
        grid.addWidget(lbl_status_title, 1, 0)
        grid.addWidget(self.lbl_status_val, 1, 1)
        a_layout.addLayout(grid)
        
        pct_layout = QHBoxLayout()
        self.lbl_pct_chin = QLabel("Chín: 0%")
        self.lbl_pct_chin.setObjectName("PctLabel")
        self.lbl_pct_chin.setStyleSheet("color: #34C759;")
        self.lbl_pct_xanh = QLabel("Xanh: 0%")
        self.lbl_pct_xanh.setObjectName("PctLabel")
        self.lbl_pct_xanh.setStyleSheet("color: #FFCC00;")
        self.lbl_pct_hong = QLabel("Hỏng: 0%")
        self.lbl_pct_hong.setObjectName("PctLabel")
        self.lbl_pct_hong.setStyleSheet("color: #FF3B30;")
        
        pct_layout.addWidget(self.lbl_pct_chin)
        pct_layout.addWidget(self.lbl_pct_xanh)
        pct_layout.addWidget(self.lbl_pct_hong)
        a_layout.addLayout(pct_layout)
        
        conf_layout = QHBoxLayout()
        lbl_conf_title = QLabel("ĐỘ TIN CẬY (TỔNG HỢP)")
        lbl_conf_title.setObjectName("DataLabel")
        self.lbl_conf_val = QLabel("0.0%")
        self.lbl_conf_val.setObjectName("DataValue")
        self.lbl_conf_val.setAlignment(Qt.AlignRight)
        conf_layout.addWidget(lbl_conf_title)
        conf_layout.addWidget(self.lbl_conf_val)
        
        a_layout.addLayout(conf_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        a_layout.addWidget(self.progress_bar)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("border: 1px solid #333333;")
        a_layout.addWidget(line)
        
        qa_title = QLabel("📝 PHÂN TÍCH & LỜI KHUYÊN (EXPERT SYSTEM)")
        qa_title.setObjectName("SectionTitle")
        a_layout.addWidget(qa_title)
        
        self.lbl_qa_val = QLabel("HỆ THỐNG ĐANG CHỜ...\nVui lòng tải ảnh hoặc mở camera.")
        self.lbl_qa_val.setTextFormat(Qt.RichText)
        self.lbl_qa_val.setWordWrap(True)
        self.lbl_qa_val.setStyleSheet("color: #AAAAAA; font-size: 14px; line-height: 1.6; padding: 10px; background-color: #1A1A1A; border-radius: 8px;")
        self.lbl_qa_val.setAlignment(Qt.AlignTop)
        a_layout.addWidget(self.lbl_qa_val, 1) 
        
        right_layout.addWidget(analysis_frame)
        main_layout.addLayout(right_layout)
        
        if self.model is None:
            self.lbl_qa_val.setText("LỖI NGHIÊM TRỌNG: Không tìm thấy Model AI.")
            self.lbl_qa_val.setStyleSheet("color: #F44336; font-weight: bold;")

    def toggle_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Lỗi Camera", "Không thể kết nối với Webcam máy tính!")
                self.cap = None
                return
            self.camera_active = True
            self.btn_camera.setProperty("is_active", "true")
            self.btn_camera.style().unpolish(self.btn_camera)
            self.btn_camera.style().polish(self.btn_camera)
            self.btn_camera.setText("⏹ TẮT CAMERA")
            self.frame_counter = 0
            self.timer.start(30)
        else:
            self.camera_active = False
            self.timer.stop()
            if self.cap:
                self.cap.release()
                self.cap = None
            self.btn_camera.setProperty("is_active", "false")
            self.btn_camera.style().unpolish(self.btn_camera)
            self.btn_camera.style().polish(self.btn_camera)
            self.btn_camera.setText("📷 BẬT CAMERA")
            self.img_display.setText("ĐÃ TẮT CAMERA")
            self.img_display.setPixmap(QPixmap())

    def update_camera_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h_frame, w_frame, _ = frame_rgb.shape
            
            # Khung Ngắm (Target Box) ở giữa màn hình
            box_size = 280
            x_start = max(0, (w_frame - box_size) // 2)
            y_start = max(0, (h_frame - box_size) // 2)
            x_end = min(w_frame, x_start + box_size)
            y_end = min(h_frame, y_start + box_size)
            
            target_crop = frame_rgb[y_start:y_end, x_start:x_end]
            
            # Vẽ Khung ngắm
            cv2.rectangle(frame_rgb, (x_start, y_start), (x_end, y_end), (255, 204, 0), 3)
            text = "DAT TRAI CAY VAO O NAY"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = x_start + (box_size - text_size[0]) // 2
            text_y = y_start - 15
            cv2.rectangle(frame_rgb, (text_x - 5, text_y - text_size[1] - 5), 
                          (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
            cv2.putText(frame_rgb, text, (text_x, text_y), font, font_scale, (255, 204, 0), thickness)
            
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            square_pixmap = QPixmap(380, 380)
            square_pixmap.fill(Qt.transparent)
            painter = QPainter(square_pixmap)
            x_offset = (pixmap.width() - 380) // 2
            y_offset = (pixmap.height() - 380) // 2
            painter.drawPixmap(0, 0, pixmap, x_offset, y_offset, 380, 380)
            painter.end()

            self.img_display.setPixmap(square_pixmap)

            self.frame_counter += 1
            if self.frame_counter >= 15:
                self.frame_counter = 0
                if target_crop.shape[0] > 0 and target_crop.shape[1] > 0:
                    img_resized = cv2.resize(target_crop, IMG_SIZE)
                    img_array = np.expand_dims(img_resized, axis=0) / 255.0
                    self.run_prediction(img_array, source="Live_Camera", save_to_log=False)

    def show_logs(self):
        dialog = LogDialog(self)
        dialog.exec()

    def process_uploaded_image(self, file_path):
        """Hàm xử lý ảnh tải lên (Letterboxing để giữ đúng tỷ lệ)"""
        # Đọc ảnh gốc bằng PIL
        input_image = Image.open(file_path).convert("RGB")
        
        # Letterboxing (Căn giữa và giữ nguyên tỷ lệ, thêm viền đen)
        w, h = input_image.size
        max_dim = max(w, h)
        padded_img = Image.new("RGB", (max_dim, max_dim), (0, 0, 0))
        pad_w = (max_dim - w) // 2
        pad_h = (max_dim - h) // 2
        padded_img.paste(input_image, (pad_w, pad_h))
        
        # Resize về đúng 224x224
        # Dùng LANCZOS để ảnh mượt mà nhất
        resized_img = padded_img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
        
        # Chuyển sang dạng Array cho mô hình AI
        img_array = np.array(resized_img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        return img_array, padded_img

    def select_image(self):
        if self.camera_active:
            self.toggle_camera()
            
        if self.model is None: return
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh trái cây", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Hiện thông báo chờ
            self.lbl_qa_val.setText("ĐANG PHÂN TÍCH HÌNH ẢNH...\nVui lòng chờ trong giây lát.")
            self.lbl_qa_val.setStyleSheet("color: #2196F3; font-size: 15px; font-weight: bold; background-color: #1A1A1A;")
            QApplication.processEvents()
            
            try:
                # Xử lý Letterboxing
                img_array, padded_img = self.process_uploaded_image(file_path)
                
                # Hiển thị ảnh lên giao diện
                byte_arr = io.BytesIO()
                padded_img.save(byte_arr, format='PNG')
                qimg = QImage()
                qimg.loadFromData(byte_arr.getvalue())
                
                pixmap = QPixmap.fromImage(qimg)
                pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                
                square_pixmap = QPixmap(380, 380)
                square_pixmap.fill(Qt.transparent)
                painter = QPainter(square_pixmap)
                x_offset = (square_pixmap.width() - pixmap.width()) // 2
                y_offset = (square_pixmap.height() - pixmap.height()) // 2
                painter.drawPixmap(x_offset, y_offset, pixmap)
                painter.end()

                self.img_display.setPixmap(square_pixmap)
                
                # Chạy phân tích AI
                self.run_prediction(img_array, source=os.path.basename(file_path), save_to_log=True)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Tải Ảnh", f"Lỗi trong quá trình xử lý ảnh:\n{e}")

    def save_log(self, filename, fruit, status, conf):
        file_exists = os.path.exists("scan_logs.csv")
        with open("scan_logs.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["THỜI GIAN", "TÊN FILE", "ĐỐI TƯỢNG", "TRẠNG THÁI", "ĐỘ TIN CẬY"])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, filename, fruit, status, conf])
            
    def get_advice_html(self, loai_qua, do_chin):
        if do_chin == "Hư hỏng":
            return f"""
            <b style='color:#FF3B30; font-size:16px;'>TỪ CHỐI (REJECTED) ❌</b><br><br>
            <b>🩺 Đánh giá chất lượng:</b> Mẫu <b style='color:#FF9800;'>{loai_qua}</b> đã có dấu hiệu thối rữa, dập nát, bị vi khuẩn xâm nhập hoặc nấm mốc phát triển.<br><br>
            <b>🛠️ Đề xuất xử lý:</b> Loại bỏ <b>ngay lập tức</b> khỏi lô hàng đang kiểm định. Cần cách ly sớm để tránh lây nhiễm nấm mốc qua đường không khí sang các trái cây khỏe mạnh khác. Tiến hành vệ sinh khay chứa.
            """
            
        advice = ""
        if loai_qua == "Chuối":
            if do_chin == "Chín": advice = "Chuối đã chín vàng, lượng đường fructose và kali đạt mức hoàn hảo cho tiêu dùng. Sinh tố tự nhiên phát triển đầy đủ mùi thơm.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn xuất xưởng và bán lẻ. Khuyên người dùng bảo quản ở nhiệt độ phòng, không cho vào tủ lạnh để tránh thâm vỏ."
            elif do_chin == "Xanh": advice = "Chuối còn xanh, chứa lượng lớn tinh bột kháng và tanin gây ra vị chát. Quả chưa phát triển đủ mùi thơm.<br><br><b>🛠️ Đề xuất xử lý:</b> Phân loại vào khu vực ủ. Nên ủ kín ở nhiệt độ 20°C cùng khí Ethylene sinh học (hoặc táo/cà chua) trong 2-3 ngày để kích chín đồng loạt."
        elif loai_qua == "Cam":
            if do_chin == "Chín": advice = "Cam mọng nước, vỏ mỏng dần, lượng vitamin C và độ ngọt (Brix) đạt ngưỡng cao nhất.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn cho các dây chuyền vắt nước ép hoặc bán lẻ trái cây tươi. Bảo quản ở kho lạnh 5-10°C để kéo dài độ tươi."
            elif do_chin == "Xanh": advice = "Cam còn xanh, vỏ cứng chứa nhiều tinh dầu đắng, lượng nước ít và hàm lượng axit cao (vị chua gắt).<br><br><b>🛠️ Đề xuất xử lý:</b> Để ở nhiệt độ phòng có độ ẩm thích hợp thêm vài ngày cho quả xuống nước và tăng độ ngọt tự nhiên."
        elif loai_qua == "Táo":
            if do_chin == "Chín": advice = "Táo chín tới, cấu trúc thịt quả giòn và độ ngọt đạt đỉnh (đỉnh sinh trưởng).<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt tiêu chuẩn xuất khẩu Loại 1. Chuyển ngay vào hệ thống kho lạnh (0-4°C) để ức chế quá trình sinh hơi Ethylene, giúp duy trì độ giòn."
            elif do_chin == "Xanh": advice = "Táo chưa đạt tiêu chuẩn độ đường (Brix), thịt quả cứng và có vị chát nhẹ.<br><br><b>🛠️ Đề xuất xử lý:</b> Đặt ở môi trường thoáng mát vài ngày. Táo tự sinh khí ethylene nên sẽ tự làm chín rất nhanh chóng."
        elif loai_qua == "Dâu Tây":
            if do_chin == "Chín": advice = "Dâu chín đỏ mọng toàn phần, hương thơm nồng nàn đặc trưng, rất dễ bị dập.<br><br><b>🛠️ Đề xuất xử lý:</b> Phải phân phối ngay trong ngày. Nếu lưu kho, bắt buộc bảo quản ngăn mát tủ lạnh và dùng trong tối đa 3 ngày. Tránh rửa nước khi chưa sử dụng."
            elif do_chin == "Xanh": advice = "Phần lớn vỏ quả còn trắng hoặc xanh non. Dâu tây đặc biệt <b>KHÔNG</b> tự chín thêm sau khi đã bị hái khỏi cây.<br><br><b>🛠️ Đề xuất xử lý:</b> Không đạt chuẩn ăn tươi do quá chua. Đề xuất chuyển thẳng sang các xưởng chế biến công nghiệp để ngâm đường, sấy khô hoặc làm mứt."
        elif loai_qua == "Ổi":
            if do_chin == "Chín": advice = "Ổi đã mềm, có hương thơm lan tỏa cực mạnh, thịt quả xốp và ngọt.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn cho nhu cầu ăn ổi mềm hoặc đưa vào dây chuyền ép nước trái cây đóng chai."
            elif do_chin == "Xanh": advice = "Ổi cứng, vỏ xanh đậm, vị chát do lượng tanin còn rất cao.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn cho phân khúc khách hàng thích ăn ổi giòn. Nếu muốn ăn mềm, người dùng cần ủ thêm 2-4 ngày ở nhiệt độ phòng."
        elif loai_qua == "Nho":
            if do_chin == "Chín": advice = "Nho chín mọng, lớp vỏ căng bóng, độ đường phân bố đều toàn chùm.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn cao cấp. Đóng gói vào hộp nhựa có lỗ thoáng khí và chuyển vào kho lạnh bảo quản ngay lập tức để tránh lên men."
            elif do_chin == "Xanh": advice = "Nho chưa chín kỹ, vị chua gắt. Giống như Dâu Tây, Nho không có khả năng tự chín thêm sau khi hái.<br><br><b>🛠️ Đề xuất xử lý:</b> Đề xuất chuyển loại này sang các dây chuyền ép nước trái cây hỗn hợp chua ngọt hoặc ủ rượu vang non."
        elif loai_qua == "Lựu":
            if do_chin == "Chín": advice = "Vỏ lựu căng, hạt bên trong đỏ thẫm và chứa lượng nước tối đa.<br><br><b>🛠️ Đề xuất xử lý:</b> Hoàn toàn đạt chuẩn thu hoạch. Tách hạt bán tươi hoặc chuyển qua khâu ép nước giải khát."
            elif do_chin == "Xanh": advice = "Lựu chưa chín, vỏ còn rất cứng, hạt nhạt màu và chát.<br><br><b>🛠️ Đề xuất xử lý:</b> Lựu chín khá chậm. Cần để trong môi trường tối, thoáng mát ở nhiệt độ phòng vài ngày chờ chuyển hóa đường."
        else:
            if do_chin == "Chín": advice = "Trái cây đã đạt độ chín.<br><br><b>🛠️ Đề xuất xử lý:</b> Đạt chuẩn tiêu dùng. Đưa ra thị trường hoặc bảo quản kho lạnh."
            elif do_chin == "Xanh": advice = "Chưa đạt tiêu chuẩn độ chín tự nhiên.<br><br><b>🛠️ Đề xuất xử lý:</b> Đưa vào kho ủ thêm thời gian để đạt độ ngọt chuẩn."

        color = "#34C759" if do_chin == "Chín" else "#FFCC00"
        status = "ĐẠT CHUẨN (APPROVED) ✅" if do_chin == "Chín" else "CẢNH BÁO (WARNING) ⚠️"
        
        return f"""
        <b style='color:{color}; font-size:16px;'>{status}</b><br><br>
        <b>🩺 Đánh giá chất lượng:</b> {advice}
        """

    def run_prediction(self, img_array, source, save_to_log=True):
        if not self.camera_active:
            # Chỉ cập nhật trạng thái nếu không báo Xóa phông trước đó
            if "ĐANG XÓA PHÔNG" not in self.lbl_qa_val.text():
                self.lbl_qa_val.setText("ĐANG PHÂN TÍCH MẠNG NEURAL...")
                self.lbl_qa_val.setStyleSheet("color: #FF9800; font-size: 15px; font-weight: bold; background-color: #1A1A1A;")
                QApplication.processEvents()
        
        try:
            predictions = self.model.predict(img_array, verbose=0)
            best_idx = np.argmax(predictions[0])
            predicted_label = self.labels[best_idx]
            
            loai_qua = "Chưa rõ"
            do_chin = "Chưa rõ"
            
            if "Apple" in predicted_label: loai_qua = "Táo"
            elif "Banana" in predicted_label: loai_qua = "Chuối"
            elif "Grape" in predicted_label: loai_qua = "Nho"
            elif "Orange" in predicted_label: loai_qua = "Cam"
            elif "Guava" in predicted_label: loai_qua = "Ổi"
            elif "Pomegranate" in predicted_label: loai_qua = "Lựu"
            elif "Strawberry" in predicted_label: loai_qua = "Dâu Tây"
                
            if "Ripe" in predicted_label and "Unripe" not in predicted_label: do_chin = "Chín"
            elif "Unripe" in predicted_label: do_chin = "Xanh"
            elif "Rotten" in predicted_label: do_chin = "Hư hỏng"
            
            prob_chin, prob_xanh, prob_hu_hong = 0.0, 0.0, 0.0
            for i, label in enumerate(self.labels):
                if "Ripe" in label and "Unripe" not in label: prob_chin += predictions[0][i] * 100
                elif "Unripe" in label: prob_xanh += predictions[0][i] * 100
                elif "Rotten" in label: prob_hu_hong += predictions[0][i] * 100

            if do_chin == "Chín": confidence = prob_chin
            elif do_chin == "Xanh": confidence = prob_xanh
            else: confidence = prob_hu_hong
                
            if confidence > 99.9: confidence = 99.9 
            
            self.lbl_pct_chin.setText(f"Chín: {prob_chin:.1f}%")
            self.lbl_pct_xanh.setText(f"Xanh: {prob_xanh:.1f}%")
            self.lbl_pct_hong.setText(f"Hỏng: {prob_hu_hong:.1f}%")
            
            if do_chin == "Hư hỏng":
                color = "#FF3B30"
                status_dot = "● HƯ HỎNG (ROTTEN)"
            elif do_chin == "Xanh":
                color = "#FFCC00"
                status_dot = "● QUẢ XANH (UNRIPE)"
            elif do_chin == "Chín":
                color = "#34C759"
                status_dot = "● CHÍN ĐẠT CHUẨN"
            else:
                color = "#FF3B30"
                status_dot = "● LỖI (ERROR)"
                
            self.lbl_type_val.setText(f"{loai_qua.upper()}")
            self.lbl_status_val.setText(status_dot)
            self.lbl_status_val.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            
            self.lbl_conf_val.setText(f"{confidence:.1f}%")
            self.lbl_conf_val.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            self.progress_bar.setValue(int(confidence))
            
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #252525; border: none; border-radius: 4px; height: 8px; }}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
            """)
            
            ket_luan_html = self.get_advice_html(loai_qua, do_chin)
            
            self.lbl_qa_val.setText(ket_luan_html)
            self.lbl_qa_val.setStyleSheet("color: #AAAAAA; font-size: 14px; line-height: 1.6; padding: 10px; background-color: #1A1A1A; border-radius: 8px;")

            if save_to_log:
                self.save_log(source, loai_qua, do_chin, f"{confidence:.1f}%")
            
        except Exception as e:
            self.lbl_qa_val.setText(f"LỖI HỆ THỐNG:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FruitScannerApp()
    window.show()
    sys.exit(app.exec())
